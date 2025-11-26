#!/usr/bin/env python3
"""
Integration test for agent wallet functionality
Tests the complete agent account management flow.
"""

import asyncio
import json

def test_agent_account_management_integration(test_client):
    """Test agent account management functionality"""

    print("🤖 Testing Agent Account Management Integration")
    print("=" * 50)

    # Test 1: Check agent system status
    print("\n📋 Test 1: Check agent system status")
    response = test_client.get("/health")
    assert response.status_code == 200
    result = response.json()
    print("✅ System health check passed")
    print(f"LLM configured: {result.get('openai_configured', False)}")
    print(f"Stellar tools ready: {result.get('stellar_tools_ready', False)}")

    # Test 2: Create agent account via API
    print("\n🏗️  Test 2: Create agent account via API")
    response = test_client.post("/api/agent/create-account", json={
        "name": "Integration Test Account"
    })
    assert response.status_code == 200
    result = response.json()
    account_address = result.get('address')
    print("✅ Agent account created successfully")
    print(f"Address: {account_address}")
    print(f"Name: {result.get('name')}")
    print(f"Network: {result.get('network')}")
    print(f"Funded: {result.get('funded', False)}")

    # Test 3: List agent accounts
    print("\n📝 Test 3: List agent accounts")
    response = test_client.get("/api/agent/accounts")
    assert response.status_code == 200
    accounts = response.json()
    print(f"✅ Found {len(accounts)} agent accounts")
    for account in accounts:
        print(f"- {account.get('name', 'Unnamed')}: {account.get('address', 'N/A')}")
        print(f"  Balance: {account.get('balance', 0):.2f} XLM")

    # Test 4: Get specific account info
    print("\n🔍 Test 4: Get account details")
    if account_address:
        response = test_client.get(f"/api/agent/accounts/{account_address}")
        assert response.status_code == 200
        result = response.json()
        print("✅ Account details retrieved")
        print(f"Address: {result.get('address')}")
        print(f"Balance: {result.get('balance', 0):.2f} XLM")
        print(f"Network: {result.get('network')}")
    else:
        print("⚠️  Skipped account info test (no account address)")

    # Test 5: Chat with agent about accounts
    print("\n💬 Test 5: Chat with agent about accounts")
    response = test_client.post("/chat", json={
        "message": "Can you show me my agent accounts and their balances?",
        "history": [],
        "agent_account": account_address if account_address else None
    })
    assert response.status_code == 200
    result = response.json()
    print("✅ Agent chat response received")
    print(f"Success: {result.get('success', False)}")
    print(f"Response: {result.get('response', 'No response')[:200]}...")

    print("\n🎉 Agent Account Management Integration Tests Complete!")

def test_agent_tools_integration(test_client):
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
        response = test_client.post("/chat", json={
            "message": message,
            "history": [],
            "agent_account": None
        })
        assert response.status_code == 200
        result = response.json()
        print("✅ Success!")
        print(f"Response: {result.get('response', 'No response')[:150]}...")

if __name__ == "__main__":
    # This test must be run with pytest
    print("This test must be run with pytest.")
