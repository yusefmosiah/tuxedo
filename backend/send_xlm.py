#!/usr/bin/env python3
"""
Send XLM to a Stellar address.

Usage:
    python send_xlm.py <destination_address> <amount>
"""

import sys
import asyncio
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset

async def send_xlm(secret_key: str, destination: str, amount: str):
    """Send XLM payment on Stellar mainnet."""

    # Create keypair from secret
    keypair = Keypair.from_secret(secret_key)
    source_address = keypair.public_key

    # Connect to Horizon
    server = Server(horizon_url="https://horizon.stellar.org")

    print(f"Sending {amount} XLM")
    print(f"From: {source_address}")
    print(f"To: {destination}")
    print("-" * 60)

    try:
        # Load source account
        source_account = server.load_account(source_address)

        # Build transaction
        transaction = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_payment_operation(
                destination=destination,
                asset=Asset.native(),
                amount=amount
            )
            .set_timeout(30)
            .build()
        )

        # Sign transaction
        transaction.sign(keypair)

        # Submit to network
        response = server.submit_transaction(transaction)

        print("✅ Payment Successful!")
        print(f"\n💰 Sent: {amount} XLM")
        print(f"📍 To: {destination}")
        print(f"🔗 Hash: {response['hash']}")
        print(f"📊 Ledger: {response.get('ledger', 'N/A')}")
        print(f"\n🔍 View on Stellar Expert:")
        print(f"   https://stellar.expert/explorer/public/tx/{response['hash']}")

        return response

    except Exception as e:
        print(f"❌ Error sending payment: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python send_xlm.py <destination_address> <amount>")
        print("Example: python send_xlm.py GABC...XYZ 10.5")
        sys.exit(1)

    destination = sys.argv[1]
    amount = sys.argv[2]

    # Read secret key from file
    try:
        with open('.stellar_secret', 'r') as f:
            secret_key = f.read().strip()
    except FileNotFoundError:
        print("❌ Error: .stellar_secret file not found")
        print("Run create_stellar_account.py first")
        sys.exit(1)

    asyncio.run(send_xlm(secret_key, destination, amount))
