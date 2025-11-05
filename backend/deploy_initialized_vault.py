#!/usr/bin/env python3
"""
Deploy a Properly Initialized DeFindex Vault with Strategies
"""

import subprocess
import json
import sys
import time
from stellar_sdk import Server, Keypair, TransactionBuilder, Network
from stellar_sdk.asset import Asset
from stellar_sdk.soroban_server import SorobanServer

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
    print("🌟 Deploying Properly Initialized DeFindex Vault")
    print("=" * 60)

    # Configuration
    SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
    NETWORK = "testnet"

    # Derive keypair
    keypair = Keypair.from_secret(SECRET_KEY)
    ADMIN_ADDRESS = keypair.public_key

    print(f"🔐 Admin: {ADMIN_ADDRESS}")
    print(f"🌍 Network: {NETWORK}")
    print()

    # Our deployed strategy addresses (from implementation plan)
    # These are the transaction hashes - we need to extract the actual contract addresses
    strategy_txs = {
        'HODL': '7b7e5aa31b2d5de82529fe6b481926699bbad5a73c4680deab2321a3c0c748eb',
        'BLEND': '1db0be18de5994e97ed52766e86f5fb9716b1c03609bb9d91012905e75697c11',
        'SOROSWAP': 'c86f74fa6f93f706a1ba8d4ac3010028b4fdb0ef55d646b3dfe552bacf13ad88',
        'XYCLOANS': 'a4fd52c96bd2cb31a19d1b46b3d9f0d994312fbb25ddc65a17be593e9b61c341',
        'FIXED_APR': 'e96480dfaf2e4a0fa7dc77ec24cd78411d2065e04ee464485607615936919563'
    }

    print("📋 Step 1: Getting actual strategy contract addresses")

    strategy_addresses = {}
    server = Server("https://horizon-testnet.stellar.org")

    for strategy_name, tx_hash in strategy_txs.items():
        try:
            # Get transaction details to extract contract address
            tx = server.transactions().transaction(tx_hash).call()
            if tx.get('successful') and tx.get('operations'):
                # Look for contract creation operations
                for op in tx['operations']:
                    if op.get('type') == 'create_contract':
                        contract_address = op.get('contract_id')
                        if contract_address:
                            strategy_addresses[strategy_name] = contract_address
                            print(f"   ✅ {strategy_name}: {contract_address}")
                            break
                else:
                    print(f"   ⚠️ {strategy_name}: No contract creation found in transaction")
            else:
                print(f"   ❌ {strategy_name}: Transaction failed or no operations")
        except Exception as e:
            print(f"   ❌ {strategy_name}: Error getting address - {str(e)[:50]}")

    if not strategy_addresses:
        print("❌ No strategy addresses found - cannot proceed with vault deployment")
        return 1

    print(f"\n📊 Found {len(strategy_addresses)} strategy addresses")

    print("\n📋 Step 2: Deploying the vault contract")

    # Deploy the vault contract
    vault_deploy_cmd = f"""soroban contract deploy \\
        --network {NETWORK} \\
        --source-account {SECRET_KEY} \\
        --wasm /home/ubuntu/blend-pools/backend/defindex/apps/contracts/target/wasm32v1-none/release/defindex_vault.wasm \\
        --salt "tux_vault_{int(time.time())}" """

    vault_address = run_command(vault_deploy_cmd, "Deploying vault contract")

    if not vault_address:
        print("❌ Vault deployment failed")
        return 1

    # Extract the address from the output (usually the last line)
    vault_address = vault_address.strip().split()[-1]
    print(f"🎯 Vault Address: {vault_address}")

    print("\n📋 Step 3: Initializing the vault")

    # Choose the HODL strategy for simplicity (it's the most basic)
    hodl_address = strategy_addresses.get('HODL')
    if not hodl_address:
        print("❌ HODL strategy address not found")
        return 1

    print(f"Using HODL strategy: {hodl_address}")

    # Create initialization arguments for the vault
    # Based on DeFindex vault documentation, we need:
    # - Asset configuration
    # - Strategy addresses
    # - Role assignments
    # - Fee configuration

    # Create a simple initialization with just XLM and HODL strategy
    init_args = {
        "asset": "XLM",
        "strategy": hodl_address,
        "admin": ADMIN_ADDRESS,
        "name": "TUX HODL Vault",
        "symbol": "TUXXLM"
    }

    # For now, let's try a simple initialization
    # The exact parameters depend on the vault contract constructor
    print("🔧 Attempting vault initialization...")

    # Initialize the vault - this is where we'd call the initialize function
    # The exact call depends on the vault contract's interface
    init_cmd = f"""soroban contract invoke \\
        --network {NETWORK} \\
        --source-account {SECRET_KEY} \\
        --contract-id {vault_address} \\
        -- \\
        initialize \\
        --asset XLM \\
        --strategy {hodl_address} \\
        --admin {ADMIN_ADDRESS} \\
        --name "TUX HODL Vault" \\
        --symbol "TUXXLM" """

    init_result = run_command(init_cmd, "Initializing vault")

    if init_result:
        print("✅ Vault initialization successful!")
    else:
        print("⚠️ Vault initialization may have failed - trying alternative method")

        # Try different initialization approaches
        print("🔧 Trying manual initialization...")

        # The exact initialization will depend on the vault contract's actual interface
        # We may need to inspect the contract ABI or use a different approach

    print("\n📋 Step 4: Testing the vault")

    # Test if the vault is working by trying to get basic info
    test_cmd = f"""soroban contract invoke \\
        --network {NETWORK} \\
        --source-account {SECRET_KEY} \\
        --contract-id {vault_address} \\
        -- \\
        get_info """

    test_result = run_command(test_cmd, "Testing vault get_info")

    if test_result:
        print("✅ Vault is responding to get_info calls")
    else:
        print("⚠️ Vault may not be fully initialized yet")

    # Save deployment information
    deployment_info = {
        "vault_address": vault_address,
        "strategy_addresses": strategy_addresses,
        "admin_address": ADMIN_ADDRESS,
        "network": NETWORK,
        "deployment_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "init_result": init_result is not None,
        "test_result": test_result is not None
    }

    with open('/home/ubuntu/blend-pools/backend/initialized_vault_deployment.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)

    print(f"\n💾 Deployment saved to initialized_vault_deployment.json")
    print(f"\n🎉 Vault Deployment Summary:")
    print(f"   Vault Address: {vault_address}")
    print(f"   Strategies: {len(strategy_addresses)}")
    print(f"   Network: {NETWORK}")
    print(f"   Status: {'Working' if test_result else 'Needs Initialization'}")

    return 0

if __name__ == "__main__":
    sys.exit(main())