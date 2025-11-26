#!/usr/bin/env python3
"""
Test multi-turn conversation to verify 422 error is fixed.
"""
import json

def test_multiturn_conversation(test_client):
    """Test a multi-turn conversation."""
    print("=" * 60)
    print("Testing Multi-Turn Conversation")
    print("=" * 60)

    # Turn 1: Ask about network status
    print("\n📤 Turn 1: What's the network status?")
    response1 = test_client.post(
        "/chat",
        json={
            "message": "What's the Stellar network status?",
            "history": [],
            "wallet_address": None
        },
    )

    print(f"Status: {response1.status_code}")
    assert response1.status_code == 200, f"❌ FAILED: Turn 1 got {response1.status_code}\nError: {response1.text}"

    data1 = response1.json()
    print(f"✅ Turn 1 Response: {data1['response'][:100]}...")

    # Turn 2: Ask a follow-up question
    print("\n📤 Turn 2: Follow-up question")
    response2 = test_client.post(
        "/chat",
        json={
            "message": "What was that again?",
            "history": [
                {"role": "user", "content": "What's the Stellar network status?"},
                {"role": "assistant", "content": data1['response']}
            ],
            "wallet_address": None
        },
    )

    print(f"Status: {response2.status_code}")
    assert response2.status_code == 200, f"❌ FAILED: Turn 2 got {response2.status_code}\nError: {response2.text}"

    data2 = response2.json()
    print(f"✅ Turn 2 Response: {data2['response'][:100]}...")
    print("\n✅ SUCCESS: Multi-turn conversation works!")

if __name__ == "__main__":
    try:
        # Note: This test can't be run standalone anymore without a test client.
        # Use pytest to run it.
        print("This test must be run with pytest.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
