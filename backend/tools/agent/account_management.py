"""
Agent Account Management Tools
Functions for AI agents to manage their own Stellar accounts

⚠️ SECURITY WARNING - NOT USER-ISOLATED ⚠️

This file uses KeyManager which does NOT enforce user isolation.
All users share the same agent accounts, which is a security risk.

STATUS: Pending migration to AccountManager with per-user agent accounts

QUANTUM LEAP TODO:
- Add user_id parameter to all functions
- Use AccountManager instead of KeyManager
- Create per-user agent accounts (each user has their own agent accounts)
- Add permission checks before operations

For now: These tools are loaded but should be used with caution in multi-user environments.
"""

from typing import Dict, Optional, List
from stellar_sdk import Keypair
from stellar_sdk.server import Server
from key_manager import KeyManager  # ⚠️ NOT USER-ISOLATED
import json
import os
import requests

# Initialize Stellar server
HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")
FRIENDBOT_URL = os.getenv("FRIENDBOT_URL", "https://friendbot.stellar.org")
server = Server(HORIZON_URL)

def create_agent_account(account_name: Optional[str] = None) -> Dict:
    """Create new agent-controlled account"""
    try:
        # Generate new keypair
        keypair = Keypair.random()

        # Initialize key manager
        key_manager = KeyManager()

        # Store in key manager with metadata
        metadata = {
            "name": account_name or f"Account {len(key_manager.list_accounts()) + 1}",
            "created_at": "2025-01-03T00:00:00Z",
            "network": "testnet"
        }

        key_manager.store(keypair.public_key, keypair.secret)

        # Fund with testnet lumens
        funded = False
        try:
            response = requests.get(f"{FRIENDBOT_URL}?addr={keypair.public_key}")
            if response.status_code == 200:
                funded = True
        except Exception as e:
            print(f"Failed to fund account: {e}")

        return {
            "address": keypair.public_key,
            "name": metadata["name"],
            "funded": funded,
            "network": "testnet",
            "success": True
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def list_agent_accounts() -> List[Dict]:
    """List all agent-controlled accounts"""
    try:
        key_manager = KeyManager()
        accounts = []

        for address in key_manager.list_accounts():
            try:
                # Get account info from Stellar
                account = server.load_account(address)
                balance = 0
                # Access balances from raw_data
                for balance_item in account.raw_data.get('balances', []):
                    if balance_item.get('asset_type') == "native":
                        balance = float(balance_item.get('balance', '0'))
                        break

                accounts.append({
                    "address": address,
                    "balance": balance,
                    "network": "testnet"
                })
            except Exception as e:
                # Account exists but might not be funded
                print(f"Warning: Could not load account {address}: {e}")
                accounts.append({
                    "address": address,
                    "balance": 0,
                    "network": "testnet"
                })

        return accounts

    except Exception as e:
        return [{"error": str(e)}]

def get_agent_account_info(address: str) -> Dict:
    """Get detailed account information"""
    try:
        key_manager = KeyManager()

        if not key_manager.has_account(address):
            return {"error": f"Account {address} not found", "success": False}

        # Get stellar account data
        balance = 0
        try:
            account = server.load_account(address)
            # Access balances from raw_data
            for balance_item in account.raw_data.get('balances', []):
                if balance_item.get('asset_type') == "native":
                    balance = float(balance_item.get('balance', '0'))
                    break
        except Exception as e:
            print(f"Warning: Could not load account {address}: {e}")
            balance = 0

        # Simple metadata since KeyManager doesn't support complex metadata
        metadata = {
            "name": "Agent Account",
            "created_at": "2025-01-03T00:00:00Z"
        }

        return {
            "address": address,
            "balance": balance,
            "metadata": metadata,
            "network": "testnet",
            "success": True
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }