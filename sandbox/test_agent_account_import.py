#!/usr/bin/env python3
"""
Test agent account import functionality
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_agent_account():
    """Test the agent account import"""
    from agent.core import import_agent_account_if_exists
    from account_manager import AccountManager

    print("=" * 60)
    print("AGENT ACCOUNT IMPORT TEST")
    print("=" * 60)

    # Check env var
    agent_secret = os.getenv("AGENT_STELLAR_SECRET")
    print(f"\n1. AGENT_STELLAR_SECRET env var: {'SET' if agent_secret else 'NOT SET'}")

    if agent_secret:
        from stellar_sdk import Keypair
        kp = Keypair.from_secret(agent_secret)
        print(f"   Public key: {kp.public_key}")

    # Try import
    print("\n2. Running import_agent_account_if_exists()...")
    await import_agent_account_if_exists()

    # Check if imported
    print("\n3. Checking AccountManager for system_agent accounts...")
    am = AccountManager()
    accounts = am.get_user_accounts("system_agent", chain="stellar")

    print(f"   Found {len(accounts)} account(s)")
    for acc in accounts:
        print(f"\n   Account Details:")
        print(f"   - ID: {acc.get('id')}")
        print(f"   - Public Key: {acc.get('public_key')}")
        print(f"   - Name: {acc.get('name')}")
        print(f"   - Balance: {acc.get('balance', 'N/A')}")
        print(f"   - Metadata: {acc.get('metadata', {})}")
        if 'error' in acc:
            print(f"   - Error: {acc['error']}")

    # Check get_agent_own_account
    print("\n4. Testing get_agent_own_account()...")
    from agent.core import get_agent_own_account
    agent_acc = get_agent_own_account()

    if agent_acc:
        print(f"   ✅ Agent account found!")
        print(f"   - Address: {agent_acc.get('address')}")
        print(f"   - Balance: {agent_acc.get('balance')}")
    else:
        print("   ❌ Agent account NOT found via get_agent_own_account()")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent_account())
