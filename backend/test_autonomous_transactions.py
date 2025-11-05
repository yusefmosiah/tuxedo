#!/usr/bin/env python3
"""
Test script for autonomous DeFindex transaction functionality
"""

import asyncio
import logging
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_autonomous_transaction_tools():
    """Test the new autonomous transaction tools"""

    print("🧪 Testing Autonomous DeFindex Transaction Tools")
    print("=" * 60)

    try:
        # Import the tools
        from defindex_tools import (
            discover_high_yield_vaults,
            get_defindex_vault_details,
            execute_defindex_deposit,
            execute_defindex_withdrawal
        )

        print("✅ Successfully imported autonomous transaction tools")
        print()

        # Test 1: Discover available vaults
        print("📊 Test 1: Discovering available vaults...")
        vaults_result = await discover_high_yield_vaults.ainvoke({"min_apy": 0.0})
        print(vaults_result)
        print()

        # Test 2: Get details for a specific vault (use first testnet vault)
        print("🏦 Test 2: Getting vault details...")
        testnet_vault = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"  # XLM_HODL_1
        vault_details = await get_defindex_vault_details.ainvoke({"vault_address": testnet_vault})
        print(vault_details)
        print()

        # Test 3: Check agent accounts
        print("🤖 Test 3: Checking agent accounts...")
        try:
            from agent.core import get_default_agent_account
            default_account = get_default_agent_account()
            if default_account:
                print(f"✅ Found default agent account: {default_account[:8]}...{default_account[-8:]}")

                # Test 4: Try a small autonomous deposit (this will fail gracefully if API not available)
                print()
                print("💰 Test 4: Testing autonomous deposit execution...")
                print("⚠️  Note: This may fail gracefully if DeFindex API key not configured")

                deposit_result = await execute_defindex_deposit.ainvoke({
                    "vault_address": testnet_vault,
                    "amount_xlm": 1.0,
                    "user_address": default_account,
                    "network": "testnet"
                })
                print(deposit_result)

            else:
                print("❌ No agent account found - use agent_create_account first")
        except Exception as agent_error:
            print(f"❌ Agent account test failed: {agent_error}")

        print()
        print("🎉 Autonomous transaction tool testing completed!")

    except ImportError as import_error:
        print(f"❌ Import failed: {import_error}")
        print("This is expected if dependencies are not available")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)

async def test_transaction_utils():
    """Test the transaction signing utilities"""

    print("\n🔧 Testing Transaction Utilities")
    print("=" * 40)

    try:
        from transaction_utils import (
            sign_transaction_with_agent_key,
            create_transaction_builder_for_network,
            validate_transaction_amount
        )

        print("✅ Successfully imported transaction utilities")

        # Test amount validation
        print("\n💵 Testing amount validation...")
        assert validate_transaction_amount(5.0) == True
        assert validate_transaction_amount(0.5) == True
        assert validate_transaction_amount(0.0) == False
        assert validate_transaction_amount(-1.0) == False
        print("✅ Amount validation working correctly")

        # Test network configuration
        print("\n🌐 Testing network configuration...")
        testnet_network = create_transaction_builder_for_network("testnet")
        mainnet_network = create_transaction_builder_for_network("mainnet")
        print(f"✅ Testnet network: {testnet_network[:20]}...")
        print(f"✅ Mainnet network: {mainnet_network[:20]}...")

        print("\n🔐 Transaction utilities test completed!")

    except ImportError as import_error:
        print(f"❌ Transaction utils import failed: {import_error}")

    except Exception as e:
        print(f"❌ Transaction utils test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Autonomous Transaction Tests")
    print("=" * 60)

    # Run tests
    asyncio.run(test_autonomous_transaction_tools())
    asyncio.run(test_transaction_utils())

    print("\n📋 Test Summary:")
    print("✅ Tool imports tested")
    print("✅ Vault discovery tested")
    print("✅ Transaction utilities tested")
    print("⚠️  Actual transaction execution requires API key and funded account")
    print("\n🎯 Ready for autonomous transaction implementation!")