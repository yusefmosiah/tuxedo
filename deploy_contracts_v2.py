#!/usr/bin/env python3
"""
Simplified TUX Contract Deployment Script using Stellar SDK with Soroban support
"""

import os
import sys
import json
import time
import requests
from stellar_sdk import Server, Keypair, TransactionBuilder, scval
from stellar_sdk.contract import ContractClient
from stellar_sdk.xdr import TransactionResult, TransactionMeta

# Network configuration
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"
RPC_URL = "https://soroban-testnet.stellar.org"

class SorobanDeployer:
    def __init__(self):
        self.server = Server(horizon_url=HORIZON_URL)
        self.network_passphrase = NETWORK_PASSPHRASE
        self.rpc_url = RPC_URL

        # Get admin key from environment or generate new
        admin_secret = os.getenv("ADMIN_SECRET_KEY")
        if admin_secret:
            self.admin_keypair = Keypair.from_secret(admin_secret)
            print(f"Using existing admin account: {self.admin_keypair.public_key}")
        else:
            self.admin_keypair = Keypair.random()
            print(f"Generated new admin account:")
            print(f"Public Key: {self.admin_keypair.public_key}")
            print(f"Secret Key: {self.admin_keypair.secret}")
            print("IMPORTANT: Save this secret key for future use!")

        # Ensure account is funded
        self.ensure_account_funded(self.admin_keypair)

    def ensure_account_funded(self, keypair):
        """Ensure account exists on testnet using friendbot"""
        try:
            self.server.load_account(keypair.public_key)
            print(f"Account {keypair.public_key} already exists")
            return
        except:
            print(f"Funding account {keypair.public_key} using friendbot...")
            friendbot_url = f"https://friendbot.stellar.org?addr={keypair.public_key}"
            response = requests.get(friendbot_url)

            if response.status_code == 200:
                print("Account successfully funded!")
            else:
                raise Exception(f"Failed to fund account: {response.text}")

    def upload_contract_wasm(self, wasm_file_path):
        """Upload contract WASM to the network"""
        print(f"\n=== Uploading WASM from {wasm_file_path} ===")

        # Read WASM file
        try:
            with open(wasm_file_path, "rb") as f:
                contract_wasm = f.read()
            print(f"✅ Read WASM file: {wasm_file_path} ({len(contract_wasm)} bytes)")
        except Exception as e:
            print(f"❌ Failed to read WASM file: {e}")
            return None

        # Create upload transaction using the proper format
        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Build transaction with Soroban upload contract operation
            upload_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_upload_contract_wasm_op(contract_wasm)
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            upload_tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(upload_tx)

            if response["successful"]:
                wasm_id = response["result"]["wasm_id"]
                print(f"✅ Contract WASM uploaded successfully!")
                print(f"   WASM ID: {wasm_id}")
                return wasm_id
            else:
                print(f"❌ Failed to upload WASM: {response}")
                return None

        except Exception as e:
            print(f"❌ WASM upload failed: {e}")
            return None

    def create_contract_instance(self, wasm_id):
        """Create contract instance from uploaded WASM"""
        print(f"\n=== Creating Contract Instance ===")

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Build transaction with create contract operation
            create_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_create_contract_op(wasm_id)
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            create_tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(create_tx)

            if response["successful"]:
                contract_id = response["result"]["id"]
                print(f"✅ Contract instance created successfully!")
                print(f"   Contract ID: {contract_id}")
                return contract_id
            else:
                print(f"❌ Failed to create contract: {response}")
                return None

        except Exception as e:
            print(f"❌ Contract creation failed: {e}")
            return None

    def deploy_contract_from_wasm(self, wasm_file_path, contract_name):
        """Deploy a contract from WASM file"""
        print(f"\n=== Deploying {contract_name} ===")

        # Upload WASM
        wasm_id = self.upload_contract_wasm(wasm_file_path)
        if not wasm_id:
            return None

        # Create contract instance
        contract_id = self.create_contract_instance(wasm_id)
        if not contract_id:
            return None

        print(f"✅ {contract_name} deployed successfully!")
        print(f"   Contract ID: {contract_id}")
        return contract_id

    def invoke_contract_function(self, contract_id, function_name, args=None):
        """Invoke a function on a deployed contract"""
        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Build invoke contract operation
            op_kwargs = {
                "contract_id": contract_id,
                "function_name": function_name,
            }

            if args:
                op_kwargs["args"] = args

            # Create transaction
            tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_invoke_contract_op(**op_kwargs)
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(tx)

            if response["successful"]:
                print(f"✅ Function {function_name} invoked successfully!")
                if "result" in response and "return_value" in response["result"]:
                    print(f"   Return value: {response['result']['return_value']}")
                return True
            else:
                print(f"❌ Failed to invoke {function_name}: {response}")
                return False

        except Exception as e:
            print(f"❌ Function invocation failed: {e}")
            return False

    def initialize_tux_token(self, contract_id):
        """Initialize TUX token contract"""
        print(f"\n=== Initializing TUX Token ===")

        args = [
            scval.to_address(self.admin_keypair.public_key),
            scval.to_int128(100_000_000 * 10_000_000), # 100M TUX with 7 decimals
        ]

        return self.invoke_contract_function(contract_id, "initialize", args)

    def initialize_farming_contract(self, contract_id, tux_token_id):
        """Initialize farming contract"""
        print(f"\n=== Initializing Farming Contract ===")

        args = [
            scval.to_address(self.admin_keypair.public_key),
            scval.to_address(tux_token_id),
        ]

        return self.invoke_contract_function(contract_id, "initialize", args)

    def add_usdc_pool(self, farming_contract_id, usdc_token_id):
        """Add USDC pool to farming contract"""
        print(f"\n=== Adding USDC Pool ===")

        args = [
            scval.to_address(self.admin_keypair.public_key),
            scval.to_symbol("USDC"),
            scval.to_address(usdc_token_id),
        ]

        return self.invoke_contract_function(farming_contract_id, "add_pool", args)

def main():
    print("🚀 TUX Contract Deployment Script v2")
    print("=" * 50)

    # Initialize deployer
    deployer = SorobanDeployer()

    # Contract WASM paths
    tux_wasm = "/home/ubuntu/blend-pools/target/wasm32-unknown-unknown/release/tux_token.wasm"
    farming_wasm = "/home/ubuntu/blend-pools/target/wasm32-unknown-unknown/release/tux_farming.wasm"

    # Deploy TUX Token
    tux_contract_id = deployer.deploy_contract_from_wasm(tux_wasm, "TUX Token")
    if not tux_contract_id:
        print("❌ TUX token deployment failed")
        return

    # Deploy Farming Contract
    farming_contract_id = deployer.deploy_contract_from_wasm(farming_wasm, "Farming Contract")
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
        "admin_public_key": deployer.admin_keypair.public_key,
        "admin_secret_key": deployer.admin_keypair.secret,
        "network": "testnet",
        "timestamp": int(time.time()),
    }

    with open("tux_deployment_v2.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("\n" + "=" * 50)
    print("🎉 Deployment Successful!")
    print(f"TUX Token Contract: {tux_contract_id}")
    print(f"Farming Contract: {farming_contract_id}")
    print(f"Admin Account: {deployer.admin_keypair.public_key}")
    print("Deployment info saved to tux_deployment_v2.json")

    print("\n🎯 Ready for Demo!")
    print("You can now:")
    print("1. Test the TUX token contract")
    print("2. Stake USDC in the farming pool")
    print("3. Mint and distribute TUX rewards")
    print("4. Update the backend with contract addresses")

if __name__ == "__main__":
    main()