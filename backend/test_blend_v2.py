#!/usr/bin/env python3
"""
Test Blend V2 implementation using get_ledger_entries

This version requires NO ACCOUNT - uses direct ledger queries!
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_get_reserve_apy_v2 import blend_get_reserve_apy_v2

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test pools and assets
BLEND_MAINNET_CONTRACTS = {
    'comet': 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM',
    'usdc': 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75',
}

async def test_blend_v2():
    """Test the new V2 implementation (no account needed)"""

    # Initialize
    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)
    account_manager = AccountManager()

    pool_address = BLEND_MAINNET_CONTRACTS['comet']
    usdc_address = BLEND_MAINNET_CONTRACTS['usdc']

    user_id = "test"  # Doesn't matter - no account needed!

    try:
        logger.info("=" * 80)
        logger.info("Testing Blend V2 - get_ledger_entries (NO ACCOUNT NEEDED!)")
        logger.info("=" * 80)
        logger.info(f"Pool: Comet ({pool_address[:8]}...)")
        logger.info(f"Asset: USDC ({usdc_address[:8]}...)")
        logger.info("")

        result = await blend_get_reserve_apy_v2(
            pool_address=pool_address,
            asset_address=usdc_address,
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            network="mainnet"
        )

        logger.info("=" * 80)
        logger.info("✅ SUCCESS! Results:")
        logger.info("=" * 80)
        logger.info(f"Asset: {result.get('asset_symbol', 'Unknown')}")
        logger.info(f"Supply APY: {result.get('supply_apy', 0):.4f}%")
        logger.info(f"Borrow APY: {result.get('borrow_apy', 0):.4f}%")
        logger.info(f"Total Supplied: {result.get('total_supplied', 0):,.0f}")
        logger.info(f"Total Borrowed: {result.get('total_borrowed', 0):,.0f}")
        logger.info(f"Utilization: {result.get('utilization', 0):.2%}")
        logger.info(f"Data Source: {result.get('data_source', 'unknown')}")
        logger.info(f"Latest Ledger: {result.get('latest_ledger', 'unknown')}")
        logger.info("")
        logger.info(f"Raw rates:")
        logger.info(f"  b_rate: {result.get('b_rate', 0)}")
        logger.info(f"  d_rate: {result.get('d_rate', 0)}")
        logger.info("")

        supply_apy = result.get('supply_apy', 0)
        borrow_apy = result.get('borrow_apy', 0)

        if supply_apy > 0 or borrow_apy > 0:
            logger.info("🎉 SUCCESS! Got positive APY values!")
            logger.info("✅ Blend V2 query working perfectly - NO ACCOUNT NEEDED!")
            return True
        else:
            logger.warning("⚠️  APY values are zero - need to investigate further")
            logger.info("   Check if rates are being calculated correctly")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_blend_v2())
    sys.exit(0 if success else 1)
