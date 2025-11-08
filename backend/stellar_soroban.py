"""
Stellar Soroban (Smart Contract) Operations
Async-first implementation using SorobanServerAsync

Updated for Quantum Leap migration:
- Uses AccountManager instead of KeyManager
- Enforces user_id isolation
- Permission checks before signing
"""

import asyncio
from stellar_sdk import TransactionBuilder, scval
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk.soroban_rpc import EventFilter, EventFilterType, GetEventsRequest
from account_manager import AccountManager
from typing import Optional, Dict, Any
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
            "address": scval.to_address,
            "bool": scval.to_bool,
            "bytes": lambda v: scval.to_bytes(v.encode() if isinstance(v, str) else v),
            "duration": scval.to_duration,
            "int32": scval.to_int32,
            "int64": scval.to_int64,
            "int128": scval.to_int128,
            "int256": scval.to_int256,
            "string": scval.to_string,
            "symbol": scval.to_symbol,
            "timepoint": scval.to_timepoint,
            "uint32": scval.to_uint32,
            "uint64": scval.to_uint64,
            "uint128": scval.to_uint128,
            "uint256": scval.to_uint256,
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
    return _parse_parameters(json.dumps([param]))[0]


async def soroban_operations(
    action: str,
    user_id: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
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
    network_passphrase: str = None
) -> Dict[str, Any]:
    """
    Unified Soroban operations handler with async support and user isolation.

    Actions:
        - "get_data": Query contract storage (read-only)
        - "simulate": Simulate contract call (read-only)
        - "invoke": Execute contract function (write, requires account_id)
        - "get_events": Query contract events (read-only)

    Args:
        action: Operation type
        user_id: User identifier (MANDATORY - injected by auth layer)
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        contract_id: Contract ID
        key: Storage key (for get_data)
        function_name: Contract function name
        parameters: JSON-encoded parameters
        account_id: Account ID (internal ID, required for invoke with auto_sign)
        durability: Storage durability ("persistent" or "temporary")
        start_ledger: Starting ledger for event queries
        event_types: Event type filters
        limit: Result limit
        auto_sign: Auto-sign transactions (requires account_id)
        network_passphrase: Network passphrase

    Security:
        - user_id enforced for all write operations
        - Permission check before signing transactions
        - Read-only operations (get_data, simulate, get_events) don't require ownership
    """
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
                "value": scval.from_scval(result.val),
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

            # Load account from blockchain
            source = await soroban_server.load_account(public_key)

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

            # Extract result
            result_scval = sim_result.results[0].return_value if sim_result.results else None

            return {
                "success": True,
                "result": scval.from_scval(result_scval) if result_scval else None,
                "cost": {
                    "cpu_instructions": sim_result.cost.cpu_insns if sim_result.cost else None,
                    "memory_bytes": sim_result.cost.mem_bytes if sim_result.cost else None
                },
                "min_resource_fee": sim_result.min_resource_fee,
                "latest_ledger": sim_result.latest_ledger
            }

        elif action == "invoke":
            # Execute contract function (writes to blockchain)
            if not contract_id or not function_name or not account_id:
                return {"error": "contract_id, function_name, and account_id required"}

            # PERMISSION CHECK: verify user owns this account
            if not account_manager.user_owns_account(user_id, account_id):
                return {
                    "error": "Permission denied: account not owned by user",
                    "success": False
                }

            # Get account details
            account_data = account_manager._get_account_by_id(account_id)
            if not account_data:
                return {"error": "Account not found", "success": False}

            public_key = account_data['public_key']

            # Get keypair for signing
            keypair = None
            if auto_sign:
                keypair_result = account_manager.get_keypair_for_signing(user_id, account_id)
                keypair = keypair_result.keypair  # StellarAdapter returns object with .keypair attribute

            # Load account from blockchain
            source = await soroban_server.load_account(public_key)

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
            tx = await soroban_server.prepare_transaction(tx, sim_result)

            if not auto_sign:
                return {
                    "transaction_xdr": tx.to_xdr(),
                    "message": "Transaction ready for wallet signing"
                }

            # Sign and submit
            tx.sign(keypair)
            send_response = await soroban_server.send_transaction(tx)

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
                        "topics": [scval.from_scval(t) for t in e.topic],
                        "data": scval.from_scval(e.value) if e.value else None,
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
                "valid_actions": ["get_data", "simulate", "invoke", "get_events"]
            }

    except Exception as e:
        return {"error": str(e)}
