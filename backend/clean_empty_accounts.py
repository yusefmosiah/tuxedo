#!/usr/bin/env python3
"""
Clean up empty Stellar accounts from the keystore.
Removes all accounts with 0 XLM balance to reduce clutter.

⚠️ DEPRECATED - OBSOLETE AFTER QUANTUM LEAP ⚠️

This script is NO LONGER NEEDED after migration to AccountManager.

Old System (KeyManager):
- Used .stellar_keystore.json file
- All accounts in single JSON file
- This script cleaned up empty accounts

New System (AccountManager):
- Uses database with user_id isolation
- Accounts stored per-user in wallet_accounts table
- No need for cleanup script (use SQL queries instead)

If you need to clean up accounts in the new system:
  python -c "from account_manager import AccountManager; am = AccountManager(); am.delete_account(user_id, account_id)"

Or use SQL directly:
  DELETE FROM wallet_accounts WHERE user_id='...' AND id='...'
"""

import json
import os
from stellar_sdk.server import Server
# from key_manager import KeyManager  # DEPRECATED - DO NOT USE

def clean_empty_accounts():
    """
    DEPRECATED: This function is obsolete after quantum leap migration.

    Use AccountManager methods instead for cleaning up accounts.
    """
    print("⚠️  This script is DEPRECATED and no longer works.")
    print("The KeyManager and .stellar_keystore.json have been replaced with AccountManager.")
    print("")
    print("To manage accounts in the new system:")
    print("1. Use AccountManager methods:")
    print("   from account_manager import AccountManager")
    print("   am = AccountManager()")
    print("   am.delete_account(user_id, account_id)")
    print("")
    print("2. Or use SQL queries on wallet_accounts table")
    return

    # OLD CODE (kept for reference, but not executed):
    """
    # Initialize Stellar server
    HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")
    server = Server(HORIZON_URL)

    # Initialize key manager
    from key_manager import KeyManager
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