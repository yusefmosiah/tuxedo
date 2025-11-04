"""
Chat API Routes
Endpoints for AI agent chat functionality.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
import json
import asyncio
from live_summary_service import get_live_summary_service, is_live_summary_enabled
from agent.core import process_agent_message_streaming

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
    async def generate_chat_stream():
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

    return StreamingResponse(
        generate_chat_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

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

# Add endpoints to match frontend expectations
@router.post("/chat-stream")
async def chat_stream_endpoint_alias(request: StreamChatRequest):
    """Alias for /chat/stream to match frontend expectations"""
    return await chat_stream_endpoint(request)

@router.post("/chat-live-summary")
async def chat_live_summary_endpoint(request: StreamChatRequest):
    """Chat with live summary and streaming agent execution"""
    async def generate_stream():
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

            # Get the live summary service
            summary_service = get_live_summary_service()

            # Collect all messages for final summary
            all_messages = []
            agent_response_content = ""

            # Stream the agent execution
            async for event in process_agent_message_streaming(
                message=request.message,
                history=history,
                agent_account=request.agent_account
            ):
                # Convert event to SSE format
                yield f"data: {json.dumps(event)}\n\n"

                # Collect messages for summary
                if event["type"] in ["llm_response", "tool_result", "agent_complete"]:
                    all_messages.append({
                        "type": event["type"],
                        "content": event["content"],
                        "tool_name": event.get("tool_name", ""),
                        "iteration": event.get("iteration", 0)
                    })

                # Save the final response
                if event["type"] == "agent_complete":
                    agent_response_content = event["content"]

            # Generate live summary if available
            if is_live_summary_enabled() and all_messages:
                try:
                    # Prepare messages for summarization
                    messages_for_summary = [
                        {"role": "user", "content": request.message},
                        {"role": "assistant", "content": agent_response_content}
                    ]

                    # Add history if available
                    for msg in history:
                        messages_for_summary.append(msg)

                    # Add all tool results for comprehensive summary
                    for msg in all_messages:
                        if msg["type"] == "tool_result":
                            messages_for_summary.append({
                                "role": "tool",
                                "content": f"[{msg['tool_name']}] {msg['content']}"
                            })

                    # Generate final summary
                    final_summary = await summary_service.generate_final_summary(messages_for_summary)

                    summary_event = {
                        "type": "final_summary",
                        "content": final_summary,
                        "summary": final_summary,
                        "iterations_used": event.get("iterations_used", 0)
                    }
                    yield f"data: {json.dumps(summary_event)}\n\n"

                except Exception as e:
                    logger.error(f"Error generating final summary: {e}")
                    summary_event = {
                        "type": "final_summary",
                        "content": f"Completed after {event.get('iterations_used', 0)} iterations",
                        "summary": f"Completed: {request.message[:50]}...",
                        "iterations_used": event.get("iterations_used", 0)
                    }
                    yield f"data: {json.dumps(summary_event)}\n\n"

            # Signal completion
            done_event = {
                "type": "done",
                "content": "Processing complete",
                "success": True
            }
            yield f"data: {json.dumps(done_event)}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            error_data = {
                "type": "error",
                "content": f"Error processing your request: {str(e)}",
                "success": False
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )