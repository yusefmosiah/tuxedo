#!/usr/bin/env python3
"""
Check all DeFindex strategies are ready for deployment
"""

import os
import json

def check_strategies():
    print("🌟 DeFindex Strategy Deployment Status")
    print("=" * 50)

    # Correct paths for built strategies
    base_path = "/home/ubuntu/blend-pools/defindex/apps/contracts/target/wasm32v1-none/release"

    strategies = [
        {"name": "HODL", "wasm": "hodl_strategy.wasm"},
        {"name": "BLEND", "wasm": "blend_strategy.wasm"},
        {"name": "SOROSWAP", "wasm": "soroswap_strategy.wasm"},
        {"name": "XYCLOANS", "wasm": "xycloans_adapter.wasm"},  # Note: this is xycloans_adapter
        {"name": "FIXED_APR", "wasm": "fixed_apr_strategy.wasm"}
    ]

    ready_strategies = []
    deployer_secret = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"

    print(f"🔐 Deployer Secret Key: {deployer_secret[:10]}...{deployer_secret[-10:]}")
    print(f"📁 Target Directory: {base_path}")
    print()

    for strategy in strategies:
        full_path = os.path.join(base_path, strategy['wasm'])

        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✅ {strategy['name']}: {strategy['wasm']} ({size:,} bytes)")
            ready_strategies.append({
                "name": strategy['name'],
                "wasm_file": full_path,
                "size_bytes": size,
                "status": "ready"
            })
        else:
            print(f"❌ {strategy['name']}: {strategy['wasm']} - NOT FOUND")

    print(f"\n📊 Summary:")
    print(f"   Total strategies: {len(strategies)}")
    print(f"   Ready to deploy: {len(ready_strategies)}")

    # Create final deployment info
    deployment_info = {
        "deployer_secret": deployer_secret,
        "network": "testnet",
        "horizon_url": "https://horizon-testnet.stellar.org",
        "soroban_rpc": "https://soroban-testnet.stellar.org",
        "status": "ready",
        "strategies": ready_strategies
    }

    # Save deployment info
    with open('final_deployment_info.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)

    print(f"💾 Final deployment info saved to final_deployment_info.json")

    if ready_strategies:
        print(f"\n🚀 All {len(ready_strategies)} strategies are ready for deployment!")
        print(f"\n📋 Deployment commands for manual deployment:")
        for strategy in ready_strategies:
            print(f"   # Deploy {strategy['name']}")
            print(f"   soroban contract install \\")
            print(f"     --wasm {strategy['wasm_file']} \\")
            print(f"     --network testnet")
            print()
    else:
        print(f"\n❌ No strategies are ready for deployment")

    return len(ready_strategies) == len(strategies)

if __name__ == "__main__":
    all_ready = check_strategies()
    exit(0 if all_ready else 1)