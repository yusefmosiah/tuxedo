#!/usr/bin/env python3
"""
Test what methods are available on the Blend pool contract
"""

import asyncio
import os
import json
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from stellar_soroban import soroban_operations

# Load environment variables
load_dotenv()

async def test_contract_methods():
    """Test what methods are available on the contract"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)
    account_manager = AccountManager()

    # Use the system_agent account
    user_id = "system_agent"

    # Get the system_agent account
    accounts = account_manager.get_user_accounts(user_id)
    if not accounts:
        print("❌ No system_agent account found")
        return False

    account_id = accounts[0]['id']

    pool_address = 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM'
    usdc_address = 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'

    try:
        print("Testing available methods on Blend pool contract...")
        print(f"Pool: {pool_address}")
        print(f"Asset: {usdc_address}")
        print("")

        # Test methods that might exist
        methods_to_test = [
            "get_reserve",
            "getReserve",
            "get_reserve_list",
            "getReserveList",
            "get_config",
            "getConfig"
        ]

        for method in methods_to_test:
            print(f"Testing method: {method}")
            result = await soroban_operations(
                action="simulate",
                user_id=user_id,
                soroban_server=soroban_server,
                account_manager=account_manager,
                account_id=account_id,
                contract_id=pool_address,
                function_name=method,
                parameters=json.dumps([{"type": "address", "value": usdc_address}]) if 'reserve' in method and 'list' not in method else '[]',
                network_passphrase="Public Global Stellar Network ; September 2015"
            )

            if result.get('success'):
                print(f"  ✅ {method}: {result.get('result', 'No result')}")
            else:
                print(f"  ❌ {method}: {result.get('error', 'Unknown error')}")
            print("")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_contract_methods())
    print(f"\nTest {'COMPLETED' if success else 'FAILED'}")