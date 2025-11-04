"""
LangChain-compatible wrappers for Stellar tools.
Handles internal dependencies while providing schema-clean interfaces.
"""

from langchain.tools import tool
from typing import Optional, Dict, Any, List
import os
from stellar_sdk import Server
from stellar_sdk.soroban_server_async import SorobanServerAsync

# Import original Stellar tools
from stellar_tools import (
    account_manager as _account_manager,
    trading as _trading,
    trustline_manager as _trustline_manager,
    market_data as _market_data,
    utilities as _utilities
)
from stellar_soroban import soroban_operations as _soroban_operations
from key_manager import KeyManager

# Constants from environment or defaults
HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")
SOROBAN_RPC_URL = os.getenv("SOROBAN_RPC_URL", "https://soroban-testnet.stellar.org")
STELLAR_NETWORK = os.getenv("STELLAR_NETWORK", "testnet")
NETWORK_PASSPHRASE = os.getenv("NETWORK_PASSPHRASE", "Test SDF Network ; September 2015")

# ============================================================================
# TOOL WRAPPER 1: ACCOUNT MANAGER
# ============================================================================

@tool
def stellar_account_manager(
    action: str,
    account_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Stellar account management operations consolidating 7 operations.

    Actions:
        - "create": Generate new testnet account
        - "fund": Fund account via Friendbot (testnet only)
        - "get": Get account details (balances, sequence, trustlines)
        - "transactions": Get transaction history
        - "list": List all managed accounts
        - "export": Export secret key (⚠️ dangerous!)
        - "import": Import existing keypair

    Args:
        action: Operation to perform
        account_id: Stellar public key (required for most actions)
        secret_key: Secret key (required only for "import")
        limit: Transaction limit (for "transactions" action)

    Returns:
        Action-specific response dict
    """
    # Initialize dependencies internally
    horizon = Server(HORIZON_URL)
    key_manager = KeyManager()

    return _account_manager(
        action=action,
        key_manager=key_manager,
        horizon=horizon,
        account_id=account_id,
        secret_key=secret_key,
        limit=limit
    )

# ============================================================================
# TOOL WRAPPER 2: TRADING
# ============================================================================

@tool
def stellar_trading(
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
    max_slippage: float = 0.05,
    auto_sign: bool = True
) -> Dict[str, Any]:
    """
    Unified SDEX trading tool with intuitive buying/selling semantics.

    Actions:
        - "buy": Acquire buying_asset by spending selling_asset
        - "sell": Give up selling_asset to acquire buying_asset
        - "cancel_order": Cancel an open order
        - "get_orders": Get all open orders

    Args:
        action: Trading operation ("buy", "sell", "cancel_order", "get_orders")
        account_id: Stellar public key
        buying_asset: Asset you want to acquire (e.g., "USDC")
        selling_asset: Asset you're spending (e.g., "XLM")
        buying_issuer: Issuer of buying_asset (required if buying_asset != "XLM")
        selling_issuer: Issuer of selling_asset (required if selling_asset != "XLM")
        amount: For buy: amount of buying_asset to acquire; For sell: amount of selling_asset to spend
        price: Price (for limit orders). For buy: selling_asset per buying_asset. For sell: buying_asset per selling_asset
        order_type: "limit" or "market" (default: "limit")
        offer_id: Offer ID (for cancel_order action)
        max_slippage: Maximum slippage tolerance for market orders (default: 0.05 = 5%)
        auto_sign: Auto-sign and submit (default: True)

    Returns:
        {"success": bool, "hash": "...", "ledger": 123, "market_execution": {...}}
    """
    # Initialize dependencies internally
    horizon = Server(HORIZON_URL)
    key_manager = KeyManager()

    return _trading(
        action=action,
        account_id=account_id,
        key_manager=key_manager,
        horizon=horizon,
        buying_asset=buying_asset,
        selling_asset=selling_asset,
        buying_issuer=buying_issuer,
        selling_issuer=selling_issuer,
        amount=amount,
        price=price,
        order_type=order_type,
        offer_id=offer_id,
        max_slippage=max_slippage,
        auto_sign=auto_sign
    )

# ============================================================================
# TOOL WRAPPER 3: TRUSTLINE MANAGER
# ============================================================================

@tool
def stellar_trustline_manager(
    action: str,
    account_id: str,
    asset_code: str,
    asset_issuer: str,
    limit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage trustlines for issued assets.

    Actions:
        - "establish": Create trustline (required before receiving assets)
        - "remove": Remove trustline (requires zero balance)

    Args:
        action: Trustline operation
        account_id: Stellar public key
        asset_code: Asset code (e.g., "USDC")
        asset_issuer: Asset issuer public key
        limit: Optional trust limit (default: maximum)

    Returns:
        {"success": bool, "hash": "...", "message": "..."}
    """
    # Initialize dependencies internally
    horizon = Server(HORIZON_URL)
    key_manager = KeyManager()

    return _trustline_manager(
        action=action,
        account_id=account_id,
        asset_code=asset_code,
        asset_issuer=asset_issuer,
        key_manager=key_manager,
        horizon=horizon,
        limit=limit
    )

# ============================================================================
# TOOL WRAPPER 4: MARKET DATA
# ============================================================================

@tool
def stellar_market_data(
    action: str,
    base_asset: str = "XLM",
    quote_asset: Optional[str] = None,
    quote_issuer: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Query SDEX market data.

    Actions:
        - "orderbook": Get orderbook for asset pair

    Args:
        action: Market data query type
        base_asset: Base asset code (default: "XLM")
        quote_asset: Quote asset code
        quote_issuer: Quote asset issuer (if not XLM)
        limit: Number of results (default: 20)

    Returns:
        Action-specific market data
    """
    # Initialize dependencies internally
    horizon = Server(HORIZON_URL)

    return _market_data(
        action=action,
        horizon=horizon,
        base_asset=base_asset,
        quote_asset=quote_asset,
        quote_issuer=quote_issuer,
        limit=limit
    )

# ============================================================================
# TOOL WRAPPER 5: UTILITIES
# ============================================================================

@tool
def stellar_utilities(action: str) -> Dict[str, Any]:
    """
    Network utilities and server information.

    Actions:
        - "status": Get Horizon server status
        - "fee": Estimate current transaction fee

    Args:
        action: Utility operation

    Returns:
        Action-specific utility data
    """
    # Initialize dependencies internally
    horizon = Server(HORIZON_URL)

    return _utilities(action=action, horizon=horizon)

# ============================================================================
# TOOL WRAPPER 6: SOROBAN OPERATIONS (ASYNC)
# ============================================================================

@tool
def stellar_soroban_operations(
    action: str,
    contract_id: Optional[str] = None,
    key: Optional[str] = None,
    function_name: Optional[str] = None,
    parameters: Optional[str] = None,
    source_account: Optional[str] = None,
    durability: str = "persistent",
    start_ledger: Optional[int] = None,
    event_types: Optional[List[str]] = None,
    limit: int = 100,
    auto_sign: bool = True
) -> Dict[str, Any]:
    """
    Unified Soroban operations handler with async support.

    Actions:
        - "get_data": Query contract storage
        - "simulate": Simulate contract call (read-only)
        - "invoke": Execute contract function (write)
        - "get_events": Query contract events
        - "get_ledger_entries": Low-level ledger access

    Args:
        action: Soroban operation type
        contract_id: Contract ID (required for most operations)
        key: Storage key (for get_data)
        function_name: Contract function name (for simulate/invoke)
        parameters: JSON string of parameters (for simulate/invoke)
        source_account: Source account for transactions
        durability: Data durability ("persistent" or "temporary")
        start_ledger: Starting ledger for event queries
        event_types: List of event types to filter
        limit: Result limit
        auto_sign: Auto-sign transactions

    Returns:
        Operation-specific response
    """
    import asyncio

    # Initialize dependencies internally
    soroban_server = SorobanServerAsync(SOROBAN_RPC_URL)
    key_manager = KeyManager()

    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            _soroban_operations(
                action=action,
                soroban_server=soroban_server,
                key_manager=key_manager,
                contract_id=contract_id,
                key=key,
                function_name=function_name,
                parameters=parameters,
                source_account=source_account,
                durability=durability,
                start_ledger=start_ledger,
                event_types=event_types,
                limit=limit,
                auto_sign=auto_sign,
                network_passphrase=NETWORK_PASSPHRASE
            )
        )
    finally:
        loop.close()

    return result