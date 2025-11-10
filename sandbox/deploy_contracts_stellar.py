#!/usr/bin/env python3
"""
TUX Token and Farming Contract Deployment Script

This script deploys the TUX token and farming contracts to Stellar testnet.
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import stellar modules
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from stellar_sdk import (
    Keypair,
    Network,
    Server,
    TransactionBuilder,
    ContractClient,
    scval,
)
from stellar_sdk.contract import ContractClient
from stellar_sdk.exceptions import PrepareTransactionException
import requests

class TuxContractDeployer:
    def __init__(self):
        # Network configuration
        self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
        self.horizon_url = "https://horizon-testnet.stellar.org"
        self.rpc_url = "https://soroban-testnet.stellar.org"

        # Initialize server and RPC client
        self.server = Server(horizon_url=self.horizon_url)

        # Admin keypair (for deployment)
        self.admin_secret = os.getenv("ADMIN_SECRET_KEY")
        if not self.admin_secret:
            # Generate new admin key if not provided
            self.admin_keypair = Keypair.random()
            self.admin_secret = self.admin_keypair.secret
            print(f"Generated new admin keypair:")
            print(f"Public Key: {self.admin_keypair.public_key}")
            print(f"Secret Key: {self.admin_keypair.secret}")
            print("Save this secret key for future use!")
        else:
            self.admin_keypair = Keypair.from_secret(self.admin_secret)

        # Ensure admin account is funded
        self.ensure_account_funded(self.admin_keypair)

        print(f"Admin account: {self.admin_keypair.public_key}")

    def ensure_account_funded(self, keypair):
        """Ensure the account exists on testnet using friendbot"""
        try:
            account = self.server.load_account(keypair.public_key)
            print(f"Account already exists: {account.account_id}")
            return
        except:
            print(f"Funding account {keypair.public_key} using friendbot...")
            friendbot_url = f"https://friendbot.stellar.org?addr={keypair.public_key}"
            response = requests.get(friendbot_url)

            if response.status_code == 200:
                print("Account successfully funded!")
            else:
                raise Exception(f"Failed to fund account: {response.text}")

    def deploy_contract(self, wasm_file_path):
        """Deploy a contract to the network"""
        print(f"Deploying contract from {wasm_file_path}")

        # Read WASM file
        with open(wasm_file_path, "rb") as f:
            contract_wasm = f.read()

        # Create upload transaction
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
            print(f"Contract WASM uploaded successfully! ID: {wasm_id}")
            return wasm_id
        else:
            raise Exception(f"Failed to upload contract WASM: {response}")

    def create_contract(self, wasm_id):
        """Create a contract instance from uploaded WASM"""
        account = self.server.load_account(self.admin_keypair.public_key)

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

        create_tx.sign(self.admin_keypair)
        response = self.server.submit_transaction(create_tx)

        if response["successful"]:
            contract_id = response["result"]["id"]
            print(f"Contract created successfully! ID: {contract_id}")
            return contract_id
        else:
            raise Exception(f"Failed to create contract: {response}")

    def initialize_tux_token(self, contract_id):
        """Initialize the TUX token contract"""
        print(f"Initializing TUX token contract: {contract_id}")

        # Contract parameters
        name = "Tuxedo Token"
        symbol = "TUX"
        decimals = 7
        total_supply = 100_000_000 * (10 ** decimals)  # 100M TUX with 7 decimals

        # Use admin as initial recipient for simplicity
        recipient = self.admin_keypair.public_key

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Create contract client
            contract_client = ContractClient(
                contract_id=contract_id,
                client=self.server,
            )

            # Prepare initialize transaction
            tx = contract_client.invoke(
                function="initialize",
                args=[
                    scval.to_address(self.admin_keypair.public_key),
                    scval.to_string(name),
                    scval.to_string(symbol),
                    scval.to_uint32(decimals),
                    scval.to_int128(total_supply),
                    scval.to_address(recipient),
                ]
            )

            # Build and sign transaction
            invoke_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_invoke_contract_op(tx)
                .set_timeout(30)
                .build()
            )

            invoke_tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(invoke_tx)

            if response["successful"]:
                print("TUX token contract initialized successfully!")
                print(f"Name: {name}")
                print(f"Symbol: {symbol}")
                print(f"Total Supply: {total_supply}")
                print(f"Initial recipient: {recipient}")
                return True
            else:
                print(f"Failed to initialize TUX token: {response}")
                return False

        except Exception as e:
            print(f"Error initializing TUX token: {e}")
            return False

    def initialize_farming_contract(self, contract_id, tux_token_id):
        """Initialize the farming contract"""
        print(f"Initializing farming contract: {contract_id}")

        # Contract parameters
        reward_rate = 100  # 100 TUX per second
        current_time = int(time.time())
        start_time = current_time  # Start immediately
        end_time = current_time + (365 * 24 * 60 * 60)  # Run for 1 year

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Create contract client
            contract_client = ContractClient(
                contract_id=contract_id,
                client=self.server,
            )

            # Prepare initialize transaction
            tx = contract_client.invoke(
                function="initialize",
                args=[
                    scval.to_address(self.admin_keypair.public_key),
                    scval.to_address(tux_token_id),
                    scval.to_uint128(reward_rate),
                    scval.to_uint64(start_time),
                    scval.to_uint64(end_time),
                ]
            )

            # Build and sign transaction
            invoke_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_invoke_contract_op(tx)
                .set_timeout(30)
                .build()
            )

            invoke_tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(invoke_tx)

            if response["successful"]:
                print("Farming contract initialized successfully!")
                print(f"TUX Token: {tux_token_id}")
                print(f"Reward Rate: {reward_rate} TUX/second")
                print(f"Start Time: {start_time}")
                print(f"End Time: {end_time}")
                return True
            else:
                print(f"Failed to initialize farming contract: {response}")
                return False

        except Exception as e:
            print(f"Error initializing farming contract: {e}")
            return False

    def add_farming_pool(self, contract_id, pool_id, staking_token_address):
        """Add a pool to the farming contract"""
        print(f"Adding pool {pool_id} to farming contract")

        allocation_points = 100  # Standard allocation points

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Create contract client
            contract_client = ContractClient(
                contract_id=contract_id,
                client=self.server,
            )

            # Prepare add_pool transaction
            tx = contract_client.invoke(
                function="add_pool",
                args=[
                    scval.to_address(self.admin_keypair.public_key),
                    scval.to_symbol(pool_id),
                    scval.to_address(staking_token_address),
                    scval.to_uint64(allocation_points),
                ]
            )

            # Build and sign transaction
            invoke_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_invoke_contract_op(tx)
                .set_timeout(30)
                .build()
            )

            invoke_tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(invoke_tx)

            if response["successful"]:
                print(f"Pool {pool_id} added successfully!")
                return True
            else:
                print(f"Failed to add pool: {response}")
                return False

        except Exception as e:
            print(f"Error adding pool: {e}")
            return False

    def deploy_all_contracts(self):
        """Deploy all contracts and set up initial configuration"""
        print("Starting TUX contract deployment process...")

        # Build contracts first
        print("Building contracts...")
        self.build_contracts()

        # Deploy TUX Token
        print("\n=== Deploying TUX Token ===")
        tux_wasm_id = self.deploy_contract("contracts/token/target/wasm32-unknown-unknown/release/tux-token.wasm")
        tux_contract_id = self.create_contract(tux_wasm_id)

        if self.initialize_tux_token(tux_contract_id):
            print(f"✅ TUX Token deployed successfully: {tux_contract_id}")
        else:
            print("❌ Failed to initialize TUX token")
            return

        # Deploy Farming Contract
        print("\n=== Deploying Farming Contract ===")
        farming_wasm_id = self.deploy_contract("contracts/farming/target/wasm32-unknown-unknown/release/tux-farming.wasm")
        farming_contract_id = self.create_contract(farming_wasm_id)

        if self.initialize_farming_contract(farming_contract_id, tux_contract_id):
            print(f"✅ Farming contract deployed successfully: {farming_contract_id}")
        else:
            print("❌ Failed to initialize farming contract")
            return

        # Save deployment info
        deployment_info = {
            "tux_token_contract": tux_contract_id,
            "farming_contract": farming_contract_id,
            "admin_public_key": self.admin_keypair.public_key,
            "network": "testnet",
            "timestamp": int(time.time()),
        }

        with open("contracts/deployment.json", "w") as f:
            import json
            json.dump(deployment_info, f, indent=2)

        print("\n=== Deployment Summary ===")
        print(f"TUX Token Contract: {tux_contract_id}")
        print(f"Farming Contract: {farming_contract_id}")
        print(f"Admin Account: {self.admin_keypair.public_key}")
        print(f"Network: Testnet")
        print("\nDeployment info saved to contracts/deployment.json")
        print("✅ All contracts deployed successfully!")

    def build_contracts(self):
        """Build the Rust contracts"""
        import subprocess

        print("Building TUX token contract...")
        result = subprocess.run(
            ["cargo", "build", "--release", "--target", "wasm32-unknown-unknown"],
            cwd="contracts/token",
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Failed to build TUX token contract: {result.stderr}")

        print("Building farming contract...")
        result = subprocess.run(
            ["cargo", "build", "--release", "--target", "wasm32-unknown-unknown"],
            cwd="contracts/farming",
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Failed to build farming contract: {result.stderr}")

if __name__ == "__main__":
    deployer = TuxContractDeployer()
    deployer.deploy_all_contracts()