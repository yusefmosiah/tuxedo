#!/usr/bin/env python3
"""
Test if the backstop contract exists
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

async def test_backstop():
    """Test if the backstop contract exists"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)

    backstop_address = 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7'
    pool_address = 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM'

    try:
        logger.info("Testing backstop contract...")
        logger.info(f"Backstop: {backstop_address}")
        logger.info(f"Pool: {pool_address}")
        logger.info("")

        # Test backstop instance
        logger.info("1. Testing backstop contract instance...")
        instance_key = xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(backstop_address).to_xdr_sc_address(),
                key=scval.to_symbol("__instance__"),
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )

        try:
            response = await soroban_server.get_ledger_entries([instance_key])
            if response.entries:
                logger.info(f"  ✅ Backstop contract exists!")
            else:
                logger.error(f"  ❌ Backstop contract not found!")
        except Exception as e:
            logger.error(f"  ❌ Error checking backstop: {e}")

        logger.info("")

        # Test pool instance
        logger.info("2. Testing pool contract instance...")
        pool_instance_key = xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(pool_address).to_xdr_sc_address(),
                key=scval.to_symbol("__instance__"),
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )

        try:
            response = await soroban_server.get_ledger_entries([pool_instance_key])
            if response.entries:
                logger.info(f"  ✅ Pool contract exists!")
            else:
                logger.error(f"  ❌ Pool contract not found!")
        except Exception as e:
            logger.error(f"  ❌ Error checking pool: {e}")

        return True

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_backstop())
    print(f"\nTest {'COMPLETED' if success else 'FAILED'}")