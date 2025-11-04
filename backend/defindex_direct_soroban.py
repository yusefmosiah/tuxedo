#!/usr/bin/env python3
"""
Direct DeFindex Vault Interaction via Soroban RPC
Bypasses the DeFindex API and calls vault contracts directly
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from stellar_sdk import TransactionBuilder, scval
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk.keypair import Keypair
import json

logger = logging.getLogger(__name__)

class DeFindexDirectSoroban:
    """Direct interaction with DeFindex vault contracts via Soroban RPC"""

    def __init__(self, network: str = "testnet"):
        self.network = network
        if network == "testnet":
            self.rpc_url = "https://soroban-testnet.stellar.org"
            self.network_passphrase = "Test SDF Network ; September 2015"
        else:
            self.rpc_url = "https://mainnet.stellar.expert/explorer/rpc"
            self.network_passphrase = "Public Global Stellar Network ; September 2015"

        self.soroban_server = SorobanServerAsync(self.rpc_url)

        # Real testnet vault addresses (from our analysis)
        self.testnet_vaults = {
            'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
            'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
            'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
            'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
        }

    async def get_vault_info(self, vault_address: str) -> Dict[str, Any]:
        """Get vault information directly from contract storage"""
        try:
            logger.info(f"Getting vault info for {vault_address[:8]}... via Soroban RPC")

            # Try common vault storage keys based on error analysis
            storage_keys = [
                "Assets",           # From error: get_assets
                "TotalFunds",       # From error: fetch_total_managed_funds
                "Fees",             # From error: get_fees
                "Manager",          # From error: get_manager
                "Name",             # From error: name
                "Symbol",           # From error: symbol
                "EmergencyManager", # From error: get_emergency_manager
                "RebalanceManager", # From error: get_rebalance_manager
                "FeeReceiver",      # From error: get_fee_receiver
                "TVL",              # Total Value Locked
                "APY"               # Annual Percentage Yield
            ]

            vault_data = {}
            errors = []

            for key in storage_keys:
                try:
                    key_scval = scval.to_symbol(key)
                    result = await self.soroban_server.get_contract_data(
                        contract_id=vault_address,
                        key=key_scval,
                        durability="persistent"
                    )

                    if result.val:
                        decoded_value = scval.from_scval(result.val)
                        vault_data[key.lower()] = {
                            "value": decoded_value,
                            "last_modified": result.last_modified_ledger_seq,
                            "live_until": result.live_until_ledger_seq
                        }
                        logger.debug(f"Found {key}: {decoded_value}")

                except Exception as e:
                    # Expected for uninitialized contracts
                    errors.append(f"{key}: {str(e)}")
                    logger.debug(f"No data for key {key}: {e}")

            return {
                "success": len(vault_data) > 0,
                "vault_address": vault_address,
                "data": vault_data,
                "errors": errors,
                "data_source": "soroban_direct",
                "network": self.network
            }

        except Exception as e:
            logger.error(f"Error getting vault info: {e}")
            return {
                "success": False,
                "error": str(e),
                "vault_address": vault_address,
                "data_source": "soroban_direct"
            }

    async def get_vault_balance(self, vault_address: str, user_address: str) -> Dict[str, Any]:
        """Get user's balance in vault directly from contract"""
        try:
            logger.info(f"Getting balance for user {user_address[:8]}... in vault {vault_address[:8]}...")

            # Try user-specific storage keys
            user_keys = [
                f"Balance:{user_address}",
                f"Shares:{user_address}",
                f"Deposit:{user_address}",
                f"Position:{user_address}",
                user_address  # Some contracts use address directly as key
            ]

            for key in user_keys:
                try:
                    key_scval = scval.to_string(key)
                    result = await self.soroban_server.get_contract_data(
                        contract_id=vault_address,
                        key=key_scval,
                        durability="persistent"
                    )

                    if result.val:
                        decoded_value = scval.from_scval(result.val)
                        return {
                            "success": True,
                            "balance": decoded_value,
                            "key_used": key,
                            "last_modified": result.last_modified_ledger_seq,
                            "data_source": "soroban_direct"
                        }

                except Exception as e:
                    logger.debug(f"No balance found with key {key}: {e}")
                    continue

            return {
                "success": False,
                "error": "No balance found for user",
                "tried_keys": user_keys,
                "data_source": "soroban_direct"
            }

        except Exception as e:
            logger.error(f"Error getting vault balance: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_source": "soroban_direct"
            }

    async def simulate_deposit(
        self,
        vault_address: str,
        amount_stroops: int,
        user_address: str
    ) -> Dict[str, Any]:
        """Simulate a deposit transaction without executing it"""
        try:
            logger.info(f"Simulating deposit of {amount_stroops/10_000_000:.2f} XLM to {vault_address[:8]}...")

            # Load user account
            try:
                source_account = await self.soroban_server.load_account(user_address)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not load account {user_address}: {str(e)}",
                    "suggestion": "Make sure the account exists and is funded on the network"
                }

            # Build deposit transaction
            # Common deposit function signatures found in vault contracts
            deposit_functions = [
                "deposit",
                "deposit_native",
                "invest",
                "deposit_for",
                "enter"
            ]

            results = []

            for function_name in deposit_functions:
                try:
                    # Try different parameter combinations
                    param_sets = [
                        [],  # No params (might use native asset)
                        [scval.to_uint64(amount_stroops)],  # Amount only
                        [scval.to_address(user_address)],  # User address only
                        [scval.to_uint64(amount_stroops), scval.to_address(user_address)],  # Both
                    ]

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
                                results.append({
                                    "function": function_name,
                                    "param_set": i,
                                    "success": False,
                                    "error": str(sim_result.error)
                                })
                            else:
                                # Success! Extract the result
                                result_scval = sim_result.results[0].return_value if sim_result.results else None
                                decoded_result = scval.from_scval(result_scval) if result_scval else None

                                return {
                                    "success": True,
                                    "function": function_name,
                                    "param_set": i,
                                    "parameters_used": len(params),
                                    "result": decoded_result,
                                    "simulation_details": {
                                        "cpu_instructions": sim_result.cost.cpu_insns if sim_result.cost else None,
                                        "memory_bytes": sim_result.cost.mem_bytes if sim_result.cost else None,
                                        "min_resource_fee": sim_result.min_resource_fee,
                                        "latest_ledger": sim_result.latest_ledger
                                    },
                                    "ready_to_build": True,
                                    "data_source": "soroban_direct"
                                }

                        except Exception as e:
                            results.append({
                                "function": function_name,
                                "param_set": i,
                                "success": False,
                                "error": str(e)
                            })
                            continue

                except Exception as e:
                    logger.debug(f"Function {function_name} not available: {e}")
                    continue

            return {
                "success": False,
                "error": "No working deposit function found",
                "tried_functions": deposit_functions,
                "results": results,
                "data_source": "soroban_direct"
            }

        except Exception as e:
            logger.error(f"Error simulating deposit: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_source": "soroban_direct"
            }

    async def build_deposit_transaction(
        self,
        vault_address: str,
        amount_stroops: int,
        user_address: str,
        auto_sign: bool = False,
        secret_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a real deposit transaction for signing"""
        try:
            logger.info(f"Building deposit transaction for {amount_stroops/10_000_000:.2f} XLM")

            # First simulate to find the right function
            sim_result = await self.simulate_deposit(vault_address, amount_stroops, user_address)

            if not sim_result.get("success"):
                return {
                    "success": False,
                    "error": f"Could not simulate deposit: {sim_result.get('error', 'Unknown error')}",
                    "data_source": "soroban_direct"
                }

            # Load user account
            source_account = await self.soroban_server.load_account(user_address)

            # Build the actual transaction using the successful simulation
            function_name = sim_result["function"]

            # Recreate the successful parameters
            param_set = sim_result["param_set"]
            all_params = [
                [],  # No params
                [scval.to_uint64(amount_stroops)],
                [scval.to_address(user_address)],
                [scval.to_uint64(amount_stroops), scval.to_address(user_address)],
            ]
            params = all_params[param_set]

            # Build transaction
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

            # Simulate to get footprint
            sim = await self.soroban_server.simulate_transaction(tx)

            if sim.error:
                return {
                    "success": False,
                    "error": f"Simulation failed: {sim.error}",
                    "data_source": "soroban_direct"
                }

            # Prepare transaction (adds soroban data)
            tx = await self.soroban_server.prepare_transaction(tx, sim)

            if not auto_sign:
                return {
                    "success": True,
                    "transaction_xdr": tx.to_xdr(),
                    "function": function_name,
                    "parameters": params,
                    "estimated_fee": sim.min_resource_fee,
                    "ready_for_wallet": True,
                    "description": f"Deposit {amount_stroops/10_000_000:.2f} XLM to vault {vault_address[:8]}...",
                    "data_source": "soroban_direct"
                }

            # Sign and submit if auto_sign is True
            if secret_key:
                try:
                    keypair = Keypair.from_secret(secret_key)
                    tx.sign(keypair)

                    # Submit transaction
                    send_response = await self.soroban_server.send_transaction(tx)

                    if send_response.error:
                        return {
                            "success": False,
                            "error": f"Failed to send transaction: {send_response.error}",
                            "data_source": "soroban_direct"
                        }

                    # Poll for result
                    result = await self.soroban_server.poll_transaction(send_response.hash)

                    return {
                        "success": result.status == "SUCCESS",
                        "transaction_hash": send_response.hash,
                        "ledger": result.ledger,
                        "status": result.status,
                        "function": function_name,
                        "data_source": "soroban_direct"
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Signing/submitting failed: {str(e)}",
                        "data_source": "soroban_direct"
                    }
            else:
                return {
                    "success": False,
                    "error": "Auto-sign requires secret_key parameter",
                    "data_source": "soroban_direct"
                }

        except Exception as e:
            logger.error(f"Error building deposit transaction: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_source": "soroban_direct"
            }

    async def test_vault_connectivity(self, vault_address: str) -> Dict[str, Any]:
        """Test if we can connect to and interact with a vault contract"""
        try:
            logger.info(f"Testing connectivity to vault {vault_address[:8]}...")

            # Try to call basic read-only functions
            test_functions = [
                ("name", []),
                ("symbol", []),
                ("get_assets", []),
                ("get_manager", []),
                ("get_fees", []),
                ("total_supply", []),
                ("balance", []),
            ]

            working_functions = []
            failed_functions = []

            # Load a test account for simulation
            test_account = "GBWUVTWLIKJJOTAYPJFINOEJY6S7EFNCOESYWABSFZALHOLVBDE3YXVG"

            try:
                source_account = await self.soroban_server.load_account(test_account)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Cannot load test account: {str(e)}",
                    "vault_address": vault_address
                }

            for function_name, params in test_functions:
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

                    sim_result = await self.soroban_server.simulate_transaction(tx)

                    if sim_result.error:
                        failed_functions.append({
                            "function": function_name,
                            "error": str(sim_result.error)
                        })
                    else:
                        result_scval = sim_result.results[0].return_value if sim_result.results else None
                        decoded_result = scval.from_scval(result_scval) if result_scval else None

                        working_functions.append({
                            "function": function_name,
                            "result": decoded_result,
                            "cost": {
                                "cpu": sim_result.cost.cpu_insns if sim_result.cost else None,
                                "memory": sim_result.cost.mem_bytes if sim_result.cost else None
                            }
                        })

                except Exception as e:
                    failed_functions.append({
                        "function": function_name,
                        "error": str(e)
                    })

            # Also test contract storage
            storage_data = await self.get_vault_info(vault_address)

            return {
                "success": True,
                "vault_address": vault_address,
                "network": self.network,
                "working_functions": working_functions,
                "failed_functions": failed_functions,
                "storage_data": storage_data.get("data", {}),
                "summary": {
                    "total_functions_tested": len(test_functions),
                    "working_count": len(working_functions),
                    "failed_count": len(failed_functions),
                    "storage_keys_found": len(storage_data.get("data", {}))
                },
                "data_source": "soroban_direct"
            }

        except Exception as e:
            logger.error(f"Error testing vault connectivity: {e}")
            return {
                "success": False,
                "error": str(e),
                "vault_address": vault_address,
                "data_source": "soroban_direct"
            }

# Convenience functions for easy access
async def get_defindex_direct_soroban(network: str = "testnet") -> DeFindexDirectSoroban:
    """Get configured DeFindex direct Soroban client"""
    return DeFindexDirectSoroban(network=network)

async def test_all_testnet_vaults() -> Dict[str, Any]:
    """Test connectivity to all known testnet vaults"""
    client = await get_defindex_direct_soroban("testnet")
    results = {}

    for vault_name, vault_address in client.testnet_vaults.items():
        logger.info(f"Testing vault: {vault_name}")
        result = await client.test_vault_connectivity(vault_address)
        results[vault_name] = result

        # Add delay to avoid rate limiting
        await asyncio.sleep(1)

    return {
        "success": True,
        "results": results,
        "summary": {
            "total_vaults": len(client.testnet_vaults),
            "working_vaults": sum(1 for r in results.values() if r.get("success")),
            "data_source": "soroban_direct"
        }
    }