#!/usr/bin/env python3
"""
Check the balance of a Stellar account.

Usage:
    python check_account_balance.py [PUBLIC_KEY]

If no public key is provided, reads from .stellar_public
"""

import sys
import asyncio
from stellar_sdk import Server

async def check_balance(public_key: str):
    """Check account balance on Stellar mainnet."""

    print(f"Checking account: {public_key}")
    print("Network: Mainnet (https://horizon.stellar.org)")
    print("-" * 60)

    server = Server(horizon_url="https://horizon.stellar.org")

    try:
        account = server.accounts().account_id(public_key).call()

        print("✅ Account is FUNDED and active!")
        print(f"\nSequence: {account['sequence']}")
        print(f"\n💰 Balances:")

        for balance in account['balances']:
            asset_type = balance['asset_type']
            if asset_type == 'native':
                print(f"   XLM: {float(balance['balance']):,.7f}")
            else:
                asset_code = balance.get('asset_code', 'Unknown')
                asset_issuer = balance.get('asset_issuer', 'Unknown')[:8]
                print(f"   {asset_code}: {float(balance['balance']):,.7f} (issuer: {asset_issuer}...)")

        print("\n✅ This account is ready to use!")
        print("\n📋 Next step: Add to backend/.env:")

        # Try to read secret from file
        try:
            with open('.stellar_secret', 'r') as f:
                secret = f.read().strip()
                print(f"   AGENT_STELLAR_SECRET={secret}")
        except FileNotFoundError:
            print("   AGENT_STELLAR_SECRET=<your_secret_key_here>")

    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "not found" in error_str.lower():
            print("❌ Account NOT FUNDED yet")
            print("\nThis account doesn't exist on the Stellar mainnet.")
            print("\n⚠️  ACTION REQUIRED:")
            print("   1. Send at least 1 XLM to this address:")
            print(f"      {public_key}")
            print("   2. You can send from:")
            print("      - A crypto exchange (Coinbase, Kraken, etc.)")
            print("      - Another Stellar wallet")
            print("      - Lobstr or other Stellar apps")
            print("\n   3. After sending, run this script again to verify")
            print("\n🔗 Track the account here:")
            print(f"   https://stellar.expert/explorer/public/account/{public_key}")
        else:
            print(f"❌ Error checking account: {e}")

if __name__ == "__main__":
    # Get public key from argument or file
    if len(sys.argv) > 1:
        public_key = sys.argv[1]
    else:
        try:
            with open('.stellar_public', 'r') as f:
                public_key = f.read().strip()
        except FileNotFoundError:
            print("❌ Error: No public key provided and .stellar_public not found")
            print("\nUsage:")
            print("  python check_account_balance.py [PUBLIC_KEY]")
            print("  python check_account_balance.py  # reads from .stellar_public")
            sys.exit(1)

    asyncio.run(check_balance(public_key))
