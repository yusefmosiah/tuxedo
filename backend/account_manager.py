"""
Account Manager - Chain-agnostic wallet account management
Provides filesystem primitives for agents to organize accounts
Agents construct "portfolio" patterns dynamically from these primitives
"""
from typing import Dict, Optional, List, TYPE_CHECKING
from database_passkeys import PasskeyDatabaseManager
from encryption import EncryptionManager
from chains.base import ChainAdapter
from chains.stellar import StellarAdapter
import secrets
import sqlite3
import json

if TYPE_CHECKING:
    from agent.context import AgentContext

class AccountManager:
    """
    Manages user wallet accounts with multi-chain support

    This is NOT a portfolio manager. Agents use these primitives to:
    - Generate/import/export accounts
    - Organize accounts in user's filesystem workspace
    - Construct portfolio views dynamically when needed

    Portfolio = Pattern agents construct, not a database abstraction
    """

    def __init__(self, db_path: str = "tuxedo_passkeys.db"):
        self.db = PasskeyDatabaseManager(db_path)
        self.encryption = EncryptionManager()

        # Registry of chain adapters - MAINNET ONLY
        self.chains: Dict[str, ChainAdapter] = {
            "stellar": StellarAdapter(network="mainnet"),
            # Future: "solana": SolanaAdapter(),
            # Future: "ethereum": EthereumAdapter(),
            # Future: "sui": SuiAdapter(),
        }

    def generate_account(
        self,
        user_id: str,
        chain: str,
        name: Optional[str] = None,
        network: str = "mainnet",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Generate new account for user on specified chain and network (MAINNET ONLY)

        Args:
            user_id: User identifier
            chain: Blockchain (e.g., "stellar")
            name: Optional account name
            network: Network to use (always "mainnet" in this version)
            metadata: Optional metadata dict

        Returns:
            Dict with account details or error

        Note:
            - Mainnet-only system - all accounts created on mainnet
            - Accounts must be funded manually by user with real XLM
        """
        try:
            # Validate chain
            if chain not in self.chains:
                return {
                    "error": f"Unsupported chain: {chain}",
                    "success": False
                }

            # Generate keypair
            adapter = self.chains[chain]
            keypair = adapter.generate_keypair()

            # Encrypt private key
            encrypted_private_key = self.encryption.encrypt(
                keypair.private_key,
                user_id
            )

            # Store in database
            account_id = f"account_{secrets.token_urlsafe(16)}"

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wallet_accounts
                    (id, user_id, chain, public_key, encrypted_private_key,
                     name, source, network, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    account_id,
                    user_id,
                    chain,
                    keypair.public_key,
                    encrypted_private_key,
                    name or f"{chain.capitalize()} Account",
                    "generated",
                    network,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()

            return {
                "account_id": account_id,
                "chain": chain,
                "network": network,
                "address": keypair.public_key,
                "name": name or f"{chain.capitalize()} Account",
                "source": "generated",
                "success": True
            }

        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }

    def import_account(
        self,
        user_id: str,
        chain: str,
        private_key: str,
        name: Optional[str] = None,
        network: str = "mainnet",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Import existing wallet for user (MAINNET ONLY)
        KILLER FEATURE: Bridges existing DeFi users into Tuxedo

        Args:
            user_id: User identifier
            chain: Blockchain (e.g., "stellar")
            private_key: Private key to import
            name: Optional account name
            network: Network this account is on (always "mainnet" in this version)
            metadata: Optional metadata dict
        """
        try:
            # Validate chain
            if chain not in self.chains:
                return {
                    "error": f"Unsupported chain: {chain}",
                    "success": False
                }

            # Import keypair
            adapter = self.chains[chain]
            try:
                keypair = adapter.import_keypair(private_key)
            except Exception as e:
                return {
                    "error": f"Invalid private key for {chain}: {e}",
                    "success": False
                }

            # Encrypt private key
            encrypted_private_key = self.encryption.encrypt(
                keypair.private_key,
                user_id
            )

            # Store in database
            account_id = f"account_{secrets.token_urlsafe(16)}"

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wallet_accounts
                    (id, user_id, chain, public_key, encrypted_private_key,
                     name, source, network, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    account_id,
                    user_id,
                    chain,
                    keypair.public_key,
                    encrypted_private_key,
                    name or f"Imported {chain.capitalize()} Account",
                    "imported",
                    network,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()

            return {
                "account_id": account_id,
                "chain": chain,
                "network": network,
                "address": keypair.public_key,
                "name": name or f"Imported {chain.capitalize()} Account",
                "source": "imported",
                "success": True
            }

        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }

    def export_account(
        self,
        agent_context: "AgentContext",
        account_id: str
    ) -> Dict:
        """
        Export wallet private key with delegated authority support.
        KILLER FEATURE: Users maintain full custodial control

        Args:
            agent_context: Agent execution context with dual authority
            account_id: Account to export
        """
        try:
            # Get account
            account = self._get_account_by_id(account_id)
            if not account:
                return {
                    "error": "Account not found",
                    "success": False
                }

            # Verify permission
            if not agent_context.has_permission(account['user_id']):
                return {
                    "error": "Permission denied: account not owned by authorized users",
                    "success": False
                }

            # Decrypt private key using actual owner
            private_key = self.encryption.decrypt(
                account['encrypted_private_key'],
                account['user_id']  # Use actual owner for decryption
            )

            # Get chain adapter for export format
            chain = account['chain']
            adapter = self.chains[chain]

            return {
                "chain": chain,
                "address": account['public_key'],
                "private_key": private_key,
                "export_format": f"{chain}_secret_key",
                "warning": "Keep this private key secure. Anyone with access can control these funds.",
                "success": True
            }

        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }

    def get_user_accounts(
        self,
        user_id: str,
        chain: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all accounts for user, optionally filtered by chain
        Agent constructs portfolio views from this data
        """
        try:
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if chain:
                    cursor.execute('''
                        SELECT id, chain, public_key, name, source, created_at, last_used_at, metadata
                        FROM wallet_accounts
                        WHERE user_id = ? AND chain = ?
                        ORDER BY created_at DESC
                    ''', (user_id, chain))
                else:
                    cursor.execute('''
                        SELECT id, chain, public_key, name, source, created_at, last_used_at, metadata
                        FROM wallet_accounts
                        WHERE user_id = ?
                        ORDER BY chain, created_at DESC
                    ''', (user_id,))

                accounts = [dict(row) for row in cursor.fetchall()]

            # Enhance with on-chain data
            for account in accounts:
                try:
                    # Parse metadata JSON if present
                    if account.get('metadata'):
                        account['metadata'] = json.loads(account['metadata'])

                    adapter = self.chains[account['chain']]
                    chain_account = adapter.get_account(account['public_key'])
                    account['balance'] = chain_account.balance
                    account['balances'] = chain_account.balances
                except Exception as e:
                    account['balance'] = 0
                    account['balances'] = []
                    account['error'] = str(e)

            return accounts

        except Exception as e:
            return [{"error": str(e)}]

    def delete_account(
        self,
        agent_context: "AgentContext",
        account_id: str
    ) -> Dict:
        """
        Delete an account with delegated authority support.

        Args:
            agent_context: Agent execution context with dual authority
            account_id: Account to delete
        """
        try:
            # Get account
            account = self._get_account_by_id(account_id)
            if not account:
                return {
                    "error": "Account not found",
                    "success": False
                }

            # Verify permission
            if not agent_context.has_permission(account['user_id']):
                return {
                    "error": "Permission denied: account not owned by authorized users",
                    "success": False
                }

            # Delete from database
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM wallet_accounts WHERE id = ?
                ''', (account_id,))
                conn.commit()

            return {
                "success": True,
                "message": f"Account {account_id} deleted successfully"
            }

        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }

    def _get_account_by_id(self, account_id: str) -> Optional[Dict]:
        """Get account by ID"""
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM wallet_accounts WHERE id = ?
            ''', (account_id,))
            row = cursor.fetchone()
        return dict(row) if row else None

    def user_owns_account(self, agent_context: "AgentContext", account_id: str) -> bool:
        """
        Check if agent has permission to access account.

        Args:
            agent_context: Agent execution context with dual authority
            account_id: Account to check

        Returns:
            True if agent has permission to access this account
        """
        account = self._get_account_by_id(account_id)
        return account is not None and agent_context.has_permission(account['user_id'])

    def get_keypair_for_signing(self, agent_context: "AgentContext", account_id: str):
        """
        Get decrypted keypair for transaction signing with delegated authority.

        Agent can sign for accounts owned by any of the authorized user IDs
        in the agent context.

        Args:
            agent_context: Agent execution context with dual authority
            account_id: Account to access

        Returns:
            Keypair object for signing

        Raises:
            ValueError: If account not found
            PermissionError: If agent not authorized for this account
        """
        # Get account
        account = self._get_account_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        # Check permission using context
        if not agent_context.has_permission(account['user_id']):
            raise PermissionError(
                f"Permission denied: account owned by {account['user_id']}, "
                f"agent context: {agent_context}"
            )

        # Decrypt private key using the account's actual owner
        private_key = self.encryption.decrypt(
            account['encrypted_private_key'],
            account['user_id']  # Use actual owner for decryption
        )

        # Create keypair object (in-memory)
        adapter = self.chains[account['chain']]
        keypair = adapter.import_keypair(private_key)

        return keypair
