"""
Stellar Soroban (Smart Contract) Operations
Async-first implementation using SorobanServerAsync

Updated for Quantum Leap migration:
- Uses AccountManager instead of KeyManager
- Enforces user_id isolation
- Permission checks before signing
- TransactionHandler integration for external wallet support
"""

import asyncio
from stellar_sdk import TransactionBuilder, scval, xdr, Address
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk.soroban_rpc import EventFilter, EventFilterType, GetEventsRequest
from account_manager import AccountManager
from agent.context import AgentContext
from agent.transaction_handler import TransactionHandler
from typing import Optional, Dict, Any, List, Union
import json


def _parse_parameters(parameters_json: str) -> list:
    """
    Convert JSON parameter specification to scval objects.

    Args:
        parameters_json: JSON string like '[{"type": "address", "value": "G..."}, ...]'

    Returns:
        List of SCVal objects ready for contract invocation

    Example:
        '[{"type": "uint32", "value": 100}]' -> [scval.to_uint32(100)]
    """
    if not parameters_json:
        return []

    params = json.loads(parameters_json)
    scval_params = []

    for param in params:
        param_type = param["type"]
        value = param["value"]

        # Map type to scval function
        type_map = {
            "address": lambda v: scval.to_address(Address(v) if isinstance(v, str) else v),
            "bool": scval.to_bool,
            "bytes": lambda v: scval.to_bytes(v.encode() if isinstance(v, str) else v),
            "duration": scval.to_duration,
            "int32": lambda v: scval.to_int32(int(v) if isinstance(v, str) else v),
            "int64": lambda v: scval.to_int64(int(v) if isinstance(v, str) else v),
            "int128": lambda v: scval.to_int128(int(v) if isinstance(v, str) else v),
            "int256": lambda v: scval.to_int256(int(v) if isinstance(v, str) else v),
            "string": scval.to_string,
            "symbol": scval.to_symbol,
            "timepoint": scval.to_timepoint,
            "uint32": lambda v: scval.to_uint32(int(v) if isinstance(v, str) else v),
            "uint64": lambda v: scval.to_uint64(int(v) if isinstance(v, str) else v),
            "uint128": lambda v: scval.to_uint128(int(v) if isinstance(v, str) else v),
            "uint256": lambda v: scval.to_uint256(int(v) if isinstance(v, str) else v),
            "void": lambda v: scval.to_void(),
            "native": lambda v: scval.to_native(),
            # Complex types need recursive parsing
            "vec": lambda v: scval.to_vec([_parse_single_param(item) for item in v]),
            "map": lambda v: scval.to_map({k: _parse_single_param(val) for k, val in v.items()}),
        }

        if param_type not in type_map:
            raise ValueError(f"Unsupported parameter type: {param_type}")

        scval_params.append(type_map[param_type](value))

    return scval_params


def _parse_single_param(param: dict):
    """Helper for recursive parameter parsing"""
    param_type = param["type"]
    value = param["value"]

    # Handle simple types directly
    if param_type == "address":
        return scval.to_address(Address(value) if isinstance(value, str) else value)
    elif param_type in ["int32", "int64", "int128", "int256", "uint32", "uint64", "uint128", "uint256"]:
        int_val = int(value) if isinstance(value, str) else value
        if param_type == "int32":
            return scval.to_int32(int_val)
        elif param_type == "int64":
            return scval.to_int64(int_val)
        elif param_type == "int128":
            return scval.to_int128(int_val)
        elif param_type == "int256":
            return scval.to_int256(int_val)
        elif param_type == "uint32":
            return scval.to_uint32(int_val)
        elif param_type == "uint64":
            return scval.to_uint64(int_val)
        elif param_type == "uint128":
            return scval.to_uint128(int_val)
        elif param_type == "uint256":
            return scval.to_uint256(int_val)
    elif param_type == "string":
        return scval.to_string(value)
    elif param_type == "bool":
        return scval.to_bool(value)
    elif param_type == "vec":
        return scval.to_vec([_parse_single_param(item) for item in value])
    elif param_type == "map":
        # For maps with string keys, convert keys to symbols
        map_items = []
        for key, val in value.items():
            if isinstance(key, str):
                # Convert string key to symbol
                key_scval = scval.to_symbol(key)
                val_scval = _parse_single_param(val) if isinstance(val, dict) else scval.to_native(val)
                map_items.append((key_scval, val_scval))
            else:
                # Handle non-string keys
                key_scval = _parse_single_param(key) if isinstance(key, dict) else scval.to_native(key)
                val_scval = _parse_single_param(val) if isinstance(val, dict) else scval.to_native(val)
                map_items.append((key_scval, val_scval))

        # Sort map items by key (required by Stellar Soroban)
        map_items.sort(key=lambda x: str(x[0]))

        return scval.to_map(dict(map_items))
    else:
        # Fall back to original method for complex types
        return _parse_parameters(json.dumps([param]))[0]


async def soroban_operations(
    action: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    user_id: Optional[str] = None,
    agent_context: Optional[AgentContext] = None,
    contract_id: Optional[str] = None,
    key: Optional[str] = None,
    function_name: Optional[str] = None,
    parameters: Optional[str] = None,
    account_id: Optional[str] = None,
    durability: str = "persistent",
    start_ledger: Optional[int] = None,
    event_types: Optional[list] = None,
    limit: int = 100,
    auto_sign: bool = True,
    network_passphrase: str = None,
    ledger_keys: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Unified Soroban operations handler with async support and user isolation.

    Now supports external wallet signing via TransactionHandler integration.

    Actions:
        - "get_data": Query contract storage (read-only)
        - "get_ledger_entries": Query multiple ledger entries directly (read-only, no account needed)
        - "simulate": Simulate contract call (read-only)
        - "invoke": Execute contract function (write, requires account_id, supports external wallet)
        - "get_events": Query contract events (read-only)

    Args:
        action: Operation type
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        user_id: User identifier (for backward compatibility with read operations)
        agent_context: AgentContext (required for invoke action, supports external wallet)
        contract_id: Contract ID
        key: Storage key (for get_data)
        function_name: Contract function name
        parameters: JSON-encoded parameters
        account_id: Account ID (internal ID, required for invoke)
        durability: Storage durability ("persistent" or "temporary")
        start_ledger: Starting ledger for event queries
        event_types: Event type filters
        limit: Result limit
        auto_sign: Auto-sign transactions (legacy parameter, ignored in external mode)
        network_passphrase: Network passphrase
        ledger_keys: List of ledger key specifications (for get_ledger_entries)

    Security:
        - agent_context enforced for all write operations
        - Permission check before signing transactions
        - Read-only operations (get_data, get_ledger_entries, simulate, get_events) don't require ownership
        - TransactionHandler handles dual-mode signing (agent or external wallet)
    """
    # Backward compatibility: extract user_id from agent_context if provided
    if agent_context and not user_id:
        user_id = agent_context.user_id
    try:
        if action == "get_data":
            # Read contract storage directly
            if not contract_id or not key:
                return {"error": "contract_id and key required for get_data"}

            # Convert key to SCVal
            key_scval = scval.to_symbol(key)

            # Query contract data
            result = await soroban_server.get_contract_data(
                contract_id=contract_id,
                key=key_scval,
                durability=durability
            )

            # Decode result
            return {
                "success": True,
                "value": scval.to_native(result.val),
                "last_modified_ledger": result.last_modified_ledger_seq,
                "live_until_ledger": result.live_until_ledger_seq
            }

        elif action == "simulate":
            # Simulate contract call (read-only, no fees)
            if not contract_id or not function_name or not account_id:
                return {"error": "contract_id, function_name, and account_id required"}

            # Get account details (no permission check needed for simulation)
            account_data = account_manager._get_account_by_id(account_id)
            if not account_data:
                return {"error": "Account not found", "success": False}

            public_key = account_data['public_key']

            # Load account from blockchain, use mock account for simulation if not found
            try:
                source = await soroban_server.load_account(public_key)
            except Exception as e:
                # Account doesn't exist on network - create mock account for simulation
                from stellar_sdk import Account
                source = Account(public_key, 1)  # Mock account with sequence 1

            # Parse parameters
            scval_params = _parse_parameters(parameters) if parameters else []

            # Build transaction
            tx = (
                TransactionBuilder(source, network_passphrase, base_fee=100)
                .set_timeout(30)
                .append_invoke_contract_function_op(
                    contract_id=contract_id,
                    function_name=function_name,
                    parameters=scval_params
                )
                .build()
            )

            # Simulate (doesn't hit the network)
            sim_result = await soroban_server.simulate_transaction(tx)

            if sim_result.error:
                return {
                    "success": False,
                    "error": sim_result.error
                }

            # Extract result from XDR field
            if sim_result.results:
                # Parse the result from XDR format
                result_xdr = sim_result.results[0].xdr
                if result_xdr:
                    from stellar_sdk.xdr import SCVal
                    result_scval = SCVal.from_xdr(result_xdr)
                else:
                    result_scval = None
            else:
                result_scval = None

            return {
                "success": True,
                "result": scval.to_native(result_scval) if result_scval else None,
                "cost": {
                    # Cost information might not be available in current SDK version
                    "cpu_instructions": None,
                    "memory_bytes": None
                },
                "min_resource_fee": sim_result.min_resource_fee,
                "latest_ledger": sim_result.latest_ledger,
                "transaction_data": sim_result.transaction_data
            }

        elif action == "invoke":
            # Execute contract function (writes to blockchain)
            if not contract_id or not function_name or not account_id:
                return {"error": "contract_id, function_name, and account_id required"}

            if not agent_context:
                return {"error": "agent_context required for invoke action"}

            # PERMISSION CHECK: verify user owns this account
            if not account_manager.user_owns_account(agent_context, account_id):
                return {
                    "error": "Permission denied: account not owned by user",
                    "success": False
                }

            # Get account details
            account_data = account_manager._get_account_by_id(account_id)
            if not account_data:
                return {"error": "Account not found", "success": False}

            public_key = account_data['public_key']

            # Load account from blockchain, use mock account for simulation if not found
            try:
                source = await soroban_server.load_account(public_key)
            except Exception as e:
                # Account doesn't exist on network - create mock account for simulation
                from stellar_sdk import Account
                source = Account(public_key, 1)  # Mock account with sequence 1

            # Parse parameters
            scval_params = _parse_parameters(parameters) if parameters else []

            # Build transaction
            tx = (
                TransactionBuilder(source, network_passphrase, base_fee=100)
                .set_timeout(30)
                .append_invoke_contract_function_op(
                    contract_id=contract_id,
                    function_name=function_name,
                    parameters=scval_params
                )
                .build()
            )

            # Simulate to get footprint
            sim_result = await soroban_server.simulate_transaction(tx)

            if sim_result.error:
                return {"success": False, "error": f"Simulation failed: {sim_result.error}"}

            # Prepare transaction (adds soroban data automatically!)
            prepared_tx = await soroban_server.prepare_transaction(tx, sim_result)

            # Check wallet mode for signing
            if agent_context.requires_user_signing():
                # External wallet mode - return unsigned XDR
                description = f"Invoke {function_name} on {contract_id[:8]}..."
                return {
                    "requires_signature": True,
                    "xdr": prepared_tx.to_xdr(),
                    "network_passphrase": network_passphrase,
                    "description": description,
                    "message": "Please approve this Soroban contract invocation in your wallet",
                    "wallet_address": agent_context.wallet_address,
                    "contract_id": contract_id,
                    "function_name": function_name
                }
            else:
                # Agent/imported mode - sign and submit automatically
                keypair_result = account_manager.get_keypair_for_signing(agent_context, account_id)
                from stellar_sdk import Keypair
                keypair = Keypair.from_secret(keypair_result.private_key)

                # Sign and submit
                prepared_tx.sign(keypair)
                send_response = await soroban_server.send_transaction(prepared_tx)

                if send_response.error:
                    return {"success": False, "error": send_response.error}

                # Poll for result (automatic retry with backoff!)
                result = await soroban_server.poll_transaction(send_response.hash)

                return {
                    "success": result.status == "SUCCESS",
                    "hash": send_response.hash,
                    "status": result.status,
                    "ledger": result.ledger,
                    "message": "Contract invocation successful" if result.status == "SUCCESS" else "Invocation failed"
                }

        elif action == "get_ledger_entries":
            # Direct ledger entry queries (no account required!)
            if not ledger_keys:
                return {"error": "ledger_keys required for get_ledger_entries"}

            # Convert ledger keys from dict format to XDR LedgerKey objects
            xdr_keys = []
            for key_spec in ledger_keys:
                if key_spec["type"] == "contract_instance":
                    xdr_keys.append(
                        xdr.LedgerKey(
                            type=xdr.LedgerEntryType.CONTRACT_DATA,
                            contract_data=xdr.LedgerKeyContractData(
                                contract=Address(key_spec["contract_id"]).to_xdr_sc_address(),
                                key=xdr.SCVal(xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
                                durability=xdr.ContractDataDurability.PERSISTENT
                            )
                        )
                    )
                elif key_spec["type"] == "contract_data":
                    # Handle different key formats for contract data
                    key_value = key_spec["key"]
                    if isinstance(key_value, str):
                        # Simple string key
                        scval_key = scval.to_symbol(key_value)
                    else:
                        # Complex key - try to parse as JSON
                        try:
                            if isinstance(key_value, dict):
                                # Handle tuple/vec structure for enum keys like ResData(Address)
                                if "vec" in key_value or "tuple" in key_value:
                                    elements = key_value.get("vec") or key_value.get("tuple")
                                    scval_elements = []
                                    for elem in elements:
                                        if isinstance(elem, dict):
                                            if elem.get("type") == "symbol":
                                                scval_elements.append(scval.to_symbol(elem["value"]))
                                            elif elem.get("type") == "address":
                                                scval_elements.append(Address(elem["value"]).to_xdr_sc_address())
                                        else:
                                            scval_elements.append(scval.to_symbol(str(elem)))
                                    scval_key = scval.to_vec(scval_elements)
                                else:
                                    # Default to symbol
                                    scval_key = scval.to_symbol(str(key_value))
                            else:
                                scval_key = scval.to_symbol(str(key_value))
                        except Exception as e:
                            # Fallback to symbol
                            scval_key = scval.to_symbol(str(key_value))

                    xdr_keys.append(
                        xdr.LedgerKey(
                            type=xdr.LedgerEntryType.CONTRACT_DATA,
                            contract_data=xdr.LedgerKeyContractData(
                                contract=Address(key_spec["contract_id"]).to_xdr_sc_address(),
                                key=scval_key,
                                durability=getattr(
                                    xdr.ContractDataDurability,
                                    key_spec.get("durability", "PERSISTENT")
                                )
                            )
                        )
                    )

            # Execute query
            response = await soroban_server.get_ledger_entries(xdr_keys)

            # Parse results
            entries = []
            for entry_result in response.entries:
                entry_data = xdr.LedgerEntryData.from_xdr(entry_result.xdr)
                value = entry_data.contract_data.val

                entries.append({
                    "key_xdr": entry_result.key,
                    "value": scval.to_native(value),
                    "last_modified_ledger": entry_result.last_modified_ledger_seq,
                    "live_until_ledger": entry_result.live_until_ledger_seq
                })

            return {
                "success": True,
                "entries": entries,
                "latest_ledger": response.latest_ledger,
                "count": len(entries)
            }

        elif action == "get_events":
            # Query contract events
            if not contract_id or not start_ledger:
                return {"error": "contract_id and start_ledger required for get_events"}

            # Build event filter
            event_filter = EventFilter(
                event_type=EventFilterType.CONTRACT,
                contract_ids=[contract_id],
                topics=event_types or []
            )

            # Build request
            request = GetEventsRequest(
                start_ledger=start_ledger,
                filters=[event_filter],
                limit=limit
            )

            # Query events
            events_response = await soroban_server.get_events(request)

            return {
                "success": True,
                "events": [
                    {
                        "ledger": e.ledger,
                        "topics": [scval.to_native(t) for t in e.topic],
                        "data": scval.to_native(e.value) if e.value else None,
                        "contract_id": e.contract_id
                    }
                    for e in events_response.events
                ],
                "latest_ledger": events_response.latest_ledger,
                "count": len(events_response.events)
            }

        else:
            return {
                "error": f"Unknown action: {action}",
                "valid_actions": ["get_data", "get_ledger_entries", "simulate", "invoke", "get_events"]
            }

    except Exception as e:
        return {"error": str(e)}
