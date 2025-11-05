#!/usr/bin/env python3
"""
Deploy DeFindex Vault with HODL Strategy to Stellar Testnet
"""

import subprocess
import json
import sys

def run_command(cmd, description, capture_output=True):
    """Run a command and return the result"""
    print(f"🔧 {description}")
    print(f"   Command: {cmd}")

    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Success: {result.stdout.strip()}")
                return result.stdout.strip()
            else:
                print(f"   ❌ Error: {result.stderr.strip()}")
                return None
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None

def main():
    print("🌟 DeFindex Vault Deployment with HODL Strategy")
    print("=" * 60)

    # Configuration
    SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
    NETWORK = "testnet"
    ADMIN_ADDRESS = "GDBIB3ALIA5YX5CCX4HRQXPGEKQYQPL4CIVU62U5JAWJKCLSW6CICKRX"

    print(f"🔐 Admin: {ADMIN_ADDRESS}")
    print(f"🌍 Network: {NETWORK}")
    print()

    # Step 1: Deploy HODL strategy contract instance
    print("📋 Step 1: Deploying HODL Strategy Contract Instance")

    # First we need to create an instance of the HODL strategy
    # The HODL strategy needs to be initialized with the asset it will hold
    hodl_deploy_cmd = f"""soroban contract deploy \\
        --network {NETWORK} \\
        --source-account {SECRET_KEY} \\
        --wasm-hash "$(soroban contract info --network {NETWORK} --wasm /home/ubuntu/blend-pools/backend/defindex/apps/contracts/target/wasm32v1-none/release/hodl_strategy.wasm | grep 'Wasm Hash:' | cut -d' ' -f3)" \\
        --salt "hodl_strategy_xlm_123456789012345678901234" \\
        --asset XLM"""

    result = run_command(hodl_deploy_cmd, "Deploying HODL strategy instance")

    if result:
        print(f"🎯 HODL Strategy deployed: {result}")
        # Extract contract address from result
        hodl_contract_address = result.split()[-1]  # Assuming last token is address
        print(f"📍 HODL Strategy Address: {hodl_contract_address}")
    else:
        print("❌ HODL strategy deployment failed")
        return 1

    print()

    # Step 2: Deploy the vault contract
    print("📋 Step 2: Deploying DeFindex Vault Contract")

    # For now, let's try a simple approach to see what the actual constructor expects
    # We'll need to construct the proper arguments based on the analysis

    # Create a simple JSON file with the constructor arguments
    vault_args = {
        "assets": [{
            "address": "XLM",  # Native XLM asset
            "strategies": [{
                "address": hodl_contract_address,
                "name": "HODL Strategy",
                "paused": False
            }]
        }],
        "roles": {
            "0": ADMIN_ADDRESS,  # Emergency Manager
            "1": ADMIN_ADDRESS,  # Vault Fee Receiver
            "2": ADMIN_ADDRESS,  # Manager
            "3": ADMIN_ADDRESS   # Rebalance Manager
        },
        "vault_fee": 2000,        # 0.20% = 2000 basis points
        "defindex_protocol_receiver": ADMIN_ADDRESS,
        "defindex_protocol_rate": 2500,  # 0.25% protocol fee
        "soroswap_router": ADMIN_ADDRESS,  # Using admin address for now
        "name_symbol": {
            "name": "Test Vault",
            "symbol": "TESTV"
        },
        "upgradable": True
    }

    with open('/tmp/vault_args.json', 'w') as f:
        json.dump(vault_args, f, indent=2)

    print("📝 Vault constructor arguments prepared:")
    print(json.dumps(vault_args, indent=2))
    print()

    # Try deploying with basic parameters first to see actual error
    vault_deploy_cmd = f"""soroban contract deploy \\
        --network {NETWORK} \\
        --source-account {SECRET_KEY} \\
        --wasm /home/ubuntu/blend-pools/backend/defindex/apps/contracts/target/wasm32v1-none/release/defindex_vault.wasm \\
        --salt "test_vault_123456789012345678901234" """

    result = run_command(vault_deploy_cmd, "Attempting vault deployment")

    if result:
        print(f"🎉 Vault deployment successful: {result}")
        vault_address = result.split()[-1]
        print(f"📍 Vault Address: {vault_address}")

        # Save deployment info
        deployment_info = {
            "vault_address": vault_address,
            "hodl_strategy_address": hodl_contract_address,
            "admin_address": ADMIN_ADDRESS,
            "network": NETWORK,
            "timestamp": subprocess.check_output(['date'], text=True).strip()
        }

        with open('/home/ubuntu/blend-pools/backend/vault_deployment.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)

        print("💾 Deployment info saved to vault_deployment.json")

    else:
        print("❌ Vault deployment failed - need to fix constructor arguments")
        return 1

    print()
    print("🎯 Next Steps:")
    print("1. Test vault initialization")
    print("2. Verify strategy integration")
    print("3. Test deposit/withdrawal functionality")

    return 0

if __name__ == "__main__":
    sys.exit(main())