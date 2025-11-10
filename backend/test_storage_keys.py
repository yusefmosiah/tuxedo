#!/usr/bin/env python3
"""
Test different storage key patterns to find the correct one
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk import xdr, scval
from stellar_sdk.address import Address

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_storage_keys():
    """Test different storage key patterns"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)

    pool_address = 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM'
    usdc_address = 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'

    # Different key patterns to test
    key_patterns = [
        # Pattern from V2 implementation
        ("ResData", scval.to_vec([
            scval.to_symbol("ResData"),
            scval.to_address(Address(usdc_address))
        ])),

        # Try with just the symbol
        ("ResData_Symbol", scval.to_symbol("ResData")),

        # Try with different enum patterns
        ("ResData_Address_Single", scval.to_address(Address(usdc_address))),

        # Try with different key names
        ("ReserveData", scval.to_vec([
            scval.to_symbol("ReserveData"),
            scval.to_address(Address(usdc_address))
        ])),

        ("Reserve", scval.to_vec([
            scval.to_symbol("Reserve"),
            scval.to_address(Address(usdc_address))
        ])),

        # Try with USDC as string
        ("ResData_String", scval.to_vec([
            scval.to_symbol("ResData"),
            scval.to_string(usdc_address)
        ])),

        # Try with tuple pattern
        ("ResData_Tuple", scval.to_vec([
            scval.to_symbol("ResData"),
            scval.to_vec([
                scval.to_symbol("Address"),
                scval.to_address(Address(usdc_address))
            ])
        ])),
    ]

    try:
        logger.info("Testing different storage key patterns...")
        logger.info(f"Pool: {pool_address}")
        logger.info(f"Asset: {usdc_address}")
        logger.info("")

        for name, key_value in key_patterns:
            logger.info(f"Testing pattern: {name}")

            ledger_key = xdr.LedgerKey(
                type=xdr.LedgerEntryType.CONTRACT_DATA,
                contract_data=xdr.LedgerKeyContractData(
                    contract=Address(pool_address).to_xdr_sc_address(),
                    key=key_value,
                    durability=xdr.ContractDataDurability.PERSISTENT
                )
            )

            try:
                response = await soroban_server.get_ledger_entries([ledger_key])

                if response.entries:
                    logger.info(f"  ✅ FOUND {len(response.entries)} entries!")

                    for i, entry in enumerate(response.entries):
                        if entry.xdr:
                            try:
                                entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
                                if entry_data.contract_data:
                                    value = entry_data.contract_data.val
                                    native_value = scval.to_native(value)
                                    logger.info(f"    Entry {i}: {native_value}")
                            except Exception as e:
                                logger.warning(f"    Could not decode entry {i}: {e}")
                else:
                    logger.info(f"  ❌ No entries found")

            except Exception as e:
                logger.error(f"  ❌ Error: {e}")

            logger.info("")

        return True

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_storage_keys())
    print(f"\nTest {'COMPLETED' if success else 'FAILED'}")