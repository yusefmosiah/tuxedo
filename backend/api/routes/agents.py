"""
Agent Management API Routes
Handles creation and management of AI agents with Stellar accounts
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import secrets
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Request models
class CreateAgentRequest(BaseModel):
    initial_prompt: str
    agent_name: Optional[str] = None

class AgentResponse(BaseModel):
    id: str
    agent_name: str
    stellar_address: str
    created_at: str
    permissions: str

class ThreadResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str

class CreateAgentResponse(BaseModel):
    success: bool
    agent: Optional[AgentResponse] = None
    thread: Optional[ThreadResponse] = None
    error: Optional[str] = None

async def get_current_user(request):
    """Get current authenticated user from session token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No authentication token provided")

    session_token = auth_header[7:]  # Remove "Bearer " prefix

    # Try passkey session validation first
    from database import db
    session = db.validate_passkey_session(session_token)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session

@router.post("/create", response_model=CreateAgentResponse)
async def create_agent(req: CreateAgentRequest, request):
    """Create new AI agent with Stellar account"""
    try:
        current_user = await get_current_user(request)

        # Import database and key derivation
        from database import DatabaseManager
        from crypto.key_derivation import KeyDerivation

        db_manager = DatabaseManager()
        conn = sqlite3.connect(db_manager.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get user's credentials to derive master keypair
            cursor.execute(
                """SELECT pc.* FROM passkey_credentials pc
                   WHERE pc.user_id = ? LIMIT 1""",
                (current_user['user_id'],)
            )
            credential = cursor.fetchone()

            if not credential:
                raise HTTPException(400, "No passkey found for user")

            # Get user's info for key derivation
            user_info = {
                'id': current_user['user_id'],
                'email': current_user['email']
            }

            # Get next agent index
            cursor.execute(
                """SELECT COUNT(*) as count FROM agents WHERE user_id = ?""",
                (current_user['user_id'],)
            )
            agent_count = cursor.fetchone()['count']

            # Derive user's master keypair (using server-side fallback)
            server_secret = KeyDerivation.get_server_secret()
            user_keypair = KeyDerivation.derive_from_server(
                user_info['id'], credential['credential_id'], server_secret
            )

            # Derive agent keypair from user's master keypair
            agent_keypair = KeyDerivation.generate_agent_keypair(user_keypair, agent_count)

            # Create agent
            agent_id = f"agent_{secrets.token_urlsafe(16)}"
            agent_name = req.agent_name or f"Agent {agent_count + 1}"

            cursor.execute(
                """INSERT INTO agents (id, user_id, agent_name, stellar_address, encrypted_private_key)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    agent_id,
                    current_user['user_id'],
                    agent_name,
                    agent_keypair.public_key,
                    ""  # Don't store private key if derivable
                )
            )

            # Create thread for agent
            thread_id = f"thread_{secrets.token_urlsafe(16)}"
            thread_title = f"{agent_name}: {req.initial_prompt[:50]}{'...' if len(req.initial_prompt) > 50 else ''}"

            cursor.execute(
                """INSERT INTO threads (id, user_id, agent_id, title)
                   VALUES (?, ?, ?, ?)""",
                (thread_id, current_user['user_id'], agent_id, thread_title)
            )

            # Add initial message
            message_id = f"msg_{secrets.token_urlsafe(16)}"
            cursor.execute(
                """INSERT INTO messages (id, thread_id, role, content)
                   VALUES (?, ?, ?, ?)""",
                (
                    message_id,
                    thread_id,
                    "user",
                    req.initial_prompt
                )
            )

            conn.commit()

            return CreateAgentResponse(
                success=True,
                agent=AgentResponse(
                    id=agent_id,
                    agent_name=agent_name,
                    stellar_address=agent_keypair.public_key,
                    created_at=datetime.now().isoformat(),
                    permissions="trade"
                ),
                thread=ThreadResponse(
                    id=thread_id,
                    title=thread_title,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
            )

        except sqlite3.Error as e:
            conn.rollback()
            raise HTTPException(500, f"Database error: {str(e)}")
        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to create agent: {str(e)}")

@router.get("/", response_model=Dict[str, List[AgentResponse]])
async def get_agents(request):
    """Get all agents for current user"""
    try:
        current_user = await get_current_user(request)

        from database import DatabaseManager
        db_manager = DatabaseManager()
        conn = sqlite3.connect(db_manager.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """SELECT * FROM agents
                   WHERE user_id = ? AND is_active = TRUE
                   ORDER BY created_at DESC""",
                (current_user['user_id'],)
            )

            agents = []
            for row in cursor.fetchall():
                agents.append(AgentResponse(
                    id=row['id'],
                    agent_name=row['agent_name'],
                    stellar_address=row['stellar_address'],
                    created_at=row['created_at'],
                    permissions=row['permissions']
                ))

            return {"agents": agents}

        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get agents: {str(e)}")

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, request):
    """Get specific agent by ID"""
    try:
        current_user = await get_current_user(request)

        from database import DatabaseManager
        db_manager = DatabaseManager()
        conn = sqlite3.connect(db_manager.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """SELECT * FROM agents
                   WHERE id = ? AND user_id = ? AND is_active = TRUE""",
                (agent_id, current_user['user_id'])
            )

            agent = cursor.fetchone()
            if not agent:
                raise HTTPException(404, "Agent not found")

            return AgentResponse(
                id=agent['id'],
                agent_name=agent['agent_name'],
                stellar_address=agent['stellar_address'],
                created_at=agent['created_at'],
                permissions=agent['permissions']
            )

        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get agent: {str(e)}")

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, request):
    """Delete/deactivate an agent"""
    try:
        current_user = await get_current_user(request)

        from database import DatabaseManager
        db_manager = DatabaseManager()
        conn = sqlite3.connect(db_manager.db_path)
        try:
            cursor = conn.cursor()

            # Soft delete by setting is_active = FALSE
            cursor.execute(
                """UPDATE agents SET is_active = FALSE
                   WHERE id = ? AND user_id = ?""",
                (agent_id, current_user['user_id'])
            )

            if cursor.rowcount == 0:
                raise HTTPException(404, "Agent not found")

            conn.commit()

            return {"success": True, "message": "Agent deactivated successfully"}

        except sqlite3.Error as e:
            conn.rollback()
            raise HTTPException(500, f"Database error: {str(e)}")
        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete agent: {str(e)}")