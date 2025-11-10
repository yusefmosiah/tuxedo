#!/usr/bin/env python3
"""
Test script for the new Blend ledger query implementation.

This script tests the new get_ledger_entries action and updated
blend_get_reserve_apy function to verify they work correctly.

Expected: Real APY data should be returned (not 0%).
"""

import asyncio
import sys
import os
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import (
    blend_get_reserve_apy,
    blend_find_best_yield,
    BLEND_MAINNET_CONTRACTS,
    NETWORK_CONFIG
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ledger_key_helpers():
    """Test the ledger key construction helpers."""
    print("\n=== Testing Ledger Key Helpers ===")

    from blend_pool_tools import (
        make_reserve_data_key,
        make_reserve_config_key,
        make_reserve_list_key,
        make_pool_config_key
    )

    pool_address = BLEND_MAINNET_CONTRACTS['comet']
    asset_address = BLEND_MAINNET_CONTRACTS['usdc']

    # Test reserve data key
    key = make_reserve_data_key(pool_address, asset_address)
    print(f"✅ Reserve data key: {key['type']} - {key['key']}")

    # Test reserve config key
    key = make_reserve_config_key(pool_address, asset_address)
    print(f"✅ Reserve config key: {key['type']} - {key['key']}")

    # Test reserve list key
    key = make_reserve_list_key(pool_address)
    print(f"✅ Reserve list key: {key['type']} - {key['key']}")

    # Test pool config key
    key = make_pool_config_key(pool_address)
    print(f"✅ Pool config key: {key['type']}")

async def test_get_ledger_entries_action():
    """Test the new get_ledger_entries action in stellar_soroban.py."""
    print("\n=== Testing get_ledger_entries Action ===")

    from stellar_soroban import soroban_operations
    from blend_pool_tools import make_reserve_data_key

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        pool_address = BLEND_MAINNET_CONTRACTS['comet']

        # Try different key patterns
        test_patterns = [
            # Pattern 1: ResList key
            [{
                "type": "contract_data",
                "contract_id": pool_address,
                "key": "ResList",
                "durability": "PERSISTENT"
            }],

            # Pattern 2: Contract instance key
            [{
                "type": "contract_instance",
                "contract_id": pool_address
            }],

            # Pattern 3: ResData key
            [{
                "type": "contract_data",
                "contract_id": pool_address,
                "key": "ResData",
                "durability": "PERSISTENT"
            }],

            # Pattern 4: Try to get specific asset data (USDC)
            [{
                "type": "contract_data",
                "contract_id": pool_address,
                "key": {
                    "tuple": ["ResData", BLEND_MAINNET_CONTRACTS['usdc']]
                },
                "durability": "PERSISTENT"
            }],
        ]

        for i, ledger_keys in enumerate(test_patterns):
            key_display = ledger_keys[0].get('key', 'contract_instance')
            print(f"\nTesting pattern {i+1}: {key_display}")

            result = await soroban_operations(
                action="get_ledger_entries",
                user_id="test",
                soroban_server=server,
                account_manager=manager,
                ledger_keys=ledger_keys,
                network_passphrase=NETWORK_CONFIG['passphrase']
            )

            if result.get('success') and result.get('count', 0) > 0:
                print(f"✅ Found {result['count']} entries")
                for entry in result['entries']:
                    print(f"   Entry value type: {type(entry['value'])}")
                    if isinstance(entry['value'], dict):
                        print(f"   Keys: {list(entry['value'].keys())[:10]}")  # First 10 keys
                        if 'b_rate' in entry['value']:
                            print(f"   b_rate: {entry['value']['b_rate']}")
                        if 'd_rate' in entry['value']:
                            print(f"   d_rate: {entry['value']['d_rate']}")
                    else:
                        print(f"   Value: {str(entry['value'])[:100]}...")
            else:
                print(f"❌ No entries found: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await server.close()

async def test_reserve_apy_comet_usdc():
    """Test APY query for USDC in Comet pool."""
    print("\n=== Testing USDC APY in Comet Pool ===")

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        result = await blend_get_reserve_apy(
            pool_address=BLEND_MAINNET_CONTRACTS['comet'],
            asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
            user_id='test_user',
            soroban_server=server,
            account_manager=manager,
            network='mainnet'
        )

        print(f"Asset: {result['asset_symbol']}")
        print(f"Supply APY: {result['supply_apy']:.2f}%")
        print(f"Borrow APY: {result['borrow_apy']:.2f}%")
        print(f"Utilization: {result['utilization']:.1%}")
        print(f"Total Supplied: {result['total_supplied']:,}")
        print(f"Total Borrowed: {result['total_borrowed']:,}")
        print(f"Data Source: {result['data_source']}")

        if result.get('latest_ledger'):
            print(f"Latest Ledger: {result['latest_ledger']}")

        # Validate results
        if result['supply_apy'] > 0:
            print("✅ SUCCESS: Supply APY is positive!")
        else:
            print("❌ FAILURE: Supply APY is still 0")

        if result['data_source'] == 'ledger_entries':
            print("✅ SUCCESS: Used ledger entries (not simulation)!")
        elif result['data_source'] == 'simulation_fallback':
            print("⚠️  Fallback: Used simulation (ledger queries failed)")
        else:
            print(f"❌ FAILURE: Unexpected data source: {result['data_source']}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        await server.close()

async def test_best_yield_finder():
    """Test the best yield finder with the new APY implementation."""
    print("\n=== Testing Best Yield Finder ===")

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        result = await blend_find_best_yield(
            asset_symbol="USDC",
            min_apy=0.1,
            user_id='test_user',
            soroban_server=server,
            account_manager=manager,
            network='mainnet'
        )

        print(f"Found {len(result['opportunities'])} yield opportunities")

        for opp in result['opportunities']:
            print(f"\n🌟 {opp['pool_name']} Pool")
            print(f"   APY: {opp['supply_apy']:.2f}%")
            print(f"   Utilization: {opp['utilization']:.1%}")
            print(f"   Available: {opp['available_liquidity']:,.2f} {opp['asset_symbol']}")
            print(f"   Data Source: {opp['data_source']}")

        if result['opportunities'] and any(opp['supply_apy'] > 0 for opp in result['opportunities']):
            print("✅ SUCCESS: Found positive APY opportunities!")
        else:
            print("❌ FAILURE: No positive APY opportunities found")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        await server.close()

async def main():
    """Run all tests."""
    print("🚀 Testing Blend Ledger Query Implementation")
    print("=" * 50)

    try:
        # Test 1: Ledger key helpers
        await test_ledger_key_helpers()

        # Test 2: get_ledger_entries action
        await test_get_ledger_entries_action()

        # Test 3: Reserve APY query
        apy_result = await test_reserve_apy_comet_usdc()

        # Test 4: Best yield finder
        yield_result = await test_best_yield_finder()

        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)

        if apy_result and apy_result['supply_apy'] > 0:
            print("✅ APY Query: Working (positive APY returned)")
        else:
            print("❌ APY Query: Failed (0% APY)")

        if yield_result and yield_result['opportunities']:
            print("✅ Yield Finder: Working (opportunities found)")
        else:
            print("❌ Yield Finder: Failed (no opportunities)")

        if apy_result and apy_result['data_source'] == 'ledger_entries':
            print("✅ Ledger Queries: Working (direct access)")
        else:
            print("⚠️  Ledger Queries: Using fallback")

        print("\n🎉 Implementation is working!" if (apy_result and apy_result['supply_apy'] > 0) else "\n❌ Implementation needs more work")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())