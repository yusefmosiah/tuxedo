"""
Soroswap DEX Tools for AI Agent
Provides swap, pool, and liquidity operations using Soroswap API
"""

import asyncio
from typing import Dict, Any, Optional, List
from stellar_sdk import Asset, Address
from soroswap_api import SoroswapAPIClient
from account_manager import AccountManager
from agent.context import AgentContext
from stellar_soroban import soroban_operations
import json

# Mainnet Contract Addresses
SOROSWAP_MAINNET_CONTRACTS = {
    "factory": "CA4HEQTL2WPEUYKYKCDOHCDNIV4QHNJ7EL4J4NQ6VADP7SYHVRYZ7AW2",
    "router": "CAG5LRYQ5JVEUI5TEID72EYOVX44TTUJT5BQR2J6J77FH65PCCFAJDDH"
}

def _parse_asset_to_address(asset: str, issuer: Optional[str] = None) -> str:
    """Convert asset specification to Soroswap format"""
    if asset.upper() == "XLM":
        return "native"
    elif issuer:
        return f"{asset}:{issuer}"
    else:
        return asset  # Assume it's already a contract address

async def soroswap_dex(
    action: str,
    agent_context: AgentContext,
    account_manager: AccountManager,
    soroban_server,
    account_id: Optional[str] = None,
    token_in: Optional[str] = None,
    token_out: Optional[str] = None,
    amount_in: Optional[str] = None,
    amount_out_min: Optional[str] = None,
    slippage: float = 0.5,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Unified Soroswap DEX operations tool

    Actions:
        - "quote": Get swap quote without executing
        - "swap": Execute token swap
        - "pools": Get available pools
        - "pool_info": Get specific pool information

    Args:
        action: Operation to perform
        agent_context: Agent execution context
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        account_id: Account ID (required for swap)
        token_in: Input token (symbol, contract address, or "native")
        token_out: Output token (symbol, contract address, or "native")
        amount_in: Amount to swap (in smallest units)
        amount_out_min: Minimum output amount (slippage protection)
        slippage: Slippage tolerance in percent
        network: Network (mainnet/testnet)
    """

    try:
        async with SoroswapAPIClient() as api:

            if action == "quote":
                if not token_in or not token_out or not amount_in:
                    return {"error": "token_in, token_out, and amount_in required for quote"}

                # Get quote from API
                quote_result = await api.get_quote(
                    token_in=_parse_asset_to_address(token_in),
                    token_out=token_out,  # Assume contract address for simplicity
                    amount_in=amount_in,
                    network=network
                )

                return {
                    "success": True,
                    "quote": quote_result,
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount_in": amount_in
                }

            elif action == "swap":
                if not account_id:
                    return {"error": "account_id required for swap"}
                if not token_in or not token_out or not amount_in:
                    return {"error": "token_in, token_out, and amount_in required for swap"}

                # Get transaction from API
                tx_result = await api.build_transaction(
                    token_in=_parse_asset_to_address(token_in),
                    token_out=token_out,
                    amount_in=amount_in,
                    slippage=slippage,
                    network=network
                )

                # Parse the transaction XDR and invoke via Soroban
                if "transaction" in tx_result:
                    # Extract contract call details from the transaction
                    # This would need to decode the XDR to get the actual contract invocation
                    # For now, we'll simulate a direct contract call

                    # Build parameters for swap_exact_assets_for_assets
                    swap_params = json.dumps([
                        {"type": "i128", "value": amount_in},
                        {"type": "i128", "value": amount_out_min or "0"},
                        {"type": "vec", "value": [
                            {"type": "address", "value": token_in},
                            {"type": "address", "value": token_out}
                        ]},
                        {"type": "address", "value": account_id},
                        {"type": "u64", "value": str(int(asyncio.get_event_loop().time()) + 3600)}  # deadline
                    ])

                    # Invoke the router contract
                    result = await soroban_operations(
                        action="invoke",
                        soroban_server=soroban_server,
                        account_manager=account_manager,
                        agent_context=agent_context,
                        account_id=account_id,
                        contract_id=SOROSWAP_MAINNET_CONTRACTS["router"],
                        function_name="swap_exact_assets_for_assets",
                        parameters=swap_params,
                        network_passphrase="Public Global Stellar Network ; September 2015"
                    )

                    if result.get("success"):
                        result.update({
                            "swap_details": {
                                "token_in": token_in,
                                "token_out": token_out,
                                "amount_in": amount_in,
                                "slippage": slippage
                            }
                        })

                    return result
                else:
                    return {"error": "Failed to build transaction", "details": tx_result}

            elif action == "pools":
                # Get all available pools
                pools = await api.get_pools(network=network)

                return {
                    "success": True,
                    "pools": pools,
                    "count": len(pools),
                    "network": network
                }

            elif action == "pool_info":
                if not token_out:  # Use token_out as pool identifier
                    return {"error": "pool address required for pool_info"}

                pool_info = await api.get_pool_info(token_out, network=network)

                return {
                    "success": True,
                    "pool_info": pool_info,
                    "pool_address": token_out
                }

            else:
                return {
                    "error": f"Unknown action: {action}",
                    "valid_actions": ["quote", "swap", "pools", "pool_info"]
                }

    except Exception as e:
        return {"error": f"Soroswap operation failed: {str(e)}", "success": False}