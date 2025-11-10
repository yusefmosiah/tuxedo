"""
Stellar MCP Server - Composite Tools
Consolidated tool implementations reducing 17 tools to 5 composite tools.
"""

import asyncio
from stellar_sdk import (
    Server,
    TransactionBuilder,
    Keypair,
    Network,
    Asset,
    TransactionEnvelope,
)
import requests
from account_manager import AccountManager
from agent.context import AgentContext
from agent.transaction_handler import TransactionHandler
from typing import Optional, Dict, Any
from decimal import Decimal

# Constants - MAINNET ONLY
MAINNET_NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE


def _dict_to_asset(asset_code: str, asset_issuer: Optional[str] = None) -> Asset:
    """Convert asset code/issuer to Stellar SDK Asset object"""
    if asset_code.upper() == "XLM" or asset_issuer is None:
        return Asset.native()
    return Asset(asset_code, asset_issuer)


def _calculate_market_fill(
    orderbook: Dict[str, Any],
    amount: str,
    side: str,  # "buy" or "sell"
    max_slippage: float = 0.05  # 5% default
) -> Dict[str, Any]:
    """
    Calculate market order fill details from orderbook data.

    This function works with orderbook(base, quote) semantics internally.
    The 'side' parameter indicates whether you're buying or selling the quote asset.

    Args:
        orderbook: Result from market_data(action="orderbook") for orderbook(base, quote)
        amount: Amount to trade (quote asset amount for side="buy", quote asset amount for side="sell")
        side: "buy" = buying quote asset with base; "sell" = selling quote asset for base
        max_slippage: Maximum allowed slippage (0.05 = 5%)

    Returns:
        {
            "feasible": bool,
            "fills": [{"price": "0.10", "amount": "100"}, ...],
            "total_filled": "150",
            "average_price": "0.1067",
            "best_price": "0.10",
            "worst_price": "0.12",
            "slippage": 0.067,
            "total_cost": "16.0",
            "execution_price": "0.132",
            "error": None or "error message"
        }
    """
    try:
        # Get appropriate orderbook side
        # For orderbook(base, quote):
        #   - bids: offers to buy base (sell quote) - use these when we want to buy quote
        #   - asks: offers to sell base (buy quote) - use these when we want to sell quote
        levels = orderbook.get("bids" if side == "buy" else "asks", [])

        if not levels:
            return {
                "feasible": False,
                "error": "No liquidity available in orderbook"
            }

        # Parse amount
        target_amount = Decimal(amount)
        remaining = target_amount
        fills = []
        total_cost = Decimal(0)

        # Simulate filling through orderbook levels
        # NOTE: For orderbook(base, quote) prices are in quote/base
        # When buying quote: bids show quote available at quote/base price
        # When selling quote: asks show base available at quote/base price
        for level in levels:
            level_price = Decimal(level["price"])  # quote/base (e.g., USDC/XLM)
            level_amount = Decimal(level["amount"])  # Amount of asset being offered

            if side == "buy":
                # Buying quote (USDC): level_amount is quote (USDC) available
                fill_amount = min(remaining, level_amount)
                # Cost is in base (XLM) = fill_amount / price (to get XLM from USDC)
                # Actually: if price is USDC/XLM, to get USDC we pay: USDC / (USDC/XLM) = XLM
                # No wait: if I get fill_amount USDC at level_price USDC/XLM
                # I pay: fill_amount / level_price XLM
                fill_cost = fill_amount / level_price
            else:
                # Selling quote (USDC): level_amount is base (XLM) available
                # Convert to quote amount available: level_amount * level_price
                quote_available = level_amount * level_price
                fill_amount = min(remaining, quote_available)
                # Cost is in base (XLM) = fill_amount / price
                fill_cost = fill_amount / level_price

            fills.append({
                "price": str(level_price),
                "amount": str(fill_amount)
            })

            total_cost += fill_cost
            remaining -= fill_amount

            if remaining <= 0:
                break

        # Check if fully fillable
        if remaining > 0:
            return {
                "feasible": False,
                "partial_fill": str(target_amount - remaining),
                "requested": str(target_amount),
                "error": f"Insufficient liquidity: only {target_amount - remaining} available"
            }

        # Calculate statistics
        total_filled = target_amount
        # Average cost in base (XLM) per unit of quote (USDC)
        average_cost_per_unit = total_cost / total_filled  # XLM/USDC

        # Best price from orderbook is in quote/base (USDC/XLM)
        # Convert to base/quote (XLM/USDC) for comparison
        best_orderbook_price = Decimal(levels[0]["price"])  # USDC/XLM
        best_cost_per_unit = Decimal("1") / best_orderbook_price  # XLM/USDC

        # Calculate slippage: how much worse than best price
        slippage = (average_cost_per_unit - best_cost_per_unit) / best_cost_per_unit

        # Check slippage tolerance
        if slippage > Decimal(str(max_slippage)):
            return {
                "feasible": False,
                "average_price": str(average_cost_per_unit),
                "best_price": str(best_cost_per_unit),
                "slippage": float(slippage),
                "error": f"Slippage {slippage*100:.2f}% exceeds max {max_slippage*100:.2f}%"
            }

        # Determine execution price for Stellar operation
        # For manage_buy_offer(selling=XLM, buying=USDC), price is in XLM/USDC
        # Use worst fill + 10% buffer to ensure execution
        worst_orderbook_price = Decimal(fills[-1]["price"])  # USDC/XLM
        worst_cost_per_unit = Decimal("1") / worst_orderbook_price  # XLM/USDC
        execution_price = worst_cost_per_unit * Decimal("1.1")  # 10% buffer

        return {
            "feasible": True,
            "fills": fills,
            "total_filled": str(total_filled),
            "average_price": str(average_cost_per_unit),
            "best_price": str(best_cost_per_unit),
            "worst_price": str(worst_cost_per_unit),
            "slippage": float(slippage),
            "total_cost": str(total_cost),
            "execution_price": str(execution_price),
            "error": None
        }

    except Exception as e:
        return {
            "feasible": False,
            "error": f"Fill calculation error: {str(e)}"
        }


def _build_sign_submit(
    agent_context: AgentContext,
    account_id: str,
    operations: list,
    account_manager: AccountManager,
    horizon: Server,
    auto_sign: bool = True,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Unified transaction flow: build → sign → submit with delegated authority.

    Now uses TransactionHandler to support external wallet signing flows.

    Args:
        agent_context: Agent execution context with dual authority
        account_id: Account ID (internal ID, not public key)
        operations: List of operation callbacks
        account_manager: AccountManager instance
        horizon: Horizon server instance
        auto_sign: If True, automatically sign and submit (legacy parameter, ignored in external mode)
        description: Human-readable transaction description

    Returns:
        For agent/imported mode:
            {
                "success": bool,
                "hash": str,
                "ledger": int,
                "message": str
            }

        For external mode:
            {
                "requires_signature": True,
                "xdr": str,
                "network_passphrase": str,
                "description": str,
                "message": str
            }
    """
    try:
        # Permission check: verify agent has permission for this account
        if not account_manager.user_owns_account(agent_context, account_id):
            return {
                "error": "Permission denied: account not owned by authorized users",
                "success": False
            }

        # Get account details
        account_data = account_manager._get_account_by_id(account_id)
        if not account_data:
            return {"error": "Account not found", "success": False}

        public_key = account_data['public_key']

        # Load account from blockchain
        account = horizon.load_account(public_key)
        tx_builder = TransactionBuilder(
            source_account=account,
            network_passphrase=MAINNET_NETWORK_PASSPHRASE,
            base_fee=100
        )

        # Add all operations
        for op in operations:
            op(tx_builder)

        # Use TransactionHandler for dual-mode signing
        transaction_handler = TransactionHandler(account_manager)

        # TransactionHandler will check agent_context.requires_user_signing()
        # and return either unsigned XDR or submit the transaction
        return asyncio.run(transaction_handler.sign_and_submit(
            tx_builder=tx_builder,
            agent_context=agent_context,
            account_id=account_id,
            horizon_server=horizon,
            description=description
        ))

    except PermissionError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# COMPOSITE TOOL 1: ACCOUNT MANAGER
# ============================================================================

def account_manager(
    action: str,
    agent_context: AgentContext,
    account_manager: AccountManager,
    horizon: Server,
    account_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    limit: int = 10,
    destination: Optional[str] = None,
    amount: Optional[str] = None
) -> Dict[str, Any]:
    """
    Unified account management tool with delegated authority (MAINNET ONLY).

    With dual authority, this tool can access:
    - Agent's own funded mainnet account
    - Current user's accounts (if authenticated)

    Actions:
        - "create": Generate new mainnet account (requires manual funding)
        - "get": Get account details (balances, sequence, trustlines)
        - "transactions": Get transaction history
        - "list": List all accessible accounts (agent + user)
        - "export": Export secret key (⚠️ dangerous!)
        - "import": Import existing keypair
        - "send": Send XLM payment to destination address

    Args:
        action: Operation to perform
        agent_context: Agent execution context with dual authority
        account_manager: AccountManager instance
        horizon: Horizon server instance
        account_id: Account ID (internal ID, required for most actions)
        secret_key: Secret key (required only for "import")
        limit: Transaction limit (for "transactions" action)
        destination: Destination address (required for "send")
        amount: Amount to send in XLM (required for "send")

    Returns:
        Action-specific response dict. For "list", returns accounts
        tagged with owner_context: "agent" or "user"

    Note:
        - Mainnet-only system - no Friendbot funding available
        - New accounts must be funded manually with real XLM
    """
    try:

        if action == "create":
            # Generate new account for current user (not agent)
            result = account_manager.generate_account(
                user_id=agent_context.user_id,
                chain="stellar",
                name="Stellar Account"
            )
            return result

        elif action == "fund":
            # Friendbot not available on mainnet - accounts must be funded manually
            return {
                "error": "Friendbot funding not available on mainnet. Accounts must be funded manually with real XLM.",
                "success": False,
                "message": "To fund a mainnet account, send XLM from an existing funded account or exchange."
            }

        elif action == "get":
            # EXTERNAL WALLET SUPPORT: Automatically use external wallet when connected
            if not account_id:
                # If no account_id but external wallet is connected, automatically use that
                if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                    public_key = agent_context.wallet_address
                    chain_account = horizon.accounts().account_id(public_key).call()

                    return {
                        "account_id": "external_wallet",
                        "public_key": public_key,
                        "sequence": chain_account["sequence"],
                        "balances": chain_account["balances"],
                        "signers": chain_account["signers"],
                        "thresholds": chain_account["thresholds"],
                        "flags": chain_account.get("flags", {}),
                        "owner_context": "external",
                        "success": True
                    }
                else:
                    return {"error": "account_id required", "success": False}

            # PERMISSION CHECK for managed accounts
            if account_id == "external_wallet":
                # Virtual ID for external wallet
                if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                    public_key = agent_context.wallet_address
                else:
                    return {"error": "External wallet not connected", "success": False}
            else:
                # Managed account
                if not account_manager.user_owns_account(agent_context, account_id):
                    return {"error": "Permission denied", "success": False}

                account = account_manager._get_account_by_id(account_id)
                public_key = account['public_key']

            # Fetch on-chain data
            chain_account = horizon.accounts().account_id(public_key).call()

            return {
                "account_id": account_id,
                "public_key": public_key,
                "sequence": chain_account["sequence"],
                "balances": chain_account["balances"],
                "signers": chain_account["signers"],
                "thresholds": chain_account["thresholds"],
                "flags": chain_account.get("flags", {}),
                "success": True
            }

        elif action == "transactions":
            # EXTERNAL WALLET SUPPORT: Automatically use external wallet when connected
            if not account_id:
                # If no account_id but external wallet is connected, automatically use that
                if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                    public_key = agent_context.wallet_address
                else:
                    return {"error": "account_id required", "success": False}
            elif account_id == "external_wallet":
                # Virtual ID for external wallet
                if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                    public_key = agent_context.wallet_address
                else:
                    return {"error": "External wallet not connected", "success": False}
            else:
                # PERMISSION CHECK for managed accounts
                if not account_manager.user_owns_account(agent_context, account_id):
                    return {"error": "Permission denied", "success": False}

                account = account_manager._get_account_by_id(account_id)
                public_key = account['public_key']

            transactions = (
                horizon.transactions()
                .for_account(public_key)
                .limit(limit)
                .order(desc=True)
                .call()
            )

            return {
                "transactions": [
                    {
                        "hash": tx["hash"],
                        "ledger": tx["ledger"],
                        "created_at": tx["created_at"],
                        "source_account": tx["source_account"],
                        "fee_charged": tx["fee_charged"],
                        "operation_count": tx["operation_count"],
                        "successful": tx["successful"]
                    }
                    for tx in transactions["_embedded"]["records"]
                ],
                "success": True
            }

        elif action == "list":
            # Return accounts from ALL authorized user IDs
            all_accounts = []
            for auth_user_id in agent_context.get_authorized_user_ids():
                accounts = account_manager.get_user_accounts(
                    user_id=auth_user_id,
                    chain="stellar"
                )
                # Tag each account with ownership context
                for acc in accounts:
                    acc['owner_context'] = (
                        'agent' if agent_context.is_agent_account(auth_user_id)
                        else 'user'
                    )
                    acc['owner_user_id'] = auth_user_id
                all_accounts.extend(accounts)

            # EXTERNAL WALLET SUPPORT: Add connected external wallet if present
            if agent_context.wallet_mode == "external" and agent_context.wallet_address:
                try:
                    # Fetch external wallet details from blockchain
                    chain_account = horizon.accounts().account_id(agent_context.wallet_address).call()
                    external_wallet = {
                        'id': 'external_wallet',  # Virtual ID
                        'chain': 'stellar',
                        'public_key': agent_context.wallet_address,
                        'owner_context': 'external',
                        'owner_user_id': agent_context.user_id,
                        'name': 'Connected Wallet',
                        'network': 'mainnet',
                        # Add on-chain balance info
                        'balances': chain_account.get('balances', []),
                        'sequence': chain_account.get('sequence'),
                    }
                    all_accounts.append(external_wallet)
                except Exception as e:
                    # Log error but don't fail the entire request
                    import logging
                    logging.getLogger(__name__).warning(
                        f"Could not fetch external wallet {agent_context.wallet_address}: {e}"
                    )

            return {
                "accounts": all_accounts,
                "count": len(all_accounts),
                "success": True
            }

        elif action == "export":
            # PERMISSION CHECK built into export_account
            if not account_id:
                return {"error": "account_id required", "success": False}

            result = account_manager.export_account(agent_context, account_id)
            return result

        elif action == "import":
            # Import always goes to current user, not agent
            if not secret_key:
                return {"error": "secret_key required", "success": False}

            result = account_manager.import_account(
                user_id=agent_context.user_id,
                chain="stellar",
                private_key=secret_key,
                name="Imported Account"
            )
            return result

        elif action == "send":
            # Send XLM payment
            if not account_id:
                return {"error": "account_id required", "success": False}

            if not destination:
                return {"error": "destination address required", "success": False}
            if not amount:
                return {"error": "amount required", "success": False}

            # Create payment operation
            def payment_op(builder):
                builder.append_payment_op(
                    destination=destination,
                    asset=Asset.native(),
                    amount=str(amount)
                )

            # Build, sign, and submit transaction
            result = _build_sign_submit(
                agent_context=agent_context,
                account_id=account_id,
                operations=[payment_op],
                account_manager=account_manager,
                horizon=horizon,
                auto_sign=True,
                description=f"Payment: Send {amount} XLM to {destination[:8]}..."
            )

            if result.get("success"):
                result["amount"] = amount
                result["destination"] = destination
                result["asset"] = "XLM"

            return result

        else:
            return {
                "error": f"Unknown action: {action}",
                "valid_actions": ["create", "fund", "get", "transactions", "list", "export", "import", "send"],
                "success": False
            }

    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# COMPOSITE TOOL 2: TRADING
# ============================================================================

def trading(
    action: str,
    agent_context: AgentContext,
    account_id: str,
    account_manager: AccountManager,
    horizon: Server,
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
    Unified SDEX trading tool with delegated authority.

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
        agent_context: Agent execution context with dual authority
        account_id: Account ID (internal ID)
        account_manager: AccountManager instance
        horizon: Horizon server instance
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
    try:
        # PERMISSION CHECK: verify agent has permission for this account
        if not account_manager.user_owns_account(agent_context, account_id):
            return {
                "error": "Permission denied: account not owned by authorized users",
                "success": False
            }

        # Get account details
        account = account_manager._get_account_by_id(account_id)
        if not account:
            return {"error": "Account not found", "success": False}

        public_key = account['public_key']

        if action == "get_orders":
            # Get open orders
            offers = horizon.offers().for_account(public_key).call()
            return {
                "offers": [
                    {
                        "id": offer["id"],
                        "selling": offer["selling"],
                        "buying": offer["buying"],
                        "amount": offer["amount"],
                        "price": offer["price"],
                        "last_modified_ledger": offer["last_modified_ledger"]
                    }
                    for offer in offers["_embedded"]["records"]
                ],
                "count": len(offers["_embedded"]["records"])
            }

        elif action == "cancel_order":
            if not offer_id:
                return {"error": "offer_id required for 'cancel_order' action"}

            # Get offer details
            offer = horizon.offers().offer(offer_id).call()

            selling = Asset(offer["selling"]["asset_code"], offer["selling"]["asset_issuer"]) \
                if offer["selling"]["asset_type"] != "native" else Asset.native()
            buying = Asset(offer["buying"]["asset_code"], offer["buying"]["asset_issuer"]) \
                if offer["buying"]["asset_type"] != "native" else Asset.native()

            def cancel_op(builder):
                builder.append_manage_sell_offer_op(
                    selling=selling,
                    buying=buying,
                    amount="0",
                    price=offer["price"],
                    offer_id=int(offer_id)
                )

            result = _build_sign_submit(
                agent_context, account_id, [cancel_op], account_manager, horizon, auto_sign,
                description=f"Cancel order {offer_id}"
            )
            if result.get("success"):
                result["message"] = f"Order {offer_id} cancelled successfully"
            return result

        elif action in ["buy", "sell"]:
            # Validate inputs
            if not buying_asset or not selling_asset:
                return {"error": "Both buying_asset and selling_asset required for trading"}
            if not amount:
                return {"error": "amount required for trading"}
            if order_type == "limit" and not price:
                return {"error": "price required for limit orders"}

            # Build asset objects
            buying = _dict_to_asset(buying_asset, buying_issuer)
            selling = _dict_to_asset(selling_asset, selling_issuer)

            # Determine orderbook orientation for market orders
            # Convention: XLM is base when paired with issued assets
            if order_type == "market":
                # Determine base and quote for orderbook query
                if selling_asset.upper() == "XLM":
                    base_asset = selling_asset
                    quote_asset = buying_asset
                    quote_issuer_val = buying_issuer
                    # User wants to buy quote (buying_asset) by selling base (selling_asset)
                    orderbook_side = "buy"
                elif buying_asset.upper() == "XLM":
                    base_asset = buying_asset
                    quote_asset = selling_asset
                    quote_issuer_val = selling_issuer
                    # User wants to sell quote (selling_asset) to get base (buying_asset)
                    orderbook_side = "sell"
                else:
                    # Both are issued assets - use alphabetical order
                    if buying_asset < selling_asset:
                        base_asset = buying_asset
                        quote_asset = selling_asset
                        quote_issuer_val = selling_issuer
                        orderbook_side = "sell"
                    else:
                        base_asset = selling_asset
                        quote_asset = buying_asset
                        quote_issuer_val = buying_issuer
                        orderbook_side = "buy"

                # STEP 1: Query orderbook
                orderbook_result = market_data(
                    action="orderbook",
                    horizon=horizon,
                    base_asset=base_asset,
                    quote_asset=quote_asset,
                    quote_issuer=quote_issuer_val,
                    limit=20
                )

                if "error" in orderbook_result:
                    return {"error": f"Failed to fetch orderbook: {orderbook_result['error']}"}

                # STEP 2: Calculate fill strategy
                fill_calc = _calculate_market_fill(
                    orderbook=orderbook_result,
                    amount=amount,
                    side=orderbook_side,
                    max_slippage=max_slippage
                )

                if not fill_calc.get("feasible"):
                    return {
                        "success": False,
                        "error": fill_calc.get("error"),
                        "market_data": fill_calc
                    }

                price_value = fill_calc["execution_price"]
            else:
                # Limit order - use user-provided price
                price_value = price

            # STEP 3: Execute transaction
            # For action="buy": use manage_buy_offer (amount is buying_asset amount)
            # For action="sell": use manage_sell_offer (amount is selling_asset amount)
            def trade_op(builder):
                if action == "buy":
                    builder.append_manage_buy_offer_op(
                        selling=selling,
                        buying=buying,
                        amount=amount,
                        price=price_value
                    )
                else:  # action == "sell"
                    builder.append_manage_sell_offer_op(
                        selling=selling,
                        buying=buying,
                        amount=amount,
                        price=price_value
                    )

            # Generate description
            trade_desc = f"{action.capitalize()}: {amount} {buying_asset if action == 'buy' else selling_asset}"
            if order_type == "market":
                trade_desc += f" at market price"
            else:
                trade_desc += f" at {price_value}"

            result = _build_sign_submit(
                agent_context, account_id, [trade_op], account_manager, horizon, auto_sign,
                description=trade_desc
            )

            # Add market execution details for market orders
            if result.get("success") and order_type == "market":
                result["market_execution"] = {
                    "requested_amount": amount,
                    "expected_average_price": fill_calc["average_price"],
                    "best_price": fill_calc["best_price"],
                    "execution_price": fill_calc["execution_price"],
                    "slippage": fill_calc["slippage"],
                    "total_cost_estimate": fill_calc["total_cost"],
                    "fills": fill_calc["fills"]
                }

            return result

        else:
            return {
                "error": f"Unknown action: {action}",
                "valid_actions": ["buy", "sell", "cancel_order", "get_orders"]
            }
    
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# COMPOSITE TOOL 3: TRUSTLINE MANAGER
# ============================================================================

def trustline_manager(
    action: str,
    agent_context: AgentContext,
    account_id: str,
    asset_code: str,
    asset_issuer: str,
    account_manager: AccountManager,
    horizon: Server,
    limit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage trustlines for issued assets with delegated authority.

    Actions:
        - "establish": Create trustline (required before receiving assets)
        - "remove": Remove trustline (requires zero balance)

    Args:
        action: Trustline operation
        agent_context: Agent execution context with dual authority
        account_id: Account ID (internal ID)
        asset_code: Asset code (e.g., "USDC")
        asset_issuer: Asset issuer public key
        account_manager: AccountManager instance
        horizon: Horizon server instance
        limit: Optional trust limit (default: maximum)

    Returns:
        {"success": bool, "hash": "...", "message": "..."}
    """
    try:
        # PERMISSION CHECK
        if not account_manager.user_owns_account(agent_context, account_id):
            return {
                "error": "Permission denied: account not owned by authorized users",
                "success": False
            }

        asset = Asset(asset_code, asset_issuer)

        def trustline_op(builder):
            if action == "establish":
                builder.append_change_trust_op(asset=asset, limit=limit)
            elif action == "remove":
                builder.append_change_trust_op(asset=asset, limit="0")
            else:
                raise ValueError(f"Unknown action: {action}")

        result = _build_sign_submit(
            agent_context, account_id, [trustline_op], account_manager, horizon, auto_sign=True,
            description=f"{'Establish' if action == 'establish' else 'Remove'} trustline for {asset_code}"
        )

        if result.get("success"):
            result["message"] = f"Trustline {'established' if action == 'establish' else 'removed'} for {asset_code}"

        return result

    except PermissionError as e:
        return {"error": str(e), "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# COMPOSITE TOOL 4: MARKET DATA
# ============================================================================

def market_data(
    action: str,
    agent_context: AgentContext,
    horizon: Server,
    base_asset: str = "XLM",
    quote_asset: Optional[str] = None,
    quote_issuer: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Query SDEX market data (read-only, no authentication required).

    Actions:
        - "orderbook": Get orderbook for asset pair

    Args:
        action: Market data query type
        agent_context: Agent execution context (for consistency)
        horizon: Horizon server instance
        base_asset: Base asset code (default: "XLM")
        quote_asset: Quote asset code
        quote_issuer: Quote asset issuer (if not XLM)
        limit: Number of results (default: 20)

    Returns:
        Action-specific market data
    """
    try:
        if action == "orderbook":
            if not quote_asset:
                return {"error": "quote_asset required for orderbook query"}
            
            base = _dict_to_asset(base_asset)
            quote = _dict_to_asset(quote_asset, quote_issuer)
            
            orderbook = horizon.orderbook(base, quote).limit(limit).call()
            return {
                "bids": orderbook["bids"],
                "asks": orderbook["asks"],
                "base": orderbook["base"],
                "counter": orderbook["counter"]
            }
        
        else:
            return {
                "error": f"Unknown action: {action}",
                "valid_actions": ["orderbook"]
            }
    
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# COMPOSITE TOOL 5: UTILITIES
# ============================================================================

def utilities(action: str, agent_context: AgentContext, horizon: Server) -> Dict[str, Any]:
    """
    Network utilities and server information (read-only, no authentication required).

    Actions:
        - "status": Get Horizon server status
        - "fee": Estimate current transaction fee

    Args:
        action: Utility operation
        agent_context: Agent execution context (for consistency)
        horizon: Horizon server instance

    Returns:
        Action-specific utility data
    """
    try:
        if action == "status":
            root = horizon.root().call()
            return {
                "horizon_version": root.get("horizon_version"),
                "core_version": root.get("core_version"),
                "history_latest_ledger": root.get("history_latest_ledger"),
                "network_passphrase": root.get("network_passphrase")
            }
        
        elif action == "fee":
            fee_stats = horizon.fee_stats().call()
            return {
                "fee": fee_stats.get("last_ledger_base_fee", "100"),
                "unit": "stroops",
                "fee_charged_max": fee_stats.get("max_fee", {}).get("max"),
                "fee_charged_min": fee_stats.get("min_fee", {}).get("min"),
                "message": "Fee is dynamic. Use at least the base fee for transaction."
            }
        
        else:
            return {
                "error": f"Unknown action: {action}",
                "valid_actions": ["status", "fee"]
            }
    
    except Exception as e:
        return {"error": str(e)}
