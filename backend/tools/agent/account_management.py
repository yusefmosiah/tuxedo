"""
Agent Account Management Tools
Functions for AI agents to manage their own Stellar accounts

✅ QUANTUM LEAP COMPLETE - USER-ISOLATED ✅

This file uses AccountManager which enforces user isolation.
Each user has their own isolated agent accounts.

Migration complete:
- ✅ Added user_id parameter to all functions
- ✅ Uses AccountManager instead of KeyManager
- ✅ Creates per-user agent accounts
- ✅ Permission checks enforced by AccountManager
"""

from typing import Dict, Optional, List
from account_manager import AccountManager
import os
import requests

# Initialize configuration
FRIENDBOT_URL = os.getenv("FRIENDBOT_URL", "https://friendbot.stellar.org")

def create_agent_account(user_id: str, account_name: Optional[str] = None) -> Dict:
    """Create new agent-controlled account for a specific user"""
    try:
        # Initialize account manager
        account_manager = AccountManager()

        # Generate account on Stellar chain
        result = account_manager.generate_account(
            user_id=user_id,
            chain="stellar",
            name=account_name or "Agent Account",
            metadata={
                "type": "agent",
                "network": "testnet"
            }
        )

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

        return {
            "address": result["address"],
            "name": result["name"],
            "funded": funded,
            "network": "testnet",
            "success": True
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def list_agent_accounts(user_id: str) -> List[Dict]:
    """List all agent-controlled accounts for a specific user"""
    try:
        # Initialize account manager
        account_manager = AccountManager()

        # Get user's Stellar accounts
        accounts = account_manager.get_user_accounts(
            user_id=user_id,
            chain="stellar"
        )

        # Filter for agent accounts only and format response
        agent_accounts = []
        for account in accounts:
            if account.get("error"):
                continue

            # Check if this is an agent account
            metadata = account.get("metadata", {})
            if metadata.get("type") == "agent":
                agent_accounts.append({
                    "address": account["public_key"],
                    "balance": account.get("balance", 0),
                    "network": "testnet",
                    "name": account.get("name", "Agent Account")
                })

        return agent_accounts

    except Exception as e:
        return [{"error": str(e)}]

def get_agent_account_info(user_id: str, address: str) -> Dict:
    """Get detailed account information for a specific user's agent account"""
    try:
        # Initialize account manager
        account_manager = AccountManager()

        # Get all user accounts
        accounts = account_manager.get_user_accounts(
            user_id=user_id,
            chain="stellar"
        )

        # Find the account with matching address
        target_account = None
        for account in accounts:
            if account.get("public_key") == address:
                target_account = account
                break

        if not target_account:
            return {"error": f"Account {address} not found", "success": False}

        # Check if this is an agent account
        metadata = target_account.get("metadata", {})
        if metadata.get("type") != "agent":
            return {"error": f"Account {address} is not an agent account", "success": False}

        return {
            "address": target_account["public_key"],
            "balance": target_account.get("balance", 0),
            "metadata": metadata,
            "network": "testnet",
            "name": target_account.get("name", "Agent Account"),
            "success": True
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }