"""
Agent Tools
LangChain tool wrappers for agent account management functions.

⚠️ SECURITY WARNING ⚠️
These tools use KeyManager (not user-isolated). All users share the same agent accounts.

STATUS: Pending quantum leap migration to per-user agent accounts.

TODO: Migrate to use AccountManager with user_id isolation.
"""

import asyncio
from typing import Optional
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

# Import agent account management functions
try:
    from tools.agent.account_management import create_agent_account, list_agent_accounts, get_agent_account_info
    AGENT_ACCOUNT_TOOLS_AVAILABLE = True
    logger.info("Agent account management functions loaded successfully")
except ImportError as e:
    logger.warning(f"Agent account management functions not available: {e}")
    AGENT_ACCOUNT_TOOLS_AVAILABLE = False

@tool
async def agent_create_account(account_name: Optional[str] = None) -> str:
    """
    Create a new agent-controlled Stellar account for DeFi operations.

    This allows the AI agent to manage its own accounts without requiring external wallet connections.

    Args:
        account_name: Optional descriptive name for the account

    Returns:
        Account creation details including address, name, and funding status
    """
    try:
        if not AGENT_ACCOUNT_TOOLS_AVAILABLE:
            return "Agent account management tools not available."

        # Use system user ID for agent's own accounts
        system_user_id = "system_agent"
        result = create_agent_account(user_id=system_user_id, account_name=account_name)

        if not result.get("success", True):
            return f"Error creating agent account: {result.get('error', 'Unknown error')}"

        response_parts = []
        response_parts.append("## 🤖 Agent Account Created")
        response_parts.append("")
        response_parts.append(f"**Account Name:** {result['name']}")
        response_parts.append(f"**Address:** {result['address']}")
        response_parts.append(f"**Network:** {result['network']}")
        response_parts.append(f"**Funding Status:** {'✅ Funded' if result.get('funded') else '❌ Pending funding'}")
        response_parts.append("")
        response_parts.append("This account is now managed by the AI agent and can be used for DeFi operations.")

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error creating agent account: {e}")
        return f"Error creating agent account: {str(e)}"

@tool
async def agent_list_accounts() -> str:
    """
    List all agent-controlled Stellar accounts.

    Returns a comprehensive list of all accounts managed by the AI agent
    with their current balances and status information.

    Returns:
        List of agent accounts with addresses, names, and balances
    """
    try:
        if not AGENT_ACCOUNT_TOOLS_AVAILABLE:
            return "Agent account management tools not available."

        # Use system user ID for agent's own accounts
        system_user_id = "system_agent"
        accounts = list_agent_accounts(user_id=system_user_id)

        if len(accounts) == 0:
            return "No agent accounts found. Use agent_create_account to create your first account."

        response_parts = []
        response_parts.append(f"## 🤖 Agent Accounts ({len(accounts)} accounts)")
        response_parts.append("")

        for account in accounts:
            if "error" in account:
                response_parts.append(f"**Error:** {account['error']}")
                continue

            response_parts.append(f"### {account.get('name', 'Unnamed Account')}")
            response_parts.append(f"- **Address:** {account['address']}")
            response_parts.append(f"- **Balance:** {account.get('balance', 0):.2f} XLM")
            response_parts.append(f"- **Network:** {account['network']}")
            response_parts.append("")

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error listing agent accounts: {e}")
        return f"Error listing agent accounts: {str(e)}"

@tool
async def agent_get_account_info(address: str) -> str:
    """
    Get detailed information about a specific agent account.

    Args:
        address: The Stellar account address to look up

    Returns:
        Detailed account information including balance and metadata
    """
    try:
        if not AGENT_ACCOUNT_TOOLS_AVAILABLE:
            return "Agent account management tools not available."

        if not address:
            return "Account address is required."

        # Use system user ID for agent's own accounts
        system_user_id = "system_agent"
        result = get_agent_account_info(user_id=system_user_id, address=address)

        if not result.get("success", True):
            return f"Error getting account info: {result.get('error', 'Unknown error')}"

        response_parts = []
        response_parts.append("## 🤖 Agent Account Information")
        response_parts.append("")
        response_parts.append(f"**Address:** {result['address']}")
        response_parts.append(f"**Balance:** {result.get('balance', 0):.2f} XLM")
        response_parts.append(f"**Network:** {result['network']}")

        if result.get('metadata'):
            metadata = result['metadata']
            response_parts.append(f"**Name:** {metadata.get('name', 'Unnamed')}")
            response_parts.append(f"**Created:** {metadata.get('created_at', 'Unknown')}")

        response_parts.append("")
        response_parts.append("This account is managed by the AI agent and ready for DeFi operations.")

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return f"Error getting account info: {str(e)}"