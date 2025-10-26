#!/usr/bin/env python3
"""
FastAPI + MCP backend for Tuxedo AI
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastMCP removed - using local Stellar tools directly

# Import LangChain
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import local Stellar tools
try:
    from stellar_tools import account_manager, trading, market_data
    from stellar_sdk import Server
    from key_manager import KeyManager
    STELLAR_TOOLS_AVAILABLE = True
    logger.info("Local Stellar tools loaded successfully")
except ImportError as e:
    logger.warning(f"Stellar tools not available: {e}")
    STELLAR_TOOLS_AVAILABLE = False

# Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str
    success: bool = True
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    stellar_tools_ready: bool
    openai_configured: bool

class StellarToolsResponse(BaseModel):
    available: bool
    tools_count: int
    tools: list[str]
    last_check: str

# Global variables
llm: Optional[ChatOpenAI] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global llm

    logger.info("Starting Tuxedo AI backend...")

    # Initialize LLM
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    if openai_api_key:
        llm = ChatOpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url,
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000,
        )
        logger.info("LLM initialized successfully")
    else:
        logger.warning("OpenAI API key not configured")

    logger.info("Stellar tools loaded locally")

    yield

    logger.info("Shutting down Tuxedo AI backend...")

# Create FastAPI app
app = FastAPI(
    title="Tuxedo AI Backend",
    description="FastAPI + FastMCP backend for Tuxedo AI conversational DeFi assistant",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    return {"message": "Tuxedo AI Backend is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        stellar_tools_ready=STELLAR_TOOLS_AVAILABLE,
        openai_configured=bool(os.getenv("OPENAI_API_KEY"))
    )

@app.get("/stellar-tools/status")
async def stellar_tools_status():
    """Get available Stellar tools and their status"""
    from datetime import datetime

    tools = []
    if STELLAR_TOOLS_AVAILABLE:
        tools = [
            "account_manager_tool",
            "trading_tool",
            "trustline_manager_tool",
            "market_data_tool",
            "utilities_tool"
        ]

    return StellarToolsResponse(
        available=STELLAR_TOOLS_AVAILABLE,
        tools_count=len(tools),
        tools=tools,
        last_check=datetime.now().isoformat()
    )

@app.post("/chat")
async def chat_message(request: ChatRequest):
    """Chat endpoint with LLM integration"""
    try:
        if not llm:
            raise HTTPException(
                status_code=503,
                detail="LLM not initialized"
            )

        # System prompt for Tuxedo AI
        system_prompt = """You are Tuxedo, an AI assistant that helps users discover and understand lending opportunities on Stellar through the Blend Protocol.

**Your Capabilities:**
- Query all active Blend pools to find current APY rates
- Access Stellar account information and balances
- Perform Stellar operations via available tools
- Explain DeFi lending concepts in simple, clear language
- Compare different pools and assets
- Assess risk based on utilization rates and pool metrics

**Key Principles:**
1. **Plain language first** - Avoid DeFi jargon unless the user asks for technical details
2. **Always explain risks** - High APY usually means higher risk (utilization, volatility, liquidity)
3. **Be transparent** - Yields come from borrowers paying interest to lenders
4. **Never promise returns** - Always say "current rate" or "estimated APY based on today's data"
5. **Show your work** - When comparing pools, show the numbers (APY, utilization, TVL)

**Current Context:**
- User is exploring Blend pools on Stellar testnet
- This is for educational/informational purposes
- Focus on helping users understand opportunities and risks"""

        # Build message history
        messages = [
            SystemMessage(content=system_prompt),
            *[HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)
              for msg in request.history],
            HumanMessage(content=request.message),
        ]

        # Get LLM response
        response = await llm.ainvoke(messages)

        return ChatResponse(response=response.content, success=True)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

async def call_stellar_tool(tool_name: str, arguments: dict) -> str:
    """Call Stellar tools directly"""
    if not STELLAR_TOOLS_AVAILABLE:
        return "Stellar tools not available. Please check dependencies."

    try:
        logger.info(f"Calling Stellar tool: {tool_name} with args: {arguments}")

        # Initialize Stellar components
        horizon = Server("https://horizon-testnet.stellar.org")
        key_manager = KeyManager()

        if tool_name == "account_manager_tool":
            return account_manager(
                horizon=horizon,
                key_manager=key_manager,
                **arguments
            )
        elif tool_name == "trading_tool":
            return trading(
                horizon=horizon,
                key_manager=key_manager,
                **arguments
            )
        elif tool_name == "market_data_tool":
            return market_data(
                horizon=horizon,
                **arguments
            )
        else:
            return f"Unknown tool: {tool_name}. Available tools: account_manager_tool, trading_tool, market_data_tool"

    except Exception as e:
        logger.error(f"Error calling Stellar tool {tool_name}: {e}")
        return f"Error calling Stellar tool {tool_name}: {str(e)}"

@app.post("/stellar-tool/{tool_name}")
async def test_stellar_tool(tool_name: str, arguments: dict = None):
    """Test a Stellar tool call directly"""
    if arguments is None:
        arguments = {}

    try:
        result = await call_stellar_tool(tool_name, arguments)
        return {"tool": tool_name, "arguments": arguments, "result": result, "success": True}
    except Exception as e:
        return {"tool": tool_name, "arguments": arguments, "error": str(e), "success": False}

if __name__ == "__main__":
    import uvicorn

    # Run FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )