#!/usr/bin/env python3
"""
Test get_agent_own_account function
"""
import os
import sys
sys.path.append('/home/ubuntu/blend-pools/backend')

from dotenv import load_dotenv
load_dotenv()

def test_get_agent_own_account():
    """Test the get_agent_own_account function"""
    print("=" * 60)
    print("TEST GET_AGENT_OWN_ACCOUNT")
    print("=" * 60)

    try:
        from agent.core import get_agent_own_account

        # Test getting the agent's own account
        agent_account = get_agent_own_account()

        if agent_account:
            print("✅ Agent account found!")
            print(f"   Address: {agent_account.get('address')}")
            print(f"   Balance: {agent_account.get('balance')}")
            print(f"   Network: {agent_account.get('network')}")
        else:
            print("❌ No agent account found via get_agent_own_account()")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Also test get_default_agent_account
    print("\n2. Testing get_default_agent_account()...")
    try:
        from agent.core import get_default_agent_account

        default_account = get_default_agent_account()

        if default_account:
            print(f"✅ Default account found: {default_account}")
        else:
            print("❌ No default account found")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_get_agent_own_account()