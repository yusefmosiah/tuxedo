"""
Authentication API Routes
Handles passkey session validation and user authentication.
"""

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Import database
from database import db

# Pydantic models
class AuthResponse(BaseModel):
    success: bool
    session_token: Optional[str] = None
    user: Optional[dict] = None
    message: str

class UserResponse(BaseModel):
    id: str
    email: str
    stellar_public_key: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None

class SessionValidateRequest(BaseModel):
    session_token: str

@router.post("/auth/validate-passkey-session", response_model=AuthResponse)
async def validate_passkey_session(request: SessionValidateRequest, req: Request):
    """Validate passkey session token and return user info"""
    try:
        # Validate session using database
        session = db.validate_passkey_session(request.session_token)

        if not session:
            return AuthResponse(
                success=False,
                message="Invalid or expired session"
            )

        # Update last login
        conn = sqlite3.connect(db.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), session['user_id'])
            )
            conn.commit()
        finally:
            conn.close()

        return AuthResponse(
            success=True,
            session_token=session['session_token'],
            user={
                "id": session['user_id'],
                "email": session['email'],
                "stellar_public_key": session.get('stellar_public_key')
            },
            message="Session valid"
        )

    except Exception as e:
        logger.error(f"Session validation error: {str(e)}")
        return AuthResponse(
            success=False,
            message="Session validation failed"
        )

@router.get("/auth/user", response_model=UserResponse)
async def get_user_info(request: Request):
    """Get current user info from valid session"""
    # Extract session token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session token provided"
        )

    session_token = auth_header.split(" ")[1]

    # Validate session
    session = db.validate_passkey_session(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return UserResponse(
        id=session['user_id'],
        email=session['email'],
        stellar_public_key=session.get('stellar_public_key'),
        created_at=session.get('created_at', ''),
        last_login=session.get('last_login')
    )

@router.post("/auth/logout")
async def logout(request: Request):
    """Logout user by invalidating session"""
    # Extract session token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session token provided"
        )

    session_token = auth_header.split(" ")[1]

    # Remove session from database
    conn = sqlite3.connect(db.db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM passkey_sessions WHERE session_token = ?",
            (session_token,)
        )
        conn.commit()
    finally:
        conn.close()

    return {"success": True, "message": "Logged out successfully"}

# Health check endpoint
@router.get("/auth/health")
async def health_check():
    """Authentication service health check"""
    return {"status": "healthy", "service": "authentication", "type": "passkey-only"}