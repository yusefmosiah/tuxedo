#!/usr/bin/env python3
"""
Test V2 implementation directly without soroban_operations wrapper
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

async def test_v2_direct():
    """Test V2 implementation directly"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)

    pool_address = 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM'
    usdc_address = 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'

    try:
        logger.info("Testing V2 implementation directly...")
        logger.info(f"Pool: {pool_address}")
        logger.info(f"Asset: {usdc_address}")

        # Create ledger keys for ResData and ResConfig
        # PoolDataKey::ResData(Address) encodes as Vec[Symbol("ResData"), Address(asset)]
        resdata_key = xdr.LedgerKey(
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

        resconfig_key = xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(pool_address).to_xdr_sc_address(),
                key=scval.to_vec([
                    scval.to_symbol("ResConfig"),
                    scval.to_address(Address(usdc_address))
                ]),
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )

        logger.info("Querying ledger entries...")
        response = await soroban_server.get_ledger_entries([resdata_key, resconfig_key])

        logger.info(f"Response: {response}")
        logger.info(f"Latest ledger: {response.latest_ledger}")
        logger.info(f"Number of entries: {len(response.entries)}")

        # Parse entries
        for i, entry in enumerate(response.entries):
            logger.info(f"Entry {i}:")
            logger.info(f"  Last modified: {entry.last_modified_ledger_seq}")
            logger.info(f"  Live until: {entry.live_until_ledger_seq}")

            if entry.xdr:
                try:
                    entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
                    logger.info(f"  Entry type: {entry_data.type}")

                    if entry_data.contract_data:
                        value = entry_data.contract_data.val
                        logger.info(f"  Value type: {value.type}")

                        # Try to decode the value
                        try:
                            native_value = scval.to_native(value)
                            logger.info(f"  Native value: {native_value}")

                            # If it's a map, log the keys
                            if isinstance(native_value, dict):
                                logger.info(f"  Map keys: {list(native_value.keys())}")

                        except Exception as decode_error:
                            logger.warning(f"  Could not decode value: {decode_error}")

                except Exception as xdr_error:
                    logger.warning(f"  Could not parse XDR: {xdr_error}")
            else:
                logger.warning("  No XDR data")

        return len(response.entries) > 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_v2_direct())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")