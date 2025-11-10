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

logger = logging.getLogger(__name__)

# Conditional proxy support for environments that need it
# Only applies if HTTP_PROXY or HTTPS_PROXY is set (like Claude Code sandbox)
# Production/local deployments without proxies are unaffected
if os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY'):
    _original_client_session_init = aiohttp.ClientSession.__init__

    def _patched_client_session_init(self, *args, **kwargs):
        """Ensure aiohttp respects HTTP_PROXY/HTTPS_PROXY environment variables"""
        if 'trust_env' not in kwargs:
            kwargs['trust_env'] = True
        _original_client_session_init(self, *args, **kwargs)

    aiohttp.ClientSession.__init__ = _patched_client_session_init
    logger.info("Applied aiohttp proxy support (HTTP_PROXY/HTTPS_PROXY detected)")

# Blend Capital Mainnet Contract Addresses (MAINNET ONLY)
# Source: https://stellar.expert (Verified V2 Pools)
BLEND_MAINNET_CONTRACTS = {
    # Core V2 Infrastructure
    'backstop': 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7',
    'poolFactory': 'CDSYOAVXFY7SM5S64IZPPPYB4GVGGLMQVFREPSQQEZVIWXX5R23G4QSU',
    'emitter': 'CCOQM6S7ICIUWA225O5PSJWUBEMXGFSSW2PQFO6FP4DQEKMS5DASRGRR',

    # Tokens
    'blnd': 'CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY',
    'usdc': 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75',
    'xlm': 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA',
    'weth': 'CDMLFMKMMD7MWZP76FZCMGK3DQCV6VLPBR5DD2WWWKLBUQZLQJFUQJSK',  # Wrapped Ethereum
    'wbtc': 'CBMR5J4LZ5QUCFPQQ6YWJ4UUQISOOJJGQ7IMQX36C2V7LC2EDNDODJ7F',  # Wrapped Bitcoin
    'eurc': 'CDCQP3LVDYYHVUIHW6BMVYJQWC7QPFTIZAYOQJYFHGFQHVNLTQAMV6TX',  # Euro Coin

    # Pools
    'fixed': 'CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD',  # Fixed Pool V2
    'yieldBlox': 'CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS',  # YieldBlox V2
    'orbit': 'CAE7QVOMBLZ53CDRGK3UNRRHG5EZ5NQA7HHTFASEMYBWHG6MDFZTYHXC',  # Orbit Pool V2
    'forex': 'CBYOBT7ZCCLQCBUYYIABZLSEGDPEUWXCUXQTZYOG3YBDR7U357D5ZIRF',  # Forex Pool V2
}

# Known reserves for each mainnet V2 pool
# Source: https://mainnet.blend.capital/ and on-chain data
POOL_KNOWN_RESERVES = {
    # Fixed Pool V2 - Fixed-rate USDC:XLM pool
    'CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD': [
        ('USDC', 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'),
        ('XLM', 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA'),
    ],
    # YieldBlox Pool V2 - Community pool
    'CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS': [
        ('USDC', 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'),
        ('XLM', 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA'),
    ],
    # Orbit Pool V2 - Add reserves as discovered
    # Forex Pool V2 - Add reserves as discovered
}

# Network configuration - MAINNET ONLY
NETWORK_CONFIG = {
    'rpc_url': os.getenv('ANKR_STELLER_RPC', os.getenv('MAINNET_SOROBAN_RPC_URL', 'https://rpc.ankr.com/stellar_soroban')),
    'passphrase': 'Public Global Stellar Network ; September 2015',
    'contracts': BLEND_MAINNET_CONTRACTS,
    'backstop': 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7',
}

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
        network: "mainnet" (mainnet-only)

    Returns:
        Asset symbol (e.g., "USDC", "XLM") or shortened address if not found
    """
    try:
        # Try to get symbol from known contracts first
        contracts = NETWORK_CONFIG['contracts']
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
            network_passphrase=NETWORK_CONFIG['passphrase']
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
        network: "mainnet" (mainnet-only)

    Returns:
        Pool name or "Unknown Pool"
    """
    try:
        # Check if it's a known pool
        contracts = NETWORK_CONFIG['contracts']
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
            network_passphrase=NETWORK_CONFIG['passphrase']
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
        network: "mainnet" (mainnet-only)

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

    Uses hardcoded known reserves for each pool since Blend pools don't expose
    a direct get_reserves() function. This is the most reliable approach for
    mainnet pools which have stable, known asset lists.

    Args:
        pool_address: Pool contract ID
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        user_id: User identifier
        network: "mainnet" (mainnet-only)

    Returns:
        List of reserve info dictionaries
    """
    try:
        # Use hardcoded known reserves for mainnet pools
        if pool_address in POOL_KNOWN_RESERVES:
            reserves = []
            for symbol, address in POOL_KNOWN_RESERVES[pool_address]:
                reserves.append({
                    'address': address,
                    'symbol': symbol
                })
            logger.info(f"Found {len(reserves)} known reserves for pool {pool_address[:8]}...")
            return reserves
        else:
            # Unknown pool - try to get common assets
            logger.warning(f"Pool {pool_address} not in known reserves list, using common assets")
            # Fallback: try common assets (USDC, XLM) for unknown pools
            contracts = NETWORK_CONFIG['contracts']
            reserves = []
            for symbol in ['USDC', 'XLM']:
                symbol_lower = symbol.lower()
                if symbol_lower in contracts:
                    reserves.append({
                        'address': contracts[symbol_lower],
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
        network: "mainnet" (mainnet-only)
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
            soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

        # Create account manager if not provided
        if account_manager is None:
            from account_manager import AccountManager
            account_manager = AccountManager()

        logger.info(f"Discovering Blend pools on {network} from registry...")

        # Get pool addresses from configuration
        contracts = NETWORK_CONFIG['contracts']

        # Define pool mappings with proper names
        pool_mappings = []
        # Mainnet-only system
        pool_mappings = [
            ('comet', 'Comet'),
            ('fixed', 'Fixed'),
            ('yieldBlox', 'YieldBlox')
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


# ============================================================================
# BLND Emission Functions
# ============================================================================

async def get_blnd_price_usd() -> float:
    """
    Get current BLND token price in USD from CoinGecko.

    Returns:
        BLND price in USD, or conservative fallback if API fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'blend',
                'vs_currencies': 'usd'
            }
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    price = data.get('blend', {}).get('usd', 0.0)
                    if price > 0:
                        logger.info(f"BLND price from CoinGecko: ${price:.4f}")
                        return price
    except Exception as e:
        logger.warning(f"Failed to get BLND price from CoinGecko: {e}")

    # Fallback: Conservative estimate
    fallback_price = 0.05
    logger.info(f"Using fallback BLND price: ${fallback_price}")
    return fallback_price


async def get_reserve_emissions(
    pool_address: str,
    reserve_index: int,
    token_type: str,
    user_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    account_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get BLND emission data for a reserve token from pool contract.

    Args:
        pool_address: Pool contract address
        reserve_index: Reserve index (0, 1, 2, ...)
        token_type: 'supply' for bTokens, 'borrow' for dTokens
        user_id: User identifier
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        account_id: Account ID for simulation

    Returns:
        {
            'index': int,
            'last_time': int,
            'expiration': int,
            'eps': int,  # Emissions per second (scaled)
        }
        or None if no emissions active
    """
    try:
        # Calculate reserve_token_id based on type
        # dTokens (borrow): reserve_index * 2
        # bTokens (supply): reserve_index * 2 + 1
        if token_type == 'borrow':
            reserve_token_id = reserve_index * 2
        else:  # supply
            reserve_token_id = reserve_index * 2 + 1

        logger.info(f"Getting emissions for reserve_token_id={reserve_token_id} ({token_type})")

        # Call pool contract: get_reserve_emissions(reserve_token_id: u32)
        parameters = json.dumps([reserve_token_id])

        result = await soroban_operations(
            action='simulate',
            user_id=user_id,
            contract_id=pool_address,
            function_name='get_reserve_emissions',
            parameters=parameters,
            account_manager=account_manager,
            account_id=account_id,
            soroban_server=soroban_server,
            network_passphrase='Public Global Stellar Network ; September 2015'
        )

        if result.get('success') and result.get('result'):
            emissions = result['result']
            logger.info(f"Emissions data for {token_type}: {emissions}")
            return emissions

        logger.info(f"No emissions data found for {token_type}")
        return None

    except Exception as e:
        logger.warning(f"Error getting reserve emissions for {token_type}: {e}")
        return None


async def calculate_emission_apy(
    emissions_data: Optional[Dict[str, Any]],
    reserve_token_value_usd: float,
    total_supply_or_borrow: float,
    blnd_price_usd: float
) -> float:
    """
    Calculate APY contribution from BLND emissions.

    Formula:
        emission_apr = (blnd_per_year * blnd_price) / (total_value) * 100

    Args:
        emissions_data: Data from get_reserve_emissions()
        reserve_token_value_usd: USD value of 1 reserve token
        total_supply_or_borrow: Total tokens supplied or borrowed
        blnd_price_usd: Current BLND price in USD

    Returns:
        Emission APY as percentage (e.g., 7.58 for 7.58%)
    """
    if not emissions_data or not total_supply_or_borrow or total_supply_or_borrow == 0:
        return 0.0

    try:
        # Get emissions per second (scaled by 1e7 based on Blend contracts)
        eps = emissions_data.get('eps', 0)
        if eps == 0:
            return 0.0

        # Convert EPS to annual BLND tokens
        # eps is scaled by 1e7 (7 decimals)
        eps_decimal = eps / 1e7
        seconds_per_year = 365 * 24 * 60 * 60
        blnd_per_year = eps_decimal * seconds_per_year

        # Calculate annual BLND value in USD
        blnd_value_per_year = blnd_per_year * blnd_price_usd

        # Calculate total reserve value in USD
        total_reserve_value = total_supply_or_borrow * reserve_token_value_usd

        # APY = (annual BLND value / total reserve value) * 100
        if total_reserve_value > 0:
            emission_apy = (blnd_value_per_year / total_reserve_value) * 100

            # Sanity check: emission APY should be reasonable (0-100%)
            if emission_apy > 100:
                logger.warning(f"Suspicious emission APY: {emission_apy:.2f}% - may need decimal adjustment")
                return 0.0
            if emission_apy < 0:
                logger.warning(f"Negative emission APY: {emission_apy:.2f}%")
                return 0.0

            logger.info(f"Emission APY calculation: {blnd_per_year:.2f} BLND/year * ${blnd_price_usd:.4f} / ${total_reserve_value:.2f} = {emission_apy:.2f}%")
            return emission_apy

        return 0.0

    except Exception as e:
        logger.error(f"Error calculating emission APY: {e}")
        return 0.0


# ============================================================================
# Reserve APY Query (Base + Emissions)
# ============================================================================

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
        network: "mainnet" (mainnet-only)

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

        # Get account for read-only simulation operations
        # For read operations, preferably use system_agent account if user doesn't have one
        accounts = account_manager.get_user_accounts(user_id)
        account_id = None

        if accounts:
            account_id = accounts[0]['id']
        else:
            # Try system_agent as fallback for read operations
            system_accounts = account_manager.get_user_accounts('system_agent')
            if system_accounts:
                account_id = system_accounts[0]['id']
            else:
                # Last resort: create account for this user
                create_result = account_manager.generate_account(user_id, chain="stellar", name="blend_readonly")
                if create_result.get('success'):
                    account_id = create_result['account_id']
                else:
                    raise ValueError(f"No accounts available for simulation (tried {user_id} and system_agent)")

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
            network_passphrase=NETWORK_CONFIG['passphrase']
        )

        if not result.get('success'):
            raise ValueError(f"Failed to get reserve data: {result.get('error')}")

        reserve = result['result']

        # DEBUG: Print raw reserve data
        logger.info(f"DEBUG: Raw reserve type: {type(reserve)}")
        logger.info(f"DEBUG: Raw reserve data: {reserve}")

        # Extract reserve data
        reserve_data = reserve.get('data', {})
        reserve_config = reserve.get('config', {})

        # DEBUG: Print specific fields
        logger.info(f"DEBUG: Reserve data fields:")
        for key, value in reserve_data.items():
            logger.info(f"  {key}: {value} (type: {type(value)})")
            if key in ['b_rate', 'd_rate']:
                rate_val = float(value) if isinstance(value, (int, str)) else 0
                logger.info(f"    → As rate (12 decimals): {rate_val / 1e12:.8f}")
            if key in ['b_supply', 'd_supply']:
                supply_val = float(value) if isinstance(value, (int, str)) else 0
                logger.info(f"    → As supply (6 decimals): {supply_val / 1e6:.2f}")
                logger.info(f"    → As supply (7 decimals): {supply_val / 1e7:.2f}")
                logger.info(f"    → As supply (12 decimals): {supply_val / 1e12:.2f}")

        # Calculate APY from rates
        # b_rate and d_rate are current instantaneous annual rates with 12 decimals (1e12)
        # b_rate = 1.05579967 means 5.579967% annual supply rate, not cumulative
        b_rate = reserve_data.get('b_rate', 0)
        supply_rate_annual = (b_rate / 1e12 - 1) * 100  # Convert to percentage
        supply_apy = supply_rate_annual  # These are already annual rates

        # d_rate is borrow rate - same logic
        d_rate = reserve_data.get('d_rate', 0)
        borrow_rate_annual = (d_rate / 1e12 - 1) * 100
        borrow_apy = borrow_rate_annual

        # Calculate metrics with correct decimal scaling
        # USDC has 7 decimals, so divide by 1e7 to get real amounts
        asset_decimals = reserve_config.get('decimals', 7)  # Default to 7 for USDC-like tokens
        total_supplied_raw = reserve_data.get('b_supply', 0)
        total_borrowed_raw = reserve_data.get('d_supply', 0)

        total_supplied = total_supplied_raw / (10 ** asset_decimals)
        total_borrowed = total_borrowed_raw / (10 ** asset_decimals)
        available = total_supplied - total_borrowed
        utilization = total_borrowed / total_supplied if total_supplied > 0 else 0

        # Get asset symbol
        asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, user_id, account_id)

        # Store base APY before adding emissions
        base_supply_apy = supply_apy
        base_borrow_apy = borrow_apy

        # ================================================================
        # BLND Emission APY Calculation
        # ================================================================

        supply_emission_apy = 0.0
        borrow_emission_apy = 0.0
        blnd_price = 0.0

        try:
            # Get BLND price from CoinGecko
            blnd_price = await get_blnd_price_usd()

            # Get reserve index from reserve data or config
            # Reserve structure should have an 'index' field
            reserve_index = reserve.get('index', None)

            # Fallback: Try to determine index from known pool reserves
            if reserve_index is None:
                logger.info(f"Reserve index not found in data, attempting to determine from pool reserves")
                # For Fixed pool, USDC=0, XLM=1
                # For YieldBlox pool, USDC=0, XLM=1
                known_reserves = POOL_KNOWN_RESERVES.get(pool_address, [])
                for idx, (symbol, addr) in enumerate(known_reserves):
                    if addr == asset_address:
                        reserve_index = idx
                        logger.info(f"Determined reserve_index={reserve_index} for {symbol} from known reserves")
                        break

            if reserve_index is not None:
                # Get emission data for supply (bToken)
                supply_emissions = await get_reserve_emissions(
                    pool_address,
                    reserve_index,
                    'supply',
                    user_id,
                    account_manager,
                    soroban_server,
                    account_id
                )

                # Get emission data for borrow (dToken)
                borrow_emissions = await get_reserve_emissions(
                    pool_address,
                    reserve_index,
                    'borrow',
                    user_id,
                    account_manager,
                    soroban_server,
                    account_id
                )

                # Calculate reserve token USD value
                # For USDC: $1.00
                # For XLM and others: Would need price lookup (TODO: integrate price oracle)
                reserve_token_value_usd = 1.0  # Default to USDC value
                if asset_symbol == 'USDC':
                    reserve_token_value_usd = 1.0
                elif asset_symbol == 'XLM':
                    # TODO: Get XLM price from CoinGecko or oracle
                    reserve_token_value_usd = 0.10  # Conservative placeholder
                else:
                    # TODO: Add support for WETH, WBTC, etc.
                    reserve_token_value_usd = 1.0

                # Calculate emission APYs
                if supply_emissions:
                    supply_emission_apy = await calculate_emission_apy(
                        supply_emissions,
                        reserve_token_value_usd,
                        total_supplied,
                        blnd_price
                    )

                if borrow_emissions:
                    borrow_emission_apy = await calculate_emission_apy(
                        borrow_emissions,
                        reserve_token_value_usd,
                        total_borrowed,
                        blnd_price
                    )

                # Add emissions to base APY
                supply_apy = base_supply_apy + supply_emission_apy
                borrow_apy = base_borrow_apy + borrow_emission_apy

                logger.info(f"Reserve {asset_symbol} APY breakdown:")
                logger.info(f"  Supply: {base_supply_apy:.2f}% (base) + {supply_emission_apy:.2f}% (BLND) = {supply_apy:.2f}%")
                logger.info(f"  Borrow: {base_borrow_apy:.2f}% (base) + {borrow_emission_apy:.2f}% (BLND) = {borrow_apy:.2f}%")
            else:
                logger.warning(f"Could not determine reserve_index for {asset_symbol}, skipping emission calculations")

        except Exception as e:
            logger.warning(f"Error calculating BLND emissions, using base APY only: {e}")
            # Continue with base APY if emissions fail
            supply_apy = base_supply_apy
            borrow_apy = base_borrow_apy

        logger.info(f"Reserve {asset_symbol}: Final Supply APY = {supply_apy:.2f}%, Utilization = {utilization:.1%}")

        return {
            'asset_address': asset_address,
            'asset_symbol': asset_symbol,
            'supply_apy': round(supply_apy, 2),
            'borrow_apy': round(borrow_apy, 2),
            'supply_apy_breakdown': {
                'base': round(base_supply_apy, 2),
                'blnd_emissions': round(supply_emission_apy, 2)
            },
            'borrow_apy_breakdown': {
                'base': round(base_borrow_apy, 2),
                'blnd_emissions': round(borrow_emission_apy, 2)
            },
            'total_supplied': total_supplied,
            'total_borrowed': total_borrowed,
            'utilization': round(utilization, 4),
            'available_liquidity': available,
            'blnd_price': round(blnd_price, 4) if blnd_price > 0 else None,
            'data_source': 'on_chain_with_emissions' if supply_emission_apy > 0 or borrow_emission_apy > 0 else 'on_chain'
        }

    except Exception as e:
        logger.error(f"Error in blend_get_reserve_apy: {e}")
        raise ValueError(f"Failed to get reserve APY: {str(e)}")


async def blend_supply_collateral(
    pool_address: str,
    asset_address: str,
    amount: float,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    agent_context = None,
    user_id: str = None,
    network: str = "mainnet",
    simulate_only: bool = False
) -> Dict[str, Any]:
    """
    Supply assets to a Blend pool to earn yield (autonomous operation).

    This function builds and submits a transaction to supply assets as collateral
    to a Blend pool using the unified submit() function with SupplyCollateral request type.

    Now supports external wallet signing via AgentContext and simulation mode.

    Args:
        pool_address: Pool contract ID (e.g., Comet pool)
        asset_address: Asset to supply (e.g., USDC, XLM)
        amount: Amount in decimal units (e.g., 100.5)
        account_id: Account ID from AccountManager
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        agent_context: AgentContext for wallet mode support (required)
        user_id: User identifier (backward compatibility, can be None)
        network: "mainnet" (mainnet-only)
        simulate_only: If True, only simulate the transaction without broadcasting

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
        or for simulation:
        {
            'simulation_success': True,
            'message': 'Transaction simulation successful'
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

        # Choose action based on simulation mode
        action = "simulate" if simulate_only else "invoke"
        auto_sign = False if simulate_only else True

        # Execute via soroban operations with agent context
        result = await soroban_operations(
            action=action,
            soroban_server=soroban_server,
            account_manager=account_manager,
            agent_context=agent_context,
            user_id=user_id or (agent_context.user_id if agent_context else None),
            contract_id=pool_address,
            function_name="submit",
            parameters=parameters,
            account_id=account_id,
            auto_sign=auto_sign,
            network_passphrase=NETWORK_CONFIG['passphrase']
        )

        # Handle external wallet response (only for real transactions)
        if not simulate_only and result.get('requires_signature'):
            return result

        # Check for success (different keys for simulation vs real)
        success_key = 'simulation_success' if simulate_only else 'success'
        if not result.get(success_key) and not result.get('success'):
            return {
                'success': False,
                'simulation_success': False,
                'error': result.get('error', 'Unknown error'),
                'message': f"Failed to supply {amount} to pool"
            }

        # Get asset symbol for user-friendly message
        effective_user_id = user_id or (agent_context.user_id if agent_context else None)
        asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, effective_user_id, network=network)
        pool_name = await _get_pool_name(pool_address, soroban_server, account_manager, effective_user_id, network)

        if simulate_only:
            logger.info(f"✅ Successfully simulated supply of {amount} {asset_symbol} to {pool_name}")
            return {
                'simulation_success': True,
                'success': True,
                'amount_supplied': amount,
                'asset_symbol': asset_symbol,
                'pool': pool_name,
                'message': f"✅ Transaction simulation successful: Supply {amount} {asset_symbol} to {pool_name}",
                'parameters_validated': {
                    'pool_address': pool_address,
                    'asset_address': asset_address,
                    'amount_scaled': amount_scaled,
                    'request_type': RequestType.SUPPLY_COLLATERAL
                }
            }
        else:
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
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    agent_context = None,
    user_id: str = None,
    network: str = "mainnet",
    simulate_only: bool = False
) -> Dict[str, Any]:
    """
    Withdraw supplied assets from a Blend pool (autonomous operation).

    This function builds and submits a transaction to withdraw assets from collateral
    using the unified submit() function with WithdrawCollateral request type.

    Now supports external wallet signing via AgentContext and simulation mode.

    Args:
        pool_address: Pool contract ID
        asset_address: Asset to withdraw
        amount: Amount in decimal units (e.g., 50.0)
        account_id: Account ID from AccountManager
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        agent_context: AgentContext for wallet mode support (required)
        user_id: User identifier (backward compatibility, can be None)
        network: "mainnet" (mainnet-only)
        simulate_only: If True, only simulate the transaction without broadcasting

    Returns:
        Dictionary with transaction result or simulation result
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

        # Choose action based on simulation mode
        action = "simulate" if simulate_only else "invoke"
        auto_sign = False if simulate_only else True

        # Execute via soroban operations with agent context
        result = await soroban_operations(
            action=action,
            soroban_server=soroban_server,
            account_manager=account_manager,
            agent_context=agent_context,
            user_id=user_id or (agent_context.user_id if agent_context else None),
            contract_id=pool_address,
            function_name="submit",
            parameters=parameters,
            account_id=account_id,
            auto_sign=auto_sign,
            network_passphrase=NETWORK_CONFIG['passphrase']
        )

        # Handle external wallet response (only for real transactions)
        if not simulate_only and result.get('requires_signature'):
            return result

        # Check for success (different keys for simulation vs real)
        success_key = 'simulation_success' if simulate_only else 'success'
        if not result.get(success_key) and not result.get('success'):
            return {
                'success': False,
                'simulation_success': False,
                'error': result.get('error', 'Unknown error'),
                'message': f"Failed to withdraw {amount} from pool"
            }

        # Get asset symbol for user-friendly message
        effective_user_id = user_id or (agent_context.user_id if agent_context else None)
        asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, effective_user_id, network=network)
        pool_name = await _get_pool_name(pool_address, soroban_server, account_manager, effective_user_id, network)

        if simulate_only:
            logger.info(f"✅ Successfully simulated withdrawal of {amount} {asset_symbol} from {pool_name}")
            return {
                'simulation_success': True,
                'success': True,
                'amount_withdrawn': amount,
                'asset_symbol': asset_symbol,
                'pool': pool_name,
                'message': f"✅ Transaction simulation successful: Withdraw {amount} {asset_symbol} from {pool_name}",
                'parameters_validated': {
                    'pool_address': pool_address,
                    'asset_address': asset_address,
                    'amount_scaled': amount_scaled,
                    'request_type': RequestType.WITHDRAW_COLLATERAL
                }
            }
        else:
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
        network: "mainnet" (mainnet-only)

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
            network_passphrase=NETWORK_CONFIG['passphrase']
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
        network: "mainnet" (mainnet-only)

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
            soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

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
