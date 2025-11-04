#!/usr/bin/env python3
"""
Deploy DeFindex Strategies using correct Soroban CLI syntax
"""

import subprocess
import json
import sys
import os
from datetime import datetime

# Configuration
SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
RPC_URL = "https://soroban-testnet.stellar.org"
BASE_WASM_PATH = "/home/ubuntu/blend-pools/backend/defindex/apps/contracts/target/wasm32v1-none/release"

# Strategies to deploy
strategies = {
    "HODL": "unsafe_hodl_strategy.wasm",
    "VAULT": "defindex_vault.wasm"
}

def deploy_strategy(name, wasm_file):
    """Deploy a single strategy using soroban CLI"""

    print(f"\n🚀 Deploying {name} strategy...")
    print(f"   📦 WASM: {wasm_file}")

    wasm_path = f"{BASE_WASM_PATH}/{wasm_file}"

    # Check if WASM file exists
    if not os.path.exists(wasm_path):
        print(f"   ❌ WASM file not found: {wasm_path}")
        return None, None

    # Build deployment command
    cmd = [
        "soroban", "contract", "deploy",
        "--wasm", wasm_path,
        "--source", SECRET_KEY,
        "--network-passphrase", NETWORK_PASSPHRASE,
        "--rpc-url", RPC_URL
    ]

    print(f"   🔧 Command: {' '.join(cmd)}")

    try:
        # Execute deployment
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"   ✅ {name} deployment successful!")

            # Try to extract contract ID from output
            contract_id = None
            for line in output.split('\n'):
                if line.strip().startswith('Contract ID:'):
                    contract_id = line.split('Contract ID:')[-1].strip()
                    break

            if contract_id:
                print(f"   🎯 Contract ID: {contract_id}")
                explorer_url = f"https://stellar.expert/explorer/testnet/contract/{contract_id}"
                print(f"   🔗 Explorer: {explorer_url}")
                return contract_id, explorer_url
            else:
                print(f"   ⚠️  Could not extract contract ID")
                print(f"   📋 Output: {output}")
                return None, None
        else:
            print(f"   ❌ {name} deployment failed!")
            print(f"   📋 Error: {result.stderr}")
            return None, None

    except subprocess.TimeoutExpired:
        print(f"   ⏰ {name} deployment timed out!")
        return None, None
    except Exception as e:
        print(f"   ❌ {name} deployment error: {e}")
        return None, None

def main():
    """Main deployment function"""

    print("🌟 DeFindex Strategy Deployment (Corrected)")
    print("=" * 60)
    print(f"🔐 Network: Testnet")
    print(f"📦 RPC URL: {RPC_URL}")

    # Create deployment log
    log_file = f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    print(f"📝 Logging to: {log_file}")

    deployment_results = {
        "deployment_date": datetime.now().isoformat(),
        "network": "testnet",
        "rpc_url": RPC_URL,
        "strategies": {}
    }

    successful_deployments = 0

    # Deploy each strategy
    for name, wasm_file in strategies.items():
        print(f"\n{'='*60}")

        contract_id, explorer_url = deploy_strategy(name, wasm_file)

        deployment_results["strategies"][name] = {
            "wasm_file": wasm_file,
            "contract_address": contract_id,
            "explorer_url": explorer_url,
            "status": "deployed" if contract_id else "failed"
        }

        if contract_id:
            successful_deployments += 1

        # Log to file
        with open(log_file, 'a') as f:
            f.write(f"\n{name} Strategy Deployment:\n")
            f.write(f"WASM: {wasm_file}\n")
            f.write(f"Contract ID: {contract_id}\n")
            f.write(f"Explorer: {explorer_url}\n")
            f.write(f"Status: {'Success' if contract_id else 'Failed'}\n")
            f.write("-" * 40 + "\n")

    # Save deployment results
    with open('strategy_deployment_results.json', 'w') as f:
        json.dump(deployment_results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"🎉 Deployment Summary:")

    print(f"   Total strategies: {len(strategies)}")
    print(f"   Successful: {successful_deployments}")
    print(f"   Failed: {len(strategies) - successful_deployments}")

    if successful_deployments > 0:
        print(f"\n✅ {successful_deployments} strategies deployed successfully!")
        print(f"📄 Results saved to: strategy_deployment_results.json")
        print(f"📝 Log file: {log_file}")

        # Show successful deployments
        print(f"\n🚀 Deployed Contracts:")
        for name, data in deployment_results["strategies"].items():
            if data["status"] == "deployed":
                print(f"   ✅ {name}: {data['contract_address']}")
                print(f"      🔗 {data['explorer_url']}")

        return 0
    else:
        print(f"\n❌ All deployments failed!")
        print(f"📄 Check log file for details: {log_file}")
        return 1

if __name__ == "__main__":
    sys.exit(main())