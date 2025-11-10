#!/usr/bin/env python3
"""
Working Manual Payment Test - Uses Friendbot to fund account first
"""

import os
import sys
import asyncio
import json
import requests
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stellar_sdk import Server, TransactionBuilder
from stellar_sdk.keypair import Keypair

class WorkingManualPaymentTest:
    """Working manual payment test with proper account funding"""

    def __init__(self):
        self.network = "testnet"
        self.horizon_url = "https://horizon-testnet.stellar.org"
        self.network_passphrase = "Test SDF Network ; September 2015"
        self.friendbot_url = "https://friendbot.stellar.org"
        self.server = Server(self.horizon_url)

        # Test configuration
        self.vault_address = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
        self.deposit_amount_xlm = 1.0

        # Generate test account
        self.test_account = Keypair.random()
        print(f"🔑 Test account: {self.test_account.public_key}")

    def fund_account(self):
        """Fund account using Friendbot"""
        try:
            print("💰 Funding account via Friendbot...")
            response = requests.post(
                self.friendbot_url,
                params={"addr": self.test_account.public_key}
            )

            if response.status_code == 200:
                print("✅ Account funded successfully!")
                return True
            else:
                print(f"❌ Friendbot failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Funding error: {e}")
            return False

    def check_balance(self):
        """Check account balance"""
        try:
            account = self.server.load_account(self.test_account.public_key)
            xlm_balance = 0.0

            for balance in account.balances:
                if balance.asset_type == "native":
                    xlm_balance = float(balance.balance)
                    break

            print(f"💰 Account balance: {xlm_balance} XLM")
            return xlm_balance

        except Exception as e:
            print(f"❌ Balance check error: {e}")
            return 0.0

    def execute_manual_payment(self):
        """Execute manual payment to vault"""
        try:
            print(f"💰 Sending {self.deposit_amount_xlm} XLM to vault...")
            print(f"   To: {self.vault_address}")
            print(f"   Memo: 'Deposit to DeFindex Vault'")

            # Load account
            account = self.server.load_account(self.test_account.public_key)

            # Build transaction
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100
                )
                .add_text_memo("Deposit to DeFindex Vault")
                .append_payment_op(
                    destination=self.vault_address,
                    amount=str(self.deposit_amount_xlm),
                    asset_code="XLM"
                )
                .set_timeout(30)
                .build()
            )

            # Sign transaction
            transaction.sign(self.test_account)

            # Submit transaction
            response = self.server.submit_transaction(transaction)

            if response.get("successful"):
                print(f"✅ Payment successful!")
                print(f"   Hash: {response.get('hash')}")
                print(f"   Ledger: {response.get('ledger')}")
                return response.get("hash")
            else:
                print(f"❌ Payment failed: {response.get('error_result_xdr', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"❌ Payment error: {e}")
            return None

    def verify_transaction(self, tx_hash):
        """Verify transaction on blockchain"""
        try:
            print("🔍 Verifying transaction...")
            tx = self.server.transactions().get(tx_hash)

            if tx.successful:
                print(f"✅ Transaction verified: {tx.status}")
                return True
            else:
                print(f"❌ Transaction failed: {tx.status}")
                return False

        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False

    async def run_test(self):
        """Run complete test"""
        print("🚀 Starting Working Manual Payment Test")
        print("=" * 50)

        # Step 1: Fund account
        print("\n1️⃣ Funding Account...")
        if not self.fund_account():
            return False

        # Wait for funding to process
        await asyncio.sleep(3)

        # Step 2: Check balance
        print("\n2️⃣ Checking Balance...")
        balance = self.check_balance()
        if balance < (self.deposit_amount_xlm + 0.5):
            print(f"❌ Insufficient balance: {balance} XLM")
            return False

        # Step 3: Execute payment
        print("\n3️⃣ Executing Manual Payment...")
        tx_hash = self.execute_manual_payment()
        if not tx_hash:
            return False

        # Wait for transaction processing
        await asyncio.sleep(5)

        # Step 4: Verify transaction
        print("\n4️⃣ Verifying Transaction...")
        verification = self.verify_transaction(tx_hash)
        if not verification:
            return False

        # Success!
        print("\n" + "=" * 50)
        print("✅ MANUAL PAYMENT TEST SUCCESSFUL!")
        print("=" * 50)
        print("🎯 Manual XLM payment method works perfectly!")
        print(f"📝 Transaction Hash: {tx_hash}")
        print(f"💰 Amount: {self.deposit_amount_xlm} XLM")
        print(f"🏦 Vault: {self.vault_address}")

        return True

async def main():
    tester = WorkingManualPaymentTest()
    success = await tester.run_test()

    if success:
        print("\n🚀 PRODUCTION READY!")
        print("Manual XLM payment method is verified and ready for production implementation.")
    else:
        print("\n❌ TEST FAILED")
        print("Manual payment method needs investigation.")

    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)