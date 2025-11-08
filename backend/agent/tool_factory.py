"""
Tool Factory for Per-Request Tool Creation with User Isolation
Creates LangChain tools with user_id injected from auth context.

This implements the Quantum Leap migration pattern where:
- user_id comes from auth middleware (trusted source)
- LLM cannot spoof or modify user_id
- Tools are created per-request, not globally
- Each request gets isolated tools scoped to that user
"""

import os
import logging
from typing import List, Optional
from functools import partial
from langchain.tools import tool
from stellar_sdk import Server
from account_manager import AccountManager

# Import original Stellar tools
from stellar_tools import (
    account_manager as _account_manager,
    trading as _trading,
    trustline_manager as _trustline_manager,
    market_data as _market_data,
    utilities as _utilities
)

logger = logging.getLogger(__name__)

# Constants
HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")


def create_user_tools(user_id: str) -> List:
    """
    Create tools for a specific user with user_id injected.

    Args:
        user_id: User identifier from auth context (TRUSTED SOURCE)

    Returns:
        List of LangChain tools with user_id pre-injected

    Security:
        - user_id comes from auth middleware, NOT from LLM
        - LLM cannot access or modify user_id parameter
        - Each tool enforces permission checks using user_id
        - Tools fail closed: no user_id = operation rejected
    """
    logger.info(f"Creating tools for user_id: {user_id}")

    # Initialize shared dependencies
    horizon = Server(HORIZON_URL)
    account_mgr = AccountManager()

    # Create tools with user_id pre-injected via partial application
    # LLM only sees the remaining parameters, user_id is hidden

    @tool
    def stellar_account_manager(
        action: str,
        account_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        limit: int = 10
    ):
        """
        Stellar account management operations.

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
            account_id: Account ID (internal ID, required for most actions)
            secret_key: Secret key (required only for "import")
            limit: Transaction limit (for "transactions" action)

        Returns:
            Action-specific response dict
        """
        # user_id is injected here, LLM cannot see or modify it
        return _account_manager(
            action=action,
            user_id=user_id,  # INJECTED from auth context
            account_manager=account_mgr,
            horizon=horizon,
            account_id=account_id,
            secret_key=secret_key,
            limit=limit
        )

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
    ):
        """
        Unified SDEX trading tool.

        Actions:
            - "buy": Acquire buying_asset by spending selling_asset
            - "sell": Give up selling_asset to acquire buying_asset
            - "cancel_order": Cancel an open order
            - "get_orders": Get all open orders

        Args:
            action: Trading operation ("buy", "sell", "cancel_order", "get_orders")
            account_id: Account ID (internal ID)
            buying_asset: Asset you want to acquire (e.g., "USDC")
            selling_asset: Asset you're spending (e.g., "XLM")
            buying_issuer: Issuer of buying_asset (required if != "XLM")
            selling_issuer: Issuer of selling_asset (required if != "XLM")
            amount: Amount to trade
            price: Price (for limit orders)
            order_type: "limit" or "market" (default: "limit")
            offer_id: Offer ID (for cancel_order action)
            max_slippage: Maximum slippage for market orders (default: 0.05)
            auto_sign: Auto-sign and submit (default: True)

        Returns:
            {"success": bool, "hash": "...", "ledger": 123, ...}
        """
        return _trading(
            action=action,
            user_id=user_id,  # INJECTED from auth context
            account_id=account_id,
            account_manager=account_mgr,
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

    @tool
    def stellar_trustline_manager(
        action: str,
        account_id: str,
        asset_code: str,
        asset_issuer: str,
        limit: Optional[str] = None
    ):
        """
        Manage trustlines for issued assets.

        Actions:
            - "establish": Create trustline (required before receiving assets)
            - "remove": Remove trustline (requires zero balance)

        Args:
            action: Trustline operation
            account_id: Account ID (internal ID)
            asset_code: Asset code (e.g., "USDC")
            asset_issuer: Asset issuer public key
            limit: Optional trust limit (default: maximum)

        Returns:
            {"success": bool, "hash": "...", "message": "..."}
        """
        return _trustline_manager(
            action=action,
            user_id=user_id,  # INJECTED from auth context
            account_id=account_id,
            asset_code=asset_code,
            asset_issuer=asset_issuer,
            account_manager=account_mgr,
            horizon=horizon,
            limit=limit
        )

    @tool
    def stellar_market_data(
        action: str,
        base_asset: str = "XLM",
        quote_asset: Optional[str] = None,
        quote_issuer: Optional[str] = None,
        limit: int = 20
    ):
        """
        Query SDEX market data (read-only).

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
        return _market_data(
            action=action,
            user_id=user_id,  # INJECTED from auth context (for logging)
            horizon=horizon,
            base_asset=base_asset,
            quote_asset=quote_asset,
            quote_issuer=quote_issuer,
            limit=limit
        )

    @tool
    def stellar_utilities(action: str):
        """
        Network utilities and server information (read-only).

        Actions:
            - "status": Get Horizon server status
            - "fee": Estimate current transaction fee

        Args:
            action: Utility operation

        Returns:
            Action-specific utility data
        """
        return _utilities(
            action=action,
            user_id=user_id,  # INJECTED from auth context (for logging)
            horizon=horizon
        )

    # Add DeFindex tools with user_id injection
    @tool
    def defindex_discover_vaults(min_apy: Optional[float] = 0.0):
        """
        Discover DeFindex vaults sorted by APY (highest to lowest).

        Use this when users ask about:
        - Available vaults for investment
        - Current APY rates on Stellar
        - DeFi yield opportunities
        - Where to deposit funds

        This tool shows ALL vaults including 0% APY vaults, sorted by yield.

        Args:
            min_apy: Minimum APY threshold as percentage (default 0.0% to show ALL)

        Returns:
            Complete list of available vaults sorted by APY with full details
        """
        import asyncio
        from defindex_account_tools import _defindex_discover_vaults

        # Run async function in sync context using asyncio.run() which creates its own event loop
        return asyncio.run(
            _defindex_discover_vaults(min_apy=min_apy, user_id=user_id)
        )

    @tool
    def defindex_get_vault_details(vault_address: str):
        """
        Get detailed information about a specific DeFindex vault.

        Use this when users want more details about a vault they're interested in.

        Args:
            vault_address: The contract address of the vault (56 characters starting with 'C')

        Returns:
            Detailed vault information including strategies and performance
        """
        import asyncio
        from defindex_account_tools import _defindex_get_vault_details

        # Run async function in sync context using asyncio.run() which creates its own event loop
        return asyncio.run(
            _defindex_get_vault_details(vault_address=vault_address, user_id=user_id)
        )

    @tool
    def defindex_deposit(
        vault_address: str,
        amount_xlm: float,
        account_id: str
    ):
        """
        Execute an autonomous deposit transaction to a DeFindex vault using your account.

        This tool builds and submits a real transaction to the Stellar network,
        enabling true autonomous operation without manual wallet intervention.

        Args:
            vault_address: The vault contract address (verified testnet vault)
            amount_xlm: Amount to deposit in XLM (e.g., 10.5)
            account_id: Your account ID from AccountManager (use stellar_account_manager to list accounts)

        Returns:
            Transaction execution details including hash and status

        Example:
            "Deposit 50 XLM to vault CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA using account_id 'my_main_account'"
        """
        import asyncio
        from defindex_account_tools import _defindex_deposit

        # Run async function in sync context using asyncio.run() which creates its own event loop
        return asyncio.run(
            _defindex_deposit(
                vault_address=vault_address,
                amount_xlm=amount_xlm,
                user_id=user_id,  # INJECTED from auth context
                account_id=account_id,
                account_manager=account_mgr
            )
        )

    # Return list of tools with user_id injected
    tools = [
        stellar_account_manager,
        stellar_trading,
        stellar_trustline_manager,
        stellar_market_data,
        stellar_utilities,
        # NEW - DeFindex tools with user_id injection
        defindex_discover_vaults,
        defindex_get_vault_details,
        defindex_deposit
    ]

    logger.info(f"Created {len(tools)} tools ({len(tools)-5} DeFindex + 5 Stellar) for user_id: {user_id}")
    return tools


def create_anonymous_tools() -> List:
    """
    Create read-only tools for anonymous (unauthenticated) users.

    Returns:
        List of read-only LangChain tools

    Note:
        - No account management (requires authentication)
        - No trading (requires authentication)
        - No trustline management (requires authentication)
        - Market data: read-only ✓
        - Utilities: read-only ✓
    """
    logger.info("Creating anonymous (read-only) tools")

    # Initialize shared dependencies
    horizon = Server(HORIZON_URL)
    anonymous_user_id = "anonymous"

    @tool
    def stellar_market_data(
        action: str,
        base_asset: str = "XLM",
        quote_asset: Optional[str] = None,
        quote_issuer: Optional[str] = None,
        limit: int = 20
    ):
        """
        Query SDEX market data (read-only, no authentication required).

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
        return _market_data(
            action=action,
            user_id=anonymous_user_id,
            horizon=horizon,
            base_asset=base_asset,
            quote_asset=quote_asset,
            quote_issuer=quote_issuer,
            limit=limit
        )

    @tool
    def stellar_utilities(action: str):
        """
        Network utilities and server information (read-only, no authentication required).

        Actions:
            - "status": Get Horizon server status
            - "fee": Estimate current transaction fee

        Args:
            action: Utility operation

        Returns:
            Action-specific utility data
        """
        return _utilities(
            action=action,
            user_id=anonymous_user_id,
            horizon=horizon
        )

    tools = [
        stellar_market_data,
        stellar_utilities
    ]

    logger.info(f"Created {len(tools)} anonymous tools")
    return tools
