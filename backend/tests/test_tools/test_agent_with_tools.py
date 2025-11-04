#!/usr/bin/env python3
"""
Test script for the LLM Agent with explicit tool calling
"""

import asyncio
import requests
import json

BACKEND_URL = "http://localhost:8000"

async def test_agent_with_tools():
    """Test the LLM agent with explicit tool usage"""

    print("🤖 Testing Tuxedo AI Agent with Tool Calling")
    print("=" * 50)

    # Test with a prompt that should trigger tools
    print("\n📊 Test: Query that requires network status tool")
    response = requests.post(f"{BACKEND_URL}/chat", json={
        "message": "What is the current Stellar network status and what are the transaction fees?",
        "history": [],
        "wallet_address": None
    })

    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Agent Response: {result['response'][:300]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

    # Test with account operations
    print("\n👤 Test: Create and fund testnet account")
    response = requests.post(f"{BACKEND_URL}/chat", json={
        "message": "Please create a new Stellar testnet account and fund it with Friendbot",
        "history": [],
        "wallet_address": None
    })

    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Agent Response: {result['response'][:300]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

    # Test with market data that should use market_data tool
    print("\n📈 Test: Query XLM/USDC orderbook")
    response = requests.post(f"{BACKEND_URL}/chat", json={
        "message": "Can you check the current orderbook for XLM/USDC on the Stellar DEX?",
        "history": [],
        "wallet_address": None
    })

    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Agent Response: {result['response'][:300]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

    # Test with wallet address integration
    print("\n🔗 Test: Account operations with wallet address")
    test_wallet = "GBBM6BKZPEHWYO3E3YKREDPQXMS4VK35YLNU7NFBRI26RAN7GI5POFBB"
    response = requests.post(f"{BACKEND_URL}/chat", json={
        "message": "Can you check the balance and transaction history for this account?",
        "history": [],
        "wallet_address": test_wallet
    })

    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Agent Response: {result['response'][:300]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(test_agent_with_tools())