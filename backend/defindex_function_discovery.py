#!/usr/bin/env python3
"""
DeFindex Contract Function Discovery
Find the exact function signatures for vault operations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from stellar_sdk import TransactionBuilder, scval
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk.keypair import Keypair

logger = logging.getLogger(__name__)

class DeFindexFunctionDiscovery:
    """Discover exact function signatures for DeFindex vault contracts"""

    def __init__(self, network: str = "testnet"):
        self.network = network
        if network == "testnet":
            self.rpc_url = "https://soroban-testnet.stellar.org"
            self.network_passphrase = "Test SDF Network ; September 2015"
        else:
            self.rpc_url = "https://mainnet.stellar.expert/explorer/rpc"
            self.network_passphrase = "Public Global Stellar Network ; September 2015"

        self.soroban_server = SorobanServerAsync(self.rpc_url)

        # Testnet vault addresses
        self.testnet_vaults = {
            'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
        }

    async def discover_function_signatures(self, vault_address: str) -> Dict[str, Any]:
        """Discover the exact signatures for vault functions"""
        try:
            logger.info(f"Discovering function signatures for vault {vault_address[:8]}...")

            # Load a test account for simulation
            test_account = "GBWUVTWLIKJJOTAYPJFINOEJY6S7EFNCOESYWABSFZALHOLVBDE3YXVG"
            source_account = await self.soroban_server.load_account(test_account)

            # Test common vault functions with various parameter combinations
            function_tests = {
                # Deposit functions
                'deposit': [
                    [],  # No parameters
                    [scval.to_uint64(10000000)],  # Amount only
                    [scval.to_address(test_account)],  # User address only
                    [scval.to_uint64(10000000), scval.to_address(test_account)],  # Amount, user
                    [scval.to_address(test_account), scval.to_uint64(10000000)],  # User, amount
                    [scval.to_uint64(10000000), scval.to_bool(True)],  # Amount, invest flag
                    [scval.to_uint64(10000000), scval.to_address(test_account), scval.to_bool(True)],  # All params
                ],
                'deposit_native': [
                    [scval.to_uint64(10000000)],
                    [scval.to_uint64(10000000), scval.to_address(test_account)],
                ],
                'invest': [
                    [scval.to_uint64(10000000)],
                    [scval.to_uint64(10000000), scval.to_address(test_account)],
                    [scval.to_bool(True)],
                    [],
                ],
                'enter': [
                    [scval.to_uint64(10000000)],
                    [],
                ],
                # Withdraw functions
                'withdraw': [
                    [scval.to_uint64(10000000)],
                    [scval.to_uint64(10000000), scval.to_address(test_account)],
                    [scval.to_address(test_account)],
                    [],
                ],
                'withdraw_native': [
                    [scval.to_uint64(10000000)],
                    [scval.to_uint64(10000000), scval.to_address(test_account)],
                ],
                'exit': [
                    [scval.to_uint64(10000000)],
                    [],
                ],
                # Query functions
                'get_assets': [[]],
                'balance': [[]],
                'balance_of': [
                    [],
                    [scval.to_address(test_account)],
                ],
                'total_supply': [[]],
                'get_manager': [[]],
                'get_fees': [[]],
                'name': [[]],
                'symbol': [[]],
                # Advanced functions
                'claim': [[]],
                'harvest': [[]],
                'rebalance': [[]],
                'emergency_withdraw': [
                    [scval.to_uint64(10000000)],
                    [scval.to_uint64(10000000), scval.to_address(test_account)],
                ],
            }

            results = {}
            working_functions = {}

            for function_name, param_sets in function_tests.items():
                logger.info(f"Testing function: {function_name}")
                function_results = []

                for i, params in enumerate(param_sets):
                    try:
                        tx = (
                            TransactionBuilder(source_account, self.network_passphrase, base_fee=100)
                            .set_timeout(30)
                            .append_invoke_contract_function_op(
                                contract_id=vault_address,
                                function_name=function_name,
                                parameters=params
                            )
                            .build()
                        )

                        # Simulate the transaction
                        sim_result = await self.soroban_server.simulate_transaction(tx)

                        if sim_result.error:
                            error_str = str(sim_result.error)
                            function_results.append({
                                "param_set": i,
                                "param_count": len(params),
                                "success": False,
                                "error": error_str,
                                "error_type": self.classify_error(error_str)
                            })
                        else:
                            # SUCCESS! Extract the result
                            result_scval = sim_result.results[0].return_value if sim_result.results else None
                            decoded_result = scval.from_scval(result_scval) if result_scval else None

                            success_result = {
                                "param_set": i,
                                "param_count": len(params),
                                "success": True,
                                "result": decoded_result,
                                "result_type": type(decoded_result).__name__,
                                "cost": {
                                    "cpu_instructions": sim_result.cost.cpu_insns if sim_result.cost else None,
                                    "memory_bytes": sim_result.cost.mem_bytes if sim_result.cost else None,
                                },
                                "min_fee": sim_result.min_resource_fee
                            }

                            function_results.append(success_result)

                            # Store the first successful signature as the working one
                            if function_name not in working_functions:
                                working_functions[function_name] = success_result

                            logger.info(f"  ✅ SUCCESS: {function_name} with {len(params)} parameters")

                    except Exception as e:
                        function_results.append({
                            "param_set": i,
                            "param_count": len(params),
                            "success": False,
                            "error": str(e),
                            "error_type": "exception"
                        })

                results[function_name] = function_results

                # Add delay to avoid overwhelming the RPC
                await asyncio.sleep(0.5)

            return {
                "success": True,
                "vault_address": vault_address,
                "working_functions": working_functions,
                "all_results": results,
                "summary": {
                    "total_functions_tested": len(function_tests),
                    "working_functions_count": len(working_functions),
                    "working_function_names": list(working_functions.keys())
                },
                "data_source": "soroban_discovery"
            }

        except Exception as e:
            logger.error(f"Error discovering function signatures: {e}")
            return {
                "success": False,
                "error": str(e),
                "vault_address": vault_address
            }

    def classify_error(self, error_str: str) -> str:
        """Classify error types for better understanding"""
        error_str_lower = error_str.lower()

        if "MismatchingParameterLen" in error_str or "mismatching" in error_str_lower:
            return "wrong_parameter_count"
        elif "HostError: Error(WasmVm, UnexpectedValue)" in error_str:
            return "unexpected_value"
        elif "HostError: Error(WasmVm, MissingValue)" in error_str:
            return "missing_value"
        elif "HostError: Error(WasmVm, UnexpectedSize)" in error_str:
            return "unexpected_size"
        elif "contract error" in error_str_lower:
            return "contract_error"
        elif "Func(MismatchingParameterLen)" in error_str:
            return "parameter_length_mismatch"
        else:
            return "unknown_error"

    async def test_deposit_with_discovered_signature(self, vault_address: str) -> Dict[str, Any]:
        """Test deposit using the discovered correct signature"""
        try:
            logger.info(f"Testing deposit with discovered signature for {vault_address[:8]}...")

            # First discover signatures
            discovery = await self.discover_function_signatures(vault_address)

            if not discovery.get("success"):
                return {
                    "success": False,
                    "error": f"Could not discover signatures: {discovery.get('error')}"
                }

            working_functions = discovery.get("working_functions", {})
            deposit_functions = [f for f in working_functions.keys() if 'deposit' in f.lower() or 'invest' in f.lower() or 'enter' in f.lower()]

            if not deposit_functions:
                return {
                    "success": False,
                    "error": "No working deposit-like functions found"
                }

            # Use the first working deposit function
            deposit_function = deposit_functions[0]
            function_info = working_functions[deposit_function]

            # Build a real deposit transaction
            test_user = "GBWUVTWLIKJJOTAYPJFINOEJY6S7EFNCOESYWABSFZALHOLVBDE3YXVG"
            amount_stroops = 10_000_000  # 1 XLM

            # Load account
            source_account = await self.soroban_server.load_account(test_user)

            # Recreate the successful parameters
            param_count = function_info["param_count"]
            if param_count == 0:
                params = []
            elif param_count == 1:
                params = [scval.to_uint64(amount_stroops)]
            elif param_count == 2:
                params = [scval.to_uint64(amount_stroops), scval.to_address(test_user)]
            else:
                params = [scval.to_uint64(amount_stroops)]

            # Build transaction
            tx = (
                TransactionBuilder(source_account, self.network_passphrase, base_fee=100)
                .set_timeout(30)
                .append_invoke_contract_function_op(
                    contract_id=vault_address,
                    function_name=deposit_function,
                    parameters=params
                )
                .build()
            )

            # Simulate
            sim_result = await self.soroban_server.simulate_transaction(tx)

            if sim_result.error:
                return {
                    "success": False,
                    "error": f"Deposit simulation failed: {sim_result.error}",
                    "function_used": deposit_function,
                    "parameters": params
                }

            # Prepare transaction
            prepared_tx = await self.soroban_server.prepare_transaction(tx, sim_result)

            return {
                "success": True,
                "function_used": deposit_function,
                "parameters_used": len(params),
                "transaction_xdr": prepared_tx.to_xdr(),
                "estimated_fee": sim_result.min_resource_fee,
                "ready_for_wallet": True,
                "description": f"Deposit {amount_stroops/10_000_000:.1f} XLM to {deposit_function}",
                "data_source": "soroban_discovery"
            }

        except Exception as e:
            logger.error(f"Error testing deposit with discovered signature: {e}")
            return {
                "success": False,
                "error": str(e)
            }

async def main():
    """Run function discovery test"""
    print("=" * 80)
    print("🔍 DeFindex Function Discovery")
    print("=" * 80)

    discovery = DeFindexFunctionDiscovery("testnet")
    vault_address = list(discovery.testnet_vaults.values())[0]

    print(f"Testing vault: {vault_address}")

    # Discover all function signatures
    result = await discovery.discover_function_signatures(vault_address)

    if result.get("success"):
        working_funcs = result.get("working_functions", {})
        print(f"\n✅ Found {len(working_funcs)} working functions:")
        for func_name, info in working_funcs.items():
            print(f"   {func_name}: {info['param_count']} parameters")
            if info.get("result"):
                print(f"      Result: {info['result']} (type: {info['result_type']})")

        # Test deposit specifically
        print(f"\n🎯 Testing deposit with discovered signature...")
        deposit_test = await discovery.test_deposit_with_discovered_signature(vault_address)

        if deposit_test.get("success"):
            print(f"   ✅ Deposit transaction ready!")
            print(f"   Function: {deposit_test.get('function_used')}")
            print(f"   XDR length: {len(deposit_test.get('transaction_xdr', ''))}")
        else:
            print(f"   ❌ Deposit test failed: {deposit_test.get('error')}")

    else:
        print(f"❌ Discovery failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())