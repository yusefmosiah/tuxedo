#!/usr/bin/env python3
"""
Create a new Stellar account and save credentials to a file.

Usage:
    python create_stellar_account.py

This will:
1. Generate a new Stellar keypair
2. Save the secret key to .stellar_secret
3. Save the public key to .stellar_public
4. Display the public address for funding
"""

from stellar_sdk import Keypair
import os

def create_account():
    """Generate a new Stellar account and save to files."""

    # Generate new keypair
    keypair = Keypair.random()

    # Get keys
    secret_key = keypair.secret
    public_key = keypair.public_key

    # Save to files in backend directory
    secret_file = os.path.join(os.path.dirname(__file__), '.stellar_secret')
    public_file = os.path.join(os.path.dirname(__file__), '.stellar_public')

    # Write secret key
    with open(secret_file, 'w') as f:
        f.write(secret_key)
    os.chmod(secret_file, 0o600)  # Read/write for owner only

    # Write public key
    with open(public_file, 'w') as f:
        f.write(public_key)

    print("✅ Stellar Account Created Successfully!")
    print("=" * 60)
    print(f"\n📍 Public Address (share this to receive funds):")
    print(f"   {public_key}")
    print(f"\n🔐 Secret Key (NEVER share this):")
    print(f"   {secret_key}")
    print(f"\n💾 Files Created:")
    print(f"   Secret: {secret_file}")
    print(f"   Public: {public_file}")
    print("\n" + "=" * 60)
    print("\n⚠️  IMPORTANT NEXT STEPS:")
    print("1. Fund this account with at least 1 XLM to activate it")
    print("   - Use Stellar's account viewer: https://stellar.expert/explorer/public")
    print("   - Or send from an exchange/wallet")
    print("\n2. After funding, add to backend/.env:")
    print(f"   AGENT_STELLAR_SECRET={secret_key}")
    print("\n3. The agent will use this account for all operations")
    print("=" * 60)

    return {
        'public_key': public_key,
        'secret_key': secret_key,
        'secret_file': secret_file,
        'public_file': public_file
    }

if __name__ == "__main__":
    create_account()
