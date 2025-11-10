#!/usr/bin/env python3
"""
Test the current mainnet pools from mainnet.blend.capital
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

# Current mainnet pools from blend.capital
MAINNET_POOLS = {
    'fixed': 'CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD',
    'yieldBlox': 'CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS',
    'orbit': 'CAE7QVOMBLZ53CDRGK3UNRRHG5EZ5NQA7HHTFASEMYBWHG6MDFZTYHXC',
    'forex': 'CBYOBT7ZCCLQCBUYYIABZLSEGDPEUWXCUXQTZYOG3YBDR7U357D5ZIRF',
}

# Common tokens
TOKENS = {
    'blnd': 'CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY',
    'usdc': 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75',
    'xlm': 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA',
}

async def test_current_pools():
    """Test the current mainnet pools"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)

    try:
        logger.info("Testing current mainnet pools...")
        logger.info(f"RPC URL: {rpc_url}")
        logger.info("")

        # Test each pool
        for pool_name, pool_address in MAINNET_POOLS.items():
            logger.info(f"Testing {pool_name} pool: {pool_address}")

            # Test if pool exists
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
                    logger.info(f"  ✅ Pool exists!")

                    # Try to find some storage data
                    logger.info(f"  Looking for storage entries...")

                    # Try common patterns
                    patterns_to_test = [
                        ("ResData", scval.to_vec([
                            scval.to_symbol("ResData"),
                            scval.to_address(Address(TOKENS['usdc']))
                        ])),
                        ("ResData_XLM", scval.to_vec([
                            scval.to_symbol("ResData"),
                            scval.to_address(Address(TOKENS['xlm']))
                        ])),
                        ("ResData_BLND", scval.to_vec([
                            scval.to_symbol("ResData"),
                            scval.to_address(Address(TOKENS['blnd']))
                        ])),
                    ]

                    found_data = False
                    for pattern_name, key_value in patterns_to_test:
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
                                logger.info(f"    ✅ Found {pattern_name}: {len(response.entries)} entries")
                                found_data = True

                                # Parse first entry
                                entry = response.entries[0]
                                if entry.xdr:
                                    try:
                                        entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
                                        if entry_data.contract_data:
                                            value = entry_data.contract_data.val
                                            native_value = scval.to_native(value)
                                            logger.info(f"    Data: {type(native_value)} - {str(native_value)[:100]}...")
                                    except Exception as e:
                                        logger.warning(f"    Could not decode: {e}")
                        except Exception as e:
                            pass  # Silently continue

                    if not found_data:
                        logger.info(f"  ℹ️  No reserve data found with common patterns")

                else:
                    logger.error(f"  ❌ Pool not found!")
            except Exception as e:
                logger.error(f"  ❌ Error checking pool: {e}")

            logger.info("")

        return True

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_current_pools())
    print(f"\nTest {'COMPLETED' if success else 'FAILED'}")