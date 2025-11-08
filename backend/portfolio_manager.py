"""
Portfolio Manager - Chain-agnostic wallet portfolio management
Replaces KeyManager with secure, multi-chain portfolio system
"""
from typing import Dict, Optional, List
from database_passkeys import PasskeyDatabaseManager
from encryption import EncryptionManager
from chains.base import ChainAdapter
from chains.stellar import StellarAdapter
import secrets
import sqlite3
import logging

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manages user portfolios with multi-chain wallet accounts"""

    def __init__(self, db_path: str = "tuxedo_passkeys.db"):
        self.db = PasskeyDatabaseManager(db_path)
        self.encryption = EncryptionManager()

        # Registry of chain adapters
        self.chains: Dict[str, ChainAdapter] = {
            "stellar": StellarAdapter(network="testnet"),
            # Future: "solana": SolanaAdapter(),
            # Future: "ethereum": EthereumAdapter(),
            # Future: "sui": SuiAdapter(),
        }
        logger.info(f"PortfolioManager initialized with chains: {list(self.chains.keys())}")

    def create_portfolio(
        self,
        user_id: str,
        name: str = "Main Portfolio"
    ) -> Dict:
        """Create new portfolio for user"""
        try:
            portfolio_id = f"portfolio_{secrets.token_urlsafe(16)}"

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO portfolios (id, user_id, name, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (portfolio_id, user_id, name))
                conn.commit()

            logger.info(f"Created portfolio {portfolio_id} for user {user_id}")
            return {
                "portfolio_id": portfolio_id,
                "name": name,
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to create portfolio for user {user_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def generate_account(
        self,
        user_id: str,
        portfolio_id: str,
        chain: str,
        name: Optional[str] = None
    ) -> Dict:
        """Generate new account in portfolio for specified chain"""
        try:
            # Validate chain
            if chain not in self.chains:
                return {
                    "error": f"Unsupported chain: {chain}. Supported: {list(self.chains.keys())}",
                    "success": False
                }

            # Verify user owns portfolio
            if not self._verify_portfolio_ownership(user_id, portfolio_id):
                return {
                    "error": "Portfolio not found or not owned by user",
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
                    (id, portfolio_id, chain, public_key, encrypted_private_key,
                     name, source, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    account_id,
                    portfolio_id,
                    chain,
                    keypair.public_key,
                    encrypted_private_key,
                    name or f"{chain.capitalize()} Account",
                    "generated",
                    None  # metadata
                ))
                conn.commit()

            logger.info(f"Generated {chain} account {account_id} for user {user_id}")
            return {
                "account_id": account_id,
                "chain": chain,
                "address": keypair.public_key,
                "name": name or f"{chain.capitalize()} Account",
                "source": "generated",
                "success": True
            }

        except Exception as e:
            logger.error(f"Failed to generate account for user {user_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def import_account(
        self,
        user_id: str,
        portfolio_id: str,
        chain: str,
        private_key: str,
        name: Optional[str] = None
    ) -> Dict:
        """
        Import existing wallet into portfolio
        KILLER FEATURE: Bridges existing DeFi users into Tuxedo
        """
        try:
            # Validate chain
            if chain not in self.chains:
                return {
                    "error": f"Unsupported chain: {chain}. Supported: {list(self.chains.keys())}",
                    "success": False
                }

            # Verify user owns portfolio
            if not self._verify_portfolio_ownership(user_id, portfolio_id):
                return {
                    "error": "Portfolio not found or not owned by user",
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
                    (id, portfolio_id, chain, public_key, encrypted_private_key,
                     name, source, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    account_id,
                    portfolio_id,
                    chain,
                    keypair.public_key,
                    encrypted_private_key,
                    name or f"Imported {chain.capitalize()} Account",
                    "imported",
                    None  # metadata
                ))
                conn.commit()

            logger.info(f"Imported {chain} account {account_id} for user {user_id}")
            return {
                "account_id": account_id,
                "chain": chain,
                "address": keypair.public_key,
                "name": name or f"Imported {chain.capitalize()} Account",
                "source": "imported",
                "success": True
            }

        except Exception as e:
            logger.error(f"Failed to import account for user {user_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def export_account(
        self,
        user_id: str,
        account_id: str
    ) -> Dict:
        """
        Export wallet private key
        KILLER FEATURE: Users maintain full custodial control
        """
        try:
            # Get account
            account = self._get_account_by_id(account_id)
            if not account:
                return {
                    "error": "Account not found",
                    "success": False
                }

            # Verify ownership through portfolio
            portfolio_id = account['portfolio_id']
            if not self._verify_portfolio_ownership(user_id, portfolio_id):
                return {
                    "error": "Permission denied: account not owned by user",
                    "success": False
                }

            # Decrypt private key
            private_key = self.encryption.decrypt(
                account['encrypted_private_key'],
                user_id
            )

            # Get chain adapter for export format
            chain = account['chain']
            adapter = self.chains.get(chain)

            logger.warning(f"User {user_id} exported account {account_id}")
            return {
                "chain": chain,
                "address": account['public_key'],
                "private_key": private_key,
                "export_format": f"{chain}_secret_key",
                "warning": "Keep this private key secure. Anyone with access can control these funds.",
                "success": True
            }

        except Exception as e:
            logger.error(f"Failed to export account {account_id} for user {user_id}: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def get_portfolio_accounts(
        self,
        user_id: str,
        portfolio_id: str,
        chain: Optional[str] = None
    ) -> List[Dict]:
        """Get all accounts in portfolio, optionally filtered by chain"""
        try:
            # Verify ownership
            if not self._verify_portfolio_ownership(user_id, portfolio_id):
                return []

            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if chain:
                    cursor.execute('''
                        SELECT id, chain, public_key, name, source, created_at, last_used_at
                        FROM wallet_accounts
                        WHERE portfolio_id = ? AND chain = ?
                        ORDER BY created_at DESC
                    ''', (portfolio_id, chain))
                else:
                    cursor.execute('''
                        SELECT id, chain, public_key, name, source, created_at, last_used_at
                        FROM wallet_accounts
                        WHERE portfolio_id = ?
                        ORDER BY chain, created_at DESC
                    ''', (portfolio_id,))

                accounts = [dict(row) for row in cursor.fetchall()]

            # Enhance with on-chain data
            for account in accounts:
                try:
                    adapter = self.chains.get(account['chain'])
                    if adapter:
                        chain_account = adapter.get_account(account['public_key'])
                        account['balance'] = chain_account.balance
                        account['balances'] = chain_account.balances
                except Exception as e:
                    account['balance'] = 0
                    account['balances'] = []
                    account['error'] = str(e)

            return accounts

        except Exception as e:
            logger.error(f"Failed to get portfolio accounts for user {user_id}: {e}")
            return [{"error": str(e)}]

    def get_user_portfolios(self, user_id: str) -> List[Dict]:
        """Get all portfolios for a user"""
        try:
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, created_at FROM portfolios
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))

                portfolios = [dict(row) for row in cursor.fetchall()]

            logger.info(f"Retrieved {len(portfolios)} portfolios for user {user_id}")
            return portfolios
        except Exception as e:
            logger.error(f"Failed to get portfolios for user {user_id}: {e}")
            return []

    def get_keypair_for_signing(self, user_id: str, account_id: str):
        """
        Get keypair for signing transactions (in-memory only)
        Used by Stellar tools for transaction signing
        """
        try:
            # Get account
            account = self._get_account_by_id(account_id)
            if not account:
                raise ValueError("Account not found")

            # Verify ownership
            portfolio_id = account['portfolio_id']
            if not self._verify_portfolio_ownership(user_id, portfolio_id):
                raise PermissionError("Not your account")

            # Decrypt private key
            private_key = self.encryption.decrypt(
                account['encrypted_private_key'],
                user_id
            )

            # Create keypair object (in-memory)
            chain = account['chain']
            adapter = self.chains.get(chain)
            if not adapter:
                raise ValueError(f"Chain {chain} not supported")

            keypair = adapter.import_keypair(private_key)

            # Update last_used_at
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE wallet_accounts SET last_used_at = datetime('now')
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()

            return keypair
        except Exception as e:
            logger.error(f"Failed to get keypair for signing: {e}")
            raise

    def _verify_portfolio_ownership(self, user_id: str, portfolio_id: str) -> bool:
        """Verify user owns portfolio"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM portfolios
                WHERE id = ? AND user_id = ?
            ''', (portfolio_id, user_id))
            count = cursor.fetchone()[0]
        return count > 0

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
