#!/usr/bin/env python3
"""
Deploy a Working DeFindex Vault Using Existing Contract Infrastructure
"""

import subprocess
import json
import sys
import time
import os

def run_command(cmd, description, capture_output=True):
    """Run a command and return the result"""
    print(f"🔧 {description}")
    print(f"   Command: {cmd}")

    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"   ✅ Success: {result.stdout.strip()}")
                return result.stdout.strip()
            else:
                print(f"   ❌ Error: {result.stderr.strip()}")
                return None
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout after 60 seconds")
        return None
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None

def main():
    print("🌟 Deploying Working DeFindex Vault")
    print("=" * 60)

    # Configuration
    SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
    NETWORK = "testnet"

    # Derive keypair
    from stellar_sdk import Keypair
    keypair = Keypair.from_secret(SECRET_KEY)
    ADMIN_ADDRESS = keypair.public_key

    print(f"🔐 Admin: {ADMIN_ADDRESS}")
    print(f"🌍 Network: {NETWORK}")
    print()

    # Load existing contract hashes
    contracts_path = "/home/ubuntu/blend-pools/backend/defindex/apps/contracts/public/testnet.contracts.json"

    if not os.path.exists(contracts_path):
        print("❌ Testnet contracts file not found")
        return 1

    with open(contracts_path, 'r') as f:
        contracts = json.load(f)

    print("📋 Available Contract Hashes:")
    for name, hash_val in contracts['hashes'].items():
        print(f"   {name}: {hash_val}")

    # Use the installed vault WASM hash
    vault_hash = "1dd9f8c885d70b8f1bd41d67c5914465e78ade8ae97c81d3e5531059a8eee79b"
    print(f"\n📋 Step 1: Deploying vault using installed hash: {vault_hash}")

    # Create unique salt
    salt_hex = format(int(time.time()), 'x')  # Convert timestamp to hex

    # Deploy vault contract instance using existing hash
    vault_deploy_cmd = f"""soroban contract deploy \\
        --network {NETWORK} \\
        --source-account {SECRET_KEY} \\
        --wasm-hash {vault_hash} \\
        --salt {salt_hex} """

    vault_result = run_command(vault_deploy_cmd, "Deploying vault contract")

    if not vault_result:
        print("❌ Vault deployment failed")
        return 1

    # Extract the address from the output
    vault_address = vault_result.strip().split()[-1]
    print(f"🎯 Vault Address: {vault_address}")

    print("\n📋 Step 2: Testing basic vault functionality")

    # Test if the vault responds to basic calls
    test_functions = [
        ("name", "Get vault name"),
        ("symbol", "Get vault symbol"),
        ("decimals", "Get token decimals"),
        ("total_supply", "Get total supply")
    ]

    working_functions = []
    for func_name, description in test_functions:
        test_cmd = f"""soroban contract invoke \\
            --network {NETWORK} \\
            --source-account {SECRET_KEY} \\
            --contract-id {vault_address} \\
            -- \\
            {func_name} """

        result = run_command(test_cmd, description, capture_output=True)
        if result and "error" not in result.lower() and "MissingValue" not in result:
            working_functions.append(func_name)
            print(f"   ✅ {func_name}() works: {result[:50]}...")
        else:
            print(f"   ❌ {func_name}() failed: {result[:50] if result else 'No result'}...")

    print(f"\n📊 Found {len(working_functions)} working functions")

    print("\n📋 Step 3: Testing DeFindex API integration")

    # Test with our DeFindex API client
    try:
        from dotenv import load_dotenv
        load_dotenv()

        from defindex_client import get_defindex_client

        client = get_defindex_client('testnet')
        print("✅ DeFindex API client initialized")

        # Test API calls to our vault
        api_tests = [
            ("get_vault_info", "Get vault info via API"),
            ("get_vault_apy", "Get vault APY via API"),
        ]

        for api_func, description in api_tests:
            try:
                if api_func == "get_vault_info":
                    result = client.get_vault_info(vault_address)
                    print(f"✅ {description}: {result.get('name', 'Unknown vault')}")
                elif api_func == "get_vault_apy":
                    result = client.get_vault_apy(vault_address)
                    print(f"✅ {description}: {result.get('apy', 0):.2f}%")
            except Exception as e:
                print(f"⚠️ {description} failed: {str(e)[:50]}...")

    except Exception as e:
        print(f"❌ API client setup failed: {e}")

    print("\n📋 Step 4: Testing deposit transaction building")

    try:
        # Test building a deposit transaction
        tx_data = client.build_deposit_transaction(
            vault_address=vault_address,
            amount_stroops=10000000,  # 1 XLM
            caller=ADMIN_ADDRESS
        )
        print("✅ API can build deposit transactions")
        print(f"   Transaction type: {tx_data.get('data_source', 'unknown')}")
    except Exception as e:
        print(f"⚠️ Deposit transaction building failed: {str(e)[:50]}...")

    # Save deployment information
    deployment_info = {
        "vault_address": vault_address,
        "vault_hash": vault_hash,
        "admin_address": ADMIN_ADDRESS,
        "network": NETWORK,
        "deployment_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "working_functions": working_functions,
        "status": "deployed",
        "contracts_used": contracts
    }

    with open('/home/ubuntu/blend-pools/backend/working_vault_deployment.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)

    print(f"\n💾 Deployment saved to working_vault_deployment.json")
    print(f"\n🎉 Working Vault Deployment Summary:")
    print(f"   Vault Address: {vault_address}")
    print(f"   Vault Hash: {vault_hash}")
    print(f"   Working Functions: {len(working_functions)}")
    print(f"   Network: {NETWORK}")

    print(f"\n📋 Step 5: Updating our tools to use this vault")

    # Update defindex_soroban.py to include this vault
    try:
        defindex_soroban_path = "/home/ubuntu/blend-pools/backend/defindex_soroban.py"

        with open(defindex_soroban_path, 'r') as f:
            content = f.read()

        # Add our new vault to TESTNET_VAULTS
        if "TESTNET_VAULTS = {" in content:
            new_vault_entry = f"    'TUX_WORKING_VAULT': '{vault_address}',"

            # Insert at the beginning of TESTNET_VAULTS
            updated_content = content.replace(
                "TESTNET_VAULTS = {",
                f"TESTNET_VAULTS = {{\n{new_vault_entry}"
            )

            with open(defindex_soroban_path, 'w') as f:
                f.write(updated_content)

            print("✅ Added new vault to TESTNET_VAULTS in defindex_soroban.py")

            # Also update the tools to use this vault
            defindex_tools_path = "/home/ubuntu/blend-pools/backend/defindex_tools.py"
            with open(defindex_tools_path, 'r') as f:
                tools_content = f.read()

            if "TESTNET_VAULTS = {" in tools_content:
                updated_tools_content = tools_content.replace(
                    "TESTNET_VAULTS = {",
                    f"TESTNET_VAULTS = {{\n    'TUX_WORKING_VAULT': '{vault_address}',"
                )

                with open(defindex_tools_path, 'w') as f:
                    f.write(updated_tools_content)

                print("✅ Added new vault to TESTNET_VAULTS in defindex_tools.py")

    except Exception as e:
        print(f"⚠️ Could not update tool files: {e}")

    print(f"\n🚀 Ready to test with new vault: {vault_address}")
    print(f"   Next step: Test the AI agent tools with this vault")

    return 0

if __name__ == "__main__":
    sys.exit(main())