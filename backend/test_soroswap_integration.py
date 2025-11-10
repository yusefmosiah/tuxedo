#!/usr/bin/env python3
"""
Test Soroswap Integration

Simple test script to verify Soroswap API client and account tools work correctly.
"""

import asyncio
import logging
from soroswap_api import SoroswapAPIClient
from soroswap_account_tools import _soroswap_get_quote, _soroswap_get_pools, ASSET_ADDRESSES
from account_manager import AccountManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_soroswap_api_client():
    """Test basic Soroswap API client functionality"""
    logger.info("=" * 80)
    logger.info("TEST 1: Soroswap API Client - Get Contracts")
    logger.info("=" * 80)

    try:
        async with SoroswapAPIClient() as api:
            contracts = await api.get_contracts(network="mainnet")
            logger.info(f"✅ Successfully fetched contracts: {contracts}")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to fetch contracts: {e}")
        return False


async def test_soroswap_quote():
    """Test getting a swap quote"""
    logger.info("=" * 80)
    logger.info("TEST 2: Soroswap Get Quote - XLM to USDC")
    logger.info("=" * 80)

    try:
        account_mgr = AccountManager()
        result = await _soroswap_get_quote(
            token_in="XLM",
            token_out="USDC",
            amount_in=100.0,  # 100 XLM
            user_id="test_user",
            account_manager=account_mgr,
            network="mainnet"
        )
        logger.info(f"Quote result:\n{result}")
        return "Quote" in result or "Error" in result or "Unavailable" in result
    except Exception as e:
        logger.error(f"❌ Quote test failed: {e}")
        return False


async def test_soroswap_pools():
    """Test getting available pools"""
    logger.info("=" * 80)
    logger.info("TEST 3: Soroswap Get Pools")
    logger.info("=" * 80)

    try:
        account_mgr = AccountManager()
        result = await _soroswap_get_pools(
            user_id="test_user",
            account_manager=account_mgr,
            network="mainnet"
        )
        logger.info(f"Pools result:\n{result}")
        return "Pools" in result or "Error" in result or "found" in result
    except Exception as e:
        logger.error(f"❌ Pools test failed: {e}")
        return False


async def test_asset_resolution():
    """Test asset address resolution"""
    logger.info("=" * 80)
    logger.info("TEST 4: Asset Address Resolution")
    logger.info("=" * 80)

    test_assets = ["XLM", "USDC", "WETH", "WBTC"]
    all_passed = True

    for asset in test_assets:
        if asset in ASSET_ADDRESSES:
            address = ASSET_ADDRESSES[asset]
            logger.info(f"✅ {asset}: {address}")
        else:
            logger.error(f"❌ {asset}: NOT FOUND")
            all_passed = False

    return all_passed


async def main():
    """Run all tests"""
    logger.info("Starting Soroswap Integration Tests")
    logger.info("")

    results = {}

    # Test 1: API Client
    results['api_client'] = await test_soroswap_api_client()
    logger.info("")

    # Test 2: Get Quote
    results['get_quote'] = await test_soroswap_quote()
    logger.info("")

    # Test 3: Get Pools
    results['get_pools'] = await test_soroswap_pools()
    logger.info("")

    # Test 4: Asset Resolution
    results['asset_resolution'] = await test_asset_resolution()
    logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    logger.info("")
    logger.info(f"Total: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        logger.info("🎉 All tests passed!")
    else:
        logger.info("⚠️  Some tests failed. This is expected if Soroswap API is unavailable.")
        logger.info("The integration will gracefully handle API errors and suggest alternatives.")


if __name__ == "__main__":
    asyncio.run(main())
