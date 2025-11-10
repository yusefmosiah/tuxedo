#!/usr/bin/env python3
"""
Test working simulation approach with proper account creation.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import blend_get_reserve_apy, BLEND_MAINNET_CONTRACTS, NETWORK_CONFIG

async def test_working_simulation():
    """Test simulation approach with properly funded account."""
    print("=== Testing Working Simulation ===")

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        # Create a test account
        print("Creating test account...")
        user_id = "test_simulation_user"

        create_result = manager.generate_account(user_id, chain="stellar", name="test_account")
        if not create_result.get('success'):
            print(f"❌ Failed to create account: {create_result}")
            return

        account_id = create_result['account_id']
        public_key = create_result['address']
        print(f"✅ Created account: {public_key}")

        # Check if account has balance
        account_info = await server.load_account(public_key)
        if account_info:
            balance = account_info.balances[0].balance if account_info.balances else "0"
            print(f"Account balance: {balance} XLM")

            if float(balance) == 0:
                print("⚠️  Account has 0 XLM - this might cause simulation to fail")
                print("💡 In production, this account would need to be funded with at least 1.5 XLM")
        else:
            print("⚠️  Could not load account info")

        print("\nTesting USDC APY query with simulation fallback...")

        result = await blend_get_reserve_apy(
            pool_address=BLEND_MAINNET_CONTRACTS['comet'],
            asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
            user_id=user_id,
            soroban_server=server,
            account_manager=manager,
            network='mainnet'
        )

        print(f"\n🎯 Result:")
        print(f"   Asset: {result['asset_symbol']}")
        print(f"   Supply APY: {result['supply_apy']:.2f}%")
        print(f"   Borrow APY: {result['borrow_apy']:.2f}%")
        print(f"   Utilization: {result['utilization']:.1%}")
        print(f"   Total Supplied: {result['total_supplied']:,}")
        print(f"   Total Borrowed: {result['total_borrowed']:,}")
        print(f"   Data Source: {result['data_source']}")

        if result.get('latest_ledger'):
            print(f"   Latest Ledger: {result['latest_ledger']}")

        # Check if we got positive APY
        if result['supply_apy'] > 0:
            print("\n✅ SUCCESS: Got positive APY!")
        else:
            print(f"\n⚠️  APY is still 0% (supply_apy={result['supply_apy']})")

        if result['data_source'] == 'ledger_entries':
            print("✅ Used ledger queries (direct access)")
        elif result['data_source'] == 'simulation_fallback':
            print("✅ Used simulation fallback")
        else:
            print(f"❌ Unexpected data source: {result['data_source']}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await server.close()

async def test_direct_contract_call():
    """Test direct contract call simulation."""
    print("\n=== Testing Direct Contract Call ===")

    from stellar_soroban import soroban_operations
    import json

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        user_id = "test_direct_call"

        # Create account
        create_result = manager.generate_account(user_id, chain="stellar", name="direct_test")
        if not create_result.get('success'):
            print(f"❌ Failed to create account: {create_result}")
            return

        account_id = create_result['account_id']
        print(f"✅ Created account: {account_id}")

        # Build parameters for get_reserve
        parameters = json.dumps([
            {"type": "address", "value": BLEND_MAINNET_CONTRACTS['usdc']}
        ])

        print("Calling get_reserve(USDC) via simulation...")

        result = await soroban_operations(
            action="simulate",
            user_id=user_id,
            soroban_server=server,
            account_manager=manager,
            contract_id=BLEND_MAINNET_CONTRACTS['comet'],
            function_name="get_reserve",
            parameters=parameters,
            account_id=account_id,
            network_passphrase=NETWORK_CONFIG['passphrase']
        )

        if result.get('success'):
            reserve = result['result']
            print(f"✅ Simulation successful!")
            print(f"   Result type: {type(reserve)}")

            if isinstance(reserve, dict):
                print(f"   Reserve keys: {list(reserve.keys())}")

                if 'data' in reserve:
                    data = reserve['data']
                    print(f"   Data keys: {list(data.keys())}")
                    if 'b_rate' in data:
                        b_rate = data['b_rate']
                        supply_rate = b_rate / 1e7
                        supply_apy = ((1 + supply_rate / 365) ** 365 - 1) * 100
                        print(f"   🎯 b_rate: {b_rate} (Supply APY: {supply_apy:.2f}%)")
                    if 'd_rate' in data:
                        d_rate = data['d_rate']
                        borrow_rate = d_rate / 1e7
                        borrow_apy = ((1 + borrow_rate / 365) ** 365 - 1) * 100
                        print(f"   🎯 d_rate: {d_rate} (Borrow APY: {borrow_apy:.2f}%)")
            else:
                print(f"   Reserve value: {reserve}")
        else:
            print(f"❌ Simulation failed: {result.get('error')}")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await server.close()

async def main():
    """Run tests."""
    print("🚀 Testing Working Simulation Approach")
    print("=" * 50)

    # Test 1: Direct contract call
    await test_direct_contract_call()

    # Test 2: Full blend_get_reserve_apy function
    result = await test_working_simulation()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    if result and result['supply_apy'] > 0:
        print("✅ APY Query: Working with positive APY")
        print("✅ Implementation is functional!")
    else:
        print("❌ APY Query: Still returning 0% or failing")
        print("⚠️  May need funding or different approach")

if __name__ == '__main__':
    asyncio.run(main())