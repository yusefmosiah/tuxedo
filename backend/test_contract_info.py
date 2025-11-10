#!/usr/bin/env python3
"""
Test basic contract information
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

async def test_contract_info():
    """Test basic contract information"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)

    pool_address = 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM'
    usdc_address = 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'

    try:
        logger.info("Testing contract information...")
        logger.info(f"Pool: {pool_address}")
        logger.info(f"Asset: {usdc_address}")
        logger.info("")

        # Test 1: Get contract instance
        logger.info("1. Testing contract instance...")
        instance_key = xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(pool_address).to_xdr_sc_address(),
                key=scval.to_symbol("__instance__"),
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )

        try:
            response = await soroban_server.get_ledger_entries([instance_key])
            if response.entries:
                logger.info(f"  ✅ Contract instance found!")
                for i, entry in enumerate(response.entries):
                    if entry.xdr:
                        try:
                            entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
                            if entry_data.contract_data:
                                instance = entry_data.contract_data.contract_instance
                                logger.info(f"    Instance executable: {instance.executable}")
                                if instance.storage:
                                    logger.info(f"    Storage type: {instance.storage.type}")
                        except Exception as e:
                            logger.warning(f"    Could not parse instance: {e}")
            else:
                logger.error(f"  ❌ Contract instance not found - contract might not exist!")
        except Exception as e:
            logger.error(f"  ❌ Error getting contract instance: {e}")

        logger.info("")

        # Test 2: Try to find any storage at all
        logger.info("2. Looking for any storage entries...")

        # Try some common patterns
        common_keys = [
            ("Admin", scval.to_symbol("Admin")),
            ("Backstop", scval.to_symbol("Backstop")),
            ("BumpKey", scval.to_symbol("BumpKey")),
            ("Version", scval.to_symbol("Version")),
        ]

        for name, key_value in common_keys:
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
                    logger.info(f"  ✅ Found {name}: {len(response.entries)} entries")
                    break
            except:
                pass

        logger.info("")

        # Test 3: Check if USDC contract exists
        logger.info("3. Testing USDC contract instance...")
        usdc_instance_key = xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(usdc_address).to_xdr_sc_address(),
                key=scval.to_symbol("__instance__"),
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )

        try:
            response = await soroban_server.get_ledger_entries([usdc_instance_key])
            if response.entries:
                logger.info(f"  ✅ USDC contract exists!")
            else:
                logger.error(f"  ❌ USDC contract not found!")
        except Exception as e:
            logger.error(f"  ❌ Error checking USDC contract: {e}")

        return True

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_contract_info())
    print(f"\nTest {'COMPLETED' if success else 'FAILED'}")