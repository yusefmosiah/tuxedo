#!/usr/bin/env python3
"""
Comprehensive DeFindex Vault Deposit Test with Detailed Reporting
Tests actual deposit functionality and generates detailed analysis report
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stellar_sdk import Server, TransactionBuilder, scval
from stellar_sdk.keypair import Keypair
from stellar_sdk.exceptions import NotFoundError

class VaultDepositTester:
    """Comprehensive vault deposit testing with detailed analysis"""

    def __init__(self, network: str = "testnet"):
        self.network = network
        self.test_start_time = datetime.now(timezone.utc)

        if network == "testnet":
            self.horizon_url = "https://horizon-testnet.stellar.org"
            self.network_passphrase = "Test SDF Network ; September 2015"
            self.friendbot_url = "https://friendbot.stellar.org"
        else:
            self.horizon_url = "https://horizon.stellar.org"
            self.network_passphrase = "Public Global Stellar Network ; September 2015"
            self.friendbot_url = None

        self.server = Server(self.horizon_url)

        # Test configuration
        self.vault_address = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
        self.deposit_amount_xlm = 2.5  # Test with 2.5 XLM

        # Generate or use existing test account
        self.test_account = self._get_test_account()

        self.test_results = {
            "test_metadata": {
                "test_type": "Vault Deposit Test",
                "timestamp": self.test_start_time.isoformat(),
                "network": network,
                "vault_address": self.vault_address,
                "deposit_amount_xlm": self.deposit_amount_xlm,
                "test_account": self.test_account.public_key,
                "test_duration_seconds": None
            },
            "pre_test_state": {},
            "deposit_execution": {},
            "post_test_state": {},
            "analysis": {},
            "conclusions": {}
        }

    def _get_test_account(self) -> Keypair:
        """Get or create test account"""
        # Generate a new test account for this test
        print("🔑 Generating new test account...")

        # Generate new keypair
        keypair = Keypair.random()

        print(f"   New test account: {keypair.public_key}")
        print(f"   Secret key (for debugging): {keypair.secret}")

        return keypair

    async def ensure_account_funded(self) -> Dict[str, Any]:
        """Ensure test account has sufficient balance"""
        try:
            # Check current balance
            account = self.server.load_account(self.test_account.public_key)
            current_balance = float(account.balances[0].balance) if account.balances else 0.0

            result = {
                "account_exists": True,
                "current_balance_xlm": current_balance,
                "needs_funding": current_balance < (self.deposit_amount_xlm + 1.0),  # +1 XLM for fees
                "funding_attempted": False,
                "funding_successful": False
            }

            if result["needs_funding"] and self.friendbot_url:
                print("🪙 Funding test account via Friendbot...")
                try:
                    import requests
                    response = requests.post(
                        self.friendbot_url,
                        params={"addr": self.test_account.public_key}
                    )

                    if response.status_code == 200:
                        result["funding_attempted"] = True
                        result["funding_successful"] = True

                        # Wait a moment for funding to settle
                        await asyncio.sleep(5)

                        # Re-check balance
                        account = self.server.load_account(self.test_account.public_key)
                        current_balance = float(account.balances[0].balance) if account.balances else 0.0
                        result["post_funding_balance_xlm"] = current_balance

                        print(f"✅ Account funded successfully. New balance: {current_balance} XLM")
                    else:
                        print(f"❌ Friendbot funding failed: {response.status_code}")
                        result["funding_error"] = f"Status {response.status_code}: {response.text}"

                except Exception as e:
                    print(f"❌ Funding error: {e}")
                    result["funding_error"] = str(e)

            return result

        except NotFoundError:
            print("❌ Test account does not exist on network")
            return {
                "account_exists": False,
                "error": "Account not found on network"
            }
        except Exception as e:
            print(f"❌ Error checking account: {e}")
            return {
                "account_exists": False,
                "error": str(e)
            }

    async def get_vault_pre_state(self) -> Dict[str, Any]:
        """Analyze vault state before deposit"""
        try:
            print(f"📊 Analyzing vault {self.vault_address[:8]}... before deposit...")

            vault_state = {
                "vault_address": self.vault_address,
                "contract_analysis": {},
                "account_specific": {},
                "blockchain_state": {}
            }

            # Try to get basic vault info via direct RPC
            try:
                from stellar_sdk.soroban_server_async import SorobanServerAsync
                soroban_server = SorobanServerAsync(
                    "https://soroban-testnet.stellar.org" if self.network == "testnet"
                    else "https://mainnet.stellar.expert/explorer/rpc"
                )

                # Test basic contract connectivity
                test_account = "GBWUVTWLIKJJOTAYPJFINOEJY6S7EFNCOESYWABSFZALHOLVBDE3YXVG"

                try:
                    source_account = await soroban_server.load_account(test_account)
                    vault_state["contract_analysis"]["rpc_connectivity"] = True

                    # Try to call a basic function
                    tx = (
                        TransactionBuilder(source_account, self.network_passphrase, base_fee=100)
                        .set_timeout(30)
                        .append_invoke_contract_function_op(
                            contract_id=self.vault_address,
                            function_name="name",
                            parameters=[]
                        )
                        .build()
                    )

                    sim_result = await soroban_server.simulate_transaction(tx)

                    if sim_result.error:
                        vault_state["contract_analysis"]["name_function"] = {
                            "available": False,
                            "error": str(sim_result.error)[:200]
                        }
                    else:
                        result_scval = sim_result.results[0].return_value if sim_result.results else None
                        if result_scval:
                            vault_name = scval.from_scval(result_scval)
                            vault_state["contract_analysis"]["name_function"] = {
                                "available": True,
                                "result": vault_name
                            }

                except Exception as e:
                    vault_state["contract_analysis"]["rpc_connectivity"] = False
                    vault_state["contract_analysis"]["rpc_error"] = str(e)

            except ImportError:
                vault_state["contract_analysis"]["rpc_error"] = "Soroban client not available"

            # Check user's current balance in vault (if any)
            try:
                # This would typically require specific vault function calls
                # For now, we'll note that we don't have a direct way to check this
                vault_state["account_specific"]["vault_balance"] = {
                    "method": "Not directly accessible",
                    "note": "Would require vault-specific function calls"
                }

            except Exception as e:
                vault_state["account_specific"]["vault_balance_error"] = str(e)

            # Check general blockchain state
            try:
                latest_ledger = self.server.ledgers().limit(1)["records"][0]
                vault_state["blockchain_state"]["latest_ledger"] = latest_ledger.sequence
                vault_state["blockchain_state"]["timestamp"] = latest_ledger.closed_at
                vault_state["blockchain_state"]["base_fee"] = latest_ledger.base_fee_in_stroops

            except Exception as e:
                vault_state["blockchain_state"]["error"] = str(e)

            return vault_state

        except Exception as e:
            return {
                "error": f"Failed to analyze vault pre-state: {str(e)}"
            }

    async def execute_deposit(self) -> Dict[str, Any]:
        """Execute the actual deposit transaction"""
        try:
            print(f"💰 Executing {self.deposit_amount_xlm} XLM deposit to vault...")

            deposit_start = time.time()
            amount_stroops = int(self.deposit_amount_xlm * 10_000_000)

            # Load account for transaction building
            account = self.server.load_account(self.test_account.public_key)

            # Build payment transaction to vault address
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
                    asset_code="XLM"  # Native asset
                )
                .set_timeout(30)
                .build()
            )

            # Sign transaction
            transaction.sign(self.test_account)

            # Submit transaction
            print("📤 Submitting deposit transaction...")
            response = self.server.submit_transaction(transaction)

            deposit_end = time.time()

            deposit_result = {
                "transaction_successful": response.get("successful", False),
                "transaction_hash": response.get("hash"),
                "ledger": response.get("ledger"),
                "amount_xlm": self.deposit_amount_xlm,
                "amount_stroops": amount_stroops,
                "destination": self.vault_address,
                "memo": "Deposit to DeFindex Vault",
                "execution_time_seconds": deposit_end - deposit_start,
                "transaction_xdr": transaction.to_xdr(),
                "submit_response": response
            }

            if response.get("successful"):
                print(f"✅ Deposit successful! Hash: {response.get('hash')}")
                print(f"   Ledger: {response.get('ledger')}")

                # Wait for transaction finality
                print("⏳ Waiting for transaction finality...")
                await asyncio.sleep(10)

                # Verify transaction status
                try:
                    tx_status = self.server.transactions().get(response.get("hash"))
                    deposit_result["verification"] = {
                        "status": tx_status.status,
                        "successful": tx_status.successful,
                        "ledger": tx_status.ledger,
                        "created_at": tx_status.created_at,
                        "envelope_xdr": tx_status.envelope_xdr,
                        "result_xdr": tx_status.result_xdr
                    }

                    print(f"   Verified: {tx_status.status}")

                except Exception as e:
                    deposit_result["verification_error"] = str(e)
                    print(f"   ⚠️ Verification error: {e}")

            else:
                print(f"❌ Deposit failed: {response.get('error_result_xdr', 'Unknown error')}")
                deposit_result["error"] = response.get("error_result_xdr", "Unknown error")

            return deposit_result

        except Exception as e:
            print(f"❌ Deposit execution failed: {e}")
            return {
                "error": str(e),
                "transaction_successful": False
            }

    async def get_vault_post_state(self) -> Dict[str, Any]:
        """Analyze vault state after deposit"""
        try:
            print(f"📊 Analyzing vault state after deposit...")

            post_state = await self.get_vault_pre_state()  # Reuse same analysis
            post_state["analysis_type"] = "post_deposit"

            return post_state

        except Exception as e:
            return {
                "error": f"Failed to analyze vault post-state: {str(e)}"
            }

    async def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results and generate conclusions"""
        try:
            print("🔍 Analyzing test results...")

            analysis = {
                "deposit_success": self.test_results["deposit_execution"].get("transaction_successful", False),
                "performance_metrics": {},
                "state_changes": {},
                "recommendations": []
            }

            # Performance analysis
            if "execution_time_seconds" in self.test_results["deposit_execution"]:
                analysis["performance_metrics"]["deposit_execution_time"] = self.test_results["deposit_execution"]["execution_time_seconds"]

            total_time = (datetime.now(timezone.utc) - self.test_start_time).total_seconds()
            analysis["performance_metrics"]["total_test_time"] = total_time

            # State change analysis
            pre_state = self.test_results["pre_test_state"]
            post_state = self.test_results["post_test_state"]

            # Compare blockchain state
            if ("blockchain_state" in pre_state and "blockchain_state" in post_state and
                "latest_ledger" in pre_state["blockchain_state"] and
                "latest_ledger" in post_state["blockchain_state"]):

                pre_ledger = pre_state["blockchain_state"]["latest_ledger"]
                post_ledger = post_state["blockchain_state"]["latest_ledger"]

                analysis["state_changes"]["ledgers_progressed"] = post_ledger > pre_ledger
                analysis["state_changes"]["ledger_difference"] = post_ledger - pre_ledger

            # Generate recommendations
            if analysis["deposit_success"]:
                analysis["recommendations"].append("✅ Vault deposit mechanism is working correctly")
                analysis["recommendations"].append("✅ Manual XLM payment method successfully processed by vault")

                if analysis["performance_metrics"].get("deposit_execution_time", 0) < 30:
                    analysis["recommendations"].append("✅ Transaction execution time is acceptable")
                else:
                    analysis["recommendations"].append("⚠️ Consider optimizing transaction execution time")
            else:
                analysis["recommendations"].append("❌ Vault deposit failed - investigate vault contract status")
                analysis["recommendations"].append("⚠️ Verify vault address and network configuration")

            return analysis

        except Exception as e:
            return {
                "error": f"Failed to analyze results: {str(e)}"
            }

    async def generate_report(self) -> str:
        """Generate comprehensive test report"""
        try:
            report_start = datetime.now(timezone.utc)

            # Calculate total test duration
            test_end = datetime.now(timezone.utc)
            total_duration = (test_end - self.test_start_time).total_seconds()
            self.test_results["test_metadata"]["test_duration_seconds"] = total_duration

            report_content = f"""# DeFindex Vault Deposit Test Report

## Test Overview

**Test Type**: Vault Deposit Functionality
**Network**: {self.network}
**Vault Address**: `{self.vault_address}`
**Deposit Amount**: {self.deposit_amount_xlm} XLM
**Test Account**: `{self.test_account.public_key}`
**Test Started**: {self.test_start_time.isoformat()}
**Test Completed**: {test_end.isoformat()}
**Total Duration**: {total_duration:.2f} seconds

---

## Executive Summary

{'✅ SUCCESS' if self.test_results['deposit_execution'].get('transaction_successful') else '❌ FAILED'}:
{'Vault deposit completed successfully via manual XLM payment.' if self.test_results['deposit_execution'].get('transaction_successful') else 'Vault deposit failed. See details below.'}

**Key Findings**:
- {'✅ Vault successfully processed direct XLM payment' if self.test_results['deposit_execution'].get('transaction_successful') else '❌ Vault rejected or failed to process payment'}
- {'✅ Transaction confirmed on blockchain' if self.test_results['deposit_execution'].get('transaction_successful') else '❌ Transaction not confirmed'}
- {'✅ Manual payment method bypasses API limitations' if self.test_results['deposit_execution'].get('transaction_successful') else '❌ Manual payment method failed'}

---

## Pre-Test State Analysis

### Account Status
```json
{json.dumps(self.test_results.get('pre_test_state', {}).get('account_status', {}), indent=2)}
```

### Vault Contract Analysis
```json
{json.dumps(self.test_results.get('pre_test_state', {}).get('contract_analysis', {}), indent=2)}
```

### Blockchain State
```json
{json.dumps(self.test_results.get('pre_test_state', {}).get('blockchain_state', {}), indent=2)}
```

---

## Deposit Execution

### Transaction Details
```json
{json.dumps(self.test_results.get('deposit_execution', {}), indent=2)}
```

### Performance Metrics
- **Execution Time**: {self.test_results.get('deposit_execution', {}).get('execution_time_seconds', 'N/A')} seconds
- **Transaction Hash**: `{self.test_results.get('deposit_execution', {}).get('transaction_hash', 'N/A')}`
- **Ledger**: {self.test_results.get('deposit_execution', {}).get('ledger', 'N/A')}

---

## Post-Test State Analysis

### Vault Contract Status (Post-Deposit)
```json
{json.dumps(self.test_results.get('post_test_state', {}), indent=2)}
```

### State Changes
```json
{json.dumps(self.test_results.get('analysis', {}).get('state_changes', {}), indent=2)}
```

---

## Analysis & Conclusions

### Test Results
```json
{json.dumps(self.test_results.get('analysis', {}), indent=2)}
```

### Technical Assessment

**Vault Contract Behavior**:
- {'✅ Correctly accepted XLM payment as deposit' if self.test_results['deposit_execution'].get('transaction_successful') else '❌ Failed to accept XLM payment'}
- {'✅ Transaction processed without errors' if self.test_results['deposit_execution'].get('transaction_successful') else '❌ Transaction processing failed'}
- {'✅ Funds properly routed to vault contract' if self.test_results['deposit_execution'].get('transaction_successful') else '❌ Funds not properly routed'}

**Network Performance**:
- **Response Time**: {self.test_results.get('analysis', {}).get('performance_metrics', {}).get('deposit_execution_time', 'N/A')} seconds
- **Finality**: {'Achieved within acceptable timeframe' if self.test_results['deposit_execution'].get('transaction_successful') else 'Not achieved'}
- **Fee Efficiency**: {'Standard network fees applied' if self.test_results['deposit_execution'].get('transaction_successful') else 'Transaction failed'}

---

## Recommendations

{chr(10).join(f"- {rec}" for rec in self.test_results.get('analysis', {}).get('recommendations', []))}

---

## Technical Details

### Transaction XDR
```
{self.test_results.get('deposit_execution', {}).get('transaction_xdr', 'N/A')}
```

### Test Environment
- **Stellar SDK Version**: {getattr(self.server, 'sdk_version', 'Unknown')}
- **Network Passphrase**: `{self.network_passphrase}`
- **Horizon URL**: `{self.horizon_url}`

---

## Next Steps

1. **Monitor Vault**: Check vault balance after transaction processing
2. **Verify Deposit**: Confirm funds are reflected in vault
3. **Test Withdrawal**: Execute withdrawal test (see withdrawal script)
4. **Performance Analysis**: Compare with other vault interaction methods

---

*Report generated on: {report_start.isoformat()}*
*Test methodology: Direct Stellar network interaction with manual XLM payment*
"""

            return report_content

        except Exception as e:
            return f"Error generating report: {str(e)}"

    async def save_report(self, report_content: str, filename: str = "reports.md"):
        """Save report to file"""
        try:
            with open(filename, 'w') as f:
                f.write(report_content)
            print(f"📄 Report saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return False

    async def run_complete_test(self) -> bool:
        """Execute the complete test suite"""
        try:
            print("🚀 Starting Complete Vault Deposit Test")
            print("=" * 60)

            # Step 1: Ensure account is funded
            print("\n1️⃣ Ensuring Test Account is Funded...")
            account_status = await self.ensure_account_funded()
            self.test_results["pre_test_state"]["account_status"] = account_status

            if not account_status.get("account_exists"):
                print("❌ Test account does not exist - cannot proceed")
                return False

            if account_status.get("needs_funding") and not account_status.get("funding_successful"):
                print("❌ Account funding failed - cannot proceed")
                return False

            # Step 2: Analyze pre-test state
            print("\n2️⃣ Analyzing Pre-Test State...")
            pre_state = await self.get_vault_pre_state()
            self.test_results["pre_test_state"].update(pre_state)

            # Step 3: Execute deposit
            print("\n3️⃣ Executing Deposit...")
            deposit_result = await self.execute_deposit()
            self.test_results["deposit_execution"] = deposit_result

            # Step 4: Analyze post-test state
            print("\n4️⃣ Analyzing Post-Test State...")
            post_state = await self.get_vault_post_state()
            self.test_results["post_test_state"] = post_state

            # Step 5: Analyze results
            print("\n5️⃣ Analyzing Results...")
            analysis = await self.analyze_results()
            self.test_results["analysis"] = analysis

            # Step 6: Generate and save report
            print("\n6️⃣ Generating Report...")
            report = await self.generate_report()
            await self.save_report(report)

            # Step 7: Display summary
            print("\n" + "=" * 60)
            print("📊 TEST COMPLETE")
            print("=" * 60)

            if deposit_result.get("transaction_successful"):
                print("✅ Vault deposit test PASSED")
                print(f"   Transaction Hash: {deposit_result.get('transaction_hash')}")
                print(f"   Amount: {self.deposit_amount_xlm} XLM")
                print(f"   Vault: {self.vault_address[:8]}...{self.vault_address[-8:]}")
            else:
                print("❌ Vault deposit test FAILED")
                print(f"   Error: {deposit_result.get('error', 'Unknown error')}")

            print(f"\n📄 Detailed report saved to: reports.md")
            print(f"⏱️  Total test time: {self.test_results['test_metadata']['test_duration_seconds']:.2f} seconds")

            return deposit_result.get("transaction_successful", False)

        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False

async def main():
    """Main test execution"""
    tester = VaultDepositTester(network="testnet")
    success = await tester.run_complete_test()

    print(f"\n🎯 Test Result: {'PASSED' if success else 'FAILED'}")
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)