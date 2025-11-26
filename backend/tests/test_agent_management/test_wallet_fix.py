#!/usr/bin/env python3
"""
Test script to verify wallet address injection fix
"""

import json

def test_wallet_integration(test_client):
    """Test wallet address integration in chat"""

    print("🧪 Testing Wallet Address Integration Fix")
    print("=" * 50)

    # Test 1: Chat with wallet address
    print("\n📍 Test 1: Chat with connected wallet")

    test_wallet = "GDHEYP7WQRMVBUS2JLOVDWJ64EPCIQHVW7WQDNSRBUUTLCZYW5GBMUTG"

    chat_payload = {
        "message": "What's in my wallet?",
        "history": [],
        "wallet_address": test_wallet
    }

    response = test_client.post("/chat", json=chat_payload)

    assert response.status_code == 200
    result = response.json()
    print(f"✅ Chat request successful")
    print(f"📝 Response: {result['response'][:200]}...")

    # Check if the response contains wallet address information
    if test_wallet in result['response'] or "balance" in result['response'].lower():
        print("✅ Response appears to contain wallet information")
    else:
        print("⚠️  Response may not be using the connected wallet")

    # Test 2: Check backend health
    print("\n📍 Test 2: Backend health check")

    health_response = test_client.get("/health")

    assert health_response.status_code == 200
    health_data = health_response.json()
    print("✅ Backend is healthy")
    print(f"🔧 Stellar tools ready: {health_data.get('stellar_tools_ready', False)}")
    print(f"🤖 OpenAI configured: {health_data.get('openai_configured', False)}")


if __name__ == "__main__":
    # This test must be run with pytest
    print("This test must be run with pytest.")
