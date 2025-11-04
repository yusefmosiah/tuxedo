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
    wallet_address: Optional[str] = None

class ThreadUpdate(BaseModel):
    title: Optional[str] = None

class MessageWithMetadata(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str

# Database integration (simple in-memory for now)
# In production, this should use the database.py implementation
_threads_db = {}
_messages_db = {}

def get_thread_dict(thread_id: str) -> Optional[Dict[str, Any]]:
    """Get thread data as dict"""
    return _threads_db.get(thread_id)

def get_threads_list(wallet_address: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get threads list"""
    threads = list(_threads_db.values())

    if wallet_address:
        threads = [t for t in threads if t.get('wallet_address') == wallet_address]

    # Filter out archived threads
    threads = [t for t in threads if not t.get('is_archived', False)]

    # Sort by updated_at
    threads.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

    return threads[:limit]

@router.post("/threads", response_model=Thread)
async def create_thread(thread_data: ThreadCreate):
    """Create a new chat thread"""
    try:
        thread_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        thread = {
            "id": thread_id,
            "title": thread_data.title,
            "wallet_address": thread_data.wallet_address,
            "created_at": now,
            "updated_at": now,
            "is_archived": False
        }

        _threads_db[thread_id] = thread
        logger.info(f"Created thread {thread_id}: {thread_data.title}")

        return Thread(**thread)
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")

@router.get("/threads", response_model=List[Thread])
async def get_threads(
    wallet_address: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    """Get all threads for a wallet"""
    try:
        threads = get_threads_list(wallet_address=wallet_address, limit=limit)
        return [Thread(**thread) for thread in threads]
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
        thread = get_thread_dict(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        if thread_data.title:
            thread["title"] = thread_data.title
            thread["updated_at"] = datetime.now().isoformat()
            _threads_db[thread_id] = thread

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
        if thread_id not in _threads_db:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Delete thread and its messages
        del _threads_db[thread_id]
        if thread_id in _messages_db:
            del _messages_db[thread_id]

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
        thread = get_thread_dict(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        thread["is_archived"] = True
        thread["updated_at"] = datetime.now().isoformat()
        _threads_db[thread_id] = thread

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
        thread = get_thread_dict(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        messages = _messages_db.get(thread_id, [])
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
        thread = get_thread_dict(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Convert messages to proper format and add metadata
        saved_messages = []
        for i, msg in enumerate(messages):
            message_id = str(uuid.uuid4())
            now = datetime.now().isoformat()

            message_data = {
                "id": message_id,
                "thread_id": thread_id,
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
                "metadata": {
                    "type": msg.get("type", "chat"),
                    "toolName": msg.get("toolName"),
                    "iteration": msg.get("iteration"),
                    "isStreaming": msg.get("isStreaming", False),
                    "summary": msg.get("summary")
                },
                "created_at": now
            }
            saved_messages.append(message_data)

        _messages_db[thread_id] = saved_messages

        # Update thread's updated_at
        thread["updated_at"] = now
        _threads_db[thread_id] = thread

        logger.info(f"Saved {len(messages)} messages to thread {thread_id}")
        return {"message": f"Saved {len(messages)} messages successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving messages to thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving thread messages: {str(e)}")