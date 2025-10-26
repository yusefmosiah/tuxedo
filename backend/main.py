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
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastMCP removed - using local Stellar tools directly

# Import LangChain
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function
import json

# Import local Stellar tools
try:
    from stellar_tools import account_manager, trading, trustline_manager, market_data, utilities
    from stellar_soroban import soroban_operations
    from stellar_ssl import create_soroban_client_with_ssl
    from stellar_sdk import Server
    from key_manager import KeyManager
    STELLAR_TOOLS_AVAILABLE = True
    logger.info("Local Stellar tools loaded successfully (including Soroban)")
except ImportError as e:
    logger.warning(f"Stellar tools not available: {e}")
    STELLAR_TOOLS_AVAILABLE = False

# Import live summary service
try:
    from live_summary_service import get_live_summary_service, is_live_summary_enabled
    LIVE_SUMMARY_AVAILABLE = is_live_summary_enabled()
    logger.info(f"Live summary service available: {LIVE_SUMMARY_AVAILABLE}")
except ImportError as e:
    logger.warning(f"Live summary service not available: {e}")
    LIVE_SUMMARY_AVAILABLE = False

# Import database
try:
    from database import db
    DATABASE_AVAILABLE = True
    logger.info("Database initialized successfully")
except ImportError as e:
    logger.warning(f"Database not available: {e}")
    DATABASE_AVAILABLE = False

# Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    wallet_address: Optional[str] = None

class LiveSummaryChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    wallet_address: Optional[str] = None
    enable_summary: bool = True

class ChatResponse(BaseModel):
    response: str
    success: bool = True
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    stellar_tools_ready: bool
    defindex_tools_ready: bool
    openai_configured: bool
    live_summary_ready: bool
    database_ready: bool

class StellarToolsResponse(BaseModel):
    available: bool
    tools_count: int
    tools: list[str]
    last_check: str

# Thread Management Models
class Thread(BaseModel):
    id: str
    title: str
    wallet_address: Optional[str] = None
    created_at: str
    updated_at: str
    is_archived: bool = False

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
    metadata: Optional[dict] = None
    created_at: str

class ChatRequestWithThread(BaseModel):
    message: str
    history: list[ChatMessage] = []
    wallet_address: Optional[str] = None
    thread_id: Optional[str] = None

# Global variables
llm: Optional[ChatOpenAI] = None

# ============================================================================
# STELLAR TOOL DEFINITIONS FOR LLM FUNCTION CALLING
# ============================================================================

@tool
async def stellar_account_manager(
    action: str,
    account_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Manage Stellar accounts. Actions: 'create', 'fund', 'get', 'transactions', 'list', 'export', 'import'.

    Args:
        action: Operation to perform ('create', 'fund', 'get', 'transactions', 'list', 'export', 'import')
        account_id: Stellar public key (required for most actions)
        secret_key: Secret key (required only for 'import')
        limit: Transaction limit (for 'transactions' action)
    """
    # If wallet_address is provided in context, use it for account_id if not specified
    if hasattr(stellar_account_manager, '_wallet_address') and not account_id:
        account_id = stellar_account_manager._wallet_address

    return await call_stellar_tool("account_manager_tool", {
        "action": action,
        "account_id": account_id,
        "secret_key": secret_key,
        "limit": limit
    })

@tool
async def stellar_trading(
    action: str,
    account_id: str,
    buying_asset: Optional[str] = None,
    selling_asset: Optional[str] = None,
    buying_issuer: Optional[str] = None,
    selling_issuer: Optional[str] = None,
    amount: Optional[str] = None,
    price: Optional[str] = None,
    order_type: str = "limit",
    offer_id: Optional[str] = None,
    max_slippage: float = 0.05
) -> str:
    """
    Execute Stellar DEX trading operations. Actions: 'buy', 'sell', 'cancel_order', 'get_orders'.

    Args:
        action: Trading operation ('buy', 'sell', 'cancel_order', 'get_orders')
        account_id: Stellar public key
        buying_asset: Asset you want to acquire (e.g., 'USDC')
        selling_asset: Asset you're spending (e.g., 'XLM')
        buying_issuer: Issuer of buying_asset (if not XLM)
        selling_issuer: Issuer of selling_asset (if not XLM)
        amount: Amount to trade
        price: Price (for limit orders)
        order_type: 'limit' or 'market'
        offer_id: Offer ID (for cancel_order)
        max_slippage: Maximum slippage tolerance for market orders
    """
    return await call_stellar_tool("trading_tool", {
        "action": action,
        "account_id": account_id,
        "buying_asset": buying_asset,
        "selling_asset": selling_asset,
        "buying_issuer": buying_issuer,
        "selling_issuer": selling_issuer,
        "amount": amount,
        "price": price,
        "order_type": order_type,
        "offer_id": offer_id,
        "max_slippage": max_slippage
    })

@tool
async def stellar_market_data(
    action: str,
    base_asset: str = "XLM",
    quote_asset: Optional[str] = None,
    quote_issuer: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    Query Stellar DEX market data. Actions: 'orderbook'.

    Args:
        action: Market data query type ('orderbook')
        base_asset: Base asset code (default: 'XLM')
        quote_asset: Quote asset code
        quote_issuer: Quote asset issuer (if not XLM)
        limit: Number of results
    """
    return await call_stellar_tool("market_data_tool", {
        "action": action,
        "base_asset": base_asset,
        "quote_asset": quote_asset,
        "quote_issuer": quote_issuer,
        "limit": limit
    })

@tool
async def stellar_trustline_manager(
    action: str,
    account_id: str,
    asset_code: str,
    asset_issuer: str,
    limit: Optional[str] = None
) -> str:
    """
    Manage Stellar trustlines for issued assets. Actions: 'establish', 'remove'.

    Args:
        action: Trustline operation ('establish', 'remove')
        account_id: Stellar public key
        asset_code: Asset code (e.g., 'USDC')
        asset_issuer: Asset issuer public key
        limit: Optional trust limit
    """
    return await call_stellar_tool("trustline_manager_tool", {
        "action": action,
        "account_id": account_id,
        "asset_code": asset_code,
        "asset_issuer": asset_issuer,
        "limit": limit
    })

@tool
async def stellar_utilities(action: str) -> str:
    """
    Get Stellar network utilities and server information. Actions: 'status', 'fee'.

    Args:
        action: Utility operation ('status', 'fee')
    """
    return await call_stellar_tool("utilities_tool", {
        "action": action
    })

@tool
async def stellar_soroban(
    action: str,
    contract_id: Optional[str] = None,
    key: Optional[str] = None,
    function_name: Optional[str] = None,
    parameters: Optional[str] = None,
    source_account: Optional[str] = None,
    durability: str = "persistent",
    start_ledger: Optional[int] = None,
    event_types: Optional[list] = None,
    limit: int = 100
) -> str:
    """
    Execute Stellar Soroban smart contract operations. Actions: 'get_data', 'simulate', 'invoke', 'get_events'.

    Args:
        action: Soroban operation ('get_data', 'simulate', 'invoke', 'get_events')
        contract_id: Smart contract address
        key: Storage key (for get_data)
        function_name: Contract function name (for simulate/invoke)
        parameters: JSON string of parameters (for simulate/invoke)
        source_account: Stellar account (for simulate/invoke)
        durability: Data durability ('persistent', 'temporary')
        start_ledger: Starting ledger (for get_events)
        event_types: Event types to filter (for get_events)
        limit: Result limit
    """
    return await call_stellar_tool("soroban_tool", {
        "action": action,
        "contract_id": contract_id,
        "key": key,
        "function_name": function_name,
        "parameters": parameters,
        "source_account": source_account,
        "durability": durability,
        "start_ledger": start_ledger,
        "event_types": event_types,
        "limit": limit
    })

# Import DeFindex tools
try:
    from defindex_tools import (
        discover_high_yield_vaults,
        get_defindex_vault_details,
        prepare_defindex_deposit
    )
    DEFINDEX_TOOLS_AVAILABLE = True
    logger.info("DeFindex tools loaded successfully")
except ImportError as e:
    logger.warning(f"DeFindex tools not available: {e}")
    DEFINDEX_TOOLS_AVAILABLE = False
    discover_high_yield_vaults = None
    get_defindex_vault_details = None
    prepare_defindex_deposit = None

# Import TUX farming tools
try:
    from tux_farming import TuxFarmingTools
    TUX_FARMING_AVAILABLE = True
    logger.info("TUX farming tools loaded successfully")
except ImportError as e:
    logger.warning(f"TUX farming tools not available: {e}")
    TUX_FARMING_AVAILABLE = False

# ============================================================================
# TUX YIELD FARMING TOOLS
# ============================================================================

@tool
async def tux_farming_overview(
    wallet_address: Optional[str] = None
) -> str:
    """
    Get overview of TUX yield farming opportunities and user positions.

    Args:
        wallet_address: User's wallet address to show personalized positions

    Returns comprehensive farming overview including:
    - TUX token information
    - Available farming pools with APYs
    - User's positions (if wallet provided)
    - Total pending rewards
    """
    try:
        if not TUX_FARMING_AVAILABLE:
            return "TUX farming tools are not available. Please check if contracts are deployed."

        tools = TuxFarmingTools()
        overview = tools.get_farming_overview(wallet_address)

        if "error" in overview:
            return f"Error getting farming overview: {overview['error']}"

        response_parts = []

        # Token info
        token_info = overview.get('token_info', {})
        if token_info:
            response_parts.append("## TUX Token Information")
            response_parts.append(f"**Name:** {token_info.get('name', 'N/A')}")
            response_parts.append(f"**Symbol:** {token_info.get('symbol', 'N/A')}")
            response_parts.append(f"**Total Supply:** {token_info.get('total_supply', 0):,} tokens")
            response_parts.append(f"**Contract:** {token_info.get('contract_address', 'N/A')}")
            response_parts.append("")

        # Available pools
        pools = overview.get('pools', [])
        response_parts.append(f"## Available Farming Pools ({len(pools)} pools)")

        for pool in pools:
            response_parts.append(f"### {pool['pool_id']} Pool")
            response_parts.append(f"- **Staking Token:** {pool['staking_token']}")
            response_parts.append(f"- **APY:** {pool['apy']:.2f}%")
            response_parts.append(f"- **Total Staked:** {pool['total_staked']:,}")
            response_parts.append(f"- **Status:** {'Active' if pool['is_active'] else 'Inactive'}")

            if wallet_address:
                user_staked = pool.get('user_staked', 0)
                pending = pool.get('formatted_pending_rewards', '0.00 TUX')
                response_parts.append(f"- **Your Stake:** {user_staked:,}")
                response_parts.append(f"- **Pending Rewards:** {pending}")

            response_parts.append("")

        # Summary if wallet provided
        if wallet_address and overview.get('totals'):
            totals = overview['totals']
            response_parts.append("## Your Farming Summary")
            response_parts.append(f"**Total Pending Rewards:** {totals.get('formatted_total_pending', '0.00 TUX')}")

            active_positions = len([p for p in pools if p.get('user_staked', 0) > 0])
            response_parts.append(f"**Active Positions:** {active_positions}")

        return "\n".join(response_parts)

    except Exception as e:
        return f"Error getting TUX farming overview: {str(e)}"

@tool
async def tux_farming_pool_details(
    pool_id: str,
    wallet_address: Optional[str] = None
) -> str:
    """
    Get detailed information about a specific TUX farming pool.

    Args:
        pool_id: Pool identifier (e.g., 'USDC', 'XLM')
        wallet_address: User's wallet address to show personalized position

    Returns detailed pool information including:
    - Pool parameters and configuration
    - APY and rewards calculation
    - User's position in the pool (if wallet provided)
    """
    try:
        if not TUX_FARMING_AVAILABLE:
            return "TUX farming tools are not available."

        tools = TuxFarmingTools()
        details = tools.get_pool_details(pool_id, wallet_address)

        if "error" in details:
            return f"Error getting pool details: {details['error']}"

        response_parts = []
        response_parts.append(f"## {pool_id} Pool Details")
        response_parts.append(f"**Staking Token:** {details.get('staking_token', 'N/A')}")
        response_parts.append(f"**Allocation Points:** {details.get('allocation_points', 0)}")
        response_parts.append(f"**Total Staked:** {details.get('total_staked', 0):,}")
        response_parts.append(f"**APY:** {details.get('apy', 0):.2f}%")
        response_parts.append(f"**Status:** {'Active' if details.get('is_active', False) else 'Inactive'}")
        response_parts.append(f"**Last Updated:** {details.get('last_update_time', 'N/A')}")

        if wallet_address:
            response_parts.append("")
            response_parts.append("### Your Position")
            response_parts.append(f"**Amount Staked:** {details.get('user_staked', 0):,}")
            response_parts.append(f"**Pending Rewards:** {details.get('formatted_pending_rewards', '0.00 TUX')}")

            stake_time = details.get('user_stake_start_time', 0)
            if stake_time > 0:
                import datetime
                stake_date = datetime.datetime.fromtimestamp(stake_time)
                response_parts.append(f"**Stake Started:** {stake_date.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(response_parts)

    except Exception as e:
        return f"Error getting pool details: {str(e)}"

@tool
async def tux_farming_user_positions(
    wallet_address: str
) -> str:
    """
    Get all TUX farming positions for a user.

    Args:
        wallet_address: User's Stellar wallet address

    Returns comprehensive user position information:
    - All active and historical positions
    - Pending rewards breakdown
    - Position performance metrics
    """
    try:
        if not TUX_FARMING_AVAILABLE:
            return "TUX farming tools are not available."

        if not wallet_address:
            return "Wallet address is required to fetch positions."

        tools = TuxFarmingTools()
        positions = tools.get_user_positions(wallet_address)

        if "error" in positions:
            return f"Error getting user positions: {positions['error']}"

        response_parts = []
        response_parts.append(f"## TUX Farming Positions for {wallet_address}")
        response_parts.append(f"**Total Pending Rewards:** {positions.get('formatted_total_pending', '0.00 TUX')}")
        response_parts.append(f"**Active Positions:** {positions.get('active_positions', 0)}")
        response_parts.append("")

        # List positions
        user_positions = positions.get('positions', [])
        if user_positions:
            response_parts.append("### Your Positions")
            for pos in user_positions:
                response_parts.append(f"#### {pos['pool_id']} Pool")
                response_parts.append(f"- **Staked:** {pos['amount_staked']:,}")
                response_parts.append(f"- **APY:** {pos['apy']:.2f}%")
                response_parts.append(f"- **Pending Rewards:** {pos['formatted_pending_rewards']}")

                if pos.get('stake_start_time', 0) > 0:
                    import datetime
                    stake_date = datetime.datetime.fromtimestamp(pos['stake_start_time'])
                    response_parts.append(f"- **Stake Started:** {stake_date.strftime('%Y-%m-%d')}")

                response_parts.append("")
        else:
            response_parts.append("You don't have any active farming positions yet.")
            response_parts.append("Start staking to earn TUX rewards!")

        return "\n".join(response_parts)

    except Exception as e:
        return f"Error getting user positions: {str(e)}"

# List of all available tools
STELLAR_TOOLS = [
    stellar_account_manager,
    stellar_trading,
    stellar_market_data,
    stellar_trustline_manager,
    stellar_utilities,
    stellar_soroban
]

# Add DeFindex tools if available
if DEFINDEX_TOOLS_AVAILABLE:
    STELLAR_TOOLS.extend([
        discover_high_yield_vaults,
        get_defindex_vault_details,
        prepare_defindex_deposit
    ])

# Add TUX farming tools if available
if TUX_FARMING_AVAILABLE:
    STELLAR_TOOLS.extend([
        tux_farming_overview,
        tux_farming_pool_details,
        tux_farming_user_positions
    ])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global llm

    logger.info("Starting Tuxedo AI backend...")

    # Initialize LLM
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")

    if openai_api_key:
        llm = ChatOpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url,
            model="deepseek/deepseek-v3.1-terminus:exacto",
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
        defindex_tools_ready=DEFINDEX_TOOLS_AVAILABLE,
        openai_configured=bool(os.getenv("OPENAI_API_KEY")),
        live_summary_ready=LIVE_SUMMARY_AVAILABLE,
        database_ready=DATABASE_AVAILABLE
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
            "utilities_tool",
            "soroban_tool"
        ]

    # Add DeFindex tools if available
    if DEFINDEX_TOOLS_AVAILABLE:
        tools.extend([
            "discover_high_yield_vaults",
            "get_defindex_vault_details",
            "prepare_defindex_deposit"
        ])

    return StellarToolsResponse(
        available=STELLAR_TOOLS_AVAILABLE,
        tools_count=len(tools),
        tools=tools,
        last_check=datetime.now().isoformat()
    )

# ============================================================================
# THREAD MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/threads", response_model=Thread)
async def create_thread(thread_data: ThreadCreate):
    """Create a new chat thread"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        thread_id = db.create_thread(
            title=thread_data.title,
            wallet_address=thread_data.wallet_address
        )

        thread = db.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=500, detail="Failed to create thread")

        return Thread(**thread)
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")

@app.get("/threads", response_model=list[Thread])
async def get_threads(wallet_address: Optional[str] = None, limit: int = 50):
    """Get all threads for a wallet"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        threads = db.get_threads(wallet_address=wallet_address, limit=limit)
        return [Thread(**thread) for thread in threads]
    except Exception as e:
        logger.error(f"Error getting threads: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting threads: {str(e)}")

@app.get("/threads/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str):
    """Get a specific thread"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        thread = db.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        return Thread(**thread)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting thread: {str(e)}")

@app.put("/threads/{thread_id}", response_model=Thread)
async def update_thread(thread_id: str, thread_data: ThreadUpdate):
    """Update a thread title"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        success = db.update_thread(thread_id, title=thread_data.title)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        thread = db.get_thread(thread_id)
        return Thread(**thread)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating thread: {str(e)}")

@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        success = db.delete_thread(thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        return {"message": "Thread deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting thread: {str(e)}")

@app.post("/threads/{thread_id}/archive")
async def archive_thread(thread_id: str):
    """Archive a thread"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        success = db.archive_thread(thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        return {"message": "Thread archived successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error archiving thread: {str(e)}")

@app.get("/threads/{thread_id}/messages", response_model=list[MessageWithMetadata])
async def get_thread_messages(thread_id: str):
    """Get all messages for a thread"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # First check if thread exists
        thread = db.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        messages = db.get_messages(thread_id)
        return [MessageWithMetadata(**msg) for msg in messages]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")

@app.post("/threads/{thread_id}/messages")
async def save_thread_messages(thread_id: str, messages: list[dict]):
    """Save messages to a thread"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # First check if thread exists
        thread = db.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        success = db.update_thread_from_chat_messages(thread_id, messages)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save messages")

        return {"message": "Messages saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving messages for thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving messages: {str(e)}")

async def chat_with_tools(
    message: str,
    history: list[ChatMessage],
    wallet_address: Optional[str] = None
) -> str:
    """
    Agent loop that uses Stellar tools to assist the user.
    """
    try:
        # Enhanced system prompt for the agent
        system_prompt = """You are Tuxedo, an AI assistant that helps users discover and understand DeFi opportunities on Stellar including Blend Protocol and DeFindex vaults.

**Your Available Tools:**
You have access to Stellar blockchain tools that can:
- Create and manage accounts (account_manager)
- Query market data and orderbooks (market_data)
- Execute trades on the Stellar DEX (trading)
- Manage trustlines for assets (trustline_manager)
- Query network status and fees (utilities)
- Interact with smart contracts (soroban)
- **NEW**: Discover and interact with DeFindex vaults for yield generation

**IMPORTANT - Automatic Transaction Signing:**
The prepare_defindex_deposit tool returns text that is ALREADY properly formatted with [STELLAR_TX]...[/STELLAR_TX] tags.
Simply include its output directly in your response - do NOT modify or re-wrap it.
The frontend will automatically detect these tags and IMMEDIATELY open the user's wallet extension for signing.
You do NOT need to instruct users to click anything or copy/paste - the wallet opens automatically within 0.5 seconds.

**CRITICAL**: NEVER manually create [STELLAR_TX] tags yourself. Only the prepare_defindex_deposit tool creates properly formatted transaction blocks.
If you want to help users practice transactions, use prepare_defindex_deposit - do NOT use stellar_trading and try to wrap its output.

**DeFindex Vault Capabilities:**
- Discover high-yield vaults with real mainnet APY data (from mainnet contracts)
- Get detailed vault information and strategies
- Prepare DEMO testnet transactions that simulate vault deposits
- **Important**: These are DEMO transactions that always succeed - they send XLM to a testnet address to demonstrate wallet signing, they do NOT actually deposit into real vaults
- The transactions are valid and can be signed/submitted on testnet for educational purposes
- If the tool returns an error, do NOT retry - investigate the actual issue or suggest alternative approaches

**Important Trading Context:**
Modern Stellar trading primarily uses **liquidity pools** rather than traditional orderbooks:
- **Orderbooks**: Show buy/sell orders but are often empty on testnet
- **Liquidity Pools**: Where most trading actually happens (automated market making)
- **DEX Trading Tool**: Works best for traditional orderbook trading
- **Testnet Reality**: Limited liquidity compared to mainnet, mostly for testing

**Agent Instructions:**
1. **Always be helpful** - Use tools to get real-time data instead of making assumptions
2. **Explain your actions** - Tell users what you're querying and why
3. **Interpret results clearly** - Translate blockchain data into understandable insights
4. **Handle gracefully** - If tools fail, explain the issue and suggest alternatives
5. **Security first** - Never expose private keys or sensitive information
6. **Use wallet address** - When user asks about "my wallet", "my account", "my balance", "check balance", "what's in my wallet", or similar phrases, ALWAYS use the stellar_account_manager tool with action='get' and the connected wallet address as account_id. Do NOT make assumptions or use placeholders.
7. **Never use placeholders** - Always provide actual addresses or say you need the address if not available.
8. **Explain trading limitations** - When orderbooks are empty, explain that most trading happens via liquidity pools and testnet has limited activity.
9. **Balance check priority** - When users mention balance or wallet without being specific, check their account balance first using stellar_account_manager with action='get'.

**Current Context:**
- User is on Stellar testnet for educational purposes
- Focus on Blend Protocol lending opportunities
- Prioritize account balance checks before suggesting operations
- Always explain risks and transaction costs
- Be transparent about testnet liquidity limitations"""

        # Build message history
        messages = [
            SystemMessage(content=system_prompt),
        ]

        # Add wallet context if available
        if wallet_address:
            wallet_context = f"""
**Connected Wallet Context:**
The user has connected their wallet with address: {wallet_address}
When users ask about "my wallet", "my account", "my balance", "check balance", "what's in my wallet", or similar phrases:
- Use stellar_account_manager tool with action='get'
- Use this exact address: {wallet_address}
- This is required for balance checks and account queries
The address is a Stellar public key starting with 'G'.
"""
            messages.append(SystemMessage(content=wallet_context))

        # Add conversation history
        messages.extend([
            *[HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)
              for msg in history],
            HumanMessage(content=message),
        ])

        # Convert tools to OpenAI tool format
        tool_schemas = [convert_to_openai_function(t) for t in STELLAR_TOOLS]

        # Convert to newer tool format
        tools = [{"type": "function", "function": schema} for schema in tool_schemas]

        # Create LLM with tools (using newer format)
        llm_with_tools = llm.bind(tools=tools)

        # Agent loop
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            # Get LLM response with potential tool calls
            response = await llm_with_tools.ainvoke(messages)

            # Add response to message history
            messages.append(response)

            # Check if LLM wants to call tools (handle both old and new LangChain formats)
            tool_calls = []

            # New LangChain format
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = response.tool_calls
                logger.info(f"LLM wants to call {len(tool_calls)} tools (new format)")
            # Old LangChain format with function_call in additional_kwargs
            elif (hasattr(response, 'additional_kwargs') and
                  response.additional_kwargs.get('function_call')):
                function_call = response.additional_kwargs['function_call']
                tool_calls = [{
                    "name": function_call["name"],
                    "args": json.loads(function_call["arguments"]),
                    "id": f"call_{function_call['name']}"
                }]
                logger.info(f"LLM wants to call {len(tool_calls)} tools (old format)")

            if tool_calls:
                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                    # Find and execute the tool
                    tool_func = None
                    for t in STELLAR_TOOLS:
                        if t.name == tool_name:
                            tool_func = t
                            break

                    if tool_func:
                        try:
                            # Auto-inject wallet address for account-related operations
                            if wallet_address:
                                # If account_id parameter exists but is empty/None/placeholder, inject real wallet address
                                if "account_id" in tool_args:
                                    current_account_id = tool_args.get("account_id")
                                    if (not current_account_id or
                                        current_account_id in ["", None, "your_connected_wallet_address", "YOUR_WALLET_PUBLIC_KEY"] or
                                        (isinstance(current_account_id, str) and
                                         ("your_wallet" in current_account_id.lower() or "placeholder" in current_account_id.lower()))):
                                        tool_args["account_id"] = wallet_address
                                        logger.info(f"Auto-injected wallet address {wallet_address} for {tool_name}")

                                # Set wallet address context on the tool function for additional logic
                                tool_func._wallet_address = wallet_address

                            result = await tool_func.ainvoke(tool_args)

                            # Format tool result
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": str(result)
                            }

                            logger.info(f"Tool {tool_name} executed successfully")

                        except Exception as e:
                            logger.error(f"Tool {tool_name} failed: {e}")
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": f"Error: {str(e)}"
                            }

                        # Add tool result to message history
                        messages.append(tool_message)
                    else:
                        logger.error(f"Tool {tool_name} not found")

            else:
                # LLM provided final response without tool calls
                logger.info("Agent completed with final response")
                return response.content if hasattr(response, 'content') else str(response)

        # Max iterations reached
        return "I apologize, but I'm having trouble completing your request. Let me try a different approach or you can rephrase your question."

    except Exception as e:
        logger.error(f"Error in agent loop: {e}")
        return f"I encountered an error while processing your request: {str(e)}"

async def chat_with_tools_stream(
    message: str,
    history: list[ChatMessage],
    wallet_address: Optional[str] = None
):
    """
    Streaming agent loop that yields intermediate results for real-time UI updates.
    """
    try:
        # Enhanced system prompt for the agent
        system_prompt = """You are Tuxedo, an AI assistant that helps users discover and understand DeFi opportunities on Stellar including Blend Protocol and DeFindex vaults.

**Your Available Tools:**
You have access to Stellar blockchain tools that can:
- Create and manage accounts (account_manager)
- Query market data and orderbooks (market_data)
- Execute trades on the Stellar DEX (trading)
- Manage trustlines for assets (trustline_manager)
- Query network status and fees (utilities)
- Interact with smart contracts (soroban)
- **NEW**: Discover and interact with DeFindex vaults for yield generation

**IMPORTANT - Automatic Transaction Signing:**
The prepare_defindex_deposit tool returns text that is ALREADY properly formatted with [STELLAR_TX]...[/STELLAR_TX] tags.
Simply include its output directly in your response - do NOT modify or re-wrap it.
The frontend will automatically detect these tags and IMMEDIATELY open the user's wallet extension for signing.
You do NOT need to instruct users to click anything or copy/paste - the wallet opens automatically within 0.5 seconds.

**CRITICAL**: NEVER manually create [STELLAR_TX] tags yourself. Only the prepare_defindex_deposit tool creates properly formatted transaction blocks.
If you want to help users practice transactions, use prepare_defindex_deposit - do NOT use stellar_trading and try to wrap its output.

**DeFindex Vault Capabilities:**
- Discover high-yield vaults with real mainnet APY data (from mainnet contracts)
- Get detailed vault information and strategies
- Prepare DEMO testnet transactions that simulate vault deposits
- **Important**: These are DEMO transactions that always succeed - they send XLM to a testnet address to demonstrate wallet signing, they do NOT actually deposit into real vaults
- The transactions are valid and can be signed/submitted on testnet for educational purposes
- If the tool returns an error, do NOT retry - investigate the actual issue or suggest alternative approaches

**Important Trading Context:**
Modern Stellar trading primarily uses **liquidity pools** rather than traditional orderbooks:
- **Orderbooks**: Show buy/sell orders but are often empty on testnet
- **Liquidity Pools**: Where most trading actually happens (automated market making)
- **DEX Trading Tool**: Works best for traditional orderbook trading
- **Testnet Reality**: Limited liquidity compared to mainnet, mostly for testing

**Agent Instructions:**
1. **Always be helpful** - Use tools to get real-time data instead of making assumptions
2. **Explain your actions** - Tell users what you're querying and why
3. **Interpret results clearly** - Translate blockchain data into understandable insights
4. **Handle gracefully** - If tools fail, explain the issue and suggest alternatives
5. **Security first** - Never expose private keys or sensitive information
6. **Use wallet address** - When user asks about "my wallet", "my account", "my balance", "check balance", "what's in my wallet", or similar phrases, ALWAYS use the stellar_account_manager tool with action='get' and the connected wallet address as account_id. Do NOT make assumptions or use placeholders.
7. **Never use placeholders** - Always provide actual addresses or say you need the address if not available.
8. **Explain trading limitations** - When orderbooks are empty, explain that most trading happens via liquidity pools and testnet has limited activity.
9. **Balance check priority** - When users mention balance or wallet without being specific, check their account balance first using stellar_account_manager with action='get'.

**Current Context:**
- User is on Stellar testnet for educational purposes
- Focus on Blend Protocol lending opportunities
- Prioritize account balance checks before suggesting operations
- Always explain risks and transaction costs
- Be transparent about testnet liquidity limitations"""

        # Build message history
        messages = [
            SystemMessage(content=system_prompt),
        ]

        # Add wallet context if available
        if wallet_address:
            wallet_context = f"""
**Connected Wallet Context:**
The user has connected their wallet with address: {wallet_address}
When users ask about "my wallet", "my account", "my balance", "check balance", "what's in my wallet", or similar phrases:
- Use stellar_account_manager tool with action='get'
- Use this exact address: {wallet_address}
- This is required for balance checks and account queries
The address is a Stellar public key starting with 'G'.
"""
            messages.append(SystemMessage(content=wallet_context))

        # Add conversation history
        messages.extend([
            *[HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)
              for msg in history],
            HumanMessage(content=message),
        ])

        # Convert tools to OpenAI tool format
        tool_schemas = [convert_to_openai_function(t) for t in STELLAR_TOOLS]

        # Convert to newer tool format
        tools = [{"type": "function", "function": schema} for schema in tool_schemas]

        # Create LLM with tools (using newer format)
        llm_with_tools = llm.bind(tools=tools)

        # Agent loop with streaming
        max_iterations = 100
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            # Yield thinking indicator
            yield {
                "type": "thinking",
                "content": f"Thinking... (iteration {iteration})",
                "iteration": iteration
            }

            # Get LLM response with potential tool calls
            response = await llm_with_tools.ainvoke(messages)

            # Check if LLM wants to call tools
            tool_calls = []

            # New LangChain format
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = response.tool_calls
                logger.info(f"LLM wants to call {len(tool_calls)} tools (new format)")
            # Old LangChain format with function_call in additional_kwargs
            elif (hasattr(response, 'additional_kwargs') and
                  response.additional_kwargs.get('function_call')):
                function_call = response.additional_kwargs['function_call']
                tool_calls = [{
                    "name": function_call["name"],
                    "args": json.loads(function_call["arguments"]),
                    "id": f"call_{function_call['name']}"
                }]
                logger.info(f"LLM wants to call {len(tool_calls)} tools (old format)")

            if tool_calls:
                # Yield LLM reasoning before tool calls
                if hasattr(response, 'content') and response.content:
                    yield {
                        "type": "llm_response",
                        "content": response.content,
                        "iteration": iteration
                    }
                    # Add to message history for next iteration
                    messages.append(response)

                # Execute each tool call and stream results
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    # Yield tool call start
                    yield {
                        "type": "tool_call_start",
                        "content": f"🔧 Calling {tool_name}...",
                        "tool_name": tool_name,
                        "tool_args": tool_args,
                        "iteration": iteration
                    }

                    # Find and execute the tool
                    tool_func = None
                    for t in STELLAR_TOOLS:
                        if t.name == tool_name:
                            tool_func = t
                            break

                    if tool_func:
                        try:
                            # Auto-inject wallet address for account-related operations
                            if wallet_address:
                                if "account_id" in tool_args:
                                    current_account_id = tool_args.get("account_id")
                                    if (not current_account_id or
                                        current_account_id in ["", None, "your_connected_wallet_address", "YOUR_WALLET_PUBLIC_KEY"] or
                                        (isinstance(current_account_id, str) and
                                         ("your_wallet" in current_account_id.lower() or "placeholder" in current_account_id.lower()))):
                                        tool_args["account_id"] = wallet_address
                                        logger.info(f"Auto-injected wallet address {wallet_address} for {tool_name}")

                                tool_func._wallet_address = wallet_address

                            result = await tool_func.ainvoke(tool_args)

                            # Generate tool summary if service is available
                            tool_summary = None
                            try:
                                summary_service = get_live_summary_service()
                                tool_summary = await summary_service.generate_tool_summary(tool_name, str(result))
                            except Exception as e:
                                logger.warning(f"Failed to generate tool summary: {e}")
                                tool_summary = None

                            # Yield tool result with summary
                            yield {
                                "type": "tool_result",
                                "content": str(result),
                                "tool_name": tool_name,
                                "tool_args": tool_args,
                                "iteration": iteration,
                                "summary": tool_summary
                            }

                            # Format tool result for next LLM iteration
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": str(result)
                            }

                            logger.info(f"Tool {tool_name} executed successfully")

                        except Exception as e:
                            logger.error(f"Tool {tool_name} failed: {e}")
                            error_msg = f"Error: {str(e)}"

                            # Yield tool error
                            yield {
                                "type": "tool_error",
                                "content": error_msg,
                                "tool_name": tool_name,
                                "tool_args": tool_args,
                                "iteration": iteration
                            }

                            # Format tool error for next LLM iteration
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": error_msg
                            }

                        # Add tool result to message history for next iteration
                        messages.append(tool_message)
                    else:
                        logger.error(f"Tool {tool_name} not found")
                        yield {
                            "type": "tool_error",
                            "content": f"Tool {tool_name} not found",
                            "tool_name": tool_name,
                            "iteration": iteration
                        }

            else:
                # LLM provided final response without tool calls
                logger.info("Agent completed with final response")
                final_content = response.content if hasattr(response, 'content') else str(response)

                yield {
                    "type": "final_response",
                    "content": final_content,
                    "iteration": iteration
                }
                return

        # Max iterations reached
        yield {
            "type": "error",
            "content": "I apologize, but I reached the maximum number of iterations. Let me try a different approach or you can rephrase your question.",
            "iteration": iteration
        }

    except Exception as e:
        logger.error(f"Error in streaming agent loop: {e}")
        yield {
            "type": "error",
            "content": f"I encountered an error while processing your request: {str(e)}"
        }

@app.post("/chat")
async def chat_message(request: ChatRequest):
    """Chat endpoint with agent integration"""
    try:
        logger.info(f"🔍 Received chat request: wallet_address={request.wallet_address}, message='{request.message[:50]}...'")

        if not llm:
            raise HTTPException(
                status_code=503,
                detail="LLM not initialized"
            )

        if not STELLAR_TOOLS_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Stellar tools not available"
            )

        # Run the agent with tools
        response = await chat_with_tools(
            message=request.message,
            history=request.history,
            wallet_address=request.wallet_address
        )

        return ChatResponse(response=response, success=True)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@app.post("/chat-stream")
async def chat_message_stream(request: ChatRequest):
    """Streaming chat endpoint using Server-Sent Events"""
    async def generate_chat_stream():
        try:
            logger.info(f"🔍 Started streaming chat request: wallet_address={request.wallet_address}")

            if not llm:
                error_data = {
                    "type": "error",
                    "content": "LLM not initialized"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return

            if not STELLAR_TOOLS_AVAILABLE:
                error_data = {
                    "type": "error",
                    "content": "Stellar tools not available"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return

            # Stream the agent response
            async for message_data in chat_with_tools_stream(
                message=request.message,
                history=request.history,
                wallet_address=request.wallet_address
            ):
                yield f"data: {json.dumps(message_data)}\n\n"
                await asyncio.sleep(0.01)  # Small delay to prevent overwhelming

        except Exception as e:
            logger.error(f"Error in streaming chat endpoint: {e}")
            error_data = {
                "type": "error",
                "content": f"Stream error: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_chat_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/chat-live-summary")
async def chat_live_summary_stream(request: LiveSummaryChatRequest):
    """Enhanced streaming chat endpoint with live summaries"""
    async def generate_live_summary_stream():
        try:
            logger.info(f"🔍 Started live summary streaming chat: wallet_address={request.wallet_address}, enable_summary={request.enable_summary}")

            if not llm:
                error_data = {
                    "type": "error",
                    "content": "LLM not initialized"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return

            if not STELLAR_TOOLS_AVAILABLE:
                error_data = {
                    "type": "error",
                    "content": "Stellar tools not available"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return

            # Initialize live summary service if enabled
            summary_service = None
            if request.enable_summary and LIVE_SUMMARY_AVAILABLE:
                summary_service = get_live_summary_service()
                logger.info("Live summary service enabled")
            else:
                logger.info("Live summary disabled or not available")

            # Create unique live summary ID
            live_summary_id = f"live-{int(asyncio.get_event_loop().time())}"

            # Buffer for collecting messages in this conversation segment
            message_buffer = []

            # Send initial live summary if enabled
            if summary_service:
                initial_summary = {
                    "type": "live_summary_start",
                    "id": live_summary_id,
                    "summary": "Processing your request...",
                    "isLive": True,
                    "isExpanded": False
                }
                yield f"data: {json.dumps(initial_summary)}\n\n"

            # Stream the agent response and collect messages
            final_response_content = None
            async for message_data in chat_with_tools_stream(
                message=request.message,
                history=request.history,
                wallet_address=request.wallet_address
            ):
                # Collect all meaningful messages for summarization
                if message_data.get('type') not in ['thinking']:
                    message_buffer.append(message_data)

                # Generate live summary updates
                if (summary_service and
                    message_data.get('type') in ['llm_response', 'tool_result', 'tool_error'] and
                    len(message_buffer) > 0):

                    try:
                        # Generate live summary
                        live_summary = await summary_service.generate_live_summary(message_buffer)

                        summary_update = {
                            "type": "live_summary_update",
                            "id": live_summary_id,
                            "summary": live_summary,
                            "isLive": True,
                            "isExpanded": False,
                            "fullContent": message_buffer.copy()
                        }
                        yield f"data: {json.dumps(summary_update)}\n\n"

                    except Exception as e:
                        logger.error(f"Error generating live summary: {e}")
                        # Continue without summary if it fails

                # Always forward the original message
                yield f"data: {json.dumps(message_data)}\n\n"

                # Store final response when we get it
                if message_data.get('type') == 'final_response':
                    final_response_content = message_data.get('content')

                await asyncio.sleep(0.01)

            # Generate final summary if we have messages and summary service
            if summary_service and message_buffer:
                try:
                    final_summary = await summary_service.generate_final_summary(message_buffer)

                    summary_complete = {
                        "type": "live_summary_complete",
                        "id": live_summary_id,
                        "summary": final_summary,
                        "isLive": False,
                        "isExpanded": False,
                        "fullContent": message_buffer.copy()
                    }
                    yield f"data: {json.dumps(summary_complete)}\n\n"

                    logger.info(f"Generated final summary: {final_summary}")

                except Exception as e:
                    logger.error(f"Error generating final summary: {e}")

        except Exception as e:
            logger.error(f"Error in live summary streaming chat endpoint: {e}")
            error_data = {
                "type": "error",
                "content": f"Live summary stream error: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_live_summary_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

async def call_stellar_tool(tool_name: str, arguments: dict, wallet_address: Optional[str] = None) -> str:
    """Call Stellar tools directly with optional wallet address"""
    if not STELLAR_TOOLS_AVAILABLE:
        return "Stellar tools not available. Please check dependencies."

    try:
        logger.info(f"Calling Stellar tool: {tool_name} with args: {arguments}")

        # Initialize Stellar components
        horizon = Server("https://horizon-testnet.stellar.org")
        soroban = create_soroban_client_with_ssl("https://soroban-testnet.stellar.org")

        # Use wallet address if provided, otherwise use key_manager for backend operations
        if wallet_address and "account_id" in arguments:
            arguments["account_id"] = wallet_address

        if tool_name == "account_manager_tool":
            # Only use key_manager for create/import actions
            if arguments.get("action") in ["create", "import"]:
                key_manager = KeyManager()
                return account_manager(
                    horizon=horizon,
                    key_manager=key_manager,
                    **arguments
                )
            else:
                # For get/fund/transactions, we don't need key_manager
                return account_manager(
                    horizon=horizon,
                    key_manager=None,
                    **arguments
                )
        elif tool_name == "trading_tool":
            # Trading requires signing, so we need to return unsigned transactions
            if "auto_sign" not in arguments:
                arguments["auto_sign"] = False  # Don't auto-sign, let wallet handle it
            return trading(
                horizon=horizon,
                key_manager=None,
                **arguments
            )
        elif tool_name == "market_data_tool":
            return market_data(
                horizon=horizon,
                **arguments
            )
        elif tool_name == "trustline_manager_tool":
            # Trustlines require signing, return unsigned transactions
            arguments["auto_sign"] = False
            return trustline_manager(
                horizon=horizon,
                key_manager=None,
                **arguments
            )
        elif tool_name == "utilities_tool":
            return utilities(
                horizon=horizon,
                **arguments
            )
        elif tool_name == "soroban_tool":
            # Soroban operations require signing
            if "auto_sign" not in arguments:
                arguments["auto_sign"] = False
            return await soroban_operations(
                soroban_server=soroban,
                key_manager=None,
                network_passphrase="Test SDF Network ; September 2015",
                **arguments
            )
        else:
            return f"Unknown tool: {tool_name}. Available tools: account_manager_tool, trading_tool, trustline_manager_tool, market_data_tool, utilities_tool, soroban_tool"

    except Exception as e:
        logger.error(f"Error calling Stellar tool {tool_name}: {e}")
        return f"Error calling Stellar tool {tool_name}: {str(e)}"

@app.post("/stellar-tool/{tool_name}")
async def test_stellar_tool(tool_name: str, arguments: dict = None, wallet_address: Optional[str] = None):
    """Test a Stellar tool call directly"""
    if arguments is None:
        arguments = {}

    try:
        result = await call_stellar_tool(tool_name, arguments, wallet_address)
        return {"tool": tool_name, "arguments": arguments, "wallet_address": wallet_address, "result": result, "success": True}
    except Exception as e:
        return {"tool": tool_name, "arguments": arguments, "wallet_address": wallet_address, "error": str(e), "success": False}

# ============================================================================
# TUX FARMING API ENDPOINTS
# ============================================================================

class TuxFarmingOverviewRequest(BaseModel):
    wallet_address: Optional[str] = None

class TuxFarmingPoolDetailsRequest(BaseModel):
    pool_id: str
    wallet_address: Optional[str] = None

class TuxFarmingUserPositionsRequest(BaseModel):
    wallet_address: str

@app.post("/api/tux-farming/overview")
async def tux_farming_overview_endpoint(request: TuxFarmingOverviewRequest):
    """Get TUX farming overview"""
    try:
        if not TUX_FARMING_AVAILABLE:
            raise HTTPException(status_code=503, detail="TUX farming tools not available")

        tools = TuxFarmingTools()
        overview = tools.get_farming_overview(request.wallet_address)

        if "error" in overview:
            raise HTTPException(status_code=400, detail=overview["error"])

        return overview

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in TUX farming overview endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/tux-farming/pool-details")
async def tux_farming_pool_details_endpoint(request: TuxFarmingPoolDetailsRequest):
    """Get TUX farming pool details"""
    try:
        if not TUX_FARMING_AVAILABLE:
            raise HTTPException(status_code=503, detail="TUX farming tools not available")

        tools = TuxFarmingTools()
        details = tools.get_pool_details(request.pool_id, request.wallet_address)

        if "error" in details:
            raise HTTPException(status_code=404, detail=details["error"])

        return details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in TUX farming pool details endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/tux-farming/user-positions")
async def tux_farming_user_positions_endpoint(request: TuxFarmingUserPositionsRequest):
    """Get TUX farming user positions"""
    try:
        if not TUX_FARMING_AVAILABLE:
            raise HTTPException(status_code=503, detail="TUX farming tools not available")

        if not request.wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address is required")

        tools = TuxFarmingTools()
        positions = tools.get_user_positions(request.wallet_address)

        if "error" in positions:
            raise HTTPException(status_code=400, detail=positions["error"])

        return positions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in TUX farming user positions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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