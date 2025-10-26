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

# Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    wallet_address: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool = True
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    stellar_tools_ready: bool
    defindex_tools_ready: bool
    openai_configured: bool

class StellarToolsResponse(BaseModel):
    available: bool
    tools_count: int
    tools: list[str]
    last_check: str

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
        defindex_tools_ready=DEFINDEX_TOOLS_AVAILABLE,
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

**DeFindex Vault Capabilities:**
- Discover high-yield vaults with real mainnet APY data
- Get detailed vault information and strategies
- Prepare testnet deposit transactions for safe testing
- Note: Vault yields come from mainnet, transactions use testnet for safety

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
6. **Use wallet address** - When user asks about "my wallet", "my account", "my balance", or similar phrases, ALWAYS use the stellar_account_manager tool with the connected wallet address. Do NOT make assumptions or use placeholders.
7. **Never use placeholders** - Always provide actual addresses or say you need the address if not available.
8. **Explain trading limitations** - When orderbooks are empty, explain that most trading happens via liquidity pools and testnet has limited activity.

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
When users ask about "my wallet", "my account", "my balance", or similar phrases,
use this address for account operations. The address is a Stellar public key starting with 'G'.
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

@app.post("/chat")
async def chat_message(request: ChatRequest):
    """Chat endpoint with agent integration"""
    try:
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