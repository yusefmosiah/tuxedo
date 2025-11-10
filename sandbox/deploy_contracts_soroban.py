#!/usr/bin/env python3
"""
Simplified TUX Contract Deployment using Soroban CLI
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

class SorobanDeployer:
    def __init__(self):
        self.network_passphrase = "Test SDF Network ; September 2015"
        self.rpc_url = "https://soroban-testnet.stellar.org"
        self.horizon_url = "https://horizon-testnet.stellar.org"

        # Get admin key from environment or generate new
        admin_secret = os.getenv("ADMIN_SECRET_KEY")
        if admin_secret:
            self.admin_secret = admin_secret
            self.admin_public = self.get_public_key_from_secret(admin_secret)
            print(f"Using existing admin account: {self.admin_public}")
        else:
            # Generate new key pair using stellar-secret-key
            result = subprocess.run(['stellar-secret-key'], capture_output=True, text=True)
            if result.returncode == 0:
                keys = result.stdout.strip().split('\n')
                self.admin_secret = keys[0].split(': ')[1]
                self.admin_public = keys[1].split(': ')[1]
                print(f"Generated new admin account:")
                print(f"Public Key: {self.admin_public}")
                print(f"Secret Key: {self.admin_secret}")
                print("IMPORTANT: Save this secret key for future use!")
            else:
                raise Exception("Failed to generate key pair")

        # Ensure account is funded
        self.ensure_account_funded(self.admin_public)

    def get_public_key_from_secret(self, secret):
        """Extract public key from secret key"""
        result = subprocess.run(['stellar-secret-key', '--secret', secret], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'Public Key:' in line:
                    return line.split(': ')[1]
        raise Exception("Failed to get public key from secret")

    def ensure_account_funded(self, public_key):
        """Ensure account exists on testnet using friendbot"""
        try:
            response = subprocess.run([
                'curl', '-s', f'https://friendbot.stellar.org?addr={public_key}'
            ], capture_output=True, text=True)

            if response.returncode == 0:
                data = json.loads(response.stdout)
                if 'successful' in data and data['successful']:
                    print(f"Account {public_key} successfully funded!")
                    return
                else:
                    print(f"Account {public_key} already exists or funding failed")
            else:
                print(f"Friendbot request failed: {response.stderr}")
        except Exception as e:
            print(f"Funding error (account may exist): {e}")

    def deploy_contract(self, wasm_file, contract_name):
        """Deploy contract using soroban CLI"""
        print(f"\n=== Deploying {contract_name} ===")

        # Check if WASM file exists
        if not Path(wasm_file).exists():
            print(f"❌ WASM file not found: {wasm_file}")
            return None

        # Deploy using soroban CLI
        try:
            # Install contract
            install_cmd = [
                'soroban', 'contract', 'install',
                '--wasm', wasm_file,
                '--source', self.admin_secret,
                '--network-passphrase', self.network_passphrase,
                '--rpc-url', self.rpc_url
            ]

            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Contract install failed: {result.stderr}")
                return None

            install_output = result.stdout.strip()
            print(f"✅ Contract installed: {install_output}")

            # Extract contract ID from install output
            contract_id = None
            for line in install_output.split('\n'):
                if 'Contract ID:' in line or contract_id is None:
                    # Try to parse the output - usually the last line contains the contract ID
                    if line.strip() and not line.startswith('Created'):
                        contract_id = line.strip()

            if not contract_id:
                print("❌ Could not extract contract ID from install output")
                return None

            print(f"✅ {contract_name} deployed successfully!")
            print(f"   Contract ID: {contract_id}")
            return contract_id

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return None

    def initialize_tux_token(self, contract_id):
        """Initialize TUX token contract"""
        print(f"\n=== Initializing TUX Token ===")

        try:
            # Initialize contract with admin and initial supply
            init_cmd = [
                'soroban', 'contract', 'invoke',
                '--id', contract_id,
                '--source', self.admin_secret,
                '--network-passphrase', self.network_passphrase,
                '--rpc-url', self.rpc_url,
                '--',
                'initialize',
                '--admin', self.admin_public,
                '--initial-supply', '1000000000000000'  # 100M TUX with 7 decimals
            ]

            result = subprocess.run(init_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ TUX token initialization failed: {result.stderr}")
                return False

            print("✅ TUX token initialized successfully!")
            print(f"   Total Supply: 100,000,000 TUX")
            print(f"   Admin: {self.admin_public}")
            return True

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def initialize_farming_contract(self, contract_id, tux_token_id):
        """Initialize farming contract"""
        print(f"\n=== Initializing Farming Contract ===")

        try:
            # Initialize farming contract
            init_cmd = [
                'soroban', 'contract', 'invoke',
                '--id', contract_id,
                '--source', self.admin_secret,
                '--network-passphrase', self.network_passphrase,
                '--rpc-url', self.rpc_url,
                '--',
                'initialize',
                '--admin', self.admin_public,
                '--tux-token', tux_token_id
            ]

            result = subprocess.run(init_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Farming contract initialization failed: {result.stderr}")
                return False

            print("✅ Farming contract initialized successfully!")
            print(f"   TUX Token: {tux_token_id}")
            print(f"   Admin: {self.admin_public}")
            return True

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def add_usdc_pool(self, farming_contract_id, usdc_token_id):
        """Add USDC pool to farming contract"""
        print(f"\n=== Adding USDC Pool ===")

        try:
            # Add USDC pool
            pool_cmd = [
                'soroban', 'contract', 'invoke',
                '--id', farming_contract_id,
                '--source', self.admin_secret,
                '--network-passphrase', self.network_passphrase,
                '--rpc-url', self.rpc_url,
                '--',
                'add_pool',
                '--admin', self.admin_public,
                '--pool-id', 'USDC',
                '--staking-token', usdc_token_id
            ]

            result = subprocess.run(pool_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ USDC pool creation failed: {result.stderr}")
                return False

            print("✅ USDC pool added successfully!")
            print(f"   Pool ID: USDC")
            print(f"   Staking Token: {usdc_token_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to add pool: {e}")
            return False

def main():
    print("🚀 TUX Contract Deployment Script (Soroban CLI)")
    print("=" * 50)

    # Check if required tools are available
    required_tools = ['stellar-secret-key', 'soroban']
    missing_tools = []

    for tool in required_tools:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode != 0:
            missing_tools.append(tool)

    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install stellar-cli and soroban-cli")
        return

    # Initialize deployer
    deployer = SorobanDeployer()

    # Contract WASM paths
    tux_wasm = "/home/ubuntu/blend-pools/target/wasm32-unknown-unknown/release/tux_token.wasm"
    farming_wasm = "/home/ubuntu/blend-pools/target/wasm32-unknown-unknown/release/tux_farming.wasm"

    # Deploy TUX Token
    tux_contract_id = deployer.deploy_contract(tux_wasm, "TUX Token")
    if not tux_contract_id:
        print("❌ TUX token deployment failed")
        return

    # Deploy Farming Contract
    farming_contract_id = deployer.deploy_contract(farming_wasm, "Farming Contract")
    if not farming_contract_id:
        print("❌ Farming contract deployment failed")
        return

    # Initialize TUX Token
    if not deployer.initialize_tux_token(tux_contract_id):
        print("❌ TUX token initialization failed")
        return

    # Initialize Farming Contract
    if not deployer.initialize_farming_contract(farming_contract_id, tux_contract_id):
        print("❌ Farming contract initialization failed")
        return

    # Add USDC Pool (using a testnet USDC token address)
    usdc_token_id = "GBXE4VMKQGYU7J4D2MHQH74U3Q7F6J3BQ4KILJL3E4I6K6F5E4J5G7E6"
    if not deployer.add_usdc_pool(farming_contract_id, usdc_token_id):
        print("❌ USDC pool creation failed")
        return

    # Save deployment info
    deployment_info = {
        "tux_token_contract": tux_contract_id,
        "farming_contract": farming_contract_id,
        "usdc_token": usdc_token_id,
        "admin_public_key": deployer.admin_public,
        "admin_secret_key": deployer.admin_secret,
        "network": "testnet",
        "timestamp": int(time.time()),
    }

    with open("tux_deployment_soroban.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("\n" + "=" * 50)
    print("🎉 Deployment Successful!")
    print(f"TUX Token Contract: {tux_contract_id}")
    print(f"Farming Contract: {farming_contract_id}")
    print(f"Admin Account: {deployer.admin_public}")
    print("Deployment info saved to tux_deployment_soroban.json")

    print("\n🎯 Ready for Demo!")
    print("You can now:")
    print("1. Test the TUX token contract")
    print("2. Stake USDC in the farming pool")
    print("3. Mint and distribute TUX rewards")
    print("4. Update the backend with contract addresses")

if __name__ == "__main__":
    main()