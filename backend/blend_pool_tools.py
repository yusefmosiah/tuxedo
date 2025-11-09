#!/usr/bin/env python3
"""
Blend Capital Pool Tools - Direct On-Chain Yield Farming

This module provides autonomous yield farming operations for Blend Capital pools
using direct Soroban RPC calls. Replaces the failing DeFindex API integration.

Features:
- Pool discovery from Backstop contract
- Real-time APY calculation from on-chain reserve data
- Supply/withdraw operations via unified submit() function
- Position tracking for users
- Best yield opportunity finder

Architecture:
- Uses existing stellar_soroban.py infrastructure
- AccountManager integration for user isolation
- No external API dependencies
- 100% on-chain data sources

Created: 2025-11-09
Status: Active - Primary yield farming solution
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
import aiohttp
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from stellar_soroban import soroban_operations

# Monkey-patch aiohttp to respect proxy environment variables
# Required for Claude Code's network proxy (HTTPS_PROXY, HTTP_PROXY)
_original_client_session_init = aiohttp.ClientSession.__init__

def _patched_client_session_init(self, *args, **kwargs):
    """Ensure aiohttp respects HTTP_PROXY/HTTPS_PROXY environment variables"""
    if 'trust_env' not in kwargs:
        kwargs['trust_env'] = True
    _original_client_session_init(self, *args, **kwargs)

aiohttp.ClientSession.__init__ = _patched_client_session_init

logger = logging.getLogger(__name__)

# Blend Capital Testnet Contract Addresses
# Source: https://github.com/blend-capital/blend-utils/blob/main/testnet.contracts.json
BLEND_TESTNET_CONTRACTS = {
    # Core V2 Infrastructure
    'poolFactory': 'CDSMKKCWEAYQW4DAUSH3XGRMIVIJB44TZ3UA5YCRHT6MP4LWEWR4GYV6',
    'backstop': 'CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X',
    'emitter': 'CCS5ACKIDOIVW2QMWBF7H3ZM4ZIH2Q2NP7I3P3GH7YXXGN7I3WND3D6G',

    # Tokens
    'xlm': 'CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC',
    'blnd': 'CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK5A2JN3HEX56T2EDAFO7QF',
    'usdc': 'CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU',
    'weth': 'CAZAQB3D7KSLSNOSQKYD2V4JP5V2Y3B4RDJZRLBFCCIXDCTE3WHSY3UE',
    'wbtc': 'CAP5AMC2OHNVREO66DFIN6DHJMPOBAJ2KCDDIMFBR7WWJH5RZBFM3UEI',

    # Pools
    'comet': 'CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF',
    'cometFactory': 'CCVR5U7CVFQNXVT74PGFSIK23HJMGEWSAAR5NZXSVTNGMFSRUIEHIXHN',

    # Utilities
    'oracleMock': 'CBKKSSMTHJJTQWSIOBJQAIGR42NSY43ZBKKXWF445PE4OLOTOGPOWWF4',
}

# Blend Capital Mainnet Contract Addresses
# Source: https://docs-v1.blend.capital/mainnet-deployments
BLEND_MAINNET_CONTRACTS = {
    # Core V2 Infrastructure
    'backstop': 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7',
    'poolFactory': 'CDSYOAVXFY7SM5S64IZPPPYB4GVGGLMQVFREPSQQEZVIWXX5R23G4QSU',
    'emitter': 'CCOQM6S7ICIUWA225O5PSJWUBEMXGFSSW2PQFO6FP4DQEKMS5DASRGRR',

    # Tokens
    'blnd': 'CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY',
    'usdc': 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75',
    'xlm': 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA',

    # Pools
    'comet': 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM',
    'fixed': 'CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD',
    'yieldBlox': 'CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS',
}

# Network configuration
NETWORK_CONFIG = {
    'testnet': {
        'rpc_url': os.getenv('TESTNET_SOROBAN_RPC_URL', 'https://soroban-testnet.stellar.org'),
        'passphrase': 'Test SDF Network ; September 2015',
        'contracts': BLEND_TESTNET_CONTRACTS,
        'backstop': 'CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X',
    },
    'mainnet': {
        'rpc_url': os.getenv('ANKR_STELLER_RPC', os.getenv('MAINNET_SOROBAN_RPC_URL', 'https://rpc.ankr.com/stellar_soroban')),
        'passphrase': 'Public Global Stellar Network ; September 2015',
        'contracts': BLEND_MAINNET_CONTRACTS,
        'backstop': 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7',
    }
}

# Default network (can be overridden via STELLAR_NETWORK env var)
DEFAULT_NETWORK = os.getenv('STELLAR_NETWORK', 'mainnet')

# Request type enum values from Blend contracts
class RequestType:
    """Blend submit() request types"""
    SUPPLY_COLLATERAL = 0      # Supply assets as collateral (can borrow against)
    WITHDRAW_COLLATERAL = 1    # Withdraw collateral
    SUPPLY = 2                 # Supply without collateral designation
    WITHDRAW = 3               # Withdraw supplied assets
    BORROW = 4                 # Borrow assets
    REPAY = 5                  # Repay borrowed assets
    FILL_USER_LIQUIDATION = 6
    FILL_BAD_DEBT = 7
    FILL_INTEREST = 8


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _get_asset_symbol(
    asset_address: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    user_id: str,
    account_id: Optional[str] = None,
    network: str = "mainnet"
) -> str:
    """
    Get the symbol for an asset token contract.

    Args:
        asset_address: Asset contract ID
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        user_id: User identifier
        account_id: Optional account ID for simulation
        network: "testnet" or "mainnet"

    Returns:
        Asset symbol (e.g., "USDC", "XLM") or shortened address if not found
    """
    try:
        # Try to get symbol from known contracts first
        contracts = NETWORK_CONFIG[network]['contracts']
        for symbol, addr in contracts.items():
            if addr == asset_address:
                return symbol.upper()

        # If no account_id provided, try to get one
        if not account_id:
            accounts = account_manager.get_user_accounts(user_id)
            if accounts:
                account_id = accounts[0]['id']
            else:
                # Can't simulate without an account, return fallback
                return f"{asset_address[:4]}...{asset_address[-4:]}"

        # Try to call the token's symbol() function
        # Most Stellar tokens implement this
        result = await soroban_operations(
            action="simulate",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=asset_address,
            function_name="symbol",
            parameters="[]",
            account_id=account_id,
            network_passphrase=NETWORK_CONFIG[network]['passphrase']
        )

        if result.get('success') and result.get('result'):
            return result['result']

    except Exception as e:
        logger.debug(f"Could not get symbol for {asset_address}: {e}")

    # Fallback: return shortened address
    return f"{asset_address[:4]}...{asset_address[-4:]}"


async def _get_pool_name(
    pool_address: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    user_id: str,
    network: str = "mainnet"
) -> str:
    """
    Get a friendly name for a pool.

    Args:
        pool_address: Pool contract ID
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        user_id: User identifier
        network: "testnet" or "mainnet"

    Returns:
        Pool name or "Unknown Pool"
    """
    try:
        # Check if it's a known pool
        contracts = NETWORK_CONFIG[network]['contracts']
        if pool_address == contracts.get('comet'):
            return "Comet Pool"
        elif pool_address == contracts.get('fixed'):
            return "Fixed Pool"
        elif pool_address == contracts.get('yieldBlox'):
            return "YieldBlox Pool"

        # Try to get name from pool contract
        result = await soroban_operations(
            action="simulate",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=pool_address,
            function_name="name",
            parameters="[]",
            network_passphrase=NETWORK_CONFIG[network]['passphrase']
        )

        if result.get('success') and result.get('result'):
            return result['result']

    except Exception as e:
        logger.debug(f"Could not get name for pool {pool_address}: {e}")

    return f"Pool {pool_address[:8]}"


async def _get_pool_basic_info(
    pool_address: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    user_id: str,
    network: str = "mainnet"
) -> Optional[Dict[str, Any]]:
    """
    Load basic information about a pool.

    Args:
        pool_address: Pool contract ID
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        user_id: User identifier
        network: "testnet" or "mainnet"

    Returns:
        Dictionary with pool info or None if failed
    """
    try:
        pool_name = await _get_pool_name(pool_address, soroban_server, account_manager, user_id, network)

        return {
            'pool_address': pool_address,
            'name': pool_name,
            'status': 'active'
        }
    except Exception as e:
        logger.error(f"Failed to load pool info for {pool_address}: {e}")
        return None


async def _get_pool_reserves(
    pool_address: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    user_id: str,
    network: str = "mainnet"
) -> List[Dict[str, Any]]:
    """
    Get list of reserves (assets) in a pool.

    This queries the pool contract to get all available reserves.
    Each reserve represents an asset that can be supplied/borrowed.

    Args:
        pool_address: Pool contract ID
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        user_id: User identifier
        network: "testnet" or "mainnet"

    Returns:
        List of reserve info dictionaries
    """
    try:
        # Try to get reserves list from pool
        # Note: The exact function name may vary - common names are:
        # - get_reserves()
        # - list_reserves()
        # - reserves()

        result = await soroban_operations(
            action="simulate",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=pool_address,
            function_name="get_reserves",
            parameters="[]",
            network_passphrase=NETWORK_CONFIG[network]['passphrase']
        )

        if not result.get('success'):
            logger.warning(f"Could not get reserves for pool {pool_address}: {result.get('error')}")
            # No fallback - return empty list to indicate failure
            return []

        # Parse the reserves list
        reserves_data = result.get('result', [])
        reserves = []

        for reserve_addr in reserves_data:
            symbol = await _get_asset_symbol(reserve_addr, soroban_server, account_manager, user_id, network=network)
            reserves.append({
                'address': reserve_addr,
                'symbol': symbol
            })

        return reserves

    except Exception as e:
        logger.error(f"Failed to get reserves for pool {pool_address}: {e}")
        return []


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

async def blend_discover_pools(
    network: str = "mainnet",
    soroban_server: Optional[SorobanServerAsync] = None,
    account_manager: Optional[AccountManager] = None,
    user_id: str = "system"
) -> List[Dict[str, Any]]:
    """
    Discover all active Blend pools from hardcoded pool registry.

    Returns information about known Blend Capital pools on the specified network.
    For mainnet: Comet, Fixed, and YieldBlox pools.

    Args:
        network: "testnet" or "mainnet"
        soroban_server: SorobanServerAsync instance (created if None)
        account_manager: AccountManager instance (created if None)
        user_id: User identifier (default "system" for discovery)

    Returns:
        List of pool dictionaries with basic information:
        [
            {
                'pool_address': 'CAS3FL6...',
                'name': 'Comet',
                'status': 'active'
            },
            ...
        ]
    """
    try:
        # Create server if not provided
        if soroban_server is None:
            soroban_server = SorobanServerAsync(NETWORK_CONFIG[network]['rpc_url'])

        # Create account manager if not provided
        if account_manager is None:
            from account_manager import AccountManager
            account_manager = AccountManager()

        logger.info(f"Discovering Blend pools on {network} from registry...")

        # Get pool addresses from configuration
        contracts = NETWORK_CONFIG[network]['contracts']

        # Define pool mappings with proper names
        pool_mappings = []
        if network == 'mainnet':
            pool_mappings = [
                ('comet', 'Comet'),
                ('fixed', 'Fixed'),
                ('yieldBlox', 'YieldBlox')
            ]
        else:  # testnet
            pool_mappings = [
                ('comet', 'Comet'),
                ('stable', 'Stable'),
                ('fixed', 'Fixed')
            ]

        pools = []
        for key, name in pool_mappings:
            if key in contracts:
                pool_address = contracts[key]
                logger.info(f"Found pool: {name} ({pool_address})")

                # Get basic info for the pool
                pool_info = await _get_pool_basic_info(
                    pool_address,
                    soroban_server,
                    account_manager,
                    user_id,
                    network
                )

                if pool_info:
                    # Override name with our known name
                    pool_info['name'] = name
                    pools.append(pool_info)
                else:
                    # Even if we can't get info, include the pool
                    pools.append({
                        'pool_address': pool_address,
                        'name': name,
                        'status': 'active'
                    })

        logger.info(f"Discovered {len(pools)} pools on {network}")
        return pools

    except Exception as e:
        error_msg = f"Fatal error in blend_discover_pools on {network}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


async def blend_get_reserve_apy(
    pool_address: str,
    asset_address: str,
    user_id: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Get real APY data for a reserve in a pool by querying on-chain data.

    This function calls the pool's get_reserve() function to fetch the
    ReserveData structure, then calculates APY from the on-chain rates.

    Args:
        pool_address: Pool contract ID
        asset_address: Asset contract ID
        user_id: User identifier
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        network: "testnet" or "mainnet"

    Returns:
        Dictionary with APY and reserve metrics:
        {
            'asset_address': 'CAQCF...',
            'asset_symbol': 'USDC',
            'supply_apy': 12.5,         # Percentage
            'borrow_apy': 15.2,
            'total_supplied': 1000000,   # Scaled units
            'total_borrowed': 750000,
            'utilization': 0.75,
            'available_liquidity': 250000,
            'data_source': 'on_chain'
        }
    """
    try:
        # Build parameters for get_reserve(asset: Address)
        parameters = json.dumps([
            {"type": "address", "value": asset_address}
        ])

        logger.info(f"Fetching reserve data for {asset_address[:8]}... from pool {pool_address[:8]}...")

        # Get or create a system account for read-only operations
        # List existing accounts first
        accounts = account_manager.get_user_accounts(user_id)

        # Use first available account, or create one if none exist
        account_id = None
        if accounts:
            account_id = accounts[0]['id']
        else:
            # Create a temporary system account for read-only operations
            create_result = account_manager.generate_account(user_id, chain="stellar", name="blend_readonly")
            if create_result.get('success'):
                account_id = create_result['account']['id']
            else:
                raise ValueError("Failed to create read-only account for simulation")

        # Use simulate (read-only, no fees)
        result = await soroban_operations(
            action="simulate",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=pool_address,
            function_name="get_reserve",
            parameters=parameters,
            account_id=account_id,
            network_passphrase=NETWORK_CONFIG[network]['passphrase']
        )

        if not result.get('success'):
            raise ValueError(f"Failed to get reserve data: {result.get('error')}")

        reserve = result['result']

        # Extract reserve data
        reserve_data = reserve.get('data', {})
        reserve_config = reserve.get('config', {})

        # Calculate APY from rates
        # b_rate is supply rate (what suppliers earn) - Stellar uses 7 decimals
        b_rate = reserve_data.get('b_rate', 0)
        supply_rate = b_rate / 1e7
        supply_apr = supply_rate
        supply_apy = ((1 + supply_apr / 365) ** 365 - 1) * 100

        # d_rate is borrow rate
        d_rate = reserve_data.get('d_rate', 0)
        borrow_rate = d_rate / 1e7
        borrow_apr = borrow_rate
        borrow_apy = ((1 + borrow_apr / 365) ** 365 - 1) * 100

        # Calculate metrics
        total_supplied = reserve_data.get('b_supply', 0)
        total_borrowed = reserve_data.get('d_supply', 0)
        available = total_supplied - total_borrowed
        utilization = total_borrowed / total_supplied if total_supplied > 0 else 0

        # Get asset symbol
        asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, user_id, account_id)

        logger.info(f"Reserve {asset_symbol}: Supply APY = {supply_apy:.2f}%, Utilization = {utilization:.1%}")

        return {
            'asset_address': asset_address,
            'asset_symbol': asset_symbol,
            'supply_apy': round(supply_apy, 2),
            'borrow_apy': round(borrow_apy, 2),
            'total_supplied': total_supplied,
            'total_borrowed': total_borrowed,
            'utilization': round(utilization, 4),
            'available_liquidity': available,
            'data_source': 'on_chain'
        }

    except Exception as e:
        logger.error(f"Error in blend_get_reserve_apy: {e}")
        raise ValueError(f"Failed to get reserve APY: {str(e)}")


async def blend_supply_collateral(
    pool_address: str,
    asset_address: str,
    amount: float,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Supply assets to a Blend pool to earn yield (autonomous operation).

    This function builds and submits a transaction to supply assets as collateral
    to a Blend pool using the unified submit() function with SupplyCollateral request type.

    Args:
        pool_address: Pool contract ID (e.g., Comet pool)
        asset_address: Asset to supply (e.g., USDC, XLM)
        amount: Amount in decimal units (e.g., 100.5)
        user_id: User identifier for permission checks
        account_id: Account ID from AccountManager
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        network: "testnet" or "mainnet"

    Returns:
        Dictionary with transaction result:
        {
            'success': True,
            'hash': 'abc123...',
            'amount_supplied': 100.5,
            'asset_symbol': 'USDC',
            'pool': 'Comet Pool',
            'message': 'Successfully supplied 100.5 USDC to Comet Pool'
        }
    """
    try:
        # Get account details for user address
        account_data = account_manager._get_account_by_id(account_id)
        user_address = account_data['public_key']

        logger.info(f"Supplying {amount} to pool {pool_address[:8]}... from account {user_address[:8]}...")

        # Scale amount to asset decimals (Stellar uses 7)
        amount_scaled = int(amount * 10_000_000)

        # Build Request struct as a map
        # Request { amount: Int128, request_type: u32, address: Address }
        request_map = {
            "amount": {"type": "int128", "value": str(amount_scaled)},
            "request_type": {"type": "uint32", "value": RequestType.SUPPLY_COLLATERAL},
            "address": {"type": "address", "value": asset_address}
        }

        # Build parameters for submit(from, spender, to, requests)
        parameters = json.dumps([
            {"type": "address", "value": user_address},  # from
            {"type": "address", "value": user_address},  # spender
            {"type": "address", "value": user_address},  # to
            {
                "type": "vec",
                "value": [
                    {"type": "map", "value": request_map}
                ]
            }
        ])

        # Execute via invoke action
        result = await soroban_operations(
            action="invoke",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=pool_address,
            function_name="submit",
            parameters=parameters,
            account_id=account_id,
            auto_sign=True,
            network_passphrase=NETWORK_CONFIG[network]['passphrase']
        )

        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': f"Failed to supply {amount} to pool"
            }

        # Get asset symbol for user-friendly message
        asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, user_id, network=network)
        pool_name = await _get_pool_name(pool_address, soroban_server, account_manager, user_id, network)

        tx_hash = result.get('hash', 'unknown')

        logger.info(f"✅ Successfully supplied {amount} {asset_symbol} to {pool_name}. Tx: {tx_hash}")

        return {
            'success': True,
            'hash': tx_hash,
            'ledger': result.get('ledger'),
            'amount_supplied': amount,
            'asset_symbol': asset_symbol,
            'pool': pool_name,
            'message': f"✅ Successfully supplied {amount} {asset_symbol} to {pool_name}. Tx: {tx_hash[:16]}..."
        }

    except Exception as e:
        logger.error(f"Error in blend_supply_collateral: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to supply collateral: {str(e)}"
        }


async def blend_withdraw_collateral(
    pool_address: str,
    asset_address: str,
    amount: float,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Withdraw supplied assets from a Blend pool (autonomous operation).

    This function builds and submits a transaction to withdraw assets from collateral
    using the unified submit() function with WithdrawCollateral request type.

    Args:
        pool_address: Pool contract ID
        asset_address: Asset to withdraw
        amount: Amount in decimal units (e.g., 50.0)
        user_id: User identifier for permission checks
        account_id: Account ID from AccountManager
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        network: "testnet" or "mainnet"

    Returns:
        Dictionary with transaction result
    """
    try:
        # Get account details for user address
        account_data = account_manager._get_account_by_id(account_id)
        user_address = account_data['public_key']

        logger.info(f"Withdrawing {amount} from pool {pool_address[:8]}... to account {user_address[:8]}...")

        # Scale amount to asset decimals (Stellar uses 7)
        amount_scaled = int(amount * 10_000_000)

        # Build Request struct for withdrawal
        request_map = {
            "amount": {"type": "int128", "value": str(amount_scaled)},
            "request_type": {"type": "uint32", "value": RequestType.WITHDRAW_COLLATERAL},
            "address": {"type": "address", "value": asset_address}
        }

        # Build parameters for submit(from, spender, to, requests)
        parameters = json.dumps([
            {"type": "address", "value": user_address},  # from
            {"type": "address", "value": user_address},  # spender
            {"type": "address", "value": user_address},  # to
            {
                "type": "vec",
                "value": [
                    {"type": "map", "value": request_map}
                ]
            }
        ])

        # Execute via invoke action
        result = await soroban_operations(
            action="invoke",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=pool_address,
            function_name="submit",
            parameters=parameters,
            account_id=account_id,
            auto_sign=True,
            network_passphrase=NETWORK_CONFIG[network]['passphrase']
        )

        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': f"Failed to withdraw {amount} from pool"
            }

        # Get asset symbol for user-friendly message
        asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, user_id, network=network)
        pool_name = await _get_pool_name(pool_address, soroban_server, account_manager, user_id, network)

        tx_hash = result.get('hash', 'unknown')

        logger.info(f"✅ Successfully withdrew {amount} {asset_symbol} from {pool_name}. Tx: {tx_hash}")

        return {
            'success': True,
            'hash': tx_hash,
            'ledger': result.get('ledger'),
            'amount_withdrawn': amount,
            'asset_symbol': asset_symbol,
            'pool': pool_name,
            'message': f"✅ Successfully withdrew {amount} {asset_symbol} from {pool_name}. Tx: {tx_hash[:16]}..."
        }

    except Exception as e:
        logger.error(f"Error in blend_withdraw_collateral: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to withdraw collateral: {str(e)}"
        }


async def blend_get_my_positions(
    pool_address: str,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Check user's current positions in a Blend pool.

    This function queries the pool contract for the user's positions,
    including supplied assets, borrowed assets, and collateral status.

    Args:
        pool_address: Pool contract ID
        user_id: User identifier
        account_id: Account ID from AccountManager
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        network: "testnet" or "mainnet"

    Returns:
        Dictionary with position information:
        {
            'pool': 'Comet Pool',
            'positions': {
                'USDC': {
                    'supplied': 100.5,
                    'borrowed': 0,
                    'collateral': True
                },
                'XLM': {
                    'supplied': 1000,
                    'borrowed': 50,
                    'collateral': True
                }
            },
            'data_source': 'on_chain'
        }
    """
    try:
        # Get user address
        account_data = account_manager._get_account_by_id(account_id)
        user_address = account_data['public_key']

        logger.info(f"Fetching positions for account {user_address[:8]}... in pool {pool_address[:8]}...")

        # Call get_positions(address: Address)
        parameters = json.dumps([
            {"type": "address", "value": user_address}
        ])

        result = await soroban_operations(
            action="simulate",  # Read-only
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=pool_address,
            function_name="get_positions",
            parameters=parameters,
            account_id=account_id,
            network_passphrase=NETWORK_CONFIG[network]['passphrase']
        )

        if not result.get('success'):
            return {
                'error': result.get('error'),
                'message': f"Failed to get positions: {result.get('error')}"
            }

        positions_data = result.get('result', {})

        # Parse positions (structure: { liabilities: Map, collateral: Map, supply: Map })
        liabilities = positions_data.get('liabilities', {})
        collateral = positions_data.get('collateral', {})
        supply = positions_data.get('supply', {})

        # Format positions by asset
        formatted_positions = {}

        # Process all assets that appear in any category
        all_assets = set()
        all_assets.update(liabilities.keys())
        all_assets.update(collateral.keys())
        all_assets.update(supply.keys())

        for asset_address in all_assets:
            symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, user_id, network=network)

            # Convert from scaled units (7 decimals)
            supplied_amount = collateral.get(asset_address, 0) / 1e7
            borrowed_amount = liabilities.get(asset_address, 0) / 1e7
            has_collateral = asset_address in collateral

            formatted_positions[symbol] = {
                'supplied': supplied_amount,
                'borrowed': borrowed_amount,
                'collateral': has_collateral
            }

        pool_name = await _get_pool_name(pool_address, soroban_server, account_manager, user_id, network)

        return {
            'pool': pool_name,
            'positions': formatted_positions,
            'data_source': 'on_chain'
        }

    except Exception as e:
        logger.error(f"Error in blend_get_my_positions: {e}")
        return {
            'error': str(e),
            'message': f"Failed to get positions: {str(e)}"
        }


async def blend_find_best_yield(
    asset_symbol: str,
    min_apy: float = 0.0,
    user_id: str = "system",
    soroban_server: Optional[SorobanServerAsync] = None,
    account_manager: Optional[AccountManager] = None,
    network: str = "mainnet"
) -> List[Dict[str, Any]]:
    """
    Find best yield opportunities across all Blend pools for a given asset.

    This function discovers all pools, queries each for the specified asset's
    APY, and returns a sorted list of opportunities.

    Args:
        asset_symbol: Asset symbol (e.g., "USDC", "XLM")
        min_apy: Minimum APY threshold (default 0.0)
        user_id: User identifier (default "system")
        soroban_server: SorobanServerAsync instance (created if None)
        account_manager: AccountManager instance (created if None)
        network: "testnet" or "mainnet"

    Returns:
        Sorted list of opportunities (highest APY first):
        [
            {
                'pool': 'Comet Pool',
                'pool_address': 'CCQ74...',
                'asset': 'USDC',
                'apy': 12.5,
                'available_liquidity': 500000,
                'utilization': 0.75
            },
            ...
        ]
    """
    try:
        # Create server if not provided
        if soroban_server is None:
            soroban_server = SorobanServerAsync(NETWORK_CONFIG[network]['rpc_url'])

        # Create account manager if not provided
        if account_manager is None:
            from account_manager import AccountManager
            account_manager = AccountManager()

        logger.info(f"Finding best yield for {asset_symbol} across all Blend pools...")

        # 1. Discover all pools
        pools = await blend_discover_pools(network, soroban_server, account_manager, user_id)

        logger.info(f"Discovered {len(pools)} pools, searching for {asset_symbol} reserves...")

        # 2. For each pool, get reserves and find the asset
        opportunities = []

        for pool in pools:
            pool_address = pool['pool_address']

            try:
                # Get reserve list from pool
                reserves = await _get_pool_reserves(pool_address, soroban_server, account_manager, user_id, network)

                # Find the asset in reserves
                for reserve in reserves:
                    if reserve['symbol'].upper() == asset_symbol.upper():
                        # Get APY data
                        try:
                            apy_data = await blend_get_reserve_apy(
                                pool_address,
                                reserve['address'],
                                user_id,
                                soroban_server,
                                account_manager,
                                network
                            )

                            if apy_data['supply_apy'] >= min_apy:
                                opportunities.append({
                                    'pool': pool['name'],
                                    'pool_address': pool_address,
                                    'asset': asset_symbol.upper(),
                                    'asset_address': reserve['address'],
                                    'apy': apy_data['supply_apy'],
                                    'available_liquidity': apy_data['available_liquidity'] / 1e7,
                                    'utilization': apy_data['utilization']
                                })

                        except Exception as e:
                            logger.warning(f"Could not get APY for {asset_symbol} in {pool['name']}: {e}")
                            continue

            except Exception as e:
                logger.warning(f"Could not process pool {pool['name']}: {e}")
                continue

        # Sort by APY descending
        opportunities.sort(key=lambda x: x['apy'], reverse=True)

        logger.info(f"Found {len(opportunities)} yield opportunities for {asset_symbol}")

        return opportunities

    except Exception as e:
        logger.error(f"Error in blend_find_best_yield: {e}")
        return []
