#!/usr/bin/env python3
"""
Test the fixed Blend query implementation

This script tests the get_reserve() function with the corrected
decimal scaling (12 decimals instead of 7).
"""

import asyncio
import os
import sys
import logging
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import blend_get_reserve_apy, BLEND_MAINNET_CONTRACTS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_reserve_query():
    """Test querying reserve APY data with fixed decimal scaling"""

    # Initialize
    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)
    account_manager = AccountManager()

    # Test with Comet pool and USDC
    pool_address = BLEND_MAINNET_CONTRACTS['comet']
    usdc_address = BLEND_MAINNET_CONTRACTS['usdc']

    user_id = "agent"  # Use agent user ID which should have funded accounts

    try:
        logger.info("=" * 80)
        logger.info("Testing Blend Reserve Query with Fixed Decimal Scaling")
        logger.info("=" * 80)
        logger.info(f"Pool: Comet ({pool_address[:8]}...)")
        logger.info(f"Asset: USDC ({usdc_address[:8]}...)")
        logger.info("")

        # Call the fixed function
        result = await blend_get_reserve_apy(
            pool_address=pool_address,
            asset_address=usdc_address,
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            network="mainnet"
        )

        logger.info("=" * 80)
        logger.info("RESULT:")
        logger.info("=" * 80)

        if 'error' in result:
            logger.error(f"❌ Error: {result['error']}")
            return False

        # Display results
        logger.info(f"✅ Asset: {result.get('asset_symbol', 'Unknown')}")
        logger.info(f"   Supply APY: {result.get('supply_apy', 0):.2f}%")
        logger.info(f"   Borrow APY: {result.get('borrow_apy', 0):.2f}%")
        logger.info(f"   Total Supplied: {result.get('total_supplied', 0):,.0f}")
        logger.info(f"   Total Borrowed: {result.get('total_borrowed', 0):,.0f}")
        logger.info(f"   Utilization: {result.get('utilization', 0):.2%}")
        logger.info(f"   Data Source: {result.get('data_source', 'unknown')}")
        logger.info("")

        # Check if we got positive APY values
        supply_apy = result.get('supply_apy', 0)
        borrow_apy = result.get('borrow_apy', 0)

        if supply_apy > 0 or borrow_apy > 0:
            logger.info("✅ SUCCESS: Got positive APY values!")
            return True
        else:
            logger.warning("⚠️  APY values are zero - may need further investigation")
            logger.info("   This could mean:")
            logger.info("   1. The reserve has no activity")
            logger.info("   2. The rate calculation needs adjustment")
            logger.info("   3. The rate fields have different meanings")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}", exc_info=True)
        return False

    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_reserve_query())
    sys.exit(0 if success else 1)
