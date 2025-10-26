#!/usr/bin/env python3
"""
Test script for the LLM Agent integration
"""

import asyncio
import requests
import json

BACKEND_URL = "http://localhost:8002"

async def test_agent():
    """Test the LLM agent with Stellar tools"""

    print("🤖 Testing Tuxedo AI Agent Integration")
    print("=" * 50)

    # Test 1: Simple Stellar query
    print("\n📊 Test 1: Query Stellar network status")
    response = requests.post(f"{BACKEND_URL}/chat", json={
        "message": "What's the current Stellar network status and fee information?",
        "history": [],
        "wallet_address": None
    })

    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Agent Response: {result['response'][:200]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

    # Test 2: Account management with testnet
    print("\n👤 Test 2: Create a testnet account")
    response = requests.post(f"{BACKEND_URL}/chat", json={
        "message": "Please create a new testnet account for me and fund it using Friendbot",
        "history": [],
        "wallet_address": None
    })

    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Agent Response: {result['response'][:200]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

    # Test 3: Market data query
    print("\n📈 Test 3: Query market data for XLM/USDC")
    response = requests.post(f"{BACKEND_URL}/chat", json={
        "message": "Can you show me the current orderbook for XLM/USDC on the Stellar DEX?",
        "history": [],
        "wallet_address": None
    })

    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Agent Response: {result['response'][:200]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(test_agent())