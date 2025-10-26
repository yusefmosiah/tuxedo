#!/usr/bin/env python3
"""
Simplified TUX Contract Deployment Script
"""

import os
import sys
import json
import time
import requests
from stellar_sdk import Server, Keypair, TransactionBuilder, scval
from stellar_sdk.contract import ContractClient

# Network configuration
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"

class SimpleDeployer:
    def __init__(self):
        self.server = Server(horizon_url=HORIZON_URL)
        self.network_passphrase = NETWORK_PASSPHRASE

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

    def deploy_contract_from_wasm(self, wasm_file_path, contract_name):
        """Deploy a contract from WASM file"""
        print(f"\n=== Deploying {contract_name} ===")

        # Read WASM file
        try:
            with open(wasm_file_path, "rb") as f:
                contract_wasm = f.read()
            print(f"✅ Read WASM file: {wasm_file_path} ({len(contract_wasm)} bytes)")
        except Exception as e:
            print(f"❌ Failed to read WASM file: {e}")
            return None

        # Create upload transaction
        try:
            account = self.server.load_account(self.admin_keypair.public_key)

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

                # Create contract instance
                create_tx = (
                    TransactionBuilder(
                        source_account=self.server.load_account(self.admin_keypair.public_key),
                        network_passphrase=self.network_passphrase,
                        base_fee=100,
                    )
                    .append_create_contract_op(wasm_id)
                    .set_timeout(30)
                    .build()
                )

                create_tx.sign(self.admin_keypair)
                response = self.server.submit_transaction(create_tx)

                if response["successful"]:
                    contract_id = response["result"]["id"]
                    print(f"✅ {contract_name} deployed successfully!")
                    print(f"   Contract ID: {contract_id}")
                    return contract_id
                else:
                    print(f"❌ Failed to create contract: {response}")
                    return None
            else:
                print(f"❌ Failed to upload WASM: {response}")
                return None

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return None

    def initialize_tux_token(self, contract_id):
        """Initialize TUX token contract"""
        print(f"\n=== Initializing TUX Token ===")

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Prepare initialization transaction
            tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_invoke_contract_op(
                    contract_id=contract_id,
                    function_name="initialize",
                    args=[
                        scval.to_address(self.admin_keypair.public_key),
                        scval.to_int128(100_000_000 * 10_000_000), # 100M TUX with 7 decimals
                    ]
                )
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(tx)

            if response["successful"]:
                print("✅ TUX token initialized successfully!")
                print(f"   Total Supply: 100,000,000 TUX")
                print(f"   Admin: {self.admin_keypair.public_key}")
                return True
            else:
                print(f"❌ Failed to initialize TUX token: {response}")
                return False

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def initialize_farming_contract(self, contract_id, tux_token_id):
        """Initialize farming contract"""
        print(f"\n=== Initializing Farming Contract ===")

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Prepare initialization transaction
            tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_invoke_contract_op(
                    contract_id=contract_id,
                    function_name="initialize",
                    args=[
                        scval.to_address(self.admin_keypair.public_key),
                        scval.to_address(tux_token_id),
                    ]
                )
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(tx)

            if response["successful"]:
                print("✅ Farming contract initialized successfully!")
                print(f"   TUX Token: {tux_token_id}")
                print(f"   Admin: {self.admin_keypair.public_key}")
                return True
            else:
                print(f"❌ Failed to initialize farming contract: {response}")
                return False

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def add_usdc_pool(self, farming_contract_id, usdc_token_id):
        """Add USDC pool to farming contract"""
        print(f"\n=== Adding USDC Pool ===")

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Prepare add_pool transaction
            tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_invoke_contract_op(
                    contract_id=farming_contract_id,
                    function_name="add_pool",
                    args=[
                        scval.to_address(self.admin_keypair.public_key),
                        scval.to_symbol("USDC"),
                        scval.to_address(usdc_token_id),
                    ]
                )
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(tx)

            if response["successful"]:
                print("✅ USDC pool added successfully!")
                print(f"   Pool ID: USDC")
                print(f"   Staking Token: {usdc_token_id}")
                return True
            else:
                print(f"❌ Failed to add USDC pool: {response}")
                return False

        except Exception as e:
            print(f"❌ Failed to add pool: {e}")
            return False

    def distribute_tux_tokens(self, tux_token_id, recipients):
        """Distribute TUX tokens to recipients"""
        print(f"\n=== Distributing TUX Tokens ===")

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            for recipient, amount in recipients:
                print(f"Sending {amount:,} TUX to {recipient}")

                # Prepare mint transaction
                tx = (
                    TransactionBuilder(
                        source_account=account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100,
                    )
                    .append_invoke_contract_op(
                        contract_id=tux_token_id,
                        function_name="mint",
                        args=[
                            scval.to_address(self.admin_keypair.public_key),
                            scval.to_address(recipient),
                            scval.to_int128(amount),
                        ]
                    )
                    .set_timeout(30)
                    .build()
                )

                # Sign and submit
                tx.sign(self.admin_keypair)
                response = self.server.submit_transaction(tx)

                if response["successful"]:
                    print(f"   ✅ Sent {amount:,} TUX to {recipient}")
                else:
                    print(f"   ❌ Failed to send to {recipient}: {response}")

                # Small delay to avoid rate limiting
                time.sleep(1)

            return True

        except Exception as e:
            print(f"❌ Token distribution failed: {e}")
            return False

def main():
    print("🚀 TUX Contract Deployment Script")
    print("=" * 50)

    # Initialize deployer
    deployer = SimpleDeployer()

    # Deploy contracts
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
        "network": "testnet",
        "timestamp": int(time.time()),
    }

    with open("tux_deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("\n" + "=" * 50)
    print("🎉 Deployment Successful!")
    print(f"TUX Token Contract: {tux_contract_id}")
    print(f"Farming Contract: {farming_contract_id}")
    print(f"Admin Account: {deployer.admin_keypair.public_key}")
    print("Deployment info saved to tux_deployment.json")

    # Distribute some demo tokens
    print("\n" + "=" * 50)
    print("🪙 Distributing Demo TUX Tokens")

    demo_recipients = [
        (deployer.admin_keypair.public_key, 10_000_000 * 10_000_000), # 10M TUX to admin
        # Add more recipients as needed
    ]

    if deployer.distribute_tux_tokens(tux_contract_id, demo_recipients):
        print("✅ Demo token distribution completed!")

    print("\n🎯 Ready for Demo!")
    print("You can now:")
    print("1. Test the TUX token contract")
    print("2. Stake USDC in the farming pool")
    print("3. Mint and distribute TUX rewards")
    print("4. Update the backend with contract addresses")

if __name__ == "__main__":
    main()