#!/usr/bin/env python3
"""
Test Blend functionality directly using the secret key without AccountManager import.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk import TransactionBuilder, scval, Keypair
from stellar_sdk.account import Account
from blend_pool_tools import BLEND_MAINNET_CONTRACTS, NETWORK_CONFIG
import json

# Get the secret from environment
AGENT_STELLAR_SECRET = os.getenv('AGENT_STELLAR_SECRET', 'SAJC4CACOKBM2TNA2QK4ODEOVAAEVMF34OAZUNUNFNBNOLTOMLK3RHAU')

async def test_direct_contract_calls():
    """Test contract calls directly using the secret key."""
    print("=== Testing Direct Contract Calls ===")

    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])

    try:
        # Create keypair from secret
        agent_keypair = Keypair.from_secret(AGENT_STELLAR_SECRET)
        public_key = agent_keypair.public_key
        print(f"✅ Using account: {public_key}")

        # Try to get account info, assume it exists since we have the secret
        try:
            # Just use a dummy sequence number for testing
            account = Account(public_key, 1)
            print(f"✅ Using account for testing (sequence: {account.sequence})")
        except Exception as e:
            print(f"❌ Account setup error: {e}")
            return False

        # Test different function names to find the correct one
        pool_address = BLEND_MAINNET_CONTRACTS['comet']
        usdc_address = BLEND_MAINNET_CONTRACTS['usdc']

        possible_functions = [
            ("get_reserve", [scval.to_address(usdc_address)]),
            ("reserve", [scval.to_address(usdc_address)]),
            ("getReserve", [scval.to_address(usdc_address)]),
            ("query_reserve", [scval.to_address(usdc_address)]),
            ("get_reserves", []),
            ("reserves", []),
            ("getReserves", []),
            ("get_user_position", [scval.to_address(public_key)]),
            ("get_positions", [scval.to_address(public_key)]),
            ("positions", [scval.to_address(public_key)]),
        ]

        for function_name, parameters in possible_functions:
            try:
                print(f"\n🔍 Testing function: {function_name} with {len(parameters)} parameters")

                # Create account for transaction
                # Use the account we already set up

                # Build transaction
                tx = (
                    TransactionBuilder(account, NETWORK_CONFIG['passphrase'], base_fee=100)
                    .set_timeout(30)
                    .append_invoke_contract_function_op(
                        contract_id=pool_address,
                        function_name=function_name,
                        parameters=parameters
                    )
                    .build()
                )

                # Simulate transaction
                sim_result = await server.simulate_transaction(tx)

                if sim_result.error:
                    print(f"   ❌ Error: {sim_result.error}")
                else:
                    print(f"   ✅ Success!")
                    if sim_result.results:
                        result_scval = sim_result.results[0].return_value
                        result = scval.to_native(result_scval) if result_scval else None
                        print(f"   📊 Result type: {type(result)}")

                        if result:
                            if isinstance(result, dict):
                                print(f"   📋 Dict keys: {list(result.keys())}")

                                # Check for APY-related data
                                if 'b_rate' in result or 'd_rate' in result:
                                    b_rate = result.get('b_rate', 0)
                                    d_rate = result.get('d_rate', 0)

                                    supply_rate = b_rate / 1e7
                                    supply_apy = ((1 + supply_rate / 365) ** 365 - 1) * 100

                                    borrow_rate = d_rate / 1e7
                                    borrow_apy = ((1 + borrow_rate / 365) ** 365 - 1) * 100

                                    print(f"   🎯 b_rate: {b_rate} → Supply APY: {supply_apy:.2f}%")
                                    print(f"   🎯 d_rate: {d_rate} → Borrow APY: {borrow_apy:.2f}%")

                                    if supply_apy > 0:
                                        print(f"   🎉 FOUND POSITIVE APY with {function_name}!")
                                        return True

                                # Check for nested data structure
                                elif 'data' in result:
                                    data = result['data']
                                    if isinstance(data, dict) and ('b_rate' in data or 'd_rate' in data):
                                        b_rate = data.get('b_rate', 0)
                                        d_rate = data.get('d_rate', 0)

                                        supply_rate = b_rate / 1e7
                                        supply_apy = ((1 + supply_rate / 365) ** 365 - 1) * 100

                                        borrow_rate = d_rate / 1e7
                                        borrow_apy = ((1 + borrow_rate / 365) ** 365 - 1) * 100

                                        print(f"   🎯 Found in data: b_rate={b_rate}, d_rate={d_rate}")
                                        print(f"   🎯 Supply APY: {supply_apy:.2f}%, Borrow APY: {borrow_apy:.2f}%")

                                        if supply_apy > 0:
                                            print(f"   🎉 FOUND POSITIVE APY with {function_name} (in data)!")
                                            return True

                                # Check for array/list results
                                elif isinstance(result, list) and len(result) > 0:
                                    print(f"   📋 List with {len(result)} items")
                                    if isinstance(result[0], dict):
                                        print(f"   📋 First item keys: {list(result[0].keys())}")

                                    # Look for APY data in list items
                                    for i, item in enumerate(result):
                                        if isinstance(item, dict) and ('b_rate' in item or 'd_rate' in item):
                                            print(f"   🎯 Found APY data in list item {i}")
                                            return True
                            else:
                                print(f"   📊 Value: {str(result)[:200]}...")

            except Exception as e:
                print(f"   ❌ Exception: {e}")
                continue

        print(f"\n❌ No function returned positive APY data")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await server.close()

async def main():
    """Run the direct contract test."""
    print("🚀 Testing Blend Contracts Directly with Secret Key")
    print("=" * 60)

    success = await test_direct_contract_calls()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)

    if success:
        print("✅ SUCCESS: Found working Blend function with positive APY!")
        print("🎉 The implementation can be updated with the correct function name!")
    else:
        print("❌ FAILURE: Could not find working function with positive APY")
        print("⚠️  May need to research Blend contract ABI or different approach")

if __name__ == '__main__':
    asyncio.run(main())