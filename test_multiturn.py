#!/usr/bin/env python3
"""
Test multi-turn conversation to verify 422 error is fixed.
"""
import requests
import json

API_URL = "http://localhost:8002"

def test_multiturn_conversation():
    """Test a multi-turn conversation."""
    print("=" * 60)
    print("Testing Multi-Turn Conversation")
    print("=" * 60)

    # Turn 1: Ask about network status
    print("\n📤 Turn 1: What's the network status?")
    response1 = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "What's the Stellar network status?",
            "history": [],
            "wallet_address": None
        },
        timeout=30
    )

    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"✅ Turn 1 Response: {data1['response'][:100]}...")

        # Turn 2: Ask a follow-up question
        print("\n📤 Turn 2: Follow-up question")
        response2 = requests.post(
            f"{API_URL}/chat",
            json={
                "message": "What was that again?",
                "history": [
                    {"role": "user", "content": "What's the Stellar network status?"},
                    {"role": "assistant", "content": data1['response']}
                ],
                "wallet_address": None
            },
            timeout=30
        )

        print(f"Status: {response2.status_code}")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Turn 2 Response: {data2['response'][:100]}...")
            print("\n✅ SUCCESS: Multi-turn conversation works!")
            return True
        else:
            print(f"❌ FAILED: Turn 2 got {response2.status_code}")
            print(f"Error: {response2.text}")
            return False
    else:
        print(f"❌ FAILED: Turn 1 got {response1.status_code}")
        print(f"Error: {response1.text}")
        return False

if __name__ == "__main__":
    try:
        success = test_multiturn_conversation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
