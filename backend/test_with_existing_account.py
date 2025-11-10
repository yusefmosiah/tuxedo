#!/usr/bin/env python3
"""
Test using an existing funded Stellar account.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from stellar_soroban import soroban_operations
import json

# Known funded accounts for testing (these are public accounts from Stellar explorer)
# Note: These are NOT private keys - just public addresses that exist on the network
TEST_ACCOUNTS = [
    "GDVDKQFPK3SGJQ7BOBEGOABKQHEGMBWHIVQIYDJFBRFEWMDREOSJ7EHR",  # Random active account
    "GBBHQMJITBEOQ2KXK6TJEQLNFJKZNLCWHAM6F7BIVZL5ENM5FSVQOWTQ",  # Another active account
    "GDTNVAZJW3Q4EB4A5C6NHQKB4VH5AIDUQFRVFV25QE3EFA5B3HBBE4XA",  # Stellar Development Foundation
]

async def test_with_existing_account():
    """Test with an existing funded account."""
    print("=== Testing with Existing Account ===")

    server = SorobanServerAsync("https://rpc.ankr.com/stellar_soroban")
    manager = AccountManager()

    for public_key in TEST_ACCOUNTS:
        try:
            print(f"\nTrying account: {public_key}")

            # Check if account exists and has balance
            account_info = await server.load_account(public_key)
            if account_info:
                balance = account_info.balances[0].balance if account_info.balances else "0"
                print(f"✅ Account exists with balance: {balance} XLM")

                # Create an AccountManager record for this account
                user_id = "test_existing_account"
                import_result = manager.import_account(
                    user_id=user_id,
                    chain="stellar",
                    private_key="dummy",  # We won't actually sign, just need the record
                    name="test_existing",
                    network="mainnet"
                )

                if import_result.get('success'):
                    account_id = import_result['account_id']
                    print(f"✅ Imported account as: {account_id}")

                    # Test contract simulation
                    parameters = json.dumps([
                        {"type": "address", "value": "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75"}  # USDC
                    ])

                    print("Testing get_reserve(USDC) simulation...")

                    result = await soroban_operations(
                        action="simulate",
                        user_id=user_id,
                        soroban_server=server,
                        account_manager=manager,
                        contract_id="CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM",  # Comet pool
                        function_name="get_reserve",
                        parameters=parameters,
                        account_id=account_id,
                        network_passphrase="Public Global Stellar Network ; September 2015"
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

                                # Calculate total metrics
                                total_supplied = data.get('b_supply', 0)
                                total_borrowed = data.get('d_supply', 0)
                                utilization = total_borrowed / total_supplied if total_supplied > 0 else 0

                                print(f"   Total Supplied: {total_supplied:,}")
                                print(f"   Total Borrowed: {total_borrowed:,}")
                                print(f"   Utilization: {utilization:.1%}")

                                # Success!
                                print(f"\n🎉 SUCCESS: Found real APY data!")
                                print(f"   Supply APY: {supply_apy:.2f}%")
                                print(f"   Borrow APY: {borrow_apy:.2f}%")
                                print(f"   Utilization: {utilization:.1%}")

                                return True

                            else:
                                print(f"   No 'data' key in reserve result")
                        else:
                            print(f"   Reserve result: {reserve}")
                    else:
                        print(f"❌ Simulation failed: {result.get('error')}")
                else:
                    print(f"❌ Failed to import account: {import_result}")
            else:
                print(f"❌ Account not found on network")

        except Exception as e:
            print(f"❌ Error with account {public_key}: {e}")
            continue

    await server.close()
    return False

async def main():
    """Run test."""
    print("🚀 Testing with Existing Funded Account")
    print("=" * 50)

    success = await test_with_existing_account()

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    if success:
        print("✅ Simulation working with real account!")
        print("✅ Blend query implementation is functional!")
    else:
        print("❌ All existing accounts failed")
        print("⚠️  May need different approach or account funding")

if __name__ == '__main__':
    asyncio.run(main())