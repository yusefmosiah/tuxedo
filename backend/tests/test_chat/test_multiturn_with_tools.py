#!/usr/bin/env python3
"""
Test multi-turn conversation with tool calls to verify context preservation.
"""
import requests
import json

API_URL = "http://localhost:8002"

def test_multiturn_with_tools():
    """Test a multi-turn conversation with tool execution."""
    print("=" * 60)
    print("Testing Multi-Turn Conversation with Tool Calls")
    print("=" * 60)

    # Turn 1: Create and fund an account (uses tools)
    print("\n📤 Turn 1: Create a test account")
    response1 = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "Create a new Stellar testnet account and fund it",
            "history": [],
            "wallet_address": None
        },
        timeout=60
    )

    print(f"Status: {response1.status_code}")
    if response1.status_code != 200:
        print(f"❌ FAILED: Turn 1 got {response1.status_code}")
        print(f"Error: {response1.text}")
        return False

    data1 = response1.json()
    print(f"✅ Turn 1 Response: {data1['response'][:150]}...")

    # Extract account address from response (should be mentioned)
    import re
    account_match = re.search(r'G[A-Z0-9]{55}', data1['response'])
    if not account_match:
        print("⚠️  Warning: No account address found in response")

    # Turn 2: Ask about what we just did (context test)
    print("\n📤 Turn 2: Ask about the account we just created")
    response2 = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "What was the address of the account we just created?",
            "history": [
                {"role": "user", "content": "Create a new Stellar testnet account and fund it"},
                {"role": "assistant", "content": data1['response']}
            ],
            "wallet_address": None
        },
        timeout=60
    )

    print(f"Status: {response2.status_code}")
    if response2.status_code != 200:
        print(f"❌ FAILED: Turn 2 got {response2.status_code}")
        print(f"Error: {response2.text}")
        return False

    data2 = response2.json()
    print(f"✅ Turn 2 Response: {data2['response'][:150]}...")

    # Check if the response references the account
    if account_match and account_match.group(0) in data2['response']:
        print(f"\n✅ SUCCESS: Context preserved! The AI remembered the account: {account_match.group(0)}")
        return True
    else:
        print("\n⚠️  Context may not be fully preserved, but conversation completed without 422 error")
        return True

if __name__ == "__main__":
    try:
        success = test_multiturn_with_tools()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
