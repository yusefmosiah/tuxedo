"""
Threads API Routes
Endpoints for chat thread management functionality.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
import uuid
from datetime import datetime
from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models (matching frontend expectations)
class Thread(BaseModel):
    id: str
    title: str
    wallet_address: Optional[str] = None
    created_at: str
    updated_at: str
    is_archived: bool

class ThreadCreate(BaseModel):
    title: str
    # wallet_address removed - threads now belong to authenticated users

class ThreadUpdate(BaseModel):
    title: Optional[str] = None

class MessageWithMetadata(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str

# Database integration using SQLite
from database import db

def get_thread_dict(thread_id: str) -> Optional[Dict[str, Any]]:
    """Get thread data as dict"""
    return db.get_thread(thread_id)


# Helper function to get authenticated user from session
async def get_authenticated_user(request: Request, session_token: Optional[str] = None) -> dict:
    """Get authenticated user from session token"""
    # Get session token from multiple sources
    if not session_token:
        session_token = request.cookies.get("session_token")

    if not session_token:
        session_token = request.headers.get("Authorization")
        if session_token and session_token.startswith("Bearer "):
            session_token = session_token[7:]  # Remove "Bearer " prefix

    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_session = db.validate_user_session(session_token)
    if not user_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user_session

@router.post("/threads", response_model=Thread)
async def create_thread(
    thread_data: ThreadCreate,
    request: Request,
    session_token: Optional[str] = None
):
    """Create a new chat thread for authenticated user"""
    try:
        # Get authenticated user
        user = await get_authenticated_user(request, session_token)

        # Create thread for user
        thread_id = db.create_thread(title=thread_data.title, user_id=user['user_id'])
        thread = db.get_thread(thread_id)

        if not thread:
            raise HTTPException(status_code=500, detail="Failed to create thread")

        logger.info(f"Created thread {thread_id} for user {user['email']}: {thread_data.title}")
        return Thread(**thread)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")

@router.get("/threads", response_model=List[Thread])
async def get_threads(
    request: Request,
    session_token: Optional[str] = None,
    limit: int = Query(50, le=100)
):
    """Get all threads for authenticated user"""
    try:
        # Get authenticated user
        user = await get_authenticated_user(request, session_token)

        # Get threads for user
        threads = db.get_threads(user_id=user['user_id'], limit=limit)
        return [Thread(**thread) for thread in threads]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting threads: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting threads: {str(e)}")

@router.get("/threads/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str):
    """Get a specific thread"""
    try:
        thread = get_thread_dict(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        if thread.get('is_archived', False):
            raise HTTPException(status_code=404, detail="Thread not found")

        return Thread(**thread)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting thread: {str(e)}")

@router.put("/threads/{thread_id}", response_model=Thread)
async def update_thread(thread_id: str, thread_data: ThreadUpdate):
    """Update a thread title"""
    try:
        success = db.update_thread(thread_id, title=thread_data.title)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        thread = db.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        return Thread(**thread)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating thread: {str(e)}")

@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread"""
    try:
        success = db.delete_thread(thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        logger.info(f"Deleted thread {thread_id}")
        return {"message": "Thread deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting thread: {str(e)}")

@router.post("/threads/{thread_id}/archive")
async def archive_thread(thread_id: str):
    """Archive a thread"""
    try:
        success = db.archive_thread(thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        logger.info(f"Archived thread {thread_id}")
        return {"message": "Thread archived successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error archiving thread: {str(e)}")

@router.get("/threads/{thread_id}/messages", response_model=List[MessageWithMetadata])
async def get_thread_messages(thread_id: str):
    """Get all messages for a thread"""
    try:
        thread = db.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        messages = db.get_messages(thread_id)
        return [MessageWithMetadata(**msg) for msg in messages]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting thread messages: {str(e)}")

@router.post("/threads/{thread_id}/messages")
async def save_thread_messages(thread_id: str, messages: List[Dict[str, Any]]):
    """Save messages to a thread"""
    try:
        thread = db.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Use the database method to update messages
        success = db.update_thread_from_chat_messages(thread_id, messages)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save messages")

        logger.info(f"Saved {len(messages)} messages to thread {thread_id}")
        return {"message": f"Saved {len(messages)} messages successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving messages to thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving thread messages: {str(e)}")