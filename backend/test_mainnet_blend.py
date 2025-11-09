#!/usr/bin/env python3
"""
Test Mainnet Blend Integration

This script tests the mainnet connectivity for Blend Capital pools.
It verifies:
1. Mainnet pool discovery
2. Real-time APY queries on mainnet
3. Best yield finder on mainnet

All tests are read-only and do not require any accounts or transactions.
"""

import asyncio
import logging
from blend_pool_tools import (
    blend_discover_pools,
    blend_find_best_yield,
    blend_get_reserve_apy,
    NETWORK_CONFIG,
    BLEND_MAINNET_CONTRACTS
)
from account_manager import AccountManager
from stellar_sdk.soroban_server_async import SorobanServerAsync

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mainnet_pool_discovery():
    """Test 1: Discover pools on mainnet"""
    print("\n" + "="*60)
    print("TEST 1: Mainnet Pool Discovery")
    print("="*60)

    try:
        # Create instances
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['mainnet']['rpc_url'])
        account_manager = AccountManager()

        print(f"🔴 Using mainnet RPC: {NETWORK_CONFIG['mainnet']['rpc_url'][:50]}...")
        print(f"🏦 Backstop contract: {NETWORK_CONFIG['mainnet']['backstop']}")

        # Discover pools
        pools = await blend_discover_pools(
            network='mainnet',
            soroban_server=soroban_server,
            account_manager=account_manager,
            user_id='test_mainnet'
        )

        print(f"\n✅ SUCCESS: Found {len(pools)} pools on mainnet")
        for i, pool in enumerate(pools, 1):
            print(f"   {i}. {pool['name']}")
            print(f"      Address: {pool['pool_address']}")
            print(f"      Status: {pool['status']}")

        await soroban_server.close()
        return True, pools

    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        return False, []


async def test_mainnet_apy_query():
    """Test 2: Query APY for USDC in Comet pool on mainnet"""
    print("\n" + "="*60)
    print("TEST 2: Mainnet APY Query (USDC in Comet Pool)")
    print("="*60)

    try:
        # Create instances
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['mainnet']['rpc_url'])
        account_manager = AccountManager()

        # Use known mainnet addresses
        comet_pool = BLEND_MAINNET_CONTRACTS['comet']
        usdc_token = BLEND_MAINNET_CONTRACTS['usdc']

        print(f"🔴 Pool: Comet ({comet_pool[:16]}...)")
        print(f"🪙 Asset: USDC ({usdc_token[:16]}...)")

        # Query APY
        apy_data = await blend_get_reserve_apy(
            pool_address=comet_pool,
            asset_address=usdc_token,
            user_id='test_mainnet',
            soroban_server=soroban_server,
            account_manager=account_manager,
            network='mainnet'
        )

        print(f"\n✅ SUCCESS: Retrieved mainnet APY data")
        print(f"   💰 Supply APY: {apy_data['supply_apy']:.2f}% (REAL YIELD!)")
        print(f"   💸 Borrow APY: {apy_data['borrow_apy']:.2f}%")
        print(f"   📊 Utilization: {apy_data['utilization']:.1%}")
        print(f"   💧 Available: {apy_data['available_liquidity'] / 1e7:,.2f} USDC")
        print(f"   📈 Total Supplied: {apy_data['total_supplied'] / 1e7:,.2f} USDC")

        await soroban_server.close()
        return True, apy_data

    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        return False, None


async def test_mainnet_best_yield():
    """Test 3: Find best yield for USDC on mainnet"""
    print("\n" + "="*60)
    print("TEST 3: Mainnet Best Yield Finder (USDC)")
    print("="*60)

    try:
        # Create instances
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['mainnet']['rpc_url'])
        account_manager = AccountManager()

        print(f"🔍 Searching for best USDC yield across all mainnet pools...")

        # Find best yield
        opportunities = await blend_find_best_yield(
            asset_symbol='USDC',
            min_apy=0.0,
            user_id='test_mainnet',
            soroban_server=soroban_server,
            account_manager=account_manager,
            network='mainnet'
        )

        print(f"\n✅ SUCCESS: Found {len(opportunities)} opportunities on mainnet")
        for i, opp in enumerate(opportunities, 1):
            print(f"\n   {i}. {opp['pool']}")
            print(f"      💰 APY: {opp['apy']:.2f}%")
            print(f"      💧 Liquidity: {opp['available_liquidity']:,.2f} USDC")
            print(f"      📊 Utilization: {opp['utilization']:.1%}")

        await soroban_server.close()
        return True, opportunities

    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        return False, []


async def run_all_tests():
    """Run all mainnet tests"""
    print("\n" + "="*60)
    print("🔴 MAINNET BLEND INTEGRATION TESTS")
    print("="*60)
    print("Testing read-only operations on Stellar mainnet")
    print("No accounts or transactions required\n")

    results = []

    # Test 1: Pool Discovery
    success1, pools = await test_mainnet_pool_discovery()
    results.append(("Pool Discovery", success1))

    # Test 2: APY Query
    success2, apy_data = await test_mainnet_apy_query()
    results.append(("APY Query", success2))

    # Test 3: Best Yield
    success3, opportunities = await test_mainnet_best_yield()
    results.append(("Best Yield Finder", success3))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Mainnet integration is working!")
        print("✅ You can now query real yields from Blend Capital mainnet pools")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

    return total_passed == total_tests


if __name__ == "__main__":
    print("Starting mainnet Blend integration tests...")
    asyncio.run(run_all_tests())
