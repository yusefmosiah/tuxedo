#!/usr/bin/env python3
"""
Clean up empty Stellar accounts from the keystore.
Removes all accounts with 0 XLM balance to reduce clutter.
"""

import json
import os
from stellar_sdk.server import Server
from key_manager import KeyManager

def clean_empty_accounts():
    """Remove all accounts with 0 XLM balance from the keystore"""

    # Initialize Stellar server
    HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")
    server = Server(HORIZON_URL)

    # Initialize key manager
    key_manager = KeyManager()
    accounts = key_manager.list_accounts()

    print(f"Total accounts in keystore: {len(accounts)}")

    accounts_to_keep = []
    accounts_to_remove = []

    for address in accounts:
        try:
            # Check account balance
            account = server.load_account(address)
            balance = 0
            for balance_item in account.balances:
                if balance_item.asset_type == "native":
                    balance = float(balance_item.balance)
                    break

            if balance > 0.001:  # Keep accounts with some XLM
                accounts_to_keep.append(address)
                print(f"✅ Keeping account {address}: {balance} XLM")
            else:
                accounts_to_remove.append(address)
                print(f"🗑️  Removing empty account {address}: {balance} XLM")

        except Exception as e:
            # Account likely doesn't exist on network (unfunded)
            accounts_to_remove.append(address)
            print(f"🗑️  Removing unfunded account {address}: {str(e)}")

    print(f"\nSummary:")
    print(f"Accounts to keep: {len(accounts_to_keep)}")
    print(f"Accounts to remove: {len(accounts_to_remove)}")

    if len(accounts_to_remove) > 0:
        # Create new keystore with only funded accounts
        new_keystore = {}

        # Load current keystore
        with open('.stellar_keystore.json', 'r') as f:
            current_keystore = json.load(f)

        # Keep only accounts with balance
        for address in accounts_to_keep:
            if address in current_keystore:
                new_keystore[address] = current_keystore[address]

        # Backup old keystore
        os.rename('.stellar_keystore.json', '.stellar_keystore.empty_accounts.json')

        # Save new keystore
        with open('.stellar_keystore.json', 'w') as f:
            json.dump(new_keystore, f, indent=2)

        # Set proper permissions
        os.chmod('.stellar_keystore.json', 0o600)

        print(f"\n✅ Cleanup complete!")
        print(f"Old keystore backed up to: .stellar_keystore.empty_accounts.json")
        print(f"New keystore contains {len(new_keystore)} accounts")
    else:
        print("\nNo accounts to remove. Keeping all accounts.")

if __name__ == "__main__":
    clean_empty_accounts()