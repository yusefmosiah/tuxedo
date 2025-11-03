"""
Chat API Routes
Endpoints for AI agent chat functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    agent_account: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None
    tools_available: Optional[int] = None
    agent_account: Optional[str] = None

class StreamChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    agent_account: Optional[str] = None
    enable_summary: bool = False

# Import agent system
try:
    from agent.core import process_agent_message, get_agent_status
    AGENT_SYSTEM_AVAILABLE = True
    logger.info("Agent system loaded successfully")
except ImportError as e:
    logger.warning(f"Agent system not available: {e}")
    AGENT_SYSTEM_AVAILABLE = False

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process a chat message through the AI agent"""
    if not AGENT_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent system not available")

    try:
        # Convert request history to dict format
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        # Process message through agent
        response = await process_agent_message(
            message=request.message,
            history=history,
            agent_account=request.agent_account
        )

        return ChatResponse(**response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/chat/stream")
async def chat_stream_endpoint(request: StreamChatRequest):
    """Stream chat response through the AI agent"""
    if not AGENT_SYSTEM_AVAILABLE:
        # Return error as SSE
        error_data = {
            "type": "error",
            "content": "Agent system not available"
        }
        yield f"data: {json.dumps(error_data)}\n\n"
        return

    try:
        # Convert request history to dict format
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        # For now, use non-streaming response (can be enhanced later)
        response = await process_agent_message(
            message=request.message,
            history=history,
            agent_account=request.agent_account
        )

        # Stream the response as data chunks
        if response.get("success", False):
            content = response.get("response", "")

            # Send streaming data
            message_data = {
                "type": "message",
                "content": content,
                "iteration": 1,
                "isStreaming": False
            }
            yield f"data: {json.dumps(message_data)}\n\n"
        else:
            # Send error
            error_data = {
                "type": "error",
                "content": response.get("error", "Unknown error")
            }
            yield f"data: {json.dumps(error_data)}\n\n"

        # Send completion signal
        done_data = {"type": "done"}
        yield f"data: {json.dumps(done_data)}\n\n"

    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        error_data = {
            "type": "error",
            "content": f"Internal server error: {str(e)}"
        }
        yield f"data: {json.dumps(error_data)}\n\n"

@router.get("/chat/status")
async def chat_status():
    """Get chat system status"""
    if not AGENT_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent system not available")

    try:
        status = await get_agent_status()
        return status
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")