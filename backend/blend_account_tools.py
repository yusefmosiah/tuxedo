#!/usr/bin/env python3
"""
Blend Capital Account Tools - AccountManager Integration

LangChain tools for autonomous Blend Capital yield farming operations.
These tools wrap the core blend_pool_tools.py functions and integrate with
the AccountManager for user-isolated operations.

Created: 2025-11-09
Status: Active - Primary yield farming tools for AI agent
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from account_manager import AccountManager
from agent.context import AgentContext
from stellar_sdk.soroban_server_async import SorobanServerAsync

logger = logging.getLogger(__name__)

# Import core Blend functions
from blend_pool_tools import (
    blend_discover_pools,
    blend_find_best_yield,
    blend_get_reserve_apy,
    blend_supply_collateral,
    blend_withdraw_collateral,
    blend_get_my_positions,
    NETWORK_CONFIG,
    BLEND_MAINNET_CONTRACTS
)


async def _blend_find_best_yield(
    asset_symbol: str,
    min_apy: float,
    user_id: str,
    account_manager: AccountManager,
    network: str = "mainnet"  # Default to mainnet for read operations (real yields!)
) -> str:
    """
    Find best yield opportunities for an asset across all Blend pools.

    Args:
        asset_symbol: Asset to search for (e.g., "USDC", "XLM")
        min_apy: Minimum APY threshold
        user_id: User identifier (injected by tool factory)
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (real yields)

    Returns:
        Formatted string with yield opportunities
    """
    try:
        # Create Soroban server (mainnet-only)
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

        logger.info(f"User {user_id[:8]}... searching for {asset_symbol} yield opportunities on {network}...")

        # Find best yield - this will raise an error if pool discovery fails
        opportunities = await blend_find_best_yield(
            asset_symbol=asset_symbol,
            min_apy=min_apy,
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            network=network
        )

        if not opportunities:
            return f"⚠️ No yield opportunities found for {asset_symbol} with APY above {min_apy}% on {network}.\n\nThis could mean:\n- The asset is not supported in any active pools\n- All pools have APY below your threshold\n- Network connectivity issues\n\nTry lowering min_apy or checking a different asset."

        # Format response
        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        result = f"🌟 Found {len(opportunities)} yield opportunities for {asset_symbol} on Blend Capital ({network_label}):\n\n"

        for i, opp in enumerate(opportunities, 1):
            result += f"{i}. {opp['pool']}\n"
            result += f"   💰 APY: {opp['apy']:.2f}%\n"
            result += f"   💧 Available Liquidity: {opp['available_liquidity']:,.2f} {asset_symbol}\n"
            result += f"   📊 Utilization: {opp['utilization']:.1%}\n"
            result += f"   📍 Pool: {opp['pool_address'][:16]}...\n"
            result += f"   🪙 Asset: {opp['asset_address'][:16]}...\n\n"

        result += "\n💡 **Next Steps:**\n"
        result += f"- Use blend_supply_to_pool to deposit {asset_symbol} and start earning\n"
        result += "- Check blend_check_my_positions to see current holdings\n"
        result += f"- All data is live from Blend protocol on {network}\n"
        if network == "mainnet":
            result += f"\n⚠️  **MAINNET**: Real funds required. Ensure you have funded your account.\n"
        result += f"\n👤 Available for user {user_id[:8]}..."

        return result

    except ValueError as e:
        # ValueError indicates a known issue like Backstop query failure
        logger.error(f"Pool discovery failed in _blend_find_best_yield: {e}")
        return f"❌ **Pool Discovery Failed on {network}**\n\n{str(e)}\n\n**This is a fatal error** - the system cannot discover Blend pools from the Backstop contract.\n\nPossible causes:\n- RPC endpoint issues (check ANKR_STELLER_RPC)\n- Backstop contract address incorrect\n- Network connectivity problems\n- Contract state corruption\n\nPlease check logs and RPC configuration."
    except RuntimeError as e:
        # RuntimeError indicates a fatal system error
        logger.error(f"Fatal error in _blend_find_best_yield: {e}")
        return f"❌ **Fatal Error**: {str(e)}\n\nPlease check system logs and RPC configuration."
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in _blend_find_best_yield: {e}", exc_info=True)
        return f"❌ **Unexpected Error**: {str(e)}\n\nPlease report this issue with logs."


async def _blend_discover_pools(
    user_id: str,
    account_manager: AccountManager,
    network: str = "mainnet"  # Default to mainnet for read operations
) -> str:
    """
    Discover all active Blend pools.

    Args:
        user_id: User identifier (injected by tool factory)
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (real pools)

    Returns:
        Formatted string with pool information
    """
    try:
        # Create Soroban server (mainnet-only)
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

        logger.info(f"User {user_id[:8]}... discovering Blend pools on {network}...")

        # Discover pools - this will raise an error if discovery fails
        pools = await blend_discover_pools(
            network=network,
            soroban_server=soroban_server,
            account_manager=account_manager,
            user_id=user_id
        )

        if not pools:
            return f"⚠️ No active Blend pools found on {network}.\n\nThis should not happen on mainnet. Please check RPC configuration."

        # Format response
        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        result = f"🏦 Found {len(pools)} active Blend Capital pools on {network_label}:\n\n"

        for i, pool in enumerate(pools, 1):
            result += f"{i}. {pool['name']}\n"
            result += f"   📍 Address: {pool['pool_address']}\n"
            result += f"   ✅ Status: {pool['status']}\n\n"

        result += "\n💡 **Next Steps:**\n"
        result += "- Use blend_find_best_yield to find the best APY for your asset\n"
        result += "- Each pool supports multiple assets (USDC, XLM, WETH, WBTC)\n"
        result += f"\n👤 Available for user {user_id[:8]}..."

        return result

    except ValueError as e:
        # ValueError indicates a known issue like Backstop query failure
        logger.error(f"Pool discovery failed in _blend_discover_pools: {e}")
        return f"❌ **Pool Discovery Failed on {network}**\n\n{str(e)}\n\n**This is a fatal error** - the system cannot discover Blend pools from the Backstop contract.\n\nPossible causes:\n- RPC endpoint issues (check ANKR_STELLER_RPC env var)\n- Backstop contract address incorrect for {network}\n- Network connectivity problems\n- Contract state issues\n\nPlease check:\n1. RPC URL: {NETWORK_CONFIG['rpc_url']}\n2. Backstop: {NETWORK_CONFIG['backstop']}\n3. Network connectivity"
    except RuntimeError as e:
        # RuntimeError indicates a fatal system error
        logger.error(f"Fatal error in _blend_discover_pools: {e}")
        return f"❌ **Fatal Error**: {str(e)}\n\nPlease check system logs and RPC configuration."
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in _blend_discover_pools: {e}", exc_info=True)
        return f"❌ **Unexpected Error**: {str(e)}\n\nPlease report this issue with logs."


async def _blend_supply_to_pool(
    pool_address: str,
    asset_address: str,
    amount: float,
    account_id: str,
    agent_context: AgentContext,
    account_manager: AccountManager,
    network: str = "mainnet"  # Mainnet-only system
) -> str:
    """
    Supply assets to a Blend pool to earn yield with delegated authority.

    Args:
        pool_address: Pool contract ID
        asset_address: Asset contract ID
        amount: Amount to supply (decimal)
        account_id: Account ID from AccountManager
        agent_context: Agent execution context with dual authority
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (real funds)

    Returns:
        Formatted string with transaction result
    """
    try:
        # Create Soroban server (mainnet-only)
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        logger.info(f"Agent context {agent_context} supplying {amount} to pool {pool_address[:8]}... on {network_label}")

        # Execute supply
        result = await blend_supply_collateral(
            pool_address=pool_address,
            asset_address=asset_address,
            amount=amount,
            user_id=agent_context.user_id,  # Use current user from context
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network=network
        )

        if not result.get('success'):
            return f"❌ **Supply Failed**\n\n{result.get('message', 'Unknown error')}"

        # Format success response
        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        response = f"🚀 **Supply Successful on {network_label}!**\n\n"
        response += f"✅ Supplied {result['amount_supplied']} {result['asset_symbol']} to {result['pool']}\n\n"
        response += f"📋 **Transaction Details:**\n"
        response += f"   • Network: {network_label}\n"
        response += f"   • Hash: {result['hash'][:16]}...\n"
        response += f"   • Ledger: {result.get('ledger', 'N/A')}\n"
        response += f"   • Pool: {pool_address[:16]}...\n"
        response += f"   • Asset: {asset_address[:16]}...\n\n"
        response += f"💡 **Next Steps:**\n"
        response += f"   • Yield generation starts immediately\n"
        response += f"   • Use blend_check_my_positions to see your holdings\n"
        response += f"   • Check back later to see earned yield\n\n"
        explorer_network = "public"  # Mainnet-only
        response += f"🔗 **Stellar Explorer**: https://stellar.expert/explorer/{explorer_network}/tx/{result['hash']}\n"
        response += f"👤 Context: {agent_context}"

        return response

    except Exception as e:
        logger.error(f"Error in _blend_supply_to_pool: {e}")
        return f"❌ Error supplying to pool: {str(e)}"


async def _blend_withdraw_from_pool(
    pool_address: str,
    asset_address: str,
    amount: float,
    account_id: str,
    agent_context: AgentContext,
    account_manager: AccountManager,
    network: str = "mainnet"  # Mainnet-only system
) -> str:
    """
    Withdraw assets from a Blend pool with delegated authority.

    Args:
        pool_address: Pool contract ID
        asset_address: Asset contract ID
        amount: Amount to withdraw (decimal)
        account_id: Account ID from AccountManager
        agent_context: Agent execution context with dual authority
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (real funds)

    Returns:
        Formatted string with transaction result
    """
    try:
        # Create Soroban server (mainnet-only)
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        logger.info(f"Agent context {agent_context} withdrawing {amount} from pool {pool_address[:8]}... on {network_label}")

        # Execute withdrawal
        result = await blend_withdraw_collateral(
            pool_address=pool_address,
            asset_address=asset_address,
            amount=amount,
            user_id=agent_context.user_id,  # Use current user from context
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network=network
        )

        if not result.get('success'):
            return f"❌ **Withdrawal Failed**\n\n{result.get('message', 'Unknown error')}"

        # Format success response
        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        response = f"🏧 **Withdrawal Successful on {network_label}!**\n\n"
        response += f"✅ Withdrew {result['amount_withdrawn']} {result['asset_symbol']} from {result['pool']}\n\n"
        response += f"📋 **Transaction Details:**\n"
        response += f"   • Network: {network_label}\n"
        response += f"   • Hash: {result['hash'][:16]}...\n"
        response += f"   • Ledger: {result.get('ledger', 'N/A')}\n"
        response += f"   • Pool: {pool_address[:16]}...\n"
        response += f"   • Asset: {asset_address[:16]}...\n\n"
        response += f"💡 **Next Steps:**\n"
        response += f"   • Funds are now available in your account\n"
        response += f"   • Consider reinvesting in other pools\n\n"
        explorer_network = "public"  # Mainnet-only
        response += f"🔗 **Stellar Explorer**: https://stellar.expert/explorer/{explorer_network}/tx/{result['hash']}\n"
        response += f"👤 Context: {agent_context}"

        return response

    except Exception as e:
        logger.error(f"Error in _blend_withdraw_from_pool: {e}")
        return f"❌ Error withdrawing from pool: {str(e)}"


async def _blend_check_my_positions(
    pool_address: str,
    account_id: str,
    agent_context: AgentContext,
    account_manager: AccountManager,
    network: str = "mainnet"  # Default to mainnet (read operation)
) -> str:
    """
    Check user's positions in a Blend pool with delegated authority.

    Args:
        pool_address: Pool contract ID
        account_id: Account ID from AccountManager
        agent_context: Agent execution context with dual authority
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (mainnet-only)

    Returns:
        Formatted string with position information
    """
    try:
        # Create Soroban server (mainnet-only)
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        logger.info(f"Agent context {agent_context} checking positions in pool {pool_address[:8]}... on {network_label}")

        # Get positions
        result = await blend_get_my_positions(
            pool_address=pool_address,
            user_id=agent_context.user_id,  # Use current user from context
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network=network
        )

        if 'error' in result:
            return f"❌ Error checking positions: {result.get('message', 'Unknown error')}"

        # Format response
        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        response = f"📊 **Your Positions in {result['pool']} ({network_label})**\n\n"

        positions = result.get('positions', {})

        if not positions:
            response += "No positions found in this pool.\n\n"
            response += "💡 Use blend_find_best_yield to find opportunities and blend_supply_to_pool to start earning!\n"
        else:
            total_value = 0
            for asset, pos in positions.items():
                if pos['supplied'] > 0 or pos['borrowed'] > 0:
                    response += f"🪙 **{asset}**\n"
                    if pos['supplied'] > 0:
                        response += f"   • Supplied: {pos['supplied']:,.4f} {asset}\n"
                        response += f"   • Collateral: {'Yes ✅' if pos['collateral'] else 'No'}\n"
                    if pos['borrowed'] > 0:
                        response += f"   • Borrowed: {pos['borrowed']:,.4f} {asset}\n"
                    response += "\n"

        response += f"📍 **Pool**: {pool_address[:16]}...\n"
        response += f"🔗 **Data Source**: {result['data_source']}\n"
        response += f"👤 **Context**: {agent_context}\n\n"
        response += "💡 **Actions**:\n"
        response += "   • Use blend_withdraw_from_pool to withdraw funds\n"
        response += "   • Use blend_supply_to_pool to add more\n"

        return response

    except Exception as e:
        logger.error(f"Error in _blend_check_my_positions: {e}")
        return f"❌ Error checking positions: {str(e)}"


async def _blend_get_pool_apy(
    pool_address: str,
    asset_address: str,
    user_id: str,
    account_manager: AccountManager,
    network: str = "mainnet"  # Default to mainnet (read operation for real yields!)
) -> str:
    """
    Get APY information for a specific asset in a pool.

    Args:
        pool_address: Pool contract ID
        asset_address: Asset contract ID
        user_id: User identifier (injected by tool factory)
        account_manager: AccountManager instance (injected by tool factory)
        network: "mainnet" (real yields)

    Returns:
        Formatted string with APY information
    """
    try:
        # Create Soroban server (mainnet-only)
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        logger.info(f"User {user_id[:8]}... fetching APY for asset in pool on {network_label}...")

        # Get APY data
        apy_data = await blend_get_reserve_apy(
            pool_address=pool_address,
            asset_address=asset_address,
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            network=network
        )

        # Format response
        network_label = "🔴 MAINNET (Real $)" if network == "mainnet" else "🟢 TESTNET (Practice)"
        response = f"📈 **APY Information for {apy_data['asset_symbol']} ({network_label})**\n\n"
        response += f"💰 **Supply APY**: {apy_data['supply_apy']:.2f}% (earn by supplying)\n"
        response += f"💸 **Borrow APY**: {apy_data['borrow_apy']:.2f}% (cost to borrow)\n\n"
        response += f"📊 **Pool Metrics**:\n"
        response += f"   • Total Supplied: {apy_data['total_supplied'] / 1e7:,.2f} {apy_data['asset_symbol']}\n"
        response += f"   • Total Borrowed: {apy_data['total_borrowed'] / 1e7:,.2f} {apy_data['asset_symbol']}\n"
        response += f"   • Available Liquidity: {apy_data['available_liquidity'] / 1e7:,.2f} {apy_data['asset_symbol']}\n"
        response += f"   • Utilization: {apy_data['utilization']:.1%}\n\n"
        response += f"🔗 **Data Source**: {apy_data['data_source']} (live from Blend protocol on {network})\n"
        response += f"📍 **Pool**: {pool_address[:16]}...\n"
        response += f"🪙 **Asset**: {asset_address[:16]}...\n"
        response += f"👤 **User**: {user_id[:8]}...\n"

        return response

    except Exception as e:
        logger.error(f"Error in _blend_get_pool_apy: {e}")
        return f"❌ Error getting APY: {str(e)}"
