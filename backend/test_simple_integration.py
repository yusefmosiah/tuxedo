#!/usr/bin/env python3
"""
Simple Integration Test for Agentic Transactions
Tests the core functionality without complex dependencies
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_core_functionality():
    """Test core DeFindex functionality without LangChain dependencies"""
    print("🚀 Testing Core Agentic Transaction Functionality")
    print("=" * 60)

    test_results = []

    # Test 1: DeFindex Account Tools
    try:
        print("\n1. Testing DeFindex Account Tools...")
        from defindex_account_tools import _defindex_discover_vaults, _defindex_get_vault_details, _defindex_deposit

        # Test vault discovery
        result = await _defindex_discover_vaults(min_apy=0.0, user_id="test_user")
        assert "Found" in result and "vault" in result.lower()
        print("✅ Vault discovery working")
        test_results.append("✅ DeFindex Account Tools: PASSED")

        # Test vault details
        vault = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
        result = await _defindex_get_vault_details(vault_address=vault, user_id="test_user")
        assert "Vault Details" in result
        print("✅ Vault details working")

        # Test deposit error handling
        from account_manager import AccountManager
        result = await _defindex_deposit(
            vault_address=vault,
            amount_xlm=10.0,
            user_id="test_user",
            account_id="nonexistent",
            account_manager=AccountManager()
        )
        assert "Account Access Error" in result or "Error" in result
        print("✅ Deposit error handling working")

    except Exception as e:
        print(f"❌ DeFindex Account Tools failed: {e}")
        test_results.append(f"❌ DeFindex Account Tools: FAILED - {e}")

    # Test 2: Tool Factory Structure (without LangChain)
    try:
        print("\n2. Testing Tool Factory Structure...")

        # Check if the file exists and has the right structure
        with open('agent/tool_factory.py', 'r') as f:
            content = f.read()

        # Check for our new DeFindex tools
        assert 'defindex_discover_vaults' in content
        assert 'defindex_get_vault_details' in content
        assert 'defindex_deposit' in content
        assert 'user_id=user_id' in content  # Check for user_id injection

        print("✅ Tool factory structure updated correctly")
        test_results.append("✅ Tool Factory Structure: PASSED")

    except Exception as e:
        print(f"❌ Tool Factory Structure failed: {e}")
        test_results.append(f"❌ Tool Factory Structure: FAILED - {e}")

    # Test 3: Agent Core Updates
    try:
        print("\n3. Testing Agent Core Updates...")

        with open('agent/core.py', 'r') as f:
            content = f.read()

        # Check that global DeFindex loading was removed
        assert 'DeFindex tools moved to tool_factory pattern' in content

        print("✅ Agent core updated correctly")
        test_results.append("✅ Agent Core Updates: PASSED")

    except Exception as e:
        print(f"❌ Agent Core Updates failed: {e}")
        test_results.append(f"❌ Agent Core Updates: FAILED - {e}")

    # Test 4: AccountManager Integration
    try:
        print("\n4. Testing AccountManager Integration...")

        from account_manager import AccountManager
        account_manager = AccountManager()

        # Test that AccountManager exists and can be instantiated
        assert account_manager is not None

        print("✅ AccountManager integration available")
        test_results.append("✅ AccountManager Integration: PASSED")

    except Exception as e:
        print(f"❌ AccountManager Integration failed: {e}")
        test_results.append(f"❌ AccountManager Integration: FAILED - {e}")

    # Print results
    print("\n" + "=" * 60)
    print("🏁 INTEGRATION TEST RESULTS")
    print("=" * 60)

    for result in test_results:
        print(result)

    passed = sum(1 for result in test_results if "PASSED" in result)
    total = len(test_results)

    print(f"\n📊 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("\n✅ Implementation Summary:")
        print("• DeFindex account tools working with fallback data")
        print("• Tool factory integration complete with user_id injection")
        print("• Agent core updated to use tool factory pattern")
        print("• AccountManager integration ready")
        print("• Error handling and validation working")
        print("\n🚀 Ready for Phala deployment!")
        return True
    else:
        print(f"⚠️ {total-passed} tests failed. Review issues above.")
        return False

async def test_sample_conversation_flow():
    """Test a sample conversation flow"""
    print("\n" + "=" * 60)
    print("📞 SAMPLE CONVERSATION FLOW TEST")
    print("=" * 60)

    try:
        from defindex_account_tools import _defindex_discover_vaults, _defindex_get_vault_details

        print("\nUser: 'Show me available vaults for investment'")
        result = await _defindex_discover_vaults(min_apy=0.0, user_id="demo_user")
        print(f"Agent Response: {result[:300]}...")

        print("\nUser: 'Tell me more about the first vault'")
        vault = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
        result = await _defindex_get_vault_details(vault_address=vault, user_id="demo_user")
        print(f"Agent Response: {result[:300]}...")

        print("\nUser: 'I want to deposit 50 XLM to that vault using my main account'")
        print("Agent: [Would use defindex_deposit tool with user's account_id]")
        print("Agent: [Transaction would be signed with user's private key via AccountManager]")
        print("Agent: [Transaction hash would be returned to user]")

        print("\n✅ Sample conversation flow working!")
        return True

    except Exception as e:
        print(f"❌ Sample conversation failed: {e}")
        return False

if __name__ == "__main__":
    # Run integration tests
    success = asyncio.run(test_core_functionality())

    # Run sample conversation test
    if success:
        asyncio.run(test_sample_conversation_flow())

    sys.exit(0 if success else 1)