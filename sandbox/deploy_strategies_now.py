#!/usr/bin/env python3
"""
Deploy DeFindex Strategies to Stellar Testnet
Using correct WASM file paths
"""

import subprocess
import json
import sys
from datetime import datetime

# Configuration
SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
NETWORK = "testnet"
BASE_WASM_PATH = "/home/ubuntu/blend-pools/backend/defindex/apps/contracts/target/wasm32v1-none/release"

# Strategies to deploy (using available WASM files)
strategies = {
    "HODL": "unsafe_hodl_strategy.wasm",
    "VAULT": "defindex_vault.wasm"
}

def deploy_strategy(name, wasm_file, secret_key):
    """Deploy a single strategy using soroban CLI"""

    print(f"\n🚀 Deploying {name} strategy...")
    print(f"   📦 WASM: {wasm_file}")

    # Build deployment command
    cmd = [
        "soroban", "contract", "deploy",
        "--wasm", f"{BASE_WASM_PATH}/{wasm_file}",
        "--network", NETWORK,
        "--source", secret_key
    ]

    print(f"   🔧 Command: {' '.join(cmd)}")

    try:
        # Execute deployment
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"   ✅ {name} deployment successful!")
            print(f"   📋 Output: {output}")

            # Try to extract contract ID
            contract_id = None
            for line in output.split('\n'):
                if 'Contract ID:' in line:
                    contract_id = line.split('Contract ID:')[-1].strip()
                    break

            if contract_id:
                print(f"   🎯 Contract ID: {contract_id}")
                explorer_url = f"https://stellar.expert/explorer/testnet/contract/{contract_id}"
                print(f"   🔗 Explorer: {explorer_url}")
                return contract_id, explorer_url
            else:
                print(f"   ⚠️  Could not extract contract ID")
                print(f"   📋 Full output: {output}")
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

    print("🌟 DeFindex Strategy Deployment")
    print("=" * 50)
    print(f"🔐 Network: {NETWORK}")
    print(f"📦 WASM Path: {BASE_WASM_PATH}")

    # Check if WASM files exist
    for name, wasm_file in strategies.items():
        wasm_path = f"{BASE_WASM_PATH}/{wasm_file}"
        if not os.path.exists(wasm_path):
            print(f"❌ WASM file not found: {wasm_path}")
            return 1

    print(f"✅ All {len(strategies)} WASM files found!")

    # Create deployment log
    log_file = f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    print(f"📝 Logging to: {log_file}")

    deployment_results = {
        "deployment_date": datetime.now().isoformat(),
        "network": NETWORK,
        "strategies": {}
    }

    # Deploy each strategy
    for name, wasm_file in strategies.items():
        print(f"\n{'='*60}")

        contract_id, explorer_url = deploy_strategy(name, wasm_file, SECRET_KEY)

        deployment_results["strategies"][name] = {
            "wasm_file": wasm_file,
            "contract_address": contract_id,
            "explorer_url": explorer_url,
            "status": "deployed" if contract_id else "failed"
        }

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

    successful = sum(1 for s in deployment_results["strategies"].values() if s["status"] == "deployed")
    total = len(strategies)

    print(f"   Total strategies: {total}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {total - successful}")

    if successful > 0:
        print(f"\n✅ {successful} strategies deployed successfully!")
        print(f"📄 Results saved to: strategy_deployment_results.json")
        print(f"📝 Log file: {log_file}")

        print(f"\n🚀 Ready for integration testing!")
        return 0
    else:
        print(f"\n❌ All deployments failed!")
        return 1

if __name__ == "__main__":
    import os
    sys.exit(main())