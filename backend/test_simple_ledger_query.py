#!/usr/bin/env python3
"""
Simple test to debug ledger entry queries for Blend pools.
"""

import asyncio
from stellar_sdk import xdr, Address, scval
from stellar_sdk.soroban_server_async import SorobanServerAsync

async def test_direct_ledger_query():
    """Test direct ledger query without our wrapper."""
    print("=== Direct SorobanServerAsync Test ===")

    server = SorobanServerAsync("https://rpc.ankr.com/stellar_soroban")

    # Test contract instance key (should always work)
    pool_address = "CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM"

    try:
        # Create contract instance key
        contract_key = xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(pool_address).to_xdr_sc_address(),
                key=xdr.SCVal(xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )

        print(f"Querying contract instance for {pool_address[:8]}...")

        response = await server.get_ledger_entries([contract_key])

        if response.entries:
            print(f"✅ Found {len(response.entries)} contract entries")
            for entry in response.entries:
                entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
                value = entry_data.contract_data.val
                native_value = scval.to_native(value)
                print(f"   Contract instance data: {native_value}")
        else:
            print("❌ No contract instance entries found")

    except Exception as e:
        print(f"❌ Contract instance query failed: {e}")
        import traceback
        traceback.print_exc()

    # Try different key patterns for ResData and ResList
    usdc_address = "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75"

    test_patterns = [
        ("Simple ResData", scval.to_symbol("ResData")),
        ("Simple ResList", scval.to_symbol("ResList")),
        ("ResData-USDC Vec", scval.to_vec([
            scval.to_symbol("ResData"),
            Address(usdc_address).to_xdr_sc_address()
        ])),
        ("ResData-USDC Symbol", scval.to_symbol(f"ResData_{usdc_address}")),
        ("ResData Address", Address(usdc_address).to_xdr_sc_address()),
        ("USDC Address", Address(usdc_address).to_xdr_sc_address()),
    ]

    for pattern_name, key_value in test_patterns:
        try:
            print(f"\nQuerying {pattern_name} for {pool_address[:8]}...")

            ledger_key = xdr.LedgerKey(
                type=xdr.LedgerEntryType.CONTRACT_DATA,
                contract_data=xdr.LedgerKeyContractData(
                    contract=Address(pool_address).to_xdr_sc_address(),
                    key=key_value,
                    durability=xdr.ContractDataDurability.PERSISTENT
                )
            )

            response = await server.get_ledger_entries([ledger_key])

            if response.entries:
                print(f"✅ Found {len(response.entries)} entries for {pattern_name}")
                for entry in response.entries:
                    entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
                    value = entry_data.contract_data.val
                    native_value = scval.to_native(value)
                    print(f"   Type: {type(native_value)}")

                    if isinstance(native_value, dict):
                        keys = list(native_value.keys())
                        print(f"   Keys: {keys[:10]}...")  # First 10 keys
                        if 'b_rate' in native_value:
                            print(f"   🎯 Found b_rate: {native_value['b_rate']}")
                        if 'd_rate' in native_value:
                            print(f"   🎯 Found d_rate: {native_value['d_rate']}")
                        if 'b_supply' in native_value:
                            print(f"   🎯 Found b_supply: {native_value['b_supply']}")
                    elif isinstance(native_value, list):
                        print(f"   List with {len(native_value)} items")
                        if len(native_value) > 0:
                            print(f"   First item: {native_value[0]}")
                    else:
                        print(f"   Value: {str(native_value)[:100]}...")
            else:
                print(f"❌ No entries found for {pattern_name}")

        except Exception as e:
            print(f"❌ {pattern_name} query failed: {e}")
            # Don't print full traceback for each one, just the error
            continue

    await server.close()

if __name__ == '__main__':
    asyncio.run(test_direct_ledger_query())