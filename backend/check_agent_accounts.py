#!/usr/bin/env python3
"""
Check what accounts exist for agent user
"""

from account_manager import AccountManager

account_manager = AccountManager()

# Check agent user accounts
accounts = account_manager.get_user_accounts("agent")

print("=" * 80)
print("AGENT USER ACCOUNTS:")
print("=" * 80)

if not accounts:
    print("No accounts found for 'agent' user")
else:
    for i, acc in enumerate(accounts, 1):
        print(f"\nAccount {i}:")
        print(f"  ID: {acc['id']}")
        print(f"  Public Key: {acc['public_key']}")
        print(f"  Name: {acc.get('name', 'N/A')}")
        print(f"  Chain: {acc['chain']}")
        print(f"  Network: {acc['network']}")
        print(f"  Source: {acc['source']}")

print("\n" + "=" * 80)
print(f"Expected agent public key: GA4KBIWEVNXJPT545A6YYZPZUFYHCG4LBDGN437PDRTBLGOE3KIW5KBZ")
print("=" * 80)
