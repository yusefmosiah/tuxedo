from typing import Optional
from langchain_core.tools import tool
from tools.agent.account_management import create_agent_account, list_agent_accounts, get_agent_account_info

@tool
def agent_create_account(account_name: Optional[str] = None) -> str:
    """
    Create a new agent-controlled Stellar account for DeFi operations.
    Args:
        account_name: Optional descriptive name for the account
    """
    try:
        # Use system user ID for agent's own accounts
        system_user_id = "system_agent"
        result = create_agent_account(user_id=system_user_id, account_name=account_name)

        if not result.get("success", True):
            return f"Error creating agent account: {result.get('error', 'Unknown error')}"

        return (
            f"## 🤖 Agent Account Created\n\n"
            f"**Account Name:** {result['name']}\n"
            f"**Address:** {result['address']}\n"
            f"**Network:** {result['network']}\n"
            f"**Funding Status:** {'✅ Funded' if result.get('funded') else '❌ Pending funding'}\n"
        )
    except Exception as e:
        return f"Error creating agent account: {str(e)}"

@tool
def agent_list_accounts(limit: int) -> str:
    """
    List all agent-controlled Stellar accounts.
    Args:
        limit: Limit on number of accounts to list (e.g. 10)
    """
    try:
        system_user_id = "system_agent"
        accounts = list_agent_accounts(user_id=system_user_id)

        if len(accounts) == 0:
            return "No agent accounts found."

        response_parts = [f"## 🤖 Agent Accounts ({len(accounts)} accounts)\n"]
        for account in accounts:
            if "error" in account:
                response_parts.append(f"**Error:** {account['error']}")
                continue
            response_parts.append(
                f"### {account.get('name', 'Unnamed Account')}\n"
                f"- **Address:** {account['address']}\n"
                f"- **Balance:** {account.get('balance', 0):.2f} XLM\n"
                f"- **Network:** {account['network']}\n"
            )
        return "\n".join(response_parts)
    except Exception as e:
        return f"Error listing agent accounts: {str(e)}"

@tool
def agent_get_account_info(address: str) -> str:
    """
    Get detailed information about a specific agent account.
    Args:
        address: The Stellar account address to look up
    """
    try:
        if not address:
            return "Account address is required."

        system_user_id = "system_agent"
        result = get_agent_account_info(user_id=system_user_id, address=address)

        if not result.get("success", True):
            return f"Error getting account info: {result.get('error', 'Unknown error')}"

        response = (
            f"## 🤖 Agent Account Information\n\n"
            f"**Address:** {result['address']}\n"
            f"**Balance:** {result.get('balance', 0):.2f} XLM\n"
            f"**Network:** {result['network']}\n"
        )
        if result.get('metadata'):
            metadata = result['metadata']
            response += f"**Name:** {metadata.get('name', 'Unnamed')}\n"
            response += f"**Created:** {metadata.get('created_at', 'Unknown')}\n"

        return response
    except Exception as e:
        return f"Error getting account info: {str(e)}"

def get_choir_account_tools():
    return [agent_create_account, agent_list_accounts, agent_get_account_info]
