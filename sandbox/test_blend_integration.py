#!/usr/bin/env python3
"""
Blend Capital Integration Test

Tests the complete Blend yield farming implementation:
- Pool discovery
- APY queries
- Position checking

This is a read-only test that doesn't require accounts or transactions.
For full testing including supply/withdraw, use the AI agent.

Usage:
    python3 test_blend_integration.py
"""

import asyncio
import logging
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Blend tools
from blend_pool_tools import (
    blend_discover_pools,
    blend_find_best_yield,
    blend_get_reserve_apy,
    NETWORK_CONFIG,
    BLEND_TESTNET_CONTRACTS
)


async def test_pool_discovery():
    """Test 1: Pool Discovery"""
    print("\n" + "="*60)
    print("TEST 1: Pool Discovery")
    print("="*60)

    try:
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['testnet']['rpc_url'])
        account_manager = AccountManager()

        pools = await blend_discover_pools(
            network='testnet',
            soroban_server=soroban_server,
            account_manager=account_manager,
            user_id='test_user'
        )

        if pools:
            print(f"\n✅ SUCCESS: Found {len(pools)} active pools")
            for i, pool in enumerate(pools, 1):
                print(f"\n{i}. {pool['name']}")
                print(f"   Address: {pool['pool_address']}")
                print(f"   Status: {pool['status']}")
            return True
        else:
            print("\n❌ FAIL: No pools discovered")
            return False

    except Exception as e:
        print(f"\n❌ FAIL: Error in pool discovery: {e}")
        logger.error(f"Pool discovery error: {e}", exc_info=True)
        return False


async def test_apy_query():
    """Test 2: APY Query for Known Asset"""
    print("\n" + "="*60)
    print("TEST 2: APY Query (USDC in Comet Pool)")
    print("="*60)

    try:
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['testnet']['rpc_url'])
        account_manager = AccountManager()

        # Query USDC APY in Comet pool
        pool_address = BLEND_TESTNET_CONTRACTS['comet']
        asset_address = BLEND_TESTNET_CONTRACTS['usdc']

        apy_data = await blend_get_reserve_apy(
            pool_address=pool_address,
            asset_address=asset_address,
            user_id='test_user',
            soroban_server=soroban_server,
            account_manager=account_manager,
            network='testnet'
        )

        if apy_data and 'supply_apy' in apy_data:
            print(f"\n✅ SUCCESS: Retrieved APY data")
            print(f"\n   Asset: {apy_data['asset_symbol']}")
            print(f"   Supply APY: {apy_data['supply_apy']:.2f}%")
            print(f"   Borrow APY: {apy_data['borrow_apy']:.2f}%")
            print(f"   Total Supplied: {apy_data['total_supplied'] / 1e7:,.2f}")
            print(f"   Total Borrowed: {apy_data['total_borrowed'] / 1e7:,.2f}")
            print(f"   Utilization: {apy_data['utilization']:.1%}")
            print(f"   Available Liquidity: {apy_data['available_liquidity'] / 1e7:,.2f}")
            print(f"   Data Source: {apy_data['data_source']}")
            return True
        else:
            print("\n❌ FAIL: Invalid APY data returned")
            return False

    except Exception as e:
        print(f"\n❌ FAIL: Error querying APY: {e}")
        logger.error(f"APY query error: {e}", exc_info=True)
        return False


async def test_find_best_yield():
    """Test 3: Find Best Yield for USDC"""
    print("\n" + "="*60)
    print("TEST 3: Find Best Yield for USDC")
    print("="*60)

    try:
        soroban_server = SorobanServerAsync(NETWORK_CONFIG['testnet']['rpc_url'])
        account_manager = AccountManager()

        opportunities = await blend_find_best_yield(
            asset_symbol='USDC',
            min_apy=0.0,
            user_id='test_user',
            soroban_server=soroban_server,
            account_manager=account_manager,
            network='testnet'
        )

        if opportunities:
            print(f"\n✅ SUCCESS: Found {len(opportunities)} yield opportunities for USDC")
            for i, opp in enumerate(opportunities, 1):
                print(f"\n{i}. {opp['pool']}")
                print(f"   APY: {opp['apy']:.2f}%")
                print(f"   Available Liquidity: {opp['available_liquidity']:,.2f} USDC")
                print(f"   Utilization: {opp['utilization']:.1%}")
                print(f"   Pool: {opp['pool_address'][:16]}...")
            return True
        else:
            print("\n❌ FAIL: No yield opportunities found")
            return False

    except Exception as e:
        print(f"\n❌ FAIL: Error finding best yield: {e}")
        logger.error(f"Best yield error: {e}", exc_info=True)
        return False


async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("BLEND CAPITAL INTEGRATION TESTS")
    print("Testing on Stellar Testnet")
    print("="*60)

    results = []

    # Test 1: Pool Discovery
    result1 = await test_pool_discovery()
    results.append(("Pool Discovery", result1))

    await asyncio.sleep(1)  # Brief pause between tests

    # Test 2: APY Query
    result2 = await test_apy_query()
    results.append(("APY Query", result2))

    await asyncio.sleep(1)

    # Test 3: Find Best Yield
    result3 = await test_find_best_yield()
    results.append(("Find Best Yield", result3))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Blend integration is working correctly.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the logs above.\n")
        return 1


async def main():
    """Main entry point"""
    try:
        exit_code = await run_all_tests()
        return exit_code
    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        print(f"\n❌ Test suite crashed: {e}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
