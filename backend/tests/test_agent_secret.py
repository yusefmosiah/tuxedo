#!/usr/bin/env python3
"""
Simple test to check if AGENT_STELLAR_SECRET is being imported correctly
"""
import os
import sys
sys.path.append('/home/ubuntu/blend-pools/backend')

from dotenv import load_dotenv
load_dotenv()

def test_agent_secret():
    """Test the agent secret import"""
    print("=" * 60)
    print("AGENT STELLAR SECRET TEST")
    print("=" * 60)

    # Check env var
    agent_secret = os.getenv("AGENT_STELLAR_SECRET")
    print(f"\n1. AGENT_STELLAR_SECRET env var: {'SET' if agent_secret else 'NOT SET'}")

    if agent_secret:
        try:
            from stellar_sdk import Keypair
            kp = Keypair.from_secret(agent_secret)
            print(f"   Public key: {kp.public_key}")

            # Check if this account is funded
            from stellar_sdk import Server
            server = Server("https://horizon.stellar.org")
            try:
                account = server.load_account(kp.public_key)
                print(f"   ✅ Account is funded!")
                for balance in account.balances:
                    print(f"      {balance.asset_code or 'XLM'}: {float(balance.balance)}")
            except Exception as e:
                print(f"   ❌ Account not funded: {str(e)[:100]}")

        except Exception as e:
            print(f"   ❌ Invalid secret: {e}")
    else:
        print("   ❌ No AGENT_STELLAR_SECRET found!")

    # Test AccountManager import
    print("\n2. Testing AccountManager import...")
    try:
        from account_manager import AccountManager
        am = AccountManager()

        # Check system_agent accounts
        accounts = am.get_user_accounts("system_agent", "stellar")
        print(f"   Found {len(accounts)} system_agent accounts")

        for acc in accounts:
            print(f"   Account: {acc.get('public_key', 'N/A')}")
            print(f"   Name: {acc.get('name', 'N/A')}")
            print(f"   Balance: {acc.get('balance', 'N/A')}")
            print(f"   Metadata: {acc.get('metadata', {})}")

    except Exception as e:
        print(f"   ❌ AccountManager error: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_agent_secret()