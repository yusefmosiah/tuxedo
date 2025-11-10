#!/usr/bin/env python3
"""
Test agent account functionality without requiring server
"""
import os
import sys
import asyncio
sys.path.append('/home/ubuntu/blend-pools/backend')

from dotenv import load_dotenv
load_dotenv()

async def test_agent_account_selection():
    """Test agent account selection logic"""
    print("=" * 60)
    print("TEST AGENT ACCOUNT SELECTION")
    print("=" * 60)

    # Import the functions we need
    try:
        from agent.core import get_agent_own_account, get_default_agent_account

        # Test 1: get_agent_own_account
        print("\n1. Testing get_agent_own_account()...")
        own_account = get_agent_own_account()

        if own_account:
            print("✅ SUCCESS: Agent own account found")
            print(f"   Address: {own_account.get('address')}")
            print(f"   Balance: {own_account.get('balance')}")
            print(f"   Network: {own_account.get('network')}")
        else:
            print("❌ FAILED: No agent own account found")

        # Test 2: get_default_agent_account
        print("\n2. Testing get_default_agent_account()...")
        default_account = get_default_agent_account()

        if default_account:
            print(f"✅ SUCCESS: Default account found: {default_account}")
        else:
            print("❌ FAILED: No default account found")

        # Test 3: Verify they match
        if own_account and default_account:
            if own_account.get('address') == default_account:
                print("\n✅ SUCCESS: Both functions return the same account!")
            else:
                print(f"\n❌ MISMATCH: own={own_account.get('address')}, default={default_account}")

        # Test 4: Check if this is the funded account from AGENT_STELLAR_SECRET
        agent_secret = os.getenv("AGENT_STELLAR_SECRET")
        if agent_secret and default_account:
            from stellar_sdk import Keypair
            expected_address = Keypair.from_secret(agent_secret).public_key
            if default_account == expected_address:
                print(f"✅ SUCCESS: Using correct AGENT_STELLAR_SECRET account: {default_account}")
            else:
                print(f"❌ ERROR: Wrong account. Expected: {expected_address}, Got: {default_account}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_account_selection())