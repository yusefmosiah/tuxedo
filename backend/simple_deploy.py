#!/usr/bin/env python3
"""
Simple Strategy Contract Deployment Preparation
"""

import os
import json
import sys
import requests
from stellar_sdk import Keypair, Server, TransactionBuilder, Network

def prepare_deployment():
    """Prepare contract for deployment by collecting necessary info"""

    print("🌟 DeFindex Strategy Contract Deployment Preparation")
    print("=" * 60)

    # Configuration
    SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
    WASM_FILE = "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/hodl/../../target/wasm32v1-none/release/hodl_strategy.wasm"

    strategies = [
        {"name": "HODL", "path": WASM_FILE},
        {"name": "BLEND", "path": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/blend/target/wasm32v1-none/release/blend_strategy.wasm"},
        {"name": "SOROSWAP", "path": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/soroswap/target/wasm32v1-none/release/soroswap_strategy.wasm"},
        {"name": "XYCLOANS", "path": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/xycloans/target/wasm32v1-none/release/xycloans_strategy.wasm"},
        {"name": "FIXED_APR", "path": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/fixed_apr/target/wasm32v1-none/release/fixed_apr_strategy.wasm"}
    ]

    deployer = Keypair.from_secret(SECRET_KEY)
    print(f"🔐 Deployer Account: {deployer.public_key}")

    # Check account balance
    try:
        server = Server("https://horizon-testnet.stellar.org")
        account = server.load_account(deployer.public_key)
        print(f"💰 Account Status: Funded")
        print(f"   Successfully loaded account")
    except Exception as e:
        print(f"❌ Account issue: {e}")
        return False

    deployment_info = {
        "deployer_secret": SECRET_KEY,
        "deployer_public": deployer.public_key,
        "network": "testnet",
        "horizon_url": "https://horizon-testnet.stellar.org",
        "soroban_rpc": "https://soroban-testnet.stellar.org",
        "status": "prepared",
        "strategies": []
    }

    # Check which strategies are ready
    for strategy in strategies:
        print(f"\n🔍 Checking {strategy['name']} strategy...")

        if os.path.exists(strategy['path']):
            size = os.path.getsize(strategy['path'])
            print(f"   ✅ Found: {strategy['path']} ({size} bytes)")
            deployment_info['strategies'].append({
                "name": strategy['name'],
                "wasm_file": strategy['path'],
                "size_bytes": size,
                "status": "ready"
            })
        else:
            print(f"   ❌ Missing: {strategy['path']}")
            deployment_info['strategies'].append({
                "name": strategy['name'],
                "wasm_file": strategy['path'],
                "status": "needs_build"
            })

    # Save deployment info
    with open('strategy_deployment_info.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)

    print(f"\n💾 Deployment info saved to strategy_deployment_info.json")

    ready_strategies = [s for s in deployment_info['strategies'] if s['status'] == 'ready']
    print(f"\n📊 Summary:")
    print(f"   Total strategies: {len(strategies)}")
    print(f"   Ready to deploy: {len(ready_strategies)}")
    print(f"   Need build: {len(strategies) - len(ready_strategies)}")

    if ready_strategies:
        print(f"\n🚀 Ready to deploy:")
        for strategy in ready_strategies:
            print(f"   - {strategy['name']}: {strategy['wasm_file']}")

    return True

def build_remaining_strategies():
    """Build strategies that aren't ready yet"""
    print("🔨 Building remaining strategies...")

    strategies_to_build = [
        {"name": "BLEND", "dir": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/blend"},
        {"name": "SOROSWAP", "dir": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/soroswap"},
        {"name": "XYCLOANS", "dir": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/xycloans"},
        {"name": "FIXED_APR", "dir": "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/fixed_apr"}
    ]

    for strategy in strategies_to_build:
        print(f"\n🔨 Building {strategy['name']}...")

        if os.path.exists(strategy['dir']):
            # Change to strategy directory and build
            original_dir = os.getcwd()
            os.chdir(strategy['dir'])

            try:
                import subprocess
                result = subprocess.run(['cargo', 'build', '--target', 'wasm32v1-none', '--release'],
                                      capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    print(f"   ✅ {strategy['name']} built successfully")
                else:
                    print(f"   ❌ {strategy['name']} build failed:")
                    print(f"      {result.stderr}")
            except subprocess.TimeoutExpired:
                print(f"   ⏰ {strategy['name']} build timed out")
            except Exception as e:
                print(f"   ❌ {strategy['name']} build error: {e}")
            finally:
                os.chdir(original_dir)
        else:
            print(f"   ❌ Directory not found: {strategy['dir']}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build_remaining_strategies()
    else:
        prepare_deployment()