# Agent Account Security Implementation Plan

**Chain-Agnostic Filesystem-Based Account Management with Wallet Import/Export**

---

## Executive Summary

**Vision:** Tuxedo is a chain-agnostic conversational AI agent for discovering and interacting with DeFi protocols. Agents have **filesystem access** to organize and manage blockchain accounts across multiple networks.

**Current Critical Issue:** No secure user isolation for agent-managed accounts. Any authenticated user can access any agent's blockchain accounts across all chains.

**Goal:** Implement production-ready security architecture that:

- Provides agents with user-isolated filesystem access
- Supports multiple blockchain networks (Stellar, Solana, EVM, Sui, etc.)
- Enables wallet import/export as a **killer feature**
- Lets agents construct portfolio abstractions dynamically from filesystem
- Respects "not-your-keys-not-your-crypto" principles

**Timeline:** 8-12 hours of focused development
**Priority:** CRITICAL - Required before mainnet deployment

---

## Strategic Vision Alignment

### Chain-Agnostic Design

Tuxedo's future is **multi-chain**. The agent backend will support:

- **Stellar** (current MVP on testnet)
- **Solana** (Phantom wallet compatibility)
- **EVM chains** (Metamask compatibility)
- **Sui** (token economics chain per Choir whitepaper)
- **Additional chains** as ecosystem grows

Wallets and blockchain tools are just **data and code** at the agent's fingertips. The architecture must abstract blockchain specifics behind a common interface.

### Filesystem-Based Account Management

Agents don't have **one account**. Agents have **filesystem access** to organize accounts:

- User-isolated directory structure
- Multiple accounts per chain stored as files/database entries
- Agent constructs "portfolio" abstractions dynamically as needed for users
- Flexible organization: trading accounts, yield accounts, experiment accounts, etc.
- Agent can create any organizational pattern the user needs
- Portfolio is a **pattern the agent constructs**, not a rigid database schema

### Wallet Import/Export: The Killer Feature

**Why this matters:**

1. **Bridges existing DeFi users** into the agentic world
2. **Onboards Tuxedo users** to enjoy full custodial control
3. **Respects "not-your-keys-not-your-crypto"** principles
4. **Legitimates Tuxedo** with blockchain enthusiasts who demand key ownership

**Use cases:**

- Import existing Stellar wallet → let agent manage it → export back to Freighter
- Import Phantom wallet → agent optimizes Solana yields → export to mobile
- Import Metamask wallet → agent executes EVM strategies → maintain full control
- Create wallet in Tuxedo → export to external wallet for safekeeping

**Transactions are also an option**, but some chains have high fees. Import/export provides **zero-cost onboarding/offboarding**.

### Mobile Future

Eventually mobile app support will enable:

- Import/export to **local mobile wallets**
- Native Phantom integration on mobile
- Native Freighter integration on mobile
- Platform-specific wallet standards (iOS Keychain, Android Keystore)

---

## Key Architectural Principle: Filesystem Over Abstraction

**Important Nuance:** This plan does NOT create a "portfolio abstraction" that agents must work with. Instead:

### ❌ Wrong Approach (Rigid Schema)

```
Agent → Portfolio Object (database table) → Must organize accounts this way
```

- Portfolio is a first-class database table
- Agent must work within portfolio structure
- Inflexible, prescriptive organization

### ✅ Correct Approach (Filesystem Primitives)

```
Agent → Filesystem Access → Organizes accounts freely → Constructs portfolio views for users
```

- Agent has user-isolated filesystem workspace
- Agent can organize accounts however it wants (files, directories, database entries)
- Agent **constructs** "portfolio" abstractions dynamically when users need them
- Portfolio is a **pattern**, not a **schema**

**Why This Matters:**

- Gives agent flexibility to create organizational patterns that match user needs
- Agent can evolve organization strategies without database migrations
- Portfolio is just one possible way to group accounts - agent might create others
- Lower-level primitives enable higher-level intelligence

**Example:**

- User: "Show me my DeFi portfolio"
- Agent: Reads accounts from filesystem, constructs portfolio view, presents it
- User: "Organize my accounts by strategy instead"
- Agent: Re-reads same accounts, constructs strategy-based view, presents it
- Same data, different abstractions - agent has the flexibility to construct what's needed

---

## Current Architecture (Insecure)

```
┌─────────────────────────────────────┐
│  Passkey Auth (✅ Secure)           │
│  - users table with id              │
│  - passkey_credentials              │
│  - recovery_codes                   │
└─────────────────────────────────────┘
              ❌ NO LINK
┌─────────────────────────────────────┐
│  Agent Accounts (❌ INSECURE)       │
│  - KeyManager: JSON file            │
│  - Stellar-specific only            │
│  - No user_id reference             │
│  - Plain text private keys          │
│  - Global access to all accounts    │
│  - Single account per agent         │
└─────────────────────────────────────┘
```

### Security Vulnerabilities

1. **No User Isolation**
   - `KeyManager` stores all accounts globally in `.stellar_keystore.json`
   - Any authenticated user can access ANY account
   - No portfolio ownership concept

2. **Chain-Specific Implementation**
   - Hardcoded to Stellar only
   - Cannot support Solana, EVM, or other chains
   - Would require complete rewrite for each chain

3. **No Import/Export Capability**
   - Users cannot import existing wallets
   - Users cannot export to external wallets
   - Locks users into Tuxedo ecosystem
   - Violates "not-your-keys-not-your-crypto"

4. **No Encryption at Rest**
   - Private keys stored in plain text JSON
   - File permissions (0600) only protect against OS-level access
   - No protection if database/filesystem is compromised

5. **No Portfolio Management**
   - Agents cannot manage multiple accounts per chain
   - Agents cannot organize accounts by purpose
   - No flexibility for advanced strategies

6. **No Audit Trail**
   - Can't track which user created which account
   - Can't identify unauthorized access attempts
   - No recovery path if user loses passkey

---

## Target Architecture (Secure & Chain-Agnostic)

**CRITICAL: No Portfolio Table! Portfolio = Pattern, Not Schema**

```
┌─────────────────────────────────────┐
│  Passkey Auth                       │
│  users.id = "user_abc123"           │
└────────────┬────────────────────────┘
             │ ✅ Links directly to accounts
             ↓
┌─────────────────────────────────────┐
│  wallet_accounts table              │
│   - user_id → users.id ✅           │
│   - chain ("stellar", "solana")     │
│   - public_key                      │
│   - encrypted_private_key ✅        │
│   - name, source, metadata          │
│   - ON DELETE CASCADE ✅            │
│                                     │
│   ❌ NO portfolio_id column!        │
│   ❌ NO portfolios table!           │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Agent Filesystem Workspace         │
│  (Optional - for file-based org)    │
│                                     │
│  /data/tuxedo/user_abc123/          │
│   ├── accounts/                     │
│   │   ├── stellar/                  │
│   │   │   ├── trading_notes.json    │
│   │   │   └── yield_config.json     │
│   │   ├── solana/                   │
│   │   └── ethereum/                 │
│   ├── strategies/                   │
│   │   └── defi_yields.json          │
│   └── tools/                        │
│                                     │
│  Agent uses metadata field to       │
│  link accounts to filesystem paths  │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Agent Constructs Abstractions      │
│  (Dynamically, on-demand)           │
│                                     │
│  User: "Show me my portfolio"       │
│  Agent:                             │
│    1. Reads user's accounts         │
│    2. Fetches on-chain balances     │
│    3. Constructs portfolio view     │
│    4. Presents to user              │
│                                     │
│  User: "Group by strategy"          │
│  Agent:                             │
│    1. Reads same accounts           │
│    2. Constructs strategy view      │
│    3. Presents different view       │
│                                     │
│  Portfolio = Pattern, not Schema    │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Multiple Blockchains               │
│  - Stellar (testnet → mainnet)      │
│  - Solana                           │
│  - EVM chains (Ethereum, Polygon)   │
│  - Sui                              │
└─────────────────────────────────────┘
```

### Security Improvements

✅ **User Isolation:** Filesystem permissions + database constraints
✅ **Chain Agnostic:** Supports any blockchain via `chain` field
✅ **Flexible Organization:** Agent constructs portfolio abstractions dynamically
✅ **Wallet Import/Export:** Users own their keys and can migrate freely
✅ **Encryption at Rest:** Private keys encrypted with user-specific keys
✅ **Access Control:** Permission checks on every operation
✅ **Audit Trail:** All operations logged to database
✅ **Recovery Support:** User passkey recovery → workspace recovery
✅ **Filesystem Primitives:** Agent has low-level access, builds high-level patterns

---

## Implementation Plan

### Phase 1: Database Schema & Encryption (3-4 hours)

#### 1.1 Update Database Schema

**CRITICAL: NO PORTFOLIO TABLE!**

Portfolios are NOT a database abstraction - they are dynamic patterns that agents construct from filesystem primitives. The database only stores the raw account data.

**File:** `backend/database_passkeys.py`

Add to `PasskeyDatabaseManager.init_database()`:

```python
def init_database(self):
    # ... existing tables ...

    # ❌ NO PORTFOLIOS TABLE - Portfolio is a pattern, not a schema!
    # Agents construct portfolio views dynamically from wallet_accounts

    # Wallet accounts table (NEW - CHAIN AGNOSTIC)
    # Accounts belong directly to users, not to portfolios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallet_accounts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            chain TEXT NOT NULL,
            public_key TEXT NOT NULL,
            encrypted_private_key TEXT NOT NULL,
            name TEXT,
            source TEXT DEFAULT 'generated',
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(chain, public_key)
        )
    ''')

    # Indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_wallet_accounts_user_id
        ON wallet_accounts(user_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_wallet_accounts_chain
        ON wallet_accounts(chain)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_wallet_accounts_user_chain
        ON wallet_accounts(user_id, chain)
    ''')

    conn.commit()
```

**Key Changes:**

- ❌ Removed `portfolios` table entirely
- ✅ `wallet_accounts.user_id` links directly to `users.id`
- ✅ Agent reads user's accounts from filesystem/database
- ✅ Agent constructs portfolio views dynamically when needed
- ✅ No rigid schema constraining how agents organize accounts

#### 1.2 Chain Abstraction Layer

**New File:** `backend/chains/base.py`

```python
"""
Base interface for blockchain interactions
All chain implementations must follow this interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ChainKeypair:
    """Chain-agnostic keypair representation"""
    public_key: str
    private_key: str
    chain: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChainAccount:
    """Chain-agnostic account representation"""
    address: str
    chain: str
    balance: float
    balances: List[Dict[str, Any]]  # For multi-asset chains

class ChainAdapter(ABC):
    """Abstract base class for chain-specific implementations"""

    @property
    @abstractmethod
    def chain_name(self) -> str:
        """Returns chain identifier (e.g., 'stellar', 'solana', 'ethereum')"""
        pass

    @abstractmethod
    def generate_keypair(self) -> ChainKeypair:
        """Generate new keypair for this chain"""
        pass

    @abstractmethod
    def import_keypair(self, private_key: str) -> ChainKeypair:
        """Import existing keypair from private key"""
        pass

    @abstractmethod
    def export_keypair(self, keypair: ChainKeypair) -> str:
        """Export keypair in chain-specific format"""
        pass

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Validate if address is valid for this chain"""
        pass

    @abstractmethod
    def get_account(self, address: str) -> ChainAccount:
        """Get account information from blockchain"""
        pass

    @abstractmethod
    def get_balance(self, address: str) -> float:
        """Get native token balance"""
        pass
```

#### 1.3 Stellar Chain Adapter (Migration from KeyManager)

**New File:** `backend/chains/stellar.py`

```python
"""
Stellar blockchain adapter
Migrates existing KeyManager functionality to chain-agnostic interface
"""
from stellar_sdk import Keypair, Server
from typing import Dict, Any, Optional
from .base import ChainAdapter, ChainKeypair, ChainAccount

class StellarAdapter(ChainAdapter):
    """Stellar blockchain implementation"""

    def __init__(self, network: str = "testnet"):
        self.network = network
        if network == "testnet":
            self.horizon_url = "https://horizon-testnet.stellar.org"
        else:
            self.horizon_url = "https://horizon.stellar.org"
        self.server = Server(self.horizon_url)

    @property
    def chain_name(self) -> str:
        return "stellar"

    def generate_keypair(self) -> ChainKeypair:
        """Generate new Stellar keypair"""
        keypair = Keypair.random()
        return ChainKeypair(
            public_key=keypair.public_key,
            private_key=keypair.secret,
            chain=self.chain_name,
            metadata={"network": self.network}
        )

    def import_keypair(self, private_key: str) -> ChainKeypair:
        """Import Stellar keypair from secret key"""
        keypair = Keypair.from_secret(private_key)
        return ChainKeypair(
            public_key=keypair.public_key,
            private_key=keypair.secret,
            chain=self.chain_name,
            metadata={"network": self.network}
        )

    def export_keypair(self, keypair: ChainKeypair) -> str:
        """Export keypair in Stellar format (secret key)"""
        return keypair.private_key

    def validate_address(self, address: str) -> bool:
        """Validate Stellar public key"""
        try:
            Keypair.from_public_key(address)
            return True
        except Exception:
            return False

    def get_account(self, address: str) -> ChainAccount:
        """Get Stellar account information"""
        try:
            account = self.server.load_account(address)
            balances = account.raw_data.get('balances', [])
            native_balance = 0

            for bal in balances:
                if bal.get('asset_type') == 'native':
                    native_balance = float(bal.get('balance', 0))

            return ChainAccount(
                address=address,
                chain=self.chain_name,
                balance=native_balance,
                balances=balances
            )
        except Exception as e:
            raise ValueError(f"Failed to load Stellar account: {e}")

    def get_balance(self, address: str) -> float:
        """Get XLM balance"""
        account = self.get_account(address)
        return account.balance
```

#### 1.4 Encryption Manager (Updated for Chain Agnostic)

**File:** `backend/encryption.py`

```python
"""
Encryption utilities for wallet private keys
Uses Fernet symmetric encryption with key derivation from user_id
Chain-agnostic implementation
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class EncryptionManager:
    """Manages encryption/decryption of wallet private keys"""

    def __init__(self):
        # Get master key from environment (generate if not exists)
        self.master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if not self.master_key:
            raise ValueError(
                "ENCRYPTION_MASTER_KEY not set in environment. "
                "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        # Fixed salt for key derivation (stored separately in production)
        self.salt = os.getenv('ENCRYPTION_SALT', 'tuxedo-agent-portfolios').encode()

    def _derive_key(self, user_id: str) -> bytes:
        """Derive encryption key from master key + user_id"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt + user_id.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return key

    def encrypt(self, plaintext: str, user_id: str) -> str:
        """Encrypt private key for storage"""
        key = self._derive_key(user_id)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, encrypted: str, user_id: str) -> str:
        """Decrypt private key for use"""
        key = self._derive_key(user_id)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted.encode())
        return decrypted.decode()
```

**Add to `.env`:**

```bash
# Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
ENCRYPTION_MASTER_KEY=your_generated_key_here
ENCRYPTION_SALT=tuxedo-agent-portfolios-v1
```

---

### Phase 2: Account Manager (2-3 hours)

**IMPORTANT: This is now AccountManager, not PortfolioManager**

Portfolio is a pattern agents construct, not a rigid manager class. This manager provides low-level primitives for account operations.

#### 2.1 Create Account Manager

**New File:** `backend/account_manager.py`

```python
"""
Account Manager - Chain-agnostic wallet account management
Provides filesystem primitives for agents to organize accounts
Agents construct "portfolio" patterns dynamically from these primitives
"""
from typing import Dict, Optional, List
from database_passkeys import PasskeyDatabaseManager
from encryption import EncryptionManager
from chains.base import ChainAdapter
from chains.stellar import StellarAdapter
import secrets

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

        # Registry of chain adapters
        self.chains: Dict[str, ChainAdapter] = {
            "stellar": StellarAdapter(network="testnet"),
            # Future: "solana": SolanaAdapter(),
            # Future: "ethereum": EthereumAdapter(),
            # Future: "sui": SuiAdapter(),
        }

    def generate_account(
        self,
        user_id: str,
        chain: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Generate new account for user on specified chain
        Agent can organize this account however it wants in filesystem
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
                     name, source, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    account_id,
                    user_id,
                    chain,
                    keypair.public_key,
                    encrypted_private_key,
                    name or f"{chain.capitalize()} Account",
                    "generated",
                    None  # metadata (agent can store filesystem path here)
                ))
                conn.commit()

            return {
                "account_id": account_id,
                "chain": chain,
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
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Import existing wallet for user
        KILLER FEATURE: Bridges existing DeFi users into Tuxedo
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
                     name, source, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    account_id,
                    user_id,
                    chain,
                    keypair.public_key,
                    encrypted_private_key,
                    name or f"Imported {chain.capitalize()} Account",
                    "imported",
                    None  # metadata
                ))
                conn.commit()

            return {
                "account_id": account_id,
                "chain": chain,
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

            # Verify ownership
            if account['user_id'] != user_id:
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
                        SELECT id, chain, public_key, name, source, created_at, last_used_at
                        FROM wallet_accounts
                        WHERE user_id = ? AND chain = ?
                        ORDER BY created_at DESC
                    ''', (user_id, chain))
                else:
                    cursor.execute('''
                        SELECT id, chain, public_key, name, source, created_at, last_used_at
                        FROM wallet_accounts
                        WHERE user_id = ?
                        ORDER BY chain, created_at DESC
                    ''', (user_id,))

                accounts = [dict(row) for row in cursor.fetchall()]

            # Enhance with on-chain data
            for account in accounts:
                try:
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
```

**Key Architectural Changes:**

- ✅ Renamed `PortfolioManager` → `AccountManager`
- ✅ Removed `create_portfolio()` - no portfolio table!
- ✅ Removed `portfolio_id` parameter from all methods
- ✅ `get_user_accounts()` returns raw account list for agent to organize
- ✅ Agent constructs portfolio patterns from account data dynamically
- ✅ `metadata` field allows agent to store filesystem organization info

---

### Phase 3: API Integration (1-2 hours)

#### 3.1 Account API Routes

**IMPORTANT: No portfolio endpoints!** Agents construct portfolio views dynamically.

**New File:** `backend/api/routes/accounts.py`

```python
"""
Account API Routes - Chain-agnostic wallet management
Provides primitives for agents to manage user accounts
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

from api.dependencies import get_current_user
from account_manager import AccountManager

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerateAccountRequest(BaseModel):
    chain: str
    name: Optional[str] = None

class ImportAccountRequest(BaseModel):
    chain: str
    private_key: str
    name: Optional[str] = None

class ExportAccountRequest(BaseModel):
    account_id: str

@router.post("/accounts/generate")
async def generate_account(
    request: GenerateAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate new blockchain account for user"""
    try:
        manager = AccountManager()
        result = manager.generate_account(
            user_id=current_user['id'],
            chain=request.chain,
            name=request.name
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate account")
            )

        return result

    except Exception as e:
        logger.error(f"Error generating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accounts/import")
async def import_account(
    request: ImportAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Import existing wallet for user
    KILLER FEATURE: Bridges existing DeFi users into Tuxedo
    """
    try:
        manager = AccountManager()
        result = manager.import_account(
            user_id=current_user['id'],
            chain=request.chain,
            private_key=request.private_key,
            name=request.name
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to import account")
            )

        return result

    except Exception as e:
        logger.error(f"Error importing account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accounts/export")
async def export_account(
    request: ExportAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Export wallet private key
    KILLER FEATURE: Users maintain full custodial control
    """
    try:
        manager = AccountManager()
        result = manager.export_account(
            user_id=current_user['id'],
            account_id=request.account_id
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to export account")
            )

        # Log export for security audit
        logger.warning(
            f"User {current_user['id']} exported account {request.account_id}"
        )

        return result

    except Exception as e:
        logger.error(f"Error exporting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts")
async def list_user_accounts(
    chain: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List all accounts for user, optionally filtered by chain
    Agent constructs portfolio views from this data
    """
    try:
        manager = AccountManager()
        accounts = manager.get_user_accounts(
            user_id=current_user['id'],
            chain=chain
        )

        return {
            "user_id": current_user['id'],
            "accounts": accounts,
            "count": len(accounts)
        }

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Key Changes:**

- ❌ Removed `/portfolios` endpoint - no portfolio table!
- ❌ Removed `portfolio_id` from all requests
- ✅ `/accounts` endpoint returns user's accounts for agent to organize
- ✅ Agent constructs portfolio views dynamically from account data

---

### Phase 4: Frontend Integration (2-3 hours)

#### 4.1 Portfolio Management UI

**Considerations for frontend:**

1. **Portfolio Dashboard**
   - Display all portfolios for authenticated user
   - Show accounts grouped by chain
   - Display balances for each account
   - Quick actions: generate, import, export

2. **Import Wallet Flow**
   - Chain selection dropdown (Stellar, Solana, EVM, Sui)
   - Private key input (with security warnings)
   - Optional account name
   - Success confirmation with address

3. **Export Wallet Flow**
   - Account selection
   - Security confirmation (re-authenticate with passkey?)
   - Display private key with copy button
   - Clear warnings about key security

4. **Multi-Chain Display**
   - Chain-specific icons and branding
   - Native token symbols (XLM, SOL, ETH, SUI)
   - Chain-specific block explorers
   - Future: wallet connection buttons (Freighter, Phantom, Metamask)

**File locations:**

- `src/components/portfolio/PortfolioDashboard.tsx`
- `src/components/portfolio/ImportWallet.tsx`
- `src/components/portfolio/ExportWallet.tsx`
- `src/hooks/usePortfolio.ts`

---

## Security Checklist

### Before Deployment

- [ ] `ENCRYPTION_MASTER_KEY` generated and stored securely
- [ ] `ENCRYPTION_SALT` configured in environment
- [ ] Database backup created
- [ ] All endpoints require authentication (`get_current_user`)
- [ ] Permission checks in place for all portfolio operations
- [ ] Test suite passes (user isolation, multi-chain support)
- [ ] Private key export requires re-authentication (future enhancement)
- [ ] Audit logging enabled for sensitive operations (export)
- [ ] Old `KeyManager` references removed or deprecated
- [ ] `.stellar_keystore.json` backed up and removed

### Export Security Enhancements (Future)

- [ ] Require passkey re-authentication before export
- [ ] Rate limiting on export endpoint
- [ ] Email/SMS notification when export occurs
- [ ] Optional 24-hour time-lock on export requests
- [ ] Multi-signature approval for high-value accounts

---

## Supported Chains

### Phase 1 (MVP - Current)

- **Stellar** (testnet) - Current implementation

### Phase 2 (Post-MVP)

- **Stellar** (mainnet) - Production deployment
- **Solana** - Phantom wallet compatibility
- **EVM** - Ethereum, Polygon, Arbitrum (Metamask compatibility)

### Phase 3 (Future)

- **Sui** - Token economics chain (per Choir whitepaper)
- **Additional chains** - Based on user demand

### Adding New Chains

To add a new chain, create adapter in `backend/chains/`:

```python
# backend/chains/solana.py
from .base import ChainAdapter, ChainKeypair, ChainAccount

class SolanaAdapter(ChainAdapter):
    @property
    def chain_name(self) -> str:
        return "solana"

    # Implement abstract methods...
```

Then register in `PortfolioManager.__init__()`:

```python
self.chains = {
    "stellar": StellarAdapter(),
    "solana": SolanaAdapter(),  # NEW
}
```

---

## Mobile Integration (Future)

### iOS

- Import/export to iOS Keychain
- Native Phantom integration
- Native Freighter integration

### Android

- Import/export to Android Keystore
- Native wallet app integrations

---

## Migration Strategy: Quantum Leap

### Complete Replacement (Not Gradual Migration)

**Approach:** Delete `KeyManager`, replace with `AccountManager` in one atomic change.

**Rationale:**

- No valuable data exists (testnet accounts only, recreatable from faucet)
- Gradual migration adds complexity without benefit
- Clean break enables simpler, more secure architecture
- Future-proof from day one

**Migration Steps:**

1. **Delete Old System** (no data migration needed)

   ```bash
   # Backup if paranoid
   cp backend/key_manager.py backend/key_manager.py.backup
   cp .stellar_keystore.json .stellar_keystore.json.backup 2>/dev/null || true

   # Delete
   git rm backend/key_manager.py
   rm -f .stellar_keystore.json

   git commit -m "Remove KeyManager: quantum leap to AccountManager"
   ```

2. **Update Tool Signatures** - Add `user_id` as mandatory second parameter

   ```python
   # OLD (insecure):
   def account_manager(action: str, key_manager, horizon: Server, ...):
       keypair = key_manager.get_keypair(account_id)  # No permission check!

   # NEW (secure):
   def account_manager(action: str, user_id: str, account_manager, horizon: Server, ...):
       # Permission check built into AccountManager
       keypair = account_manager.get_keypair_for_signing(user_id, account_id)
   ```

3. **Update Agent Tool Registration** - Inject `user_id` via lambda

   ```python
   # backend/main.py
   @app.post("/chat")
   async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
       user_id = current_user['id']  # From auth middleware (trusted)
       account_mgr = AccountManager()

       tools = [
           Tool(
               name="account_manager",
               func=lambda action, **kwargs: stellar_tools.account_manager(
                   action=action,
                   user_id=user_id,        # INJECTED from auth, not from LLM
                   account_manager=account_mgr,
                   **kwargs
               ),
               description="Manage Stellar accounts"
           ),
           # ... other tools with user_id injection
       ]
   ```

4. **Test User Isolation**
   ```bash
   cd backend
   python test_user_isolation.py  # Verify cross-user access blocked
   ```

**Timeline:** 4-6 hours

**See Also:** `AGENT_MIGRATION_QUANTUM_LEAP.md` for detailed implementation guide

---

## Timeline & Effort Estimate

| Phase       | Tasks                                          | Time           | Priority |
| ----------- | ---------------------------------------------- | -------------- | -------- |
| **Phase 1** | Database schema, chain abstraction, encryption | 3-4 hours      | CRITICAL |
| **Phase 2** | PortfolioManager, import/export logic          | 2-3 hours      | CRITICAL |
| **Phase 3** | API routes, authentication                     | 1-2 hours      | CRITICAL |
| **Phase 4** | Frontend UI, wallet flows                      | 2-3 hours      | HIGH     |
| **TOTAL**   |                                                | **8-12 hours** |          |

---

## Success Criteria

✅ **Chain Agnostic:** Architecture supports multiple blockchains
✅ **Filesystem Primitives:** Agent has user-isolated filesystem access
✅ **Dynamic Organization:** Agent constructs portfolio abstractions as needed
✅ **Wallet Import:** Users can import existing wallets from Freighter, Phantom, etc.
✅ **Wallet Export:** Users can export wallets to external applications
✅ **User Isolation:** Users can only access their own accounts
✅ **Encryption:** Private keys encrypted at rest in database
✅ **Access Control:** Permission checks on every operation
✅ **Audit Trail:** All operations logged
✅ **NO Portfolio Table:** Portfolio is a pattern agents construct, NOT a database schema
✅ **Direct User Link:** Accounts link directly to users, not through portfolios
✅ **Flexible Patterns:** Agent reads accounts and constructs any organizational pattern
✅ **"Not Your Keys":** Full custodial control maintained

---

## Alignment with Choir Vision

This architecture aligns with the Choir whitepaper vision:

1. **Multi-Chain Future:** Tuxedo agents have filesystem access to manage accounts across Stellar, Solana, EVM, Sui, etc.
2. **Agent Intelligence:** Agents have filesystem primitives and construct organizational patterns (like portfolios) dynamically for users
3. **Flexible Abstraction:** Portfolio is a pattern the agent creates, not a constraint the agent must work within
4. **User Sovereignty:** Import/export respects "not-your-keys-not-your-crypto"
5. **Network Effects:** Bridges existing DeFi users into agentic world
6. **Mobile Ready:** Architecture supports future mobile wallet integration
7. **Professional:** Engages seriously with blockchain enthusiast community

---

## Related Documents

- `CHOIR_WHITEPAPER.md` - Overall vision and north star
- `PASSKEY_ARCHITECTURE_V2.md` - Phase 1 authentication
- `CLAUDE.md` - Tuxedo project overview

---

**Document Version:** 2.0 (Chain-Agnostic Revision)
**Created:** 2025-11-08
**Status:** Planning document - Ready for implementation
**Next Action:** Review and approve plan, then begin Phase 1 implementation
