"""
Agent Account Management Tools (User-Isolated)
Functions for AI agents to manage their own Stellar accounts with user authentication
"""

from typing import Dict, Optional, List
from stellar_sdk.server import Server
from agent_account_manager import AgentAccountManager
import os
import requests

# Initialize Stellar server
HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")
FRIENDBOT_URL = os.getenv("FRIENDBOT_URL", "https://friendbot.stellar.org")
server = Server(HORIZON_URL)

def create_agent_account(user_id: str, account_name: Optional[str] = None) -> Dict:
    """Create new agent-controlled account for user"""
    try:
        # Create account using AgentAccountManager
        manager = AgentAccountManager()
        result = manager.create_account(user_id=user_id, name=account_name)

        if not result.get("success"):
            return result

        # Fund with testnet lumens
        funded = False
        try:
            response = requests.get(f"{FRIENDBOT_URL}?addr={result['address']}")
            if response.status_code == 200:
                funded = True
        except Exception as e:
            print(f"Failed to fund account: {e}")

        result["funded"] = funded
        result["network"] = "testnet"
        return result

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def list_agent_accounts(user_id: str) -> List[Dict]:
    """List agent-controlled accounts for user"""
    try:
        manager = AgentAccountManager()
        accounts = manager.get_user_accounts(user_id)

        # Enhance with Stellar network data
        enhanced_accounts = []
        for account in accounts:
            try:
                # Get account info from Stellar
                stellar_account = server.load_account(account['address'])
                balance = 0
                # Access balances from raw_data
                for balance_item in stellar_account.raw_data.get('balances', []):
                    if balance_item.get('asset_type') == "native":
                        balance = float(balance_item.get('balance', '0'))
                        break

                account['balance'] = balance
                account['network'] = "testnet"
            except Exception as e:
                # Account exists but might not be funded
                print(f"Warning: Could not load account {account['address']}: {e}")
                account['balance'] = 0
                account['network'] = "testnet"

            enhanced_accounts.append(account)

        return enhanced_accounts

    except Exception as e:
        return [{"error": str(e)}]

def get_agent_account_info(user_id: str, address: str) -> Dict:
    """Get detailed account information (if user owns it)"""
    try:
        manager = AgentAccountManager()

        # Permission check
        if not manager.has_account(user_id, address):
            return {
                "error": f"Account {address} not found or not owned by user",
                "success": False
            }

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

        # Get account metadata from database
        accounts = manager.get_user_accounts(user_id)
        account_info = next((a for a in accounts if a['address'] == address), None)

        metadata = {
            "name": account_info['name'] if account_info else "Unknown",
            "created_at": account_info['created_at'] if account_info else None
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