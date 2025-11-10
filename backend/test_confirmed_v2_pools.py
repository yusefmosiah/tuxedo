#!/usr/bin/env python3
"""
Test with CONFIRMED V2 pool addresses from stellar.expert

These are verified V2 pools:
- Fixed Pool V2: CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD
- YieldBlox V2: CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS
- Orbit Pool V2: CAE7QVOMBLZ53CDRGK3UNRRHG5EZ5NQA7HHTFASEMYBWHG6MDFZTYHXC
- Forex Pool V2: CBYOBT7ZCCLQCBUYYIABZLSEGDPEUWXCUXQTZYOG3YBDR7U357D5ZIRF
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_get_reserve_apy_v2 import blend_get_reserve_apy_v2

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CONFIRMED V2 POOLS
V2_POOLS = {
    'fixed': 'CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD',
    'yieldBlox': 'CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS',
    'orbit': 'CAE7QVOMBLZ53CDRGK3UNRRHG5EZ5NQA7HHTFASEMYBWHG6MDFZTYHXC',
    'forex': 'CBYOBT7ZCCLQCBUYYIABZLSEGDPEUWXCUXQTZYOG3YBDR7U357D5ZIRF',
}

TOKENS = {
    'usdc': 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75',
    'xlm': 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA',
}

async def test_v2_pool(pool_name, pool_address, asset_name, asset_address):
    """Test a specific V2 pool"""

    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)
    account_manager = AccountManager()

    try:
        logger.info("=" * 80)
        logger.info(f"Testing {pool_name} Pool with {asset_name}")
        logger.info("=" * 80)
        logger.info(f"Pool: {pool_address}")
        logger.info(f"Asset: {asset_address}")
        logger.info("")

        result = await blend_get_reserve_apy_v2(
            pool_address=pool_address,
            asset_address=asset_address,
            user_id="test",
            soroban_server=soroban_server,
            account_manager=account_manager,
            network="mainnet"
        )

        if 'error' in result or not result:
            logger.error(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False

        logger.info("✅ SUCCESS! Results:")
        logger.info(f"  Asset: {result.get('asset_symbol')}")
        logger.info(f"  Supply APY: {result.get('supply_apy', 0):.4f}%")
        logger.info(f"  Borrow APY: {result.get('borrow_apy', 0):.4f}%")
        logger.info(f"  Total Supplied: {result.get('total_supplied', 0):,.0f}")
        logger.info(f"  Total Borrowed: {result.get('total_borrowed', 0):,.0f}")
        logger.info(f"  Utilization: {result.get('utilization', 0):.2%}")
        logger.info(f"  Data Source: {result.get('data_source')}")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"❌ Exception: {e}", exc_info=True)
        return False

    finally:
        await soroban_server.close()

async def test_all_pools():
    """Test all V2 pools"""

    results = []

    # Test Fixed pool with USDC
    logger.info("\n" + "🧪 TEST 1: Fixed Pool with USDC")
    success = await test_v2_pool('Fixed', V2_POOLS['fixed'], 'USDC', TOKENS['usdc'])
    results.append(('Fixed/USDC', success))

    await asyncio.sleep(1)  # Rate limiting

    # Test YieldBlox pool with USDC
    logger.info("\n" + "🧪 TEST 2: YieldBlox Pool with USDC")
    success = await test_v2_pool('YieldBlox', V2_POOLS['yieldBlox'], 'USDC', TOKENS['usdc'])
    results.append(('YieldBlox/USDC', success))

    await asyncio.sleep(1)

    # Test Orbit pool with USDC
    logger.info("\n" + "🧪 TEST 3: Orbit Pool with USDC")
    success = await test_v2_pool('Orbit', V2_POOLS['orbit'], 'USDC', TOKENS['usdc'])
    results.append(('Orbit/USDC', success))

    await asyncio.sleep(1)

    # Test Fixed pool with XLM
    logger.info("\n" + "🧪 TEST 4: Fixed Pool with XLM")
    success = await test_v2_pool('Fixed', V2_POOLS['fixed'], 'XLM', TOKENS['xlm'])
    results.append(('Fixed/XLM', success))

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")

    total = len(results)
    passed = sum(1 for _, s in results if s)
    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    logger.info("=" * 80)

    return passed == total

if __name__ == "__main__":
    import sys
    success = asyncio.run(test_all_pools())
    sys.exit(0 if success else 1)
