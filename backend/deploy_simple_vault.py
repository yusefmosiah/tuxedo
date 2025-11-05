#!/usr/bin/env python3
"""
Deploy a Simple DeFindex Vault for Testing
"""

import subprocess
import json
import sys
import time

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
    print("🌟 Deploying Simple DeFindex Vault for Testing")
    print("=" * 60)

    # Configuration
    SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
    NETWORK = "testnet"

    print(f"🌍 Network: {NETWORK}")
    print()

    print("📋 Step 1: Deploying the vault contract")

    # Deploy the vault contract with constructor arguments
    # Based on DeFindex vault documentation, we need assets, strategies, and configuration
    salt_hex = f"{int(time.time()):x}"  # Convert timestamp to hex

    # Create a simple initialization with XLM asset
    # For now, we'll use a basic configuration that we can refine later
    vault_deploy_cmd = f"""soroban contract deploy \\
        --network {NETWORK} \\
        --source-account {SECRET_KEY} \\
        --wasm /home/ubuntu/blend-pools/backend/defindex/apps/contracts/target/wasm32v1-none/release/defindex_vault.wasm \\
        --salt {salt_hex} \\
        --XLM """  # Basic XLM asset configuration

    vault_result = run_command(vault_deploy_cmd, "Deploying vault contract")

    if not vault_result:
        print("❌ Vault deployment failed")
        return 1

    # Extract the address from the output
    vault_address = vault_result.strip().split()[-1]
    print(f"🎯 Vault Address: {vault_address}")

    print("\n📋 Step 2: Trying basic vault functions")

    # Try to get basic info from the vault
    # The exact function names will depend on the vault contract implementation
    test_functions = [
        "get_info",
        "name",
        "symbol",
        "total_assets",
        "total_shares"
    ]

    working_functions = []
    for func_name in test_functions:
        test_cmd = f"""soroban contract invoke \\
            --network {NETWORK} \\
            --source-account {SECRET_KEY} \\
            --contract-id {vault_address} \\
            -- \\
            {func_name} """

        result = run_command(test_cmd, f"Testing {func_name}()", capture_output=True)
        if result and "error" not in result.lower():
            working_functions.append(func_name)
            print(f"   ✅ {func_name}() works")
        else:
            print(f"   ❌ {func_name}() failed or not available")

    print(f"\n📊 Found {len(working_functions)} working functions")

    print("\n📋 Step 3: Testing with our existing test tools")

    # Test if our existing tools can work with this vault
    try:
        from dotenv import load_dotenv
        load_dotenv()

        from defindex_client import get_defindex_client

        client = get_defindex_client('testnet')
        print("✅ DeFindex API client initialized")

        # Try to get vault info via API
        try:
            vault_info = client.get_vault_info(vault_address)
            print(f"✅ API can get vault info: {vault_info.get('name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ API vault info failed: {str(e)[:50]}...")

        # Try to get APY via API
        try:
            apy_data = client.get_vault_apy(vault_address)
            print(f"✅ API can get APY: {apy_data.get('apy', 0):.2f}%")
        except Exception as e:
            print(f"⚠️ API APY failed: {str(e)[:50]}...")

        # Try building a deposit transaction
        try:
            tx_data = client.build_deposit_transaction(
                vault_address=vault_address,
                amount_stroops=10000000,  # 1 XLM
                caller="GBY5M5GPC2DUVMHO6FLQWT6YQ7TPSXGMSMU5CP2IGGJMDISQGRN2JCW5"
            )
            print(f"✅ API can build deposit transactions")
        except Exception as e:
            print(f"⚠️ API deposit building failed: {str(e)[:50]}...")

    except Exception as e:
        print(f"❌ API client setup failed: {e}")

    # Save deployment information
    deployment_info = {
        "vault_address": vault_address,
        "network": NETWORK,
        "deployment_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "working_functions": working_functions,
        "status": "deployed"
    }

    with open('/home/ubuntu/blend-pools/backend/simple_vault_deployment.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)

    print(f"\n💾 Deployment saved to simple_vault_deployment.json")
    print(f"\n🎉 Simple Vault Deployment Summary:")
    print(f"   Vault Address: {vault_address}")
    print(f"   Working Functions: {len(working_functions)}")
    print(f"   Network: {NETWORK}")

    # Now let's update our tools to use this vault
    print(f"\n📋 Step 4: Updating tools to use this vault")

    try:
        # Update the defindex_soroban.py to include this vault
        defindex_soroban_path = "/home/ubuntu/blend-pools/backend/defindex_soroban.py"

        with open(defindex_soroban_path, 'r') as f:
            content = f.read()

        # Find the TESTNET_VAULTS section and add our new vault
        if "TESTNET_VAULTS = {" in content:
            # Add our new vault to the list
            new_vault_entry = f"    'TUX_SIMPLE_VAULT': '{vault_address}',"

            # Insert before the closing brace
            updated_content = content.replace(
                "TESTNET_VAULTS = {",
                f"TESTNET_VAULTS = {{\n{new_vault_entry}"
            )

            with open(defindex_soroban_path, 'w') as f:
                f.write(updated_content)

            print("✅ Added new vault to TESTNET_VAULTS in defindex_soroban.py")

    except Exception as e:
        print(f"⚠️ Could not update defindex_soroban.py: {e}")

    print(f"\n🚀 Ready to test with new vault: {vault_address}")

    return 0

if __name__ == "__main__":
    sys.exit(main())