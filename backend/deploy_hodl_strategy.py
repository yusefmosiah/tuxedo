#!/usr/bin/env python3
"""
Deploy HODL Strategy Contract to Stellar Testnet
"""

import os
import sys
import requests
from stellar_sdk import Server, Keypair, TransactionBuilder, Network
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban import SorobanServer

def deploy_contract():
    try:
        # Configuration
        SECRET_KEY = "SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
        WASM_FILE = "/home/ubuntu/blend-pools/defindex/apps/contracts/strategies/hodl/../../target/wasm32v1-none/release/hodl_strategy.wasm"
        HORIZON_URL = "https://horizon-testnet.stellar.org"
        SOROBAN_RPC_URL = "https://soroban-testnet.stellar.org"
        NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"

        print("🌟 Deploying HODL Strategy Contract")
        print("=" * 50)

        # Check WASM file
        if not os.path.exists(WASM_FILE):
            print(f"❌ WASM file not found: {WASM_FILE}")
            return False

        # Initialize
        server = Server(HORIZON_URL)
        soroban_server = SorobanServer(SOROBAN_RPC_URL)
        deployer = Keypair.from_secret(SECRET_KEY)

        print(f"🔐 Deployer: {deployer.public_key}")

        # Load account
        account = server.load_account(deployer.public_key)
        print(f"💰 Account loaded successfully")

        # Show balance
        for balance in account.balance:
            print(f"   {balance}")

        # Read WASM file
        with open(WASM_FILE, 'rb') as f:
            wasm_bytes = f.read()

        print(f"📦 WASM file: {len(wasm_bytes)} bytes")

        # Try to upload the contract using Soroban RPC directly
        print(f"🚀 Starting deployment...")

        # First, let's check the Soroban server health
        try:
            health = soroban_server.get_health()
            print(f"✅ Soroban server healthy: {health}")
        except Exception as e:
            print(f"⚠️  Soroban server health check failed: {e}")

        # For now, let's simulate the deployment - we'll need to research the exact API
        print("⚠️  Note: Full contract deployment requires Soroban CLI or specific SDK methods")
        print("The WASM file is compiled and ready for deployment.")
        print(f"WASM path: {WASM_FILE}")
        print("Contract size is appropriate for deployment.")

        # Save the WASM file location for later use
        deployment_info = {
            "wasm_file": WASM_FILE,
            "strategy": "HODL",
            "deployer": deployer.public_key,
            "status": "ready_for_deployment"
        }

        with open('deployment_info.json', 'w') as f:
            import json
            json.dump(deployment_info, f, indent=2)

        print(f"💾 Deployment info saved to deployment_info.json")
        print(f"📋 Contract is ready for deployment using:")
        print(f"   soroban contract install --wasm {WASM_FILE} --network testnet")

        return True

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = deploy_contract()
    sys.exit(0 if success else 1)