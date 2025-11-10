"""
Tool Factory for Per-Request Tool Creation with Delegated Authority
Creates LangChain tools with AgentContext injected from auth context.

This implements the Dual Authority pattern where:
- AgentContext comes from auth middleware (trusted source)
- LLM cannot spoof or modify authorization context
- Tools are created per-request, not globally
- Each request gets isolated tools with dual authority (agent + user)
"""

import os
import logging
from typing import List, Optional
from functools import partial
from langchain.tools import tool
from stellar_sdk import Server
from account_manager import AccountManager
from agent.context import AgentContext
from stellar_soroban import create_soroban_server

# Import original Stellar tools
from stellar_tools import (
    account_manager as _account_manager,
    trading as _trading,
    trustline_manager as _trustline_manager,
    market_data as _market_data,
    utilities as _utilities
)

logger = logging.getLogger(__name__)

# Constants - MAINNET ONLY
HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon.stellar.org")


def create_user_tools(agent_context: AgentContext) -> List:
    """
    Create tools for agent with delegated authority context.

    The agent can operate on:
    - Its own system accounts (system_agent)
    - Current user's accounts (user_id)

    Args:
        agent_context: Agent execution context with dual authority

    Returns:
        List of LangChain tools with agent context injected

    Security:
        - agent_context encapsulates all authorization logic
        - LLM cannot access or modify authorization context
        - Each tool enforces permission checks via agent_context.has_permission()
        - Tools fail closed: no permission = operation rejected
    """
    logger.info(f"Creating tools for {agent_context}")

    # Initialize shared dependencies
    horizon = Server(HORIZON_URL)
    account_mgr = AccountManager()

    # Create tools with agent_context injected via closure
    # LLM only sees tool parameters, agent_context is hidden

    @tool
    def get_my_wallet():
        """
        Get the user's connected external wallet information ONLY.

        This tool ONLY works with a connected external wallet (Freighter, etc.).
        It will never return the AI agent's system account.

        Returns:
            User's external wallet information including:
            - Public address
            - Balance details
            - Account status

        Example queries:
            - "What's in my wallet?"
            - "Check my balance"
            - "Show me my account details"

        Error:
            Returns error if no external wallet is connected.
        """
        if agent_context.wallet_mode != "external" or not agent_context.wallet_address:
            return {
                "error": "No external wallet connected. Please connect your wallet first.",
                "success": False,
                "wallet_mode": agent_context.wallet_mode
            }

        return _account_manager(
            action="get",
            agent_context=agent_context,
            account_manager=account_mgr,
            horizon=horizon,
            account_id="external_wallet"  # Strictly only external wallet
        )

    @tool
    def get_agent_account():
        """
        Get the AI agent's own system account information.

        This returns the AI agent's mainnet account that it manages
        for operations and demonstrations.

        Returns:
            Agent account information including:
            - Public address
            - Balance details
            - Account status
        """

        # Get agent's primary account
        agent_accounts = account_mgr.get_user_accounts(user_id="system_agent", chain="stellar")
        if not agent_accounts:
            return {
                "error": "Agent account not available",
                "success": False
            }

        agent_account = agent_accounts[0]  # Use first agent account
        public_key = agent_account['public_key']
        chain_account = horizon.accounts().account_id(public_key).call()

        return {
            "account_id": agent_account['id'],
            "public_key": public_key,
            "sequence": chain_account["sequence"],
            "balances": chain_account["balances"],
            "signers": chain_account["signers"],
            "thresholds": chain_account["thresholds"],
            "flags": chain_account.get("flags", {}),
            "owner_context": "agent",
            "success": True
        }

    @tool
    def stellar_account_manager(
        action: str,
        account_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        limit: int = 10
    ):
        """
        Advanced Stellar account management operations (MAINNET ONLY).

        Use get_my_wallet() for user's external wallet queries.
        Use get_agent_account() for AI agent account queries.
        Use this tool for specific account operations.

        With dual authority, this tool can access:
        - Agent's own funded mainnet account
        - Current user's accounts (if authenticated)
        - Connected external wallet (when account_id="external_wallet")

        Actions:
            - "create": Generate new mainnet account (requires manual funding)
            - "get": Get specific account details (requires account_id)
            - "transactions": Get transaction history
            - "list": List all accessible accounts (agent + user + external)
            - "export": Export secret key (⚠️ dangerous!)
            - "import": Import existing keypair

        Args:
            action: Operation to perform
            account_id: Account ID (internal ID, or "external_wallet" for connected wallet)
            secret_key: Secret key (required only for "import")
            limit: Transaction limit (for "transactions" action)

        Returns:
            Action-specific response dict. For "list", returns accounts
            tagged with owner_context: "agent", "user", or "external"

        Note:
            Mainnet-only system - new accounts must be funded manually with real XLM
            For "my wallet" queries, use get_my_wallet() instead
        """
        # agent_context is injected here, LLM cannot see or modify it
        return _account_manager(
            action=action,
            agent_context=agent_context,  # INJECTED - dual authority
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
        Unified SDEX trading tool with dual authority.

        Can execute trades from:
        - Agent's funded account
        - User's accounts

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
            agent_context=agent_context,  # INJECTED - dual authority
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
        Manage trustlines for issued assets with dual authority.

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
            agent_context=agent_context,  # INJECTED - dual authority
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
            agent_context=agent_context,  # INJECTED for consistency
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
            agent_context=agent_context,  # INJECTED for consistency
            horizon=horizon
        )

    # ========================================================================
    # BLEND CAPITAL TOOLS - Primary yield farming solution (mainnet)
    # ========================================================================

    @tool
    def blend_find_best_yield(asset_symbol: str, min_apy: Optional[float] = 0.0):
        """
        Find the best yield opportunities for an asset across all Blend Capital pools.

        Use this when users ask about:
        - Best APY for their assets
        - Where to earn yield on USDC, XLM, etc.
        - Comparing yield opportunities
        - Finding the highest returns

        Args:
            asset_symbol: Asset to search for (e.g., "USDC", "XLM", "WETH", "WBTC")
            min_apy: Minimum APY threshold (default: 0.0)

        Returns:
            Sorted list of yield opportunities with APY, liquidity, and pool info
        """
        import asyncio
        from blend_account_tools import _blend_find_best_yield

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _blend_find_best_yield(
                    asset_symbol=asset_symbol,
                    min_apy=min_apy,
                    user_id=agent_context.user_id,  # Use current user from context
                    account_manager=account_mgr
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _blend_find_best_yield(
                    asset_symbol=asset_symbol,
                    min_apy=min_apy,
                    user_id=agent_context.user_id,  # Use current user from context
                    account_manager=account_mgr
                )
            )

    @tool
    def blend_discover_pools():
        """
        Discover all active Blend Capital pools on mainnet.

        Use this when users ask about:
        - What pools are available
        - Blend protocol pools
        - Active lending pools

        Returns:
            List of active pools with addresses and status (mainnet only)
        """
        import asyncio
        from blend_account_tools import _blend_discover_pools

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _blend_discover_pools(
                    user_id=agent_context.user_id,  # Use current user from context
                    account_manager=account_mgr
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _blend_discover_pools(
                    user_id=agent_context.user_id,  # Use current user from context
                    account_manager=account_mgr
                )
            )

    @tool
    def blend_supply_to_pool(
        pool_address: str,
        asset_address: str,
        amount: float,
        account_id: str = None
    ):
        """
        Supply assets to a Blend pool to start earning yield.

        This is the main function for depositing funds and earning interest.
        Use after finding the best yield with blend_find_best_yield.

        Args:
            pool_address: Pool contract address (from blend_find_best_yield)
            asset_address: Asset contract address (from blend_find_best_yield)
            amount: Amount to supply in decimal units (e.g., 100.5)
            account_id: Optional account ID. Defaults to connected wallet ("external_wallet") if not provided.

        Returns:
            Transaction result with hash and confirmation

        Example:
            "Supply 100 USDC to the Comet pool"
        """
        import asyncio
        from blend_account_tools import _blend_supply_to_pool

        # Auto-detect account: prefer external wallet if connected, otherwise use provided account_id
        if account_id is None:
            if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                account_id = "external_wallet"
            else:
                return {
                    "success": False,
                    "error": "No account specified and no external wallet connected. Please connect a wallet or specify an account_id."
                }

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _blend_supply_to_pool(
                    pool_address=pool_address,
                    asset_address=asset_address,
                    amount=amount,
                    account_id=account_id,
                    agent_context=agent_context,  # Pass context instead of user_id
                    account_manager=account_mgr
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _blend_supply_to_pool(
                    pool_address=pool_address,
                    asset_address=asset_address,
                    amount=amount,
                    account_id=account_id,
                    agent_context=agent_context,  # Pass context instead of user_id
                    account_manager=account_mgr
                )
            )

    @tool
    def blend_withdraw_from_pool(
        pool_address: str,
        asset_address: str,
        amount: float,
        account_id: str = None
    ):
        """
        Withdraw assets from a Blend pool.

        Use this to remove funds and stop earning yield.

        Args:
            pool_address: Pool contract address
            asset_address: Asset contract address
            amount: Amount to withdraw in decimal units (e.g., 50.0)
            account_id: Optional account ID. Defaults to connected wallet ("external_wallet") if not provided.

        Returns:
            Transaction result with hash and confirmation

        Example:
            "Withdraw 50 USDC from the Comet pool"
        """
        import asyncio
        from blend_account_tools import _blend_withdraw_from_pool

        # Auto-detect account: prefer external wallet if connected, otherwise use provided account_id
        if account_id is None:
            if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                account_id = "external_wallet"
            else:
                return {
                    "success": False,
                    "error": "No account specified and no external wallet connected. Please connect a wallet or specify an account_id."
                }

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _blend_withdraw_from_pool(
                    pool_address=pool_address,
                    asset_address=asset_address,
                    amount=amount,
                    account_id=account_id,
                    agent_context=agent_context,  # Pass context instead of user_id
                    account_manager=account_mgr
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _blend_withdraw_from_pool(
                    pool_address=pool_address,
                    asset_address=asset_address,
                    amount=amount,
                    account_id=account_id,
                    agent_context=agent_context,  # Pass context instead of user_id
                    account_manager=account_mgr
                )
            )

    @tool
    def blend_check_my_positions(pool_address: str, account_id: str = None):
        """
        Check your positions in a Blend pool.

        Shows what assets you've supplied, borrowed, and collateral status.

        Args:
            pool_address: Pool contract address
            account_id: Optional account ID. Defaults to connected wallet ("external_wallet") if not provided.

        Returns:
            Detailed position information for all assets in the pool

        Example:
            "Check my positions in the Comet pool"
        """
        import asyncio
        from blend_account_tools import _blend_check_my_positions

        # Auto-detect account: prefer external wallet if connected, otherwise use provided account_id
        if account_id is None:
            if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                account_id = "external_wallet"
            else:
                return {
                    "success": False,
                    "error": "No account specified and no external wallet connected. Please connect a wallet or specify an account_id."
                }

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _blend_check_my_positions(
                    pool_address=pool_address,
                    account_id=account_id,
                    agent_context=agent_context,  # Pass context instead of user_id
                    account_manager=account_mgr
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _blend_check_my_positions(
                    pool_address=pool_address,
                    account_id=account_id,
                    agent_context=agent_context,  # Pass context instead of user_id
                    account_manager=account_mgr
                )
            )

    @tool
    def blend_get_pool_apy(pool_address: str, asset_address: str):
        """
        Get current APY for a specific asset in a pool.

        Shows supply APY (what you earn), borrow APY, and pool metrics.

        Args:
            pool_address: Pool contract address
            asset_address: Asset contract address

        Returns:
            APY information and pool metrics

        Example:
            "What's the current APY for USDC in the Comet pool?"
        """
        import asyncio
        from blend_account_tools import _blend_get_pool_apy

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _blend_get_pool_apy(
                    pool_address=pool_address,
                    asset_address=asset_address,
                    user_id=agent_context.user_id,  # Use current user from context
                    account_manager=account_mgr
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _blend_get_pool_apy(
                    pool_address=pool_address,
                    asset_address=asset_address,
                    user_id=agent_context.user_id,  # Use current user from context
                    account_manager=account_mgr
                )
            )

    # ========================================================================
    # SOROSWAP DEX TOOLS - First DEX on Stellar with Soroban
    # ========================================================================

    @tool
    def soroswap_dex(
        action: str,
        token_in: Optional[str] = None,
        token_out: Optional[str] = None,
        amount_in: Optional[str] = None,
        amount_out_min: Optional[str] = None,
        slippage: float = 0.5,
        account_id: str = None
    ):
        """
        Unified Soroswap DEX operations tool for quotes, swaps, and pool information.

        Soroswap is the first DEX and exchange aggregator built on Stellar, powered by Soroban smart contracts.

        Actions:
            - "quote": Get swap quote without executing
            - "swap": Execute token swap (requires account)
            - "pools": Get available pools
            - "pool_info": Get specific pool information

        Args:
            action: Operation to perform ("quote", "swap", "pools", "pool_info")
            token_in: Input token (symbol, contract address, or "native" for XLM)
            token_out: Output token (symbol, contract address, or "native" for XLM)
            amount_in: Amount to swap (in smallest units)
            amount_out_min: Minimum output amount (slippage protection)
            slippage: Slippage tolerance in percent (default: 0.5%)
            account_id: Account ID for swap operations (optional, defaults to external wallet)

        Returns:
            Action-specific response with swap details, quotes, or pool information

        Examples:
            - "What's the best rate to swap 1000 XLM for USDC?"
            - "Swap 500 XLM for USDC with 0.5% slippage"
            - "Show me available Soroswap pools"
            - "Get pool information for address"
        """
        import asyncio
        from soroswap_tools import soroswap_dex as _soroswap_dex

        # Auto-detect account for swap operations
        if action == "swap" and account_id is None:
            if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                account_id = "external_wallet"
            else:
                return {
                    "success": False,
                    "error": "No account specified for swap. Please connect a wallet or specify an account_id."
                }

        # Create Soroban server
        soroban_server = create_soroban_server()

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _soroswap_dex(
                    action=action,
                    agent_context=agent_context,
                    account_manager=account_mgr,
                    soroban_server=soroban_server,
                    account_id=account_id,
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount_in,
                    amount_out_min=amount_out_min,
                    slippage=slippage,
                    network="mainnet"
                ))
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _soroswap_dex(
                    action=action,
                    agent_context=agent_context,
                    account_manager=account_mgr,
                    soroban_server=soroban_server,
                    account_id=account_id,
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount_in,
                    amount_out_min=amount_out_min,
                    slippage=slippage,
                    network="mainnet"
                )
            )

    # Return list of tools with agent_context injected
    tools = [
        get_my_wallet,  # User's external wallet ONLY
        get_agent_account,  # AI agent's system account
        stellar_account_manager,  # Advanced account operations
        stellar_trading,
        stellar_trustline_manager,
        stellar_market_data,
        stellar_utilities,
        # Blend Capital tools (mainnet-only yield farming)
        blend_find_best_yield,
        blend_discover_pools,
        blend_supply_to_pool,
        blend_withdraw_from_pool,
        blend_check_my_positions,
        blend_get_pool_apy,
        # Soroswap DEX tools
        soroswap_dex
    ]

    logger.info(f"Created {len(tools)} tools (7 Stellar + 6 Blend Capital + 1 Soroswap) for {agent_context}")
    return tools
