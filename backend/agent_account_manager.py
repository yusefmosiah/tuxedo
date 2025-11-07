"""
Agent Account Manager - Replaces KeyManager with secure user-linked storage
"""
from typing import Dict, Optional, List
from stellar_sdk import Keypair
from database_passkeys import PasskeyDatabaseManager
from encryption import EncryptionManager
import secrets
import logging

logger = logging.getLogger(__name__)


class AgentAccountManager:
    """Manages agent Stellar accounts with user isolation and encryption"""

    def __init__(self, db_path: str = "tuxedo_passkeys.db"):
        self.db = PasskeyDatabaseManager(db_path)
        self.encryption = EncryptionManager()

    def create_account(
        self,
        user_id: str,
        name: Optional[str] = None
    ) -> Dict:
        """Create new agent account for user"""
        try:
            # Generate Stellar keypair
            keypair = Keypair.random()

            # Encrypt private key with user-specific key
            encrypted_secret = self.encryption.encrypt(
                keypair.secret,
                user_id
            )

            # Store in database
            account = self.db.create_agent_account(
                user_id=user_id,
                stellar_public_key=keypair.public_key,
                stellar_secret_key_encrypted=encrypted_secret,
                name=name
            )

            return {
                "address": keypair.public_key,
                "name": account['name'],
                "created_at": account['created_at'],
                "success": True
            }

        except Exception as e:
            logger.error(f"Error creating agent account: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def get_user_accounts(self, user_id: str) -> List[Dict]:
        """Get all accounts owned by user"""
        try:
            accounts = self.db.get_agent_accounts_by_user(user_id)
            return [{
                "address": acc['stellar_public_key'],
                "name": acc['name'],
                "created_at": acc['created_at'],
                "last_used_at": acc['last_used_at']
            } for acc in accounts]

        except Exception as e:
            logger.error(f"Error getting user accounts: {e}")
            return [{"error": str(e)}]

    def get_keypair(
        self,
        user_id: str,
        stellar_public_key: str
    ) -> Keypair:
        """Get keypair for signing (with permission check)"""
        # Get account from database
        account = self.db.get_agent_account(stellar_public_key)

        if not account:
            raise ValueError(f"Account {stellar_public_key} not found")

        # Permission check: User must own the account
        if account['user_id'] != user_id:
            raise PermissionError(
                f"User {user_id} does not have permission to access "
                f"account {stellar_public_key}"
            )

        # Decrypt private key
        secret = self.encryption.decrypt(
            account['stellar_secret_key_encrypted'],
            user_id
        )

        # Update last used timestamp
        self.db.update_agent_account_last_used(stellar_public_key)

        return Keypair.from_secret(secret)

    def has_account(self, user_id: str, stellar_public_key: str) -> bool:
        """Check if user owns account"""
        account = self.db.get_agent_account(stellar_public_key)
        return account is not None and account['user_id'] == user_id

    def delete_account(self, user_id: str, stellar_public_key: str) -> bool:
        """Delete account (only if user owns it)"""
        return self.db.delete_agent_account(user_id, stellar_public_key)
