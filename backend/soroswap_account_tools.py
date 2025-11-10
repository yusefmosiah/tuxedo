#!/usr/bin/env python3
"""
Soroswap DEX Account Tools - AccountManager Integration

LangChain tools for Soroswap DEX operations.
These tools wrap the Soroswap API client and integrate with
the AccountManager for user-isolated operations.

Soroswap is the first DEX and exchange aggregator built on Stellar.

Created: 2025-11-10
Status: Active - DEX swap and liquidity tools for AI agent
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from account_manager import AccountManager
from agent.context import AgentContext
from soroswap_api import SoroswapAPIClient

logger = logging.getLogger(__name__)

# Mainnet Contract Addresses
SOROSWAP_MAINNET_CONTRACTS = {
    "factory": "CA4HEQTL2WPEUYKYKCDOHCDNIV4QHNJ7EL4J4NQ6VADP7SYHVRYZ7AW2",
    "router": "CAG5LRYQ5JVEUI5TEID72EYOVX44TTUJT5BQR2J6J77FH65PCCFAJDDH"
}

# Known asset contract addresses on Stellar mainnet
ASSET_ADDRESSES = {
    'XLM': 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA',
    'USDC': 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75',
    'WETH': 'CDMLFMKMMD7MWZP76FZCMGK3DQCV6VLPBR5DD2WWWKLBUQZLQJFUQJSK',
    'WBTC': 'CBMR5J4LZ5QUCFPQQ6YWJ4UUQISOOJJGQ7IMQX36C2V7LC2EDNDODJ7F',
    'EURC': 'CDCQP3LVDYYHVUIHW6BMVYJQWC7QPFTIZAYOQJYFHGFQHVNLTQAMV6TX',
    'BLND': 'CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY',
}


def _resolve_asset_address(asset_symbol: str) -> str:
    """
    Resolve asset symbol to contract address.

    Args:
        asset_symbol: Asset symbol (e.g., "XLM", "USDC") or contract address

    Returns:
        Contract address or "native" for XLM
    """
    symbol_upper = asset_symbol.upper()

    # Check if already a contract address (starts with C)
    if asset_symbol.startswith('C') and len(asset_symbol) > 50:
        return asset_symbol

    # Map known symbols
    if symbol_upper in ASSET_ADDRESSES:
        return ASSET_ADDRESSES[symbol_upper]

    # Default to native for XLM-like symbols
    if symbol_upper == "XLM" or symbol_upper == "NATIVE":
        return "native"

    raise ValueError(f"Unknown asset: {asset_symbol}. Known assets: {', '.join(ASSET_ADDRESSES.keys())}")


async def _soroswap_get_quote(
    token_in: str,
    token_out: str,
    amount_in: float,
    user_id: str,
    account_manager: AccountManager,
    network: str = "mainnet"
) -> str:
    """
    Get a swap quote from Soroswap without executing.

    Args:
        token_in: Input token symbol (e.g., "XLM") or contract address
        token_out: Output token symbol (e.g., "USDC") or contract address
        amount_in: Amount to swap (in decimal units, e.g., 100.5)
        user_id: User identifier (injected by tool factory)
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (default)

    Returns:
        Formatted string with quote information
    """
    try:
        logger.info(f"User {user_id[:8]}... requesting Soroswap quote: {amount_in} {token_in} -> {token_out}")

        # Resolve asset addresses
        token_in_address = _resolve_asset_address(token_in)
        token_out_address = _resolve_asset_address(token_out)

        # Convert amount to smallest units (7 decimals for most Stellar assets)
        amount_in_stroops = int(amount_in * 10_000_000)

        async with SoroswapAPIClient() as api:
            quote = await api.get_quote(
                token_in=token_in_address,
                token_out=token_out_address,
                amount_in=str(amount_in_stroops),
                network=network
            )

        # Format response
        amount_out = int(quote.get('amountOut', 0)) / 10_000_000
        price_impact = float(quote.get('priceImpact', 0))

        result = f"💱 **Soroswap Quote** (Mainnet)\n\n"
        result += f"📥 **You send**: {amount_in:.7f} {token_in.upper()}\n"
        result += f"📤 **You receive**: ~{amount_out:.7f} {token_out.upper()}\n"
        result += f"📊 **Price Impact**: {price_impact:.2f}%\n"
        result += f"🔗 **Route**: {len(quote.get('route', []))} hop(s)\n\n"

        result += "💡 **Next Steps:**\n"
        result += "- Use soroswap_swap to execute this trade\n"
        result += "- Consider price impact and slippage\n"
        result += f"- Quote valid for ~60 seconds\n\n"
        result += f"👤 Available for user {user_id[:8]}..."

        return result

    except Exception as e:
        logger.error(f"Soroswap quote failed: {e}", exc_info=True)
        error_msg = str(e)

        # Check for common error scenarios
        if "404" in error_msg or "Not Found" in error_msg:
            return f"❌ **Soroswap API Unavailable**\n\n" \
                   f"The Soroswap API endpoint returned a 404 error. This could mean:\n" \
                   f"- The Soroswap API is temporarily down\n" \
                   f"- The API endpoint has changed\n" \
                   f"- The requested trading pair is not supported\n\n" \
                   f"**Alternative**: You can use the Stellar DEX directly with the stellar_trading tool.\n" \
                   f"Try: \"Buy {amount_in} {token_out} with {token_in} on Stellar DEX\""

        return f"❌ **Quote Error**: {error_msg}\n\n" \
               f"Failed to get swap quote from Soroswap.\n" \
               f"You can try the Stellar DEX as an alternative."


async def _soroswap_get_pools(
    user_id: str,
    account_manager: AccountManager,
    network: str = "mainnet"
) -> str:
    """
    Get available Soroswap liquidity pools.

    Args:
        user_id: User identifier (injected by tool factory)
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (default)

    Returns:
        Formatted string with pool information
    """
    try:
        logger.info(f"User {user_id[:8]}... fetching Soroswap pools...")

        async with SoroswapAPIClient() as api:
            pools = await api.get_pools(network=network)

        if not pools:
            return "⚠️ No Soroswap pools found. The API might be unavailable."

        result = f"🏊 **Soroswap Liquidity Pools** (Mainnet)\n\n"
        result += f"Found {len(pools)} active pools:\n\n"

        for i, pool in enumerate(pools[:10], 1):  # Limit to top 10
            token0 = pool.get('token0', 'Unknown')
            token1 = pool.get('token1', 'Unknown')
            reserve0 = float(pool.get('reserve0', 0)) / 10_000_000
            reserve1 = float(pool.get('reserve1', 0)) / 10_000_000

            result += f"{i}. {token0}/{token1}\n"
            result += f"   💧 Liquidity: {reserve0:,.2f} {token0} / {reserve1:,.2f} {token1}\n"
            result += f"   📍 Address: {pool.get('address', '')[:16]}...\n\n"

        if len(pools) > 10:
            result += f"... and {len(pools) - 10} more pools\n\n"

        result += f"👤 Available for user {user_id[:8]}..."
        return result

    except Exception as e:
        logger.error(f"Failed to fetch Soroswap pools: {e}", exc_info=True)
        return f"❌ **Error**: {str(e)}\n\nFailed to fetch Soroswap pools. The API might be temporarily unavailable."


async def _soroswap_swap(
    token_in: str,
    token_out: str,
    amount_in: float,
    account_id: str,
    agent_context: AgentContext,
    account_manager: AccountManager,
    slippage: float = 0.5,
    network: str = "mainnet"
) -> str:
    """
    Execute a token swap on Soroswap.

    Args:
        token_in: Input token symbol (e.g., "XLM") or contract address
        token_out: Output token symbol (e.g., "USDC") or contract address
        amount_in: Amount to swap (in decimal units, e.g., 100.5)
        account_id: Account ID from AccountManager or "external_wallet"
        agent_context: Agent execution context
        account_manager: AccountManager instance (injected by tool factory)
        slippage: Slippage tolerance in percent (default: 0.5%)
        network: "mainnet" (default)

    Returns:
        Formatted string with transaction result
    """
    try:
        logger.info(f"User {agent_context.user_id[:8]}... executing Soroswap swap: {amount_in} {token_in} -> {token_out}")

        # Resolve asset addresses
        token_in_address = _resolve_asset_address(token_in)
        token_out_address = _resolve_asset_address(token_out)

        # Convert amount to smallest units
        amount_in_stroops = int(amount_in * 10_000_000)

        async with SoroswapAPIClient() as api:
            # Build transaction
            tx_data = await api.build_transaction(
                token_in=token_in_address,
                token_out=token_out_address,
                amount_in=str(amount_in_stroops),
                slippage=slippage,
                network=network
            )

        # For now, return information about the transaction
        # In production, this would need to sign and submit the transaction
        # via the TransactionHandler and AccountManager

        result = f"⚠️ **Swap Transaction Ready (Not Executed)**\n\n"
        result += f"The Soroswap integration currently supports quotes and pool discovery.\n"
        result += f"Transaction execution requires additional implementation.\n\n"
        result += f"**Requested Swap:**\n"
        result += f"- From: {amount_in:.7f} {token_in.upper()}\n"
        result += f"- To: {token_out.upper()}\n"
        result += f"- Slippage: {slippage}%\n"
        result += f"- Account: {account_id}\n\n"
        result += f"**Alternative**: Use the Stellar DEX via stellar_trading tool:\n"
        result += f'Try: "Buy {token_out} with {amount_in} {token_in} on Stellar DEX"'

        return result

    except Exception as e:
        logger.error(f"Soroswap swap failed: {e}", exc_info=True)
        error_msg = str(e)

        if "404" in error_msg or "Not Found" in error_msg:
            return f"❌ **Soroswap API Unavailable**\n\n" \
                   f"The Soroswap API is not accessible. Use the Stellar DEX instead:\n" \
                   f'Try: "Buy {token_out} with {amount_in} {token_in} on Stellar DEX"'

        return f"❌ **Swap Error**: {error_msg}\n\n" \
               f"Consider using the Stellar DEX as an alternative."
