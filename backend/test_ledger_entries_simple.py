#!/usr/bin/env python3
"""
Simple test for get_ledger_entries to debug the issue
"""

import asyncio
import os
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk import xdr, scval
from stellar_sdk.address import Address

async def test_get_ledger_entries():
    """Test get_ledger_entries directly"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)

    # Test with a simple contract data key
    pool_address = 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM'
    usdc_address = 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'

    try:
        # Create ledger key for ResData
        ledger_key = xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(pool_address).to_xdr_sc_address(),
                key=scval.to_vec([
                    scval.to_symbol("ResData"),
                    scval.to_address(Address(usdc_address))
                ]),
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )

        print("Querying ledger entries...")
        response = await soroban_server.get_ledger_entries([ledger_key])

        print(f"Response type: {type(response)}")
        print(f"Latest ledger: {response.latest_ledger}")
        print(f"Number of entries: {len(response.entries)}")

        for i, entry in enumerate(response.entries):
            print(f"Entry {i}:")
            print(f"  Key: {entry.key}")
            print(f"  Last modified: {entry.last_modified_ledger_seq}")
            print(f"  Live until: {entry.live_until_ledger_seq}")
            print(f"  XDR length: {len(entry.xdr) if entry.xdr else 0}")

            if entry.xdr:
                try:
                    entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
                    print(f"  Entry type: {entry_data.type}")
                    if entry_data.contract_data:
                        value = entry_data.contract_data.val
                        print(f"  Value type: {value.type}")
                        native_value = scval.to_native(value)
                        print(f"  Native value: {native_value}")
                except Exception as e:
                    print(f"  Error parsing XDR: {e}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_get_ledger_entries())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")