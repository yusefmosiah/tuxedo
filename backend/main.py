#!/usr/bin/env python3
"""
FastAPI + FastMCP backend for Tuxedo AI
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

# Import FastMCP
try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Install with: uv add fastmcp")
    FastMCP = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    fastmcp_ready: bool
    openai_configured: bool

# Global variables
mcp_server: Optional[FastMCP] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global mcp_server

    logger.info("Starting Tuxedo AI backend...")

    # Initialize FastMCP server
    if FastMCP is not None:
        mcp_server = FastMCP("Tuxedo AI 🚀")

        # Add Stellar tools
        setup_stellar_tools(mcp_server)

        logger.info("FastMCP server initialized")
    else:
        logger.warning("FastMCP not available")

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
        fastmcp_ready=mcp_server is not None,
        openai_configured=bool(os.getenv("OPENAI_API_KEY"))
    )

@app.post("/chat")
async def chat_message(request: ChatRequest):
    """Chat endpoint - simple version without tool calling for now"""
    try:
        # For now, return a simple response
        # TODO: Integrate with LLM and FastMCP tools

        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured"
            )

        # Simple rule-based responses for development
        message_lower = request.message.lower()

        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            response = "👋 Hello! I'm Tuxedo, your AI assistant for Stellar DeFi. Ask me about Blend pools, yields, or lending opportunities!"
        elif any(word in message_lower for word in ["pool", "apy", "yield", "lending"]):
            response = """I can help you find the best lending opportunities on Stellar!

Currently, I'm in development mode, but here's what I'll be able to do:
- 🏊‍♂️ Query all Blend pools for current APY rates
- 📊 Compare pools by yield, utilization, and risk
- 🎓 Explain DeFi concepts in plain language
- ⚠️ Help you understand the risks involved

Would you like to know more about how Blend lending works, or shall we look at current yields?"""
        elif any(word in message_lower for word in ["risk", "risky", "safe"]):
            response = """Great question! Here are the main risks to consider:

**🔒 Smart Contract Risk**: All DeFi carries some smart contract risk. Blend has been audited but no system is 100% risk-free.

**📈 Utilization Risk**: When pools are highly utilized (>90%), withdrawals might be delayed. Lower utilization = safer but lower yields.

**💰 Market Risk**: Stablecoins like USDC are less volatile, but crypto assets can have large price swings.

**🏦 Protocol Risk**: Changes to the Blend protocol could affect your positions.

My recommendation: Start with stablecoin lending to learn the system before taking on more risk!"""
        else:
            response = f"I received your message: '{request.message}'. I'm currently in development mode, but soon I'll be able to help you with:\n\n- Finding the best Blend pool yields\n- Understanding DeFi risks\n- Comparing lending opportunities\n- Account analysis and recommendations\n\nFor now, try asking about 'pools', 'yields', or 'risks'!"

        return ChatResponse(response=response, success=True)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

def setup_stellar_tools(mcp: FastMCP):
    """Setup Stellar-related tools for FastMCP"""

    @mcp.tool
    def get_blend_pools() -> str:
        """Get all active Blend lending pools with current APY rates and metrics"""
        # TODO: Implement actual Blend pool data fetching
        return """{
  "pools": [
    {
      "name": "Comet Pool",
      "address": "CD5Z7O...H3K2L",
      "reserves": [
        {
          "asset": "USDC",
          "supply_apy": "12.5%",
          "borrow_apy": "18.2%",
          "total_supplied": "2,345,678.90",
          "total_borrowed": "1,523,456.78",
          "utilization": "65.0%"
        }
      ]
    }
  ]
}"""

    @mcp.tool
    def get_account_info(account_id: str) -> str:
        """Get account information for a Stellar address"""
        # TODO: Implement actual account info fetching
        return f"""{{
  "account_id": "{account_id}",
  "balance": "1000.00",
  "sequence": 12345,
  "signers": 1,
  "status": "found"
}}"""

    @mcp.tool
    def calculate_risk_score(utilization: float, asset_type: str) -> str:
        """Calculate risk score for a lending opportunity"""
        if utilization > 90:
            return "HIGH RISK: Very high utilization may delay withdrawals"
        elif utilization > 75:
            return "MEDIUM-HIGH RISK: High utilization, monitor closely"
        elif utilization > 50:
            return "MEDIUM RISK: Normal utilization for active pools"
        else:
            return "LOW RISK: Good liquidity, safer for new lenders"

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