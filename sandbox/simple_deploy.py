#!/usr/bin/env python3
"""
Simple TUX Token Deployment Script using basic Stellar operations
"""

import os
import sys
import json
import time
import requests
from stellar_sdk import Server, Keypair, TransactionBuilder, scval
from stellar_sdk.asset import Asset
from stellar_sdk.operation import Payment, ChangeTrust, ManageSellOffer

# Network configuration
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"

class SimpleTokenDeployer:
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

    def create_tux_token_asset(self):
        """Create TUX token as a Stellar asset instead of smart contract"""
        print(f"\n=== Creating TUX Token Asset ===")

        try:
            # Create TUX token asset
            tux_asset = Asset("TUX", self.admin_keypair.public_key)

            print(f"✅ TUX Token Asset created!")
            print(f"   Asset Code: TUX")
            print(f"   Issuer: {self.admin_keypair.public_key}")
            print(f"   Asset Representation: {tux_asset}")

            return tux_asset

        except Exception as e:
            print(f"❌ Failed to create TUX token asset: {e}")
            return None

    def issue_tux_tokens(self, tux_asset, amount, recipient):
        """Issue TUX tokens to a recipient"""
        print(f"\n=== Issuing {amount} TUX tokens to {recipient} ===")

        try:
            # First, recipient needs to establish a trustline for TUX
            if recipient != self.admin_keypair.public_key:
                print(f"Note: Recipient {recipient} needs to establish a trustline for TUX token first")
                print(f"Trustline asset: TUX issued by {self.admin_keypair.public_key}")

            # Create payment transaction
            account = self.server.load_account(self.admin_keypair.public_key)

            payment_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_payment_op(
                    destination=recipient,
                    asset=tux_asset,
                    amount=str(amount)
                )
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            payment_tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(payment_tx)

            if response["successful"]:
                print(f"✅ Successfully issued {amount} TUX tokens to {recipient}")
                return True
            else:
                print(f"❌ Failed to issue tokens: {response}")
                return False

        except Exception as e:
            print(f"❌ Token issuance failed: {e}")
            return False

    def create_trustline_for_asset(self, asset, signer_keypair):
        """Create a trustline for an asset"""
        print(f"\n=== Creating trustline for {asset.code} ===")

        try:
            account = self.server.load_account(signer_keypair.public_key)

            change_trust_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_change_trust_op(
                    asset=asset,
                    limit="1000000000"  # Large limit
                )
                .set_timeout(30)
                .build()
            )

            change_trust_tx.sign(signer_keypair)
            response = self.server.submit_transaction(change_trust_tx)

            if response["successful"]:
                print(f"✅ Trustline created for {asset.code}")
                return True
            else:
                print(f"❌ Failed to create trustline: {response}")
                return False

        except Exception as e:
            print(f"❌ Trustline creation failed: {e}")
            return False

def main():
    print("🚀 Simple TUX Token Deployment (Stellar Asset)")
    print("=" * 50)

    # Initialize deployer
    deployer = SimpleTokenDeployer()

    # Create TUX token asset
    tux_asset = deployer.create_tux_token_asset()
    if not tux_asset:
        print("❌ TUX token creation failed")
        return

    # Issue some TUX tokens to the admin account
    initial_amount = 100_000_000.0  # 100M TUX tokens
    if not deployer.issue_tux_tokens(tux_asset, initial_amount, deployer.admin_keypair.public_key):
        print("❌ Initial token issuance failed")
        return

    # Create some additional test accounts and issue tokens
    test_accounts = []
    for i in range(3):
        test_keypair = Keypair.random()
        test_accounts.append(test_keypair)

        # Fund test account
        try:
            friendbot_url = f"https://friendbot.stellar.org?addr={test_keypair.public_key}"
            response = requests.get(friendbot_url)
            if response.status_code == 200:
                print(f"✅ Funded test account {i+1}: {test_keypair.public_key}")
            else:
                print(f"❌ Failed to fund test account {i+1}")
                continue
        except:
            print(f"❌ Failed to fund test account {i+1}")
            continue

    # Issue tokens to test accounts (note: they would need to create trustlines first)
    print(f"\n=== Test Account Info ===")
    for i, keypair in enumerate(test_accounts):
        print(f"Test Account {i+1}:")
        print(f"  Public Key: {keypair.public_key}")
        print(f"  Secret Key: {keypair.secret}")
        print(f"  To receive TUX: Create trustline for TUX:{deployer.admin_keypair.public_key}")

    # Save deployment info
    deployment_info = {
        "tux_token": {
            "asset_code": "TUX",
            "issuer": deployer.admin_keypair.public_key,
            "type": "stellar_asset"
        },
        "admin_public_key": deployer.admin_keypair.public_key,
        "admin_secret_key": deployer.admin_keypair.secret,
        "test_accounts": [
            {
                "public_key": kp.public_key,
                "secret_key": kp.secret
            } for kp in test_accounts
        ],
        "network": "testnet",
        "timestamp": int(time.time()),
        "initial_supply_issued": initial_amount
    }

    with open("tux_simple_deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("\n" + "=" * 50)
    print("🎉 Simple TUX Token Deployment Successful!")
    print(f"TUX Token Asset: TUX issued by {deployer.admin_keypair.public_key}")
    print(f"Admin Account: {deployer.admin_keypair.public_key}")
    print(f"Initial Supply: {initial_amount:,} TUX")
    print("Deployment info saved to tux_simple_deployment.json")

    print("\n🎯 Ready for Demo!")
    print("You can now:")
    print("1. Use TUX token as a Stellar asset")
    print("2. Distribute tokens to test accounts")
    print("3. Create trading offers on Stellar DEX")
    print("4. Update the backend with token info")
    print("\nNote: Recipients must create trustlines for TUX token first!")

if __name__ == "__main__":
    main()