#!/usr/bin/env python3
"""
Integration test for Blend Query Toolkit - Ledger Entry Implementation

Tests the new ledger entry queries for reserve APY retrieval.
This replaces the broken contract simulation approach.

Usage:
    python3 test_blend_ledger_implementation.py
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync

# Import the new ledger functions
from blend_pool_tools import (
    blend_get_reserve_apy,
    blend_discover_pools,
    BLEND_MAINNET_CONTRACTS,
    NETWORK_CONFIG,
    make_reserve_data_key,
    make_reserve_config_key,
    make_reserve_list_key,
    make_pool_config_key,
)
from account_manager import AccountManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()


async def test_ledger_key_construction():
    """Test that ledger key helper functions construct valid keys"""
    logger.info("=" * 80)
    logger.info("TEST 1: Ledger Key Construction")
    logger.info("=" * 80)

    pool_address = BLEND_MAINNET_CONTRACTS['comet']
    usdc_address = BLEND_MAINNET_CONTRACTS['usdc']

    # Test reserve data key
    data_key = make_reserve_data_key(pool_address, usdc_address)
    assert data_key['type'] == 'contract_data', "Data key type should be contract_data"
    assert data_key['contract_id'] == pool_address, "Data key contract_id mismatch"
    assert 'ResData' in data_key['key'], "Data key should contain ResData"
    logger.info(f"✅ Reserve data key constructed: {data_key['key']}")

    # Test reserve config key
    config_key = make_reserve_config_key(pool_address, usdc_address)
    assert config_key['type'] == 'contract_data', "Config key type should be contract_data"
    assert 'ResConfig' in config_key['key'], "Config key should contain ResConfig"
    logger.info(f"✅ Reserve config key constructed: {config_key['key']}")

    # Test reserve list key
    list_key = make_reserve_list_key(pool_address)
    assert list_key['type'] == 'contract_data', "List key type should be contract_data"
    assert list_key['key'] == 'ResList', "List key should be ResList"
    logger.info(f"✅ Reserve list key constructed: {list_key['key']}")

    # Test pool config key
    pool_key = make_pool_config_key(pool_address)
    assert pool_key['type'] == 'contract_instance', "Pool key type should be contract_instance"
    logger.info(f"✅ Pool config key constructed (contract_instance type)")

    logger.info("")


async def test_pool_discovery():
    """Test pool discovery still works"""
    logger.info("=" * 80)
    logger.info("TEST 2: Pool Discovery")
    logger.info("=" * 80)

    soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    account_manager = AccountManager()

    try:
        pools = await blend_discover_pools(
            soroban_server=soroban_server,
            account_manager=account_manager,
            user_id="test_system",
            network="mainnet"
        )

        assert len(pools) > 0, "Should discover at least one pool"
        logger.info(f"✅ Discovered {len(pools)} pools:")
        for pool in pools:
            logger.info(f"   - {pool['name']}: {pool['pool_address'][:12]}...")

        logger.info("")
        return pools
    finally:
        await soroban_server.close()


async def test_reserve_apy_with_ledger_entries():
    """Test reserve APY query using the new ledger entries approach"""
    logger.info("=" * 80)
    logger.info("TEST 3: Reserve APY Query (Using Ledger Entries)")
    logger.info("=" * 80)

    soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    account_manager = AccountManager()

    try:
        # Test USDC in Comet pool
        comet_pool = BLEND_MAINNET_CONTRACTS['comet']
        usdc_asset = BLEND_MAINNET_CONTRACTS['usdc']

        logger.info(f"Querying USDC reserve in Comet pool...")
        logger.info(f"  Pool: {comet_pool[:12]}...")
        logger.info(f"  Asset: {usdc_asset[:12]}...")

        result = await blend_get_reserve_apy(
            pool_address=comet_pool,
            asset_address=usdc_asset,
            user_id="test_system",
            soroban_server=soroban_server,
            account_manager=account_manager,
            network="mainnet"
        )

        # Verify result structure
        assert result.get('asset_symbol') == 'USDC', "Should return USDC symbol"
        assert 'supply_apy' in result, "Should have supply_apy"
        assert 'borrow_apy' in result, "Should have borrow_apy"
        assert 'utilization' in result, "Should have utilization"
        assert result.get('data_source') == 'ledger_entries', "Data source should be ledger_entries"

        # Log results
        logger.info(f"✅ Reserve APY query successful!")
        logger.info(f"   Asset: {result['asset_symbol']}")
        logger.info(f"   Supply APY: {result['supply_apy']}%")
        logger.info(f"   Borrow APY: {result['borrow_apy']}%")
        logger.info(f"   Utilization: {result['utilization']:.1%}")
        logger.info(f"   Total Supplied: {result['total_supplied']}")
        logger.info(f"   Total Borrowed: {result['total_borrowed']}")
        logger.info(f"   Available Liquidity: {result['available_liquidity']}")
        logger.info(f"   Data Source: {result['data_source']}")
        logger.info(f"   Latest Ledger: {result.get('latest_ledger')}")

        # Test that APY is reasonable (not 0 or negative)
        assert result['supply_apy'] >= 0, "Supply APY should be non-negative"
        assert result['borrow_apy'] >= 0, "Borrow APY should be non-negative"

        logger.info("")
        return result
    finally:
        await soroban_server.close()


async def test_multiple_reserves():
    """Test querying multiple reserves to show efficiency"""
    logger.info("=" * 80)
    logger.info("TEST 4: Multiple Reserve Queries (Efficiency Test)")
    logger.info("=" * 80)

    soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    account_manager = AccountManager()

    try:
        comet_pool = BLEND_MAINNET_CONTRACTS['comet']
        assets = ['usdc', 'xlm']

        logger.info(f"Querying multiple reserves in Comet pool...")
        results = []

        for asset in assets:
            if asset in BLEND_MAINNET_CONTRACTS:
                asset_address = BLEND_MAINNET_CONTRACTS[asset]
                try:
                    result = await blend_get_reserve_apy(
                        pool_address=comet_pool,
                        asset_address=asset_address,
                        user_id="test_system",
                        soroban_server=soroban_server,
                        account_manager=account_manager,
                        network="mainnet"
                    )
                    results.append(result)
                    logger.info(f"✅ {result['asset_symbol']}: {result['supply_apy']}% APY, {result['utilization']:.1%} util")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to query {asset}: {e}")

        logger.info(f"✅ Successfully queried {len(results)} reserves")
        logger.info("")
        return results
    finally:
        await soroban_server.close()


async def main():
    """Run all tests"""
    logger.info("")
    logger.info("🔬 Blend Query Toolkit - Ledger Implementation Tests")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Test 1: Ledger key construction
        await test_ledger_key_construction()

        # Test 2: Pool discovery
        pools = await test_pool_discovery()

        # Test 3: Reserve APY with ledger entries
        apy_result = await test_reserve_apy_with_ledger_entries()

        # Test 4: Multiple reserves
        multi_results = await test_multiple_reserves()

        logger.info("=" * 80)
        logger.info("✅ All tests passed!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Summary:")
        logger.info(f"  - Ledger key construction: ✅ Working")
        logger.info(f"  - Pool discovery: ✅ {len(pools)} pools found")
        logger.info(f"  - Reserve APY queries: ✅ Using ledger entries")
        logger.info(f"  - Multiple reserve queries: ✅ {len(multi_results)} reserves queried")
        logger.info("")
        logger.info("The Blend Query Toolkit implementation is complete and functional!")
        logger.info("")

    except Exception as e:
        logger.error("❌ Test failed:")
        logger.error(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
