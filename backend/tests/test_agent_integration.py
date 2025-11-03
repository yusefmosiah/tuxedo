#!/usr/bin/env python3
"""
Integration test for agent wallet functionality
Tests the complete agent account management flow.
"""

import asyncio
import requests
import json
import sys

BACKEND_URL = "http://localhost:8000"

async def test_agent_account_management():
    """Test agent account management functionality"""

    print("🤖 Testing Agent Account Management Integration")
    print("=" * 50)

    # Test 1: Check agent system status
    print("\n📋 Test 1: Check agent system status")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print("✅ System health check passed")
            print(f"LLM configured: {result.get('openai_configured', False)}")
            print(f"Stellar tools ready: {result.get('stellar_tools_ready', False)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test 2: Create agent account via API
    print("\n🏗️  Test 2: Create agent account via API")
    try:
        response = requests.post(f"{BACKEND_URL}/api/agent/create-account", json={
            "name": "Integration Test Account"
        })

        if response.status_code == 200:
            result = response.json()
            account_address = result.get('address')
            print("✅ Agent account created successfully")
            print(f"Address: {account_address}")
            print(f"Name: {result.get('name')}")
            print(f"Network: {result.get('network')}")
            print(f"Funded: {result.get('funded', False)}")
        else:
            print(f"❌ Account creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Account creation error: {e}")
        return False

    # Test 3: List agent accounts
    print("\n📝 Test 3: List agent accounts")
    try:
        response = requests.get(f"{BACKEND_URL}/api/agent/accounts")

        if response.status_code == 200:
            accounts = response.json()
            print(f"✅ Found {len(accounts)} agent accounts")
            for account in accounts:
                print(f"- {account.get('name', 'Unnamed')}: {account.get('address', 'N/A')}")
                print(f"  Balance: {account.get('balance', 0):.2f} XLM")
        else:
            print(f"❌ List accounts failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ List accounts error: {e}")
        return False

    # Test 4: Get specific account info
    print("\n🔍 Test 4: Get account details")
    try:
        if 'account_address' in locals():
            response = requests.get(f"{BACKEND_URL}/api/agent/accounts/{account_address}")

            if response.status_code == 200:
                result = response.json()
                print("✅ Account details retrieved")
                print(f"Address: {result.get('address')}")
                print(f"Balance: {result.get('balance', 0):.2f} XLM")
                print(f"Network: {result.get('network')}")
            else:
                print(f"❌ Get account info failed: {response.status_code}")
        else:
            print("⚠️  Skipped account info test (no account address)")
    except Exception as e:
        print(f"❌ Get account info error: {e}")

    # Test 5: Chat with agent about accounts
    print("\n💬 Test 5: Chat with agent about accounts")
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json={
            "message": "Can you show me my agent accounts and their balances?",
            "history": [],
            "agent_account": account_address if 'account_address' in locals() else None
        })

        if response.status_code == 200:
            result = response.json()
            print("✅ Agent chat response received")
            print(f"Success: {result.get('success', False)}")
            print(f"Response: {result.get('response', 'No response')[:200]}...")
        else:
            print(f"❌ Agent chat failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Agent chat error: {e}")

    print("\n🎉 Agent Account Management Integration Tests Complete!")
    return True

async def test_agent_tools():
    """Test agent tools via chat interface"""

    print("\n🛠️  Testing Agent Tools Integration")
    print("=" * 50)

    test_messages = [
        "Create a new agent account named 'Tool Test Account'",
        "List all my agent accounts",
        "What's the current Stellar network status?",
        "Show me the balance of my first agent account"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 Test {i}: {message}")
        try:
            response = requests.post(f"{BACKEND_URL}/chat", json={
                "message": message,
                "history": [],
                "agent_account": None
            })

            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Response: {result.get('response', 'No response')[:150]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all integration tests"""
    print("🚀 Starting Agent Wallet Integration Tests")
    print("Make sure the backend is running on http://localhost:8000")
    print("=" * 60)

    # Wait a moment for user to read
    await asyncio.sleep(2)

    success = await test_agent_account_management()

    if success:
        await test_agent_tools()

    print("\n" + "=" * 60)
    print("✨ Integration testing complete!")

if __name__ == "__main__":
    asyncio.run(main())