#!/usr/bin/env python3
"""
Test using the real funded account from .env file.
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

# Get the secret from environment
AGENT_STELLAR_SECRET = os.getenv('AGENT_STELLAR_SECRET', 'SAJC4CACOKBM2TNA2QK4ODEOVAAEVMF34OAZUNUNFNBNOLTOMLK3RHAU')

async def test_with_funded_account():
    """Test with the real funded account."""
    print("=== Testing with Funded Account ===")

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    try:
        # Try to find the agent account by checking common user IDs
        print("Checking existing accounts...")

        # Get the public key from the secret
        from stellar_sdk.keypair import Keypair
        agent_keypair = Keypair.from_secret(AGENT_STELLAR_SECRET)
        agent_public_key = agent_keypair.public_key
        print(f"Looking for account with public key: {agent_public_key}")

        # Try different user IDs that might have the agent account
        possible_user_ids = ["agent_user", "agent", "system", "default", "admin"]

        agent_account = None

        for user_id in possible_user_ids:
            try:
                existing_accounts = manager.get_user_accounts(user_id)
                print(f"Checking user '{user_id}': {len(existing_accounts)} accounts")

                for account in existing_accounts:
                    print(f"   Account: {account}")
                    if account.get('public_key') == agent_public_key:
                        agent_account = account
                        account_id = account['id']
                        public_key = account['public_key']
                        print(f"✅ Found agent account for user '{user_id}': {public_key}")
                        break

                if agent_account:
                    break
            except Exception as e:
                print(f"Error checking user '{user_id}': {e}")
                continue

        if not agent_account:
            print("❌ Agent account not found in any user")
            print("Let's try importing it as a new account...")

            # Create a unique user ID
            import time
            unique_user_id = f"agent_{int(time.time())}"

            import_result = manager.import_account(
                user_id=unique_user_id,
                chain="stellar",
                private_key=AGENT_STELLAR_SECRET,
                name="Agent Account",
                network="mainnet"
            )

            if import_result.get('success'):
                account_id = import_result['account_id']
                public_key = import_result['address']
                user_id = unique_user_id
                print(f"✅ Imported new agent account: {public_key}")
            else:
                print(f"❌ Failed to import agent account: {import_result}")
                return False

        # Check account balance
        try:
            account_info = await server.load_account(public_key)
            if account_info:
                for balance in account_info.balances:
                    if balance.asset_code == 'XLM' or (hasattr(balance, 'asset_type') and balance.asset_type == 'native'):
                        print(f"✅ XLM Balance: {balance.balance}")
                        break
        except Exception as e:
            print(f"⚠️  Could not fetch balance: {e}")

          # Ensure user_id is defined
        if 'user_id' not in locals():
            user_id = "agent_user"
        return account_id, user_id, server, manager

    except Exception as e:
        print(f"❌ Error setting up funded account: {e}")
        await server.close()
        return None

async def discover_blend_functions(account_id, user_id, server, manager):
    """Try to discover what functions are available on Blend contracts."""
    print("\n=== Discovering Blend Contract Functions ===")

    # Try different function names that might exist
    possible_functions = [
        "get_reserve",
        "reserve",
        "getReserve",
        "query_reserve",
        "get_reserves",
        "reserves",
        "getReserves",
        "get_user_position",
        "get_positions",
        "positions"
    ]

    usdc_address = BLEND_MAINNET_CONTRACTS['usdc']
    pool_address = BLEND_MAINNET_CONTRACTS['comet']

    for function_name in possible_functions:
        try:
            print(f"\nTrying function: {function_name}")

            # Try with USDC address parameter
            parameters = json.dumps([
                {"type": "address", "value": usdc_address}
            ])

            result = await soroban_operations(
                action="simulate",
                user_id=user_id,
                soroban_server=server,
                account_manager=manager,
                contract_id=pool_address,
                function_name=function_name,
                parameters=parameters,
                account_id=account_id,
                network_passphrase=NETWORK_CONFIG['passphrase']
            )

            if result.get('success'):
                print(f"✅ Function {function_name} works!")
                print(f"   Result: {result['result']}")

                # If it returns something useful, this might be our function
                if result['result'] and isinstance(result['result'], dict):
                    if 'data' in result['result'] or 'b_rate' in result['result'] or 'd_rate' in result['result']:
                        print(f"   🎯 Found reserve data with {function_name}!")
                        return function_name, result['result']
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    # Try without parameters
    print(f"\nTrying functions without parameters...")
    for function_name in possible_functions:
        try:
            print(f"Trying {function_name} (no params)")

            result = await soroban_operations(
                action="simulate",
                user_id=user_id,
                soroban_server=server,
                account_manager=manager,
                contract_id=pool_address,
                function_name=function_name,
                parameters=None,
                account_id=account_id,
                network_passphrase=NETWORK_CONFIG['passphrase']
            )

            if result.get('success'):
                print(f"✅ Function {function_name} (no params) works!")
                print(f"   Result: {result['result']}")

                if result['result'] and isinstance(result['result'], (dict, list)):
                    print(f"   🎯 Found useful data with {function_name}!")
                    return function_name, result['result']
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    return None, None

async def test_blend_with_correct_function(account_id, user_id, server, manager):
    """Test Blend queries with the correct function name."""
    print("\n=== Testing with Correct Function ===")

    # First, let's try to discover the correct function
    function_name, sample_result = await discover_blend_functions(account_id, user_id, server, manager)

    if not function_name:
        print("❌ Could not find any working Blend functions")
        return False

    print(f"\n🎯 Found working function: {function_name}")

    # If we found a function that returns reserve data, let's use it
    if sample_result and isinstance(sample_result, dict):
        # Check if we can extract APY data
        data = sample_result.get('data', sample_result)

        if isinstance(data, dict) and ('b_rate' in data or 'd_rate' in data):
            b_rate = data.get('b_rate', 0)
            d_rate = data.get('d_rate', 0)

            supply_rate = b_rate / 1e7
            supply_apy = ((1 + supply_rate / 365) ** 365 - 1) * 100

            borrow_rate = d_rate / 1e7
            borrow_apy = ((1 + borrow_rate / 365) ** 365 - 1) * 100

            print(f"✅ Calculated APY from {function_name}:")
            print(f"   Supply APY: {supply_apy:.2f}%")
            print(f"   Borrow APY: {borrow_apy:.2f}%")

            if supply_apy > 0:
                print("🎉 SUCCESS: Positive APY found!")
                return True

    return False

async def test_updated_blend_function(account_id, user_id, server, manager):
    """Test our updated blend_get_reserve_apy function with funded account."""
    print("\n=== Testing Updated blend_get_reserve_apy ===")

    try:
        result = await blend_get_reserve_apy(
            pool_address=BLEND_MAINNET_CONTRACTS['comet'],
            asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
            user_id=user_id,
            soroban_server=server,
            account_manager=manager,
            network='mainnet'
        )

        print(f"✅ blend_get_reserve_apy successful!")
        print(f"   Asset: {result['asset_symbol']}")
        print(f"   Supply APY: {result['supply_apy']:.2f}%")
        print(f"   Borrow APY: {result['borrow_apy']:.2f}%")
        print(f"   Utilization: {result['utilization']:.1%}")
        print(f"   Data Source: {result['data_source']}")

        if result['supply_apy'] > 0:
            print("🎉 SUCCESS: Got positive APY from updated function!")
            return True
        else:
            print("⚠️  APY is still 0% - may need function name fix")

    except Exception as e:
        print(f"❌ Updated blend_get_reserve_apy failed: {e}")

    return False

async def main():
    """Run all tests with funded account."""
    print("🚀 Testing with Real Funded Account")
    print("=" * 50)

    # Setup funded account
    account_setup = await test_with_funded_account()
    if not account_setup:
        print("❌ Could not setup funded account")
        return

    account_id, user_id, server, manager = account_setup

    # Test 1: Discover correct function names
    function_found = await test_blend_with_correct_function(account_id, user_id, server, manager)

    # Test 2: Test our updated function
    updated_function_works = await test_updated_blend_function(account_id, user_id, server, manager)

    await server.close()

    print("\n" + "=" * 50)
    print("📊 FINAL SUMMARY")
    print("=" * 50)

    if function_found:
        print("✅ Found working Blend contract functions")
    else:
        print("❌ No working functions found")

    if updated_function_works:
        print("✅ Updated blend_get_reserve_apy works with positive APY")
        print("🎉 IMPLEMENTATION SUCCESSFUL!")
    else:
        print("❌ Updated function still needs work")

    print(f"\nNext steps:")
    if not function_found:
        print("1. Research correct Blend contract function names")
        print("2. Update blend_get_reserve_apy with correct function")
    if function_found and not updated_function_works:
        print("1. Update blend_get_reserve_apy to use discovered function")
        print("2. Test again with funded account")

if __name__ == '__main__':
    asyncio.run(main())