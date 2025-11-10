#!/usr/bin/env python3
"""
Simple test approach to understand what's failing.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from stellar_soroban import soroban_operations
from blend_pool_tools import blend_get_reserve_apy, BLEND_MAINNET_CONTRACTS, NETWORK_CONFIG
import json

async def test_system_user():
    """Test with system user that might already exist."""
    print("=== Testing System User ===")

    manager = AccountManager()

    # Check if system user has any accounts
    system_accounts = manager.get_user_accounts("system")
    print(f"System user has {len(system_accounts)} accounts")

    for account in system_accounts:
        print(f"   Account: {account['id']} - {account.get('public_key', 'N/A')}")

    # Check for test user
    test_accounts = manager.get_user_accounts("test_user")
    print(f"Test user has {len(test_accounts)} accounts")

    return system_accounts or test_accounts

async def test_no_account_simulation():
    """Test simulation without account_id requirement."""
    print("\n=== Testing Simulation Without Account ===")

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        # Try to modify soroban_operations to work without account for simulation
        # This is a test to see if the account requirement is the issue

        from stellar_sdk import TransactionBuilder, scval
        from stellar_sdk.keypair import Keypair

        # Create a temporary keypair for simulation (doesn't need to be funded)
        temp_keypair = Keypair.random()
        print(f"Created temp keypair: {temp_keypair.public_key}")

        # Try to build transaction manually
        try:
            # Create a dummy account sequence (this might work for simulation)
            from stellar_sdk.account import Account
            dummy_account = Account(temp_keypair.public_key, 1)  # Sequence 1

            # Build transaction
            parameters = json.dumps([
                {"type": "address", "value": BLEND_MAINNET_CONTRACTS['usdc']}
            ])

            scval_params = [
                scval.to_address(BLEND_MAINNET_CONTRACTS['usdc'])
            ]

            tx = (
                TransactionBuilder(dummy_account, NETWORK_CONFIG['passphrase'], base_fee=100)
                .set_timeout(30)
                .append_invoke_contract_function_op(
                    contract_id=BLEND_MAINNET_CONTRACTS['comet'],
                    function_name="get_reserve",
                    parameters=scval_params
                )
                .build()
            )

            print("Built transaction successfully")

            # Try simulation
            sim_result = await server.simulate_transaction(tx)

            if sim_result.error:
                print(f"❌ Simulation error: {sim_result.error}")
            else:
                print("✅ Simulation successful!")
                if sim_result.results:
                    result_scval = sim_result.results[0].return_value
                    result = scval.to_native(result_scval) if result_scval else None
                    print(f"   Result: {result}")

                    if isinstance(result, dict) and 'data' in result:
                        data = result['data']
                        if 'b_rate' in data:
                            b_rate = data['b_rate']
                            supply_rate = b_rate / 1e7
                            supply_apy = ((1 + supply_rate / 365) ** 365 - 1) * 100
                            print(f"   🎯 Supply APY: {supply_apy:.2f}%")
                            return True

        except Exception as e:
            print(f"❌ Manual simulation failed: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    await server.close()
    return False

async def test_direct_blend_function():
    """Test calling blend_get_reserve_apy directly with minimal setup."""
    print("\n=== Testing Direct Blend Function ===")

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        # Try with system user first
        result = await blend_get_reserve_apy(
            pool_address=BLEND_MAINNET_CONTRACTS['comet'],
            asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
            user_id="system",
            soroban_server=server,
            account_manager=manager,
            network='mainnet'
        )

        print(f"✅ Direct function call successful!")
        print(f"   Asset: {result['asset_symbol']}")
        print(f"   Supply APY: {result['supply_apy']:.2f}%")
        print(f"   Data Source: {result['data_source']}")

        if result['supply_apy'] > 0:
            print("🎉 SUCCESS: Got positive APY!")
            return True
        else:
            print("⚠️  APY is 0%")

    except Exception as e:
        print(f"❌ Direct function call failed: {e}")

    await server.close()
    return False

async def main():
    """Run all tests."""
    print("🚀 Simple Diagnostic Tests")
    print("=" * 50)

    # Test 1: Check existing accounts
    existing_accounts = await test_system_user()

    # Test 2: Try simulation without account
    no_account_success = await test_no_account_simulation()

    # Test 3: Try direct function call
    direct_success = await test_direct_blend_function()

    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)

    if existing_accounts:
        print("✅ Found existing accounts in system")
    else:
        print("❌ No existing accounts found")

    if no_account_success:
        print("✅ Manual simulation works")
    else:
        print("❌ Manual simulation failed")

    if direct_success:
        print("✅ Direct blend function works")
    else:
        print("❌ Direct blend function failed")

    if direct_success:
        print("\n🎉 The implementation works! Positive APY detected!")
    else:
        print("\n⚠️  Need to debug account/simulation issues")

if __name__ == '__main__':
    asyncio.run(main())