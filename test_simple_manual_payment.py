#!/usr/bin/env python3
"""
Simple Manual Payment Test for DeFindex Vaults
Focuses on testing the core manual payment functionality
"""

import os
import sys
import asyncio
import json
import time
import requests
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stellar_sdk import Server, TransactionBuilder
from stellar_sdk.keypair import Keypair
from stellar_sdk.exceptions import NotFoundError

class SimpleManualPaymentTest:
    """Simple test for manual payment method"""

    def __init__(self):
        self.network = "testnet"
        self.horizon_url = "https://horizon-testnet.stellar.org"
        self.network_passphrase = "Test SDF Network ; September 2015"
        self.friendbot_url = "https://friendbot.stellar.org"
        self.server = Server(self.horizon_url)

        # Test configuration - use known working vault
        self.vault_address = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
        self.deposit_amount_xlm = 1.0

        # Generate a new test account
        self.test_account = Keypair.random()

        self.results = {
            "test_type": "Simple Manual Payment Test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vault_address": self.vault_address,
            "deposit_amount": self.deposit_amount_xlm,
            "account": self.test_account.public_key,
            "phases": {}
        }

    async def check_account_balance(self):
        """Check current account balance"""
        try:
            account = self.server.load_account(self.test_account.public_key)
            xlm_balance = 0.0

            for balance in account.balances:
                if balance.asset_type == "native":
                    xlm_balance = float(balance.balance)
                    break

            return {
                "success": True,
                "balance_xlm": xlm_balance,
                "sequence": account.sequence
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_manual_payment(self):
        """Execute manual XLM payment to vault"""
        print("💰 Executing manual XLM payment to vault...")

        try:
            # Load account
            account = self.server.load_account(self.test_account.public_key)

            # Build payment transaction
            print(f"   Amount: {self.deposit_amount_xlm} XLM")
            print(f"   To: {self.vault_address}")
            print(f"   Memo: 'Deposit to DeFindex Vault'")

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
            print("   Submitting transaction...")
            response = self.server.submit_transaction(transaction)

            if response.get("successful"):
                result = {
                    "success": True,
                    "transaction_hash": response.get("hash"),
                    "ledger": response.get("ledger"),
                    "message": "Manual payment successful"
                }
                print(f"   ✅ Success! Hash: {response.get('hash')}")
                return result
            else:
                result = {
                    "success": False,
                    "error": response.get("error_result_xdr", "Unknown error"),
                    "message": "Transaction failed"
                }
                print(f"   ❌ Failed: {result['error']}")
                return result

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": "Exception occurred"
            }
            print(f"   ❌ Exception: {e}")
            return result

    async def verify_transaction(self, tx_hash):
        """Verify transaction on blockchain"""
        print("🔍 Verifying transaction on blockchain...")

        try:
            # Wait a moment for processing
            await asyncio.sleep(5)

            # Get transaction details
            tx = self.server.transactions().get(tx_hash)

            result = {
                "success": tx.successful,
                "status": tx.status,
                "ledger": tx.ledger,
                "created_at": tx.created_at,
                "memo": tx.memo
            }

            if tx.successful:
                print(f"   ✅ Verified: {tx.status}")
            else:
                print(f"   ❌ Failed: {tx.status}")

            return result

        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ Verification error: {e}")
            return result

    async def run_test(self):
        """Run complete test"""
        print("🚀 Starting Simple Manual Payment Test")
        print("=" * 50)

        # Phase 1: Check account
        print("\n📊 Phase 1: Account Check")
        balance_check = await self.check_account_balance()
        self.results["phases"]["account_check"] = balance_check

        if not balance_check["success"]:
            print(f"   ❌ Account check failed: {balance_check['error']}")
            return False

        print(f"   ✅ Account balance: {balance_check['balance_xlm']} XLM")

        if balance_check["balance_xlm"] < (self.deposit_amount_xlm + 0.5):
            print(f"   ❌ Insufficient balance for deposit")
            return False

        # Phase 2: Execute payment
        print("\n💰 Phase 2: Manual Payment")
        payment_result = await self.execute_manual_payment()
        self.results["phases"]["manual_payment"] = payment_result

        if not payment_result["success"]:
            print(f"   ❌ Manual payment failed: {payment_result['error']}")
            return False

        # Phase 3: Verify transaction
        print("\n🔍 Phase 3: Transaction Verification")
        verification_result = await self.verify_transaction(payment_result["transaction_hash"])
        self.results["phases"]["verification"] = verification_result

        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST COMPLETE")
        print("=" * 50)

        if payment_result["success"] and verification_result["success"]:
            print("✅ Manual payment method WORKS PERFECTLY!")
            print(f"   Transaction: {payment_result['transaction_hash']}")
            print(f"   Ledger: {verification_result['ledger']}")

            # Save results
            self.save_results()
            return True
        else:
            print("❌ Manual payment test FAILED")
            return False

    def save_results(self):
        """Save test results"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simple_manual_payment_results_{timestamp}.json"

            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)

            print(f"📁 Results saved to: {filename}")

        except Exception as e:
            print(f"❌ Failed to save results: {e}")

async def main():
    tester = SimpleManualPaymentTest()
    success = await tester.run_test()

    if success:
        print("\n🎯 MANUAL PAYMENT METHOD VERIFIED!")
        print("   This method is ready for production implementation.")
    else:
        print("\n❌ MANUAL PAYMENT METHOD FAILED")
        print("   Need to investigate the issue.")

    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)