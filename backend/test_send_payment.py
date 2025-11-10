#!/usr/bin/env python3
"""
Test the account_manager send functionality.
Sends 0.142857 XLM from the agent account to the user.
"""

import sys
import os
from stellar_sdk import Server
from account_manager import AccountManager
from stellar_tools import account_manager as account_mgr_tool

def main():
    # User ID for the agent
    user_id = "agent_system"

    # Recipient address
    recipient = "GBAAXXBAFG2GWUUVS6PGZ2PMIGHT2KMNEUCLKKTS7ECJ7USFNQPTZW2F"

    # Amount to send
    amount = "0.142857"

    print("=" * 60)
    print("Testing Payment Functionality")
    print("=" * 60)
    print(f"Recipient: {recipient}")
    print(f"Amount: {amount} XLM")
    print()

    # Initialize infrastructure
    horizon = Server(horizon_url="https://horizon.stellar.org")
    acct_mgr = AccountManager()

    # Read secret key from file
    secret_file = os.path.join(os.path.dirname(__file__), '.stellar_secret')
    try:
        with open(secret_file, 'r') as f:
            secret_key = f.read().strip()
    except FileNotFoundError:
        print(f"❌ Error: {secret_file} not found")
        print("Run create_stellar_account.py first")
        return 1

    print("Step 1: Import agent account...")
    import_result = account_mgr_tool(
        action="import",
        user_id=user_id,
        account_manager=acct_mgr,
        horizon=horizon,
        secret_key=secret_key
    )

    if not import_result.get("success"):
        # Account might already be imported, try to list accounts
        list_result = account_mgr_tool(
            action="list",
            user_id=user_id,
            account_manager=acct_mgr,
            horizon=horizon
        )

        if list_result.get("success") and list_result.get("accounts"):
            account_id = list_result["accounts"][0]["id"]
            print(f"✅ Using existing account: {account_id}")
        else:
            print(f"❌ Failed to import or find account: {import_result.get('error')}")
            return 1
    else:
        account_id = import_result["account_id"]
        print(f"✅ Account imported: {account_id}")

    print()
    print("Step 2: Get account details...")
    get_result = account_mgr_tool(
        action="get",
        user_id=user_id,
        account_manager=acct_mgr,
        horizon=horizon,
        account_id=account_id
    )

    if not get_result.get("success"):
        print(f"❌ Failed to get account: {get_result.get('error')}")
        return 1

    print(f"✅ Public Key: {get_result['public_key']}")
    for balance in get_result['balances']:
        if balance['asset_type'] == 'native':
            print(f"✅ Balance: {balance['balance']} XLM")

    print()
    print("Step 3: Send payment...")
    send_result = account_mgr_tool(
        action="send",
        user_id=user_id,
        account_manager=acct_mgr,
        horizon=horizon,
        account_id=account_id,
        destination=recipient,
        amount=amount
    )

    if not send_result.get("success"):
        print(f"❌ Payment failed: {send_result.get('error')}")
        return 1

    print("✅ Payment Successful!")
    print(f"   Amount: {send_result.get('amount')} {send_result.get('asset')}")
    print(f"   To: {send_result.get('destination')}")
    print(f"   Hash: {send_result.get('hash')}")
    print(f"   Ledger: {send_result.get('ledger')}")
    print()
    print(f"🔍 View on Stellar Expert:")
    print(f"   https://stellar.expert/explorer/public/tx/{send_result.get('hash')}")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
