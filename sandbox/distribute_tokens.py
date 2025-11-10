#!/usr/bin/env python3
"""
Distribute TUX tokens to test accounts
"""

import os
import sys
import json
import requests
from stellar_sdk import Server, Keypair, TransactionBuilder, Asset
from stellar_sdk.operation import ChangeTrust, Payment

# Load deployment info
with open('tux_simple_deployment.json', 'r') as f:
    deployment_info = json.load(f)

# Network configuration
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"

class TokenDistributor:
    def __init__(self):
        self.server = Server(horizon_url=HORIZON_URL)
        self.network_passphrase = NETWORK_PASSPHRASE

        # Load admin credentials
        self.admin_keypair = Keypair.from_secret(deployment_info['admin_secret_key'])
        self.tux_asset = Asset(
            deployment_info['tux_token']['asset_code'],
            deployment_info['tux_token']['issuer']
        )

        print(f"Admin account: {self.admin_keypair.public_key}")
        print(f"TUX Token: {self.tux_asset}")

    def create_trustline(self, recipient_keypair):
        """Create trustline for TUX token for recipient"""
        print(f"\n=== Creating trustline for {recipient_keypair.public_key} ===")

        try:
            account = self.server.load_account(recipient_keypair.public_key)

            # Change trust operation
            change_trust_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_change_trust_op(
                    asset=self.tux_asset,
                    limit="100000000"  # 100M TUX limit
                )
                .set_timeout(30)
                .build()
            )

            # Sign with recipient's key
            change_trust_tx.sign(recipient_keypair)
            response = self.server.submit_transaction(change_trust_tx)

            if response["successful"]:
                print(f"✅ Trustline created for {recipient_keypair.public_key}")
                return True
            else:
                print(f"❌ Failed to create trustline: {response}")
                return False

        except Exception as e:
            print(f"❌ Trustline creation failed: {e}")
            return False

    def issue_tokens(self, recipient_public, amount):
        """Issue TUX tokens to recipient"""
        print(f"\n=== Issuing {amount} TUX to {recipient_public} ===")

        try:
            account = self.server.load_account(self.admin_keypair.public_key)

            # Payment operation
            payment_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_payment_op(
                    destination=recipient_public,
                    asset=self.tux_asset,
                    amount=str(amount)
                )
                .set_timeout(30)
                .build()
            )

            # Sign with admin key
            payment_tx.sign(self.admin_keypair)
            response = self.server.submit_transaction(payment_tx)

            if response["successful"]:
                print(f"✅ Successfully issued {amount} TUX to {recipient_public}")
                return True
            else:
                print(f"❌ Failed to issue tokens: {response}")
                return False

        except Exception as e:
            print(f"❌ Token issuance failed: {e}")
            return False

    def distribute_to_all_accounts(self):
        """Distribute tokens to all test accounts"""
        print("🚀 Distributing TUX tokens to test accounts")
        print("=" * 50)

        # Amount to distribute to each account
        distribution_amount = 10_000_000  # 10M TUX per account

        successful_distributions = []

        for test_account in deployment_info['test_accounts']:
            recipient_keypair = Keypair.from_secret(test_account['secret_key'])

            # Step 1: Create trustline
            if self.create_trustline(recipient_keypair):
                # Step 2: Issue tokens
                if self.issue_tokens(recipient_keypair.public_key, distribution_amount):
                    successful_distributions.append({
                        'public_key': recipient_keypair.public_key,
                        'amount': distribution_amount
                    })
                else:
                    print(f"❌ Failed to issue tokens to {recipient_keypair.public_key}")
            else:
                print(f"❌ Failed to create trustline for {recipient_keypair.public_key}")

        # Update deployment info
        deployment_info['token_distributions'] = successful_distributions
        deployment_info['distribution_timestamp'] = int(time.time())

        with open('tux_simple_deployment.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)

        print("\n" + "=" * 50)
        print("🎉 Token Distribution Complete!")
        print(f"Successfully distributed tokens to {len(successful_distributions)} accounts")

        for dist in successful_distributions:
            print(f"  {dist['public_key']}: {dist['amount']:,} TUX")

        return successful_distributions

    def check_balances(self):
        """Check TUX token balances for all accounts"""
        print("\n🔍 Checking TUX Token Balances")
        print("=" * 30)

        accounts_to_check = [deployment_info['admin_public_key']] + \
                           [acc['public_key'] for acc in deployment_info['test_accounts']]

        for account_id in accounts_to_check:
            try:
                # Try to get balance for TUX token
                account = self.server.load_account(account_id)
                tux_balance = 0

                for balance in account.balances:
                    if (balance.asset_code == 'TUX' and
                        balance.asset_issuer == deployment_info['tux_token']['issuer']):
                        tux_balance = float(balance.balance)
                        break

                account_type = "Admin" if account_id == deployment_info['admin_public_key'] else "Test"
                print(f"{account_type} Account {account_id}:")
                print(f"  TUX Balance: {tux_balance:,}")

            except Exception as e:
                print(f"Failed to check balance for {account_id}: {e}")

import time

def main():
    distributor = TokenDistributor()

    # Distribute tokens to all test accounts
    successful_distributions = distributor.distribute_to_all_accounts()

    if successful_distributions:
        # Check final balances
        distributor.check_balances()

        print(f"\n🎯 Demo Ready!")
        print("Test accounts with TUX tokens:")
        for i, test_account in enumerate(deployment_info['test_accounts']):
            print(f"  Test Account {i+1}: {test_account['public_key']}")
            print(f"    Secret: {test_account['secret_key']}")
            print(f"    TUX Balance: Check with wallet")
    else:
        print("❌ No successful token distributions")

if __name__ == "__main__":
    main()