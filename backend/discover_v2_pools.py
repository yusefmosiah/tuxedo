#!/usr/bin/env python3
"""
Discover actual V2 pool addresses by querying the Pool Factory

The Pool Factory contract maintains a registry of all pools.
This script queries it to find the real V2 pools.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk import TransactionBuilder, scval, Address
from stellar_sdk.keypair import Keypair

# Load environment
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# From blend-contracts-v2/pool/src/storage.rs
POOL_FACTORY = 'CDSYOAVXFY7SM5S64IZPPPYB4GVGGLMQVFREPSQQEZVIWXX5R23G4QSU'
BACKSTOP = 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7'

async def discover_v2_pools():
    """Query the Pool Factory to find deployed V2 pools"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)

    try:
        logger.info("=" * 80)
        logger.info("Discovering Blend V2 Pools from Pool Factory")
        logger.info("=" * 80)
        logger.info(f"Pool Factory: {POOL_FACTORY}")
        logger.info(f"Backstop: {BACKSTOP}")
        logger.info("")

        # Method 1: Try to query the backstop for pool list
        # Backstop should have a function to list all pools
        logger.info("Method 1: Querying Backstop contract...")

        # Need a dummy account for simulation
        dummy_keypair = Keypair.random()
        dummy_account = await soroban_server.load_account(dummy_keypair.public_key)

        # Try calling a potential get_pools or list_pools function
        for func_name in ['get_pools', 'list_pools', 'pools', 'get_pool_list']:
            try:
                logger.info(f"  Trying function: {func_name}")

                tx = (
                    TransactionBuilder(
                        dummy_account,
                        'Public Global Stellar Network ; September 2015',
                        base_fee=100
                    )
                    .set_timeout(30)
                    .append_invoke_contract_function_op(
                        contract_id=BACKSTOP,
                        function_name=func_name,
                        parameters=[]
                    )
                    .build()
                )

                result = await soroban_server.simulate_transaction(tx)

                if not result.error:
                    logger.info(f"✅ SUCCESS! Function {func_name} exists")
                    if result.results:
                        pools = scval.to_native(result.results[0].return_value)
                        logger.info(f"Found pools: {pools}")
                        return pools
                else:
                    logger.debug(f"  ❌ {func_name}: {result.error}")

            except Exception as e:
                logger.debug(f"  ❌ {func_name}: {e}")

        # Method 2: Try Pool Factory
        logger.info("\nMethod 2: Querying Pool Factory contract...")

        for func_name in ['get_pools', 'list_pools', 'pools', 'deployed_pools']:
            try:
                logger.info(f"  Trying function: {func_name}")

                tx = (
                    TransactionBuilder(
                        dummy_account,
                        'Public Global Stellar Network ; September 2015',
                        base_fee=100
                    )
                    .set_timeout(30)
                    .append_invoke_contract_function_op(
                        contract_id=POOL_FACTORY,
                        function_name=func_name,
                        parameters=[]
                    )
                    .build()
                )

                result = await soroban_server.simulate_transaction(tx)

                if not result.error:
                    logger.info(f"✅ SUCCESS! Function {func_name} exists")
                    if result.results:
                        pools = scval.to_native(result.results[0].return_value)
                        logger.info(f"Found pools: {pools}")
                        return pools
                else:
                    logger.debug(f"  ❌ {func_name}: {result.error}")

            except Exception as e:
                logger.debug(f"  ❌ {func_name}: {e}")

        # Method 3: Check storage directly via getLedgerEntries
        logger.info("\nMethod 3: Checking contract storage...")
        logger.info("  (This would require knowing the storage key format)")

        logger.info("\n" + "=" * 80)
        logger.info("Could not auto-discover pools")
        logger.info("Manual steps:")
        logger.info("1. Visit https://mainnet.blend.capital")
        logger.info("2. Note the pool contract addresses from the UI")
        logger.info("3. Verify they have get_reserve function by testing")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error during discovery: {e}", exc_info=True)

    finally:
        await soroban_server.close()

if __name__ == "__main__":
    asyncio.run(discover_v2_pools())
