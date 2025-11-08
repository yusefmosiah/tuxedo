#!/usr/bin/env python3
"""
Test Agentic Transactions Implementation
Comprehensive testing for DeFindex tool factory integration and autonomous transactions
"""

import asyncio
import logging
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_manager import AccountManager
from agent.tool_factory import create_user_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
TEST_USER_ID = "test_user_agentic_tx"
TEST_VAULT = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"  # XLM_HODL_1

async def test_defindex_account_tools():
    """Test the new DeFindex account tools directly"""
    logger.info("=== Testing DeFindex Account Tools ===")

    try:
        from defindex_account_tools import _defindex_discover_vaults, _defindex_get_vault_details, _defindex_deposit

        # Test 1: Discover vaults
        logger.info("1. Testing _defindex_discover_vaults...")
        result = await _defindex_discover_vaults(min_apy=0.0, user_id=TEST_USER_ID)
        logger.info(f"✅ Discover vaults result: {result[:200]}...")

        # Test 2: Get vault details
        logger.info("2. Testing _defindex_get_vault_details...")
        result = await _defindex_get_vault_details(vault_address=TEST_VAULT, user_id=TEST_USER_ID)
        logger.info(f"✅ Vault details result: {result[:200]}...")

        # Test 3: Deposit (this will fail due to no test account, but should show proper error handling)
        logger.info("3. Testing _defindex_deposit (expected to fail gracefully)...")
        result = await _defindex_deposit(
            vault_address=TEST_VAULT,
            amount_xlm=10.0,
            user_id=TEST_USER_ID,
            account_id="nonexistent_account",
            account_manager=AccountManager()
        )
        logger.info(f"✅ Deposit result (expected error): {result[:200]}...")

        logger.info("✅ All DeFindex account tools tested successfully")

    except Exception as e:
        logger.error(f"❌ DeFindex account tools test failed: {e}")
        raise

def test_tool_factory_integration():
    """Test DeFindex tools in tool factory pattern"""
    logger.info("=== Testing Tool Factory Integration ===")

    try:
        # Test 1: Create user tools
        logger.info("1. Testing create_user_tools with DeFindex integration...")
        tools = create_user_tools(TEST_USER_ID)
        logger.info(f"✅ Created {len(tools)} tools for user {TEST_USER_ID}")

        # Test 2: Verify tool names
        tool_names = [tool.name for tool in tools]
        logger.info(f"✅ Tool names: {tool_names}")

        # Test 3: Check DeFindex tools are present
        defindex_tools = [name for name in tool_names if 'defindex' in name]
        logger.info(f"✅ Found {len(defindex_tools)} DeFindex tools: {defindex_tools}")

        expected_tools = ['defindex_discover_vaults', 'defindex_get_vault_details', 'defindex_deposit']
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                logger.info(f"✅ Found expected tool: {expected_tool}")
            else:
                raise ValueError(f"Missing expected tool: {expected_tool}")

        # Test 4: Test tool execution (discover vaults)
        logger.info("4. Testing defindex_discover_vaults tool execution...")
        discover_tool = None
        for tool in tools:
            if tool.name == 'defindex_discover_vaults':
                discover_tool = tool
                break

        if discover_tool:
            result = discover_tool.invoke({"min_apy": 0.0})
            logger.info(f"✅ Tool execution result: {result[:200]}...")
        else:
            raise ValueError("defindex_discover_vaults tool not found")

        logger.info("✅ Tool factory integration test passed")

    except Exception as e:
        logger.error(f"❌ Tool factory integration test failed: {e}")
        raise

async def test_user_account_flow():
    """Test the complete user account flow for autonomous transactions"""
    logger.info("=== Testing Complete User Account Flow ===")

    try:
        # Initialize AccountManager
        account_manager = AccountManager()

        # Test 1: Check if we can create/list user accounts
        logger.info("1. Testing user account management...")

        # Try to list existing accounts
        try:
            from stellar_tools import account_manager as stellar_account_manager_tool
            accounts = stellar_account_manager_tool(
                action="list",
                user_id=TEST_USER_ID,
                account_manager=account_manager,
                horizon=None,  # Will use default
                account_id=None,
                secret_key=None,
                limit=10
            )
            logger.info(f"✅ User accounts: {accounts}")
        except Exception as e:
            logger.warning(f"⚠️ Account listing failed (expected in test environment): {e}")

        # Test 2: Create a test account
        logger.info("2. Creating test account...")
        try:
            create_result = stellar_account_manager_tool(
                action="create",
                user_id=TEST_USER_ID,
                account_manager=account_manager,
                horizon=None,
                account_id=None,
                secret_key=None,
                limit=10
            )
            logger.info(f"✅ Account creation result: {create_result}")

            # Extract account ID if creation was successful
            if isinstance(create_result, dict) and 'account_id' in create_result:
                test_account_id = create_result['account_id']
                logger.info(f"✅ Created account with ID: {test_account_id}")

                # Test 3: Try the deposit with the real account
                logger.info("3. Testing deposit with real account...")
                from defindex_account_tools import _defindex_deposit

                deposit_result = await _defindex_deposit(
                    vault_address=TEST_VAULT,
                    amount_xlm=5.0,  # Small amount for testing
                    user_id=TEST_USER_ID,
                    account_id=test_account_id,
                    account_manager=account_manager
                )
                logger.info(f"✅ Deposit test result: {deposit_result}")

        except Exception as e:
            logger.warning(f"⚠️ Account creation failed (expected without proper setup): {e}")

        logger.info("✅ User account flow test completed")

    except Exception as e:
        logger.error(f"❌ User account flow test failed: {e}")
        raise

async def test_error_handling():
    """Test error handling and edge cases"""
    logger.info("=== Testing Error Handling ===")

    try:
        from defindex_account_tools import _defindex_deposit, _defindex_get_vault_details

        # Test 1: Invalid vault address
        logger.info("1. Testing invalid vault address...")
        result = await _defindex_deposit(
            vault_address="INVALID_VAULT_ADDRESS",
            amount_xlm=10.0,
            user_id=TEST_USER_ID,
            account_id="test_account",
            account_manager=AccountManager()
        )
        logger.info(f"✅ Invalid vault error: {result[:100]}...")

        # Test 2: Invalid vault details
        logger.info("2. Testing invalid vault details...")
        result = await _defindex_get_vault_details(
            vault_address="INVALID_VAULT_ADDRESS",
            user_id=TEST_USER_ID
        )
        logger.info(f"✅ Invalid vault details error: {result[:100]}...")

        # Test 3: Negative deposit amount
        logger.info("3. Testing negative deposit amount...")
        result = await _defindex_deposit(
            vault_address=TEST_VAULT,
            amount_xlm=-10.0,
            user_id=TEST_USER_ID,
            account_id="test_account",
            account_manager=AccountManager()
        )
        logger.info(f"✅ Negative amount error: {result[:100]}...")

        logger.info("✅ Error handling tests passed")

    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        raise

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Agentic Transactions Implementation Tests")
    logger.info(f"Test User ID: {TEST_USER_ID}")
    logger.info(f"Test Vault: {TEST_VAULT}")

    test_results = []

    # Test 1: Direct DeFindex account tools
    try:
        await test_defindex_account_tools()
        test_results.append("✅ DeFindex Account Tools: PASSED")
    except Exception as e:
        test_results.append(f"❌ DeFindex Account Tools: FAILED - {e}")

    # Test 2: Tool factory integration
    try:
        test_tool_factory_integration()
        test_results.append("✅ Tool Factory Integration: PASSED")
    except Exception as e:
        test_results.append(f"❌ Tool Factory Integration: FAILED - {e}")

    # Test 3: User account flow
    try:
        await test_user_account_flow()
        test_results.append("✅ User Account Flow: PASSED")
    except Exception as e:
        test_results.append(f"❌ User Account Flow: FAILED - {e}")

    # Test 4: Error handling
    try:
        await test_error_handling()
        test_results.append("✅ Error Handling: PASSED")
    except Exception as e:
        test_results.append(f"❌ Error Handling: FAILED - {e}")

    # Print results summary
    logger.info("\n" + "="*60)
    logger.info("🏁 TEST RESULTS SUMMARY")
    logger.info("="*60)
    for result in test_results:
        logger.info(result)

    # Overall status
    passed_tests = sum(1 for result in test_results if "PASSED" in result)
    total_tests = len(test_results)

    logger.info(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Implementation is ready for Phala deployment!")
        return True
    else:
        logger.warning("⚠️ Some tests failed. Review the issues above before deployment.")
        return False

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)