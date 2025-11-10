"""
Agent Context - Delegated Authority Pattern with Wallet Mode Support

Provides dual authority for agent operations over both system and user accounts,
with support for external wallet modes.

The agent operates with explicit authority over multiple user contexts:
- system_agent: The agent's own funded mainnet account
- user_id: The current user's accounts (when authenticated)
- wallet_mode: Controls how transactions are signed
- wallet_address: External wallet address (for external mode)

This allows the agent to seamlessly access both its own resources and
user-specific resources without tool duplication.
"""

from typing import List, Optional


class AgentContext:
    """
    Agent execution context with delegated authority and wallet mode support.

    The agent operates with dual authority:
    - system_agent: Agent's own funded mainnet account
    - user_id: Current user's accounts (when authenticated)

    Wallet modes:
    - agent: Agent signs transactions autonomously (default)
    - external: User approves transactions via external wallet (Freighter, etc.)
    - imported: External wallet imported into agent management

    Example:
        # Create context for authenticated user with agent mode
        ctx = AgentContext(user_id="user_abc123", wallet_mode="agent")
        ctx.get_authorized_user_ids()  # ["system_agent", "user_abc123"]
        ctx.requires_user_signing()  # False

        # Create context for external wallet mode
        ctx = AgentContext(
            user_id="user_abc123",
            wallet_mode="external",
            wallet_address="GXXX..."
        )
        ctx.requires_user_signing()  # True
    """

    def __init__(
        self,
        user_id: str,
        wallet_mode: str = "agent",
        wallet_address: Optional[str] = None
    ):
        """
        Initialize agent context with dual authority and wallet mode.

        Args:
            user_id: Current user ID (or "anonymous" for unauthenticated)
            wallet_mode: Wallet operation mode ("agent" | "external" | "imported")
            wallet_address: External wallet address (required for external mode)
        """
        self.user_id = user_id  # Current user (or "anonymous")
        self.agent_user_id = "system_agent"  # Agent's identity
        self.wallet_mode = wallet_mode
        self.wallet_address = wallet_address

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

    def requires_user_signing(self) -> bool:
        """
        Check if transactions need user approval via external wallet.

        Returns:
            True if wallet_mode is "external" and user must sign
        """
        return self.wallet_mode == "external"

    def get_signing_address(self) -> Optional[str]:
        """
        Get address for transaction signing based on wallet mode.

        Returns:
            - External mode: wallet_address
            - Agent/imported mode: None (agent will select account)
        """
        if self.wallet_mode == "external":
            return self.wallet_address
        return None

    def __repr__(self) -> str:
        return f"AgentContext(agent={self.agent_user_id}, user={self.user_id}, mode={self.wallet_mode})"
