"""
Agent Context - Delegated Authority Pattern

Provides dual authority for agent operations over both system and user accounts.

The agent operates with explicit authority over multiple user contexts:
- system_agent: The agent's own funded mainnet account
- user_id: The current user's accounts (when authenticated)

This allows the agent to seamlessly access both its own resources and
user-specific resources without tool duplication.
"""

from typing import List


class AgentContext:
    """
    Agent execution context with delegated authority.

    The agent operates with dual authority:
    - system_agent: Agent's own funded mainnet account
    - user_id: Current user's accounts (when authenticated)

    This allows the agent to seamlessly access both its own
    resources and user-specific resources without tool duplication.

    Example:
        # Create context for authenticated user
        ctx = AgentContext(user_id="user_abc123")
        ctx.get_authorized_user_ids()  # ["system_agent", "user_abc123"]

        # Create context for anonymous user
        ctx = AgentContext(user_id="anonymous")
        ctx.get_authorized_user_ids()  # ["system_agent", "anonymous"]
    """

    def __init__(self, user_id: str):
        """
        Initialize agent context with dual authority.

        Args:
            user_id: Current user ID (or "anonymous" for unauthenticated)
        """
        self.user_id = user_id  # Current user (or "anonymous")
        self.agent_user_id = "system_agent"  # Agent's identity

    def get_authorized_user_ids(self) -> List[str]:
        """
        Get all user IDs this agent has authority over.

        Returns:
            List of authorized user IDs (always includes system_agent)
        """
        return [self.agent_user_id, self.user_id]

    def has_permission(self, account_user_id: str) -> bool:
        """
        Check if agent has authority over an account.

        Args:
            account_user_id: The user_id that owns the account

        Returns:
            True if agent has authority over this account
        """
        return account_user_id in self.get_authorized_user_ids()

    def is_agent_account(self, account_user_id: str) -> bool:
        """
        Check if this is the agent's own account.

        Args:
            account_user_id: The user_id that owns the account

        Returns:
            True if this is a system_agent account
        """
        return account_user_id == self.agent_user_id

    def is_user_account(self, account_user_id: str) -> bool:
        """
        Check if this is the current user's account.

        Args:
            account_user_id: The user_id that owns the account

        Returns:
            True if this is the current user's account
        """
        return account_user_id == self.user_id

    def __repr__(self) -> str:
        return f"AgentContext(agent={self.agent_user_id}, user={self.user_id})"
