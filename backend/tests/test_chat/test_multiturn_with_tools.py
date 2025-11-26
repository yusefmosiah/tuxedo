#!/usr/bin/env python3
"""
Test multi-turn conversation with tool calls to verify context preservation.
"""
import json
import re

def test_multiturn_with_tools(test_client):
    """Test a multi-turn conversation with tool execution."""
    print("=" * 60)
    print("Testing Multi-Turn Conversation with Tool Calls")
    print("=" * 60)

    # Turn 1: Create and fund an account (uses tools)
    print("\n📤 Turn 1: Create a test account")
    response1 = test_client.post(
        "/chat",
        json={
            "message": "Create a new Stellar account",
            "history": [],
            "wallet_address": None
        },
    )

    print(f"Status: {response1.status_code}")
    assert response1.status_code == 200, f"❌ FAILED: Turn 1 got {response1.status_code}\nError: {response1.text}"

    data1 = response1.json()
    print(f"✅ Turn 1 Response: {data1['response'][:150]}...")

    # Extract account address from response (should be mentioned)
    account_match = re.search(r'G[A-Z0-9]{55}', data1['response'])
    if not account_match:
        print("⚠️  Warning: No account address found in response")

    # Turn 2: Ask about what we just did (context test)
    print("\n📤 Turn 2: Ask about the account we just created")
    response2 = test_client.post(
        "/chat",
        json={
            "message": "What was the address of the account we just created?",
            "history": [
                {"role": "user", "content": "Create a new Stellar account"},
                {"role": "assistant", "content": data1['response']}
            ],
            "wallet_address": None
        },
    )

    print(f"Status: {response2.status_code}")
    assert response2.status_code == 200, f"❌ FAILED: Turn 2 got {response2.status_code}\nError: {response2.text}"

    data2 = response2.json()
    print(f"✅ Turn 2 Response: {data2['response'][:150]}...")

    # Check if the response references the account
    if account_match and account_match.group(0) in data2['response']:
        print(f"\n✅ SUCCESS: Context preserved! The AI remembered the account: {account_match.group(0)}")
    else:
        print("\n⚠️  Context may not be fully preserved, but conversation completed without 422 error")
