#!/usr/bin/env python3
"""
Import agent account and test Blend queries
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import blend_get_reserve_apy, BLEND_MAINNET_CONTRACTS

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_with_agent_account():
    """Test Blend queries using the agent account"""

    # Get agent secret from env
    agent_secret = os.getenv('AGENT_STELLAR_SECRET')
    agent_public = "GA4KBIWEVNXJPT545A6YYZPZUFYHCG4LBDGN437PDRTBLGOE3KIW5KBZ"

    if not agent_secret:
        logger.error("❌ AGENT_STELLAR_SECRET not found in environment")
        logger.info("Please set AGENT_STELLAR_SECRET environment variable")
        return False

    # Initialize
    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)
    account_manager = AccountManager()

    user_id = "system_agent"

    try:
        # Check if agent account already exists
        accounts = account_manager.get_user_accounts(user_id)
        account_id = None

        if accounts:
            logger.info(f"✅ Found existing agent account: {accounts[0]['id']}")
            account_id = accounts[0]['id']
        else:
            # Import agent account
            logger.info(f"Importing agent account {agent_public[:8]}...")
            result = account_manager.import_account(
                user_id=user_id,
                chain="stellar",
                private_key=agent_secret,
                name="Agent Account",
                network="mainnet"
            )

            if result.get('success'):
                account_id = result['account_id']
                logger.info(f"✅ Imported agent account: {account_id}")
            else:
                logger.error(f"❌ Failed to import: {result.get('error')}")
                return False

        # Test Blend query
        logger.info("\n" + "=" * 80)
        logger.info("Testing Blend Reserve Query")
        logger.info("=" * 80)

        pool_address = BLEND_MAINNET_CONTRACTS['comet']
        usdc_address = BLEND_MAINNET_CONTRACTS['usdc']

        logger.info(f"Pool: Comet ({pool_address[:8]}...)")
        logger.info(f"Asset: USDC ({usdc_address[:8]}...)")
        logger.info("")

        result = await blend_get_reserve_apy(
            pool_address=pool_address,
            asset_address=usdc_address,
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            network="mainnet"
        )

        logger.info("=" * 80)
        logger.info("RESULTS:")
        logger.info("=" * 80)

        if 'error' in result:
            logger.error(f"❌ Error: {result['error']}")
            return False

        logger.info(f"✅ Asset: {result.get('asset_symbol', 'Unknown')}")
        logger.info(f"   Supply APY: {result.get('supply_apy', 0):.2f}%")
        logger.info(f"   Borrow APY: {result.get('borrow_apy', 0):.2f}%")
        logger.info(f"   Total Supplied: {result.get('total_supplied', 0):,.0f}")
        logger.info(f"   Total Borrowed: {result.get('total_borrowed', 0):,.0f}")
        logger.info(f"   Utilization: {result.get('utilization', 0):.2%}")
        logger.info(f"   Data Source: {result.get('data_source', 'unknown')}")
        logger.info("")

        supply_apy = result.get('supply_apy', 0)
        borrow_apy = result.get('borrow_apy', 0)

        if supply_apy > 0 or borrow_apy > 0:
            logger.info("🎉 SUCCESS! Got positive APY values!")
            logger.info("✅ Blend query fix is working correctly!")
            return True
        else:
            logger.warning("⚠️  APY values are zero")
            logger.info("   Need to investigate rate structure further")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_with_agent_account())
    sys.exit(0 if success else 1)
