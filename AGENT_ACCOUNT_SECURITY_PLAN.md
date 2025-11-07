# Agent Account Security Implementation Plan

**Production-Ready User-to-Agent Account Linking**

---

## Executive Summary

**Current Critical Issue:** Agent accounts have no user isolation. Any authenticated user can access any agent's Stellar accounts and funds.

**Goal:** Implement proper user → agent account linking with encryption, access control, and audit trails.

**Timeline:** 6-9 hours of focused development
**Priority:** CRITICAL - Required before any mainnet deployment

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
│  - No user_id reference             │
│  - Plain text private keys          │
│  - Global access to all accounts    │
└─────────────────────────────────────┘
```

### Security Vulnerabilities

1. **No User Isolation**
   - `KeyManager` stores all accounts globally in `.stellar_keystore.json`
   - Any authenticated user can call `/api/agent/accounts` and see ALL accounts
   - User A can use User B's agent accounts in chat commands

2. **No Encryption at Rest**
   - Private keys stored in plain text JSON
   - File permissions (0600) only protect against OS-level access
   - No protection if database/filesystem is compromised

3. **No Access Control**
   - `create_agent_account()` has no user_id parameter
   - `list_agent_accounts()` returns all accounts globally
   - No permission checks in agent tools

4. **No Audit Trail**
   - Can't track which user created which account
   - Can't identify unauthorized access attempts
   - No recovery path if user loses passkey

---

## Target Architecture (Secure)

```
┌─────────────────────────────────────┐
│  Passkey Auth                       │
│  users.id = "user_abc123"           │
└────────────┬────────────────────────┘
             │ ✅ FOREIGN KEY
             ↓
┌─────────────────────────────────────┐
│  Agent Accounts                     │
│  agent_accounts table:              │
│   - id (primary key)                │
│   - user_id → users.id              │
│   - stellar_public_key (unique)     │
│   - stellar_secret_key_encrypted ✅ │
│   - name                            │
│   - created_at                      │
│   ON DELETE CASCADE ✅              │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Stellar Blockchain                 │
│  - Account balances                 │
│  - Transactions                     │
└─────────────────────────────────────┘
```

### Security Improvements

✅ **User Isolation:** Database-enforced foreign key constraint
✅ **Encryption at Rest:** Private keys encrypted with user-specific key
✅ **Access Control:** Permission checks on every operation
✅ **Audit Trail:** All operations logged to database
✅ **Recovery Support:** User passkey recovery → agent account recovery

---

## Implementation Plan

### Phase 1: Database Schema & Encryption (2-3 hours)

#### 1.1 Update Database Schema

**File:** `backend/database_passkeys.py`

Add to `PasskeyDatabaseManager.init_database()`:

```python
def init_database(self):
    # ... existing tables ...

    # Agent accounts table (NEW)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_accounts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            stellar_public_key TEXT UNIQUE NOT NULL,
            stellar_secret_key_encrypted TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_agent_accounts_user_id
        ON agent_accounts(user_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_agent_accounts_stellar_public_key
        ON agent_accounts(stellar_public_key)
    ''')

    conn.commit()
```

#### 1.2 Add Database Methods

Add to `PasskeyDatabaseManager` class:

```python
def create_agent_account(
    self,
    user_id: str,
    stellar_public_key: str,
    stellar_secret_key_encrypted: str,
    name: Optional[str] = None
) -> Dict[str, Any]:
    """Create agent account linked to user"""
    account_id = f"agent_{secrets.token_urlsafe(16)}"

    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO agent_accounts
            (id, user_id, stellar_public_key, stellar_secret_key_encrypted, name, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            account_id,
            user_id,
            stellar_public_key,
            stellar_secret_key_encrypted,
            name or f"Agent Account {datetime.now().strftime('%Y-%m-%d')}",
            datetime.now()
        ))
        conn.commit()

        cursor.execute('SELECT * FROM agent_accounts WHERE id = ?', (account_id,))
        return dict(cursor.fetchone())

def get_agent_accounts_by_user(self, user_id: str) -> List[Dict[str, Any]]:
    """Get all agent accounts for a specific user"""
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM agent_accounts
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))

        return [dict(row) for row in cursor.fetchall()]

def get_agent_account(
    self,
    stellar_public_key: str
) -> Optional[Dict[str, Any]]:
    """Get agent account by Stellar public key"""
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM agent_accounts
            WHERE stellar_public_key = ?
        ''', (stellar_public_key,))

        account = cursor.fetchone()
        return dict(account) if account else None

def update_agent_account_last_used(self, stellar_public_key: str):
    """Update last_used_at timestamp"""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE agent_accounts
            SET last_used_at = ?
            WHERE stellar_public_key = ?
        ''', (datetime.now(), stellar_public_key))
        conn.commit()

def delete_agent_account(self, user_id: str, stellar_public_key: str) -> bool:
    """Delete agent account (only if owned by user)"""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM agent_accounts
            WHERE user_id = ? AND stellar_public_key = ?
        ''', (user_id, stellar_public_key))
        conn.commit()
        return cursor.rowcount > 0
```

#### 1.3 Create Encryption Manager

**New File:** `backend/encryption.py`

```python
"""
Encryption utilities for agent account private keys
Uses Fernet symmetric encryption with key derivation from user_id
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class EncryptionManager:
    """Manages encryption/decryption of agent account private keys"""

    def __init__(self):
        # Get master key from environment (generate if not exists)
        self.master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if not self.master_key:
            raise ValueError(
                "ENCRYPTION_MASTER_KEY not set in environment. "
                "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        # Fixed salt for key derivation (stored separately in production)
        self.salt = os.getenv('ENCRYPTION_SALT', 'tuxedo-agent-accounts').encode()

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
ENCRYPTION_SALT=tuxedo-agent-accounts-v1
```

#### 1.4 Create Agent Account Manager

**New File:** `backend/agent_account_manager.py`

```python
"""
Agent Account Manager - Replaces KeyManager with secure user-linked storage
"""
from typing import Dict, Optional, List
from stellar_sdk import Keypair
from database_passkeys import PasskeyDatabaseManager
from encryption import EncryptionManager
import secrets

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
```

---

### Phase 2: API Integration with Auth (1-2 hours)

#### 2.1 Create Auth Dependency

**File:** `backend/api/dependencies.py`

```python
"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, Header
from typing import Optional
from database_passkeys import PasskeyDatabaseManager

db = PasskeyDatabaseManager()

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Get current authenticated user from Bearer token
    Raises 401 if not authenticated
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication header format"
        )

    # Validate session
    session = db.get_session_by_token(token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Get user
    user = db.get_user_by_id(session['user_id'])
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user

async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """Get user if authenticated, None otherwise (no error)"""
    if not authorization:
        return None

    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
```

#### 2.2 Update Agent Endpoints

**File:** `backend/api/routes/agent.py`

```python
"""
Agent API Routes with User Authentication
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

from api.dependencies import get_current_user
from agent_account_manager import AgentAccountManager

logger = logging.getLogger(__name__)
router = APIRouter()

class AccountCreateRequest(BaseModel):
    name: Optional[str] = None

@router.post("/create-account")
async def create_account(
    request: AccountCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new agent account for authenticated user"""
    try:
        manager = AgentAccountManager()
        result = manager.create_account(
            user_id=current_user['id'],
            name=request.name
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create account")
            )

        # Fund with friendbot (testnet only)
        import requests
        try:
            friendbot_url = "https://friendbot.stellar.org"
            response = requests.get(f"{friendbot_url}?addr={result['address']}")
            result['funded'] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Friendbot funding failed: {e}")
            result['funded'] = False

        return result

    except Exception as e:
        logger.error(f"Error creating agent account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts")
async def list_accounts(
    current_user: dict = Depends(get_current_user)
):
    """List agent accounts for authenticated user only"""
    try:
        manager = AgentAccountManager()
        accounts = manager.get_user_accounts(current_user['id'])

        # Enhance with Stellar network data
        from stellar_sdk.server import Server
        server = Server("https://horizon-testnet.stellar.org")

        enhanced_accounts = []
        for account in accounts:
            try:
                stellar_account = server.load_account(account['address'])
                balance = 0
                for bal in stellar_account.raw_data.get('balances', []):
                    if bal.get('asset_type') == 'native':
                        balance = float(bal.get('balance', 0))
                        break
                account['balance'] = balance
            except Exception as e:
                logger.warning(f"Could not load account {account['address']}: {e}")
                account['balance'] = 0

            enhanced_accounts.append(account)

        return enhanced_accounts

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/accounts/{address}")
async def delete_account(
    address: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete agent account (only if owned by user)"""
    try:
        manager = AgentAccountManager()
        success = manager.delete_account(current_user['id'], address)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Account not found or not owned by user"
            )

        return {"success": True, "message": "Account deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.3 Update Chat Endpoint

**File:** `backend/api/routes/chat.py`

```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)  # ✅ Require auth
):
    """Chat with AI agent using user's agent accounts"""
    try:
        # Create agent with user context
        agent = create_agent_with_user_context(
            user_id=current_user['id']  # ✅ Pass user_id to agent
        )

        # Stream response
        async def generate():
            async for chunk in agent.stream(request.message, request.history):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Phase 3: Update Agent Tools (1-2 hours)

#### 3.1 Update Account Management Tool

**File:** `backend/tools/agent/account_management.py`

```python
"""
Agent Account Management Tools (User-Isolated)
"""
from typing import Dict, Optional, List
from agent_account_manager import AgentAccountManager

def create_agent_account(
    user_id: str,  # ✅ Required parameter
    account_name: Optional[str] = None
) -> Dict:
    """Create new agent-controlled account for user"""
    manager = AgentAccountManager()
    return manager.create_account(user_id=user_id, name=account_name)

def list_agent_accounts(user_id: str) -> List[Dict]:  # ✅ Required parameter
    """List agent-controlled accounts for user"""
    manager = AgentAccountManager()
    return manager.get_user_accounts(user_id)

def get_agent_account_info(
    user_id: str,  # ✅ Required parameter
    address: str
) -> Dict:
    """Get detailed account information (if user owns it)"""
    manager = AgentAccountManager()

    # Permission check
    if not manager.has_account(user_id, address):
        return {
            "error": f"Account {address} not found or not owned by user",
            "success": False
        }

    # Get Stellar account data
    from stellar_sdk.server import Server
    server = Server("https://horizon-testnet.stellar.org")

    try:
        account = server.load_account(address)
        balance = 0
        for bal in account.raw_data.get('balances', []):
            if bal.get('asset_type') == 'native':
                balance = float(bal.get('balance', 0))
                break

        accounts = manager.get_user_accounts(user_id)
        account_info = next((a for a in accounts if a['address'] == address), None)

        return {
            "address": address,
            "balance": balance,
            "name": account_info['name'] if account_info else "Unknown",
            "created_at": account_info['created_at'] if account_info else None,
            "network": "testnet",
            "success": True
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }
```

#### 3.2 Update All Stellar Tools

**Pattern for all tools in `backend/stellar_tools.py` and `backend/defindex_tools.py`:**

```python
# Before (INSECURE):
def some_stellar_operation(account_address: str, amount: float):
    key_manager = KeyManager()
    keypair = key_manager.get_keypair(account_address)  # ❌ No permission check
    # ... use keypair ...

# After (SECURE):
def some_stellar_operation(
    user_id: str,  # ✅ Required
    account_address: str,
    amount: float
):
    manager = AgentAccountManager()
    keypair = manager.get_keypair(user_id, account_address)  # ✅ Permission check
    # ... use keypair ...
```

**Files to update:**

- `backend/stellar_tools.py` - All account operations
- `backend/defindex_tools.py` - All DeFi operations
- `backend/agent/stellar_tools_wrappers.py` - Tool wrappers

---

### Phase 4: Testing & Migration (2-3 hours)

#### 4.1 Migration Script

**New File:** `backend/migrate_keymanager_to_database.py`

```python
"""
Migrate existing KeyManager accounts to database-backed AgentAccountManager
WARNING: This is a one-way migration. Back up .stellar_keystore.json first!
"""
import json
from pathlib import Path
from agent_account_manager import AgentAccountManager
from database_passkeys import PasskeyDatabaseManager

def migrate():
    keystore_path = Path(".stellar_keystore.json")

    if not keystore_path.exists():
        print("No existing keystore found. Nothing to migrate.")
        return

    # Backup existing keystore
    backup_path = keystore_path.with_suffix('.json.backup')
    import shutil
    shutil.copy(keystore_path, backup_path)
    print(f"✅ Backed up keystore to {backup_path}")

    # Load existing accounts
    with open(keystore_path) as f:
        accounts = json.load(f)

    print(f"Found {len(accounts)} accounts to migrate")

    # Get or create a default user for migration
    db = PasskeyDatabaseManager()

    # Check if migration user exists
    user = db.get_user_by_email("migration@tuxedo.local")
    if not user:
        print("Creating migration user...")
        user = db.create_user("migration@tuxedo.local")

    print(f"Migrating to user: {user['id']}")

    # Migrate each account
    manager = AgentAccountManager()
    from encryption import EncryptionManager
    encryption = EncryptionManager()

    for public_key, secret_key in accounts.items():
        try:
            # Encrypt secret key
            encrypted = encryption.encrypt(secret_key, user['id'])

            # Store in database
            db.create_agent_account(
                user_id=user['id'],
                stellar_public_key=public_key,
                stellar_secret_key_encrypted=encrypted,
                name=f"Migrated Account"
            )

            print(f"✅ Migrated {public_key}")

        except Exception as e:
            print(f"❌ Failed to migrate {public_key}: {e}")

    print("\n✅ Migration complete!")
    print(f"   Backup saved to: {backup_path}")
    print(f"   Accounts migrated to user: {user['email']}")

if __name__ == "__main__":
    migrate()
```

#### 4.2 Test Suite

**New File:** `backend/test_agent_account_security.py`

```python
"""
Test suite for agent account security
Verifies user isolation and access control
"""
import pytest
from agent_account_manager import AgentAccountManager
from database_passkeys import PasskeyDatabaseManager

@pytest.fixture
def db():
    # Use test database
    db = PasskeyDatabaseManager("test_tuxedo.db")
    yield db
    # Cleanup
    import os
    os.remove("test_tuxedo.db")

@pytest.fixture
def manager(db):
    return AgentAccountManager("test_tuxedo.db")

def test_user_isolation(manager, db):
    """Test that users can only access their own accounts"""
    # Create two users
    user1 = db.create_user("user1@test.com")
    user2 = db.create_user("user2@test.com")

    # User 1 creates account
    result = manager.create_account(user1['id'], "User 1 Account")
    assert result['success']
    user1_address = result['address']

    # User 2 creates account
    result = manager.create_account(user2['id'], "User 2 Account")
    assert result['success']
    user2_address = result['address']

    # User 1 can access their own account
    accounts = manager.get_user_accounts(user1['id'])
    assert len(accounts) == 1
    assert accounts[0]['address'] == user1_address

    # User 1 CANNOT access User 2's account
    accounts = manager.get_user_accounts(user1['id'])
    assert user2_address not in [a['address'] for a in accounts]

    # User 2 can ONLY see their own account
    accounts = manager.get_user_accounts(user2['id'])
    assert len(accounts) == 1
    assert accounts[0]['address'] == user2_address

def test_permission_check(manager, db):
    """Test that permission checks work on keypair access"""
    user1 = db.create_user("user1@test.com")
    user2 = db.create_user("user2@test.com")

    # User 1 creates account
    result = manager.create_account(user1['id'])
    user1_address = result['address']

    # User 1 can get keypair
    keypair = manager.get_keypair(user1['id'], user1_address)
    assert keypair.public_key == user1_address

    # User 2 CANNOT get User 1's keypair
    with pytest.raises(PermissionError):
        manager.get_keypair(user2['id'], user1_address)

def test_cascade_delete(manager, db):
    """Test that agent accounts are deleted when user is deleted"""
    user = db.create_user("user@test.com")

    # Create multiple accounts
    manager.create_account(user['id'], "Account 1")
    manager.create_account(user['id'], "Account 2")

    accounts = manager.get_user_accounts(user['id'])
    assert len(accounts) == 2

    # Delete user
    db.delete_user(user['id'])

    # Accounts should be deleted (cascade)
    accounts = manager.get_user_accounts(user['id'])
    assert len(accounts) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

#### 4.3 Integration Testing Checklist

- [ ] User A creates account → only A can see it
- [ ] User B creates account → only B can see it
- [ ] User A cannot access User B's accounts
- [ ] User A cannot get User B's keypair
- [ ] Chat command uses correct user's accounts
- [ ] Account deletion only works for owner
- [ ] Cascade delete: user deletion → agent accounts deleted
- [ ] Encryption/decryption works correctly
- [ ] Session auth protects all endpoints
- [ ] Recovery: user recovers passkey → can access agent accounts

---

## Security Checklist

### Before Deployment

- [ ] `ENCRYPTION_MASTER_KEY` generated and stored securely
- [ ] `ENCRYPTION_SALT` configured in environment
- [ ] Database backup created
- [ ] All endpoints require authentication (`get_current_user`)
- [ ] All agent tools accept `user_id` parameter
- [ ] Permission checks in place for all account operations
- [ ] Test suite passes (user isolation, access control)
- [ ] Migration script tested on development data
- [ ] Audit logging enabled for account operations
- [ ] Old `KeyManager` references removed or deprecated
- [ ] `.stellar_keystore.json` backed up and removed

### Monitoring & Alerts

- [ ] Log all agent account creation events
- [ ] Log all permission denied events
- [ ] Alert on unusual account access patterns
- [ ] Monitor failed permission checks
- [ ] Track account deletion events

---

## Rollback Plan

If issues are discovered after deployment:

1. **Keep database backup** - Always back up before migration
2. **Revert code** - Git revert to previous commit
3. **Restore KeyManager** - Copy `.stellar_keystore.json.backup` back
4. **Clear agent_accounts table** - Start fresh on next attempt

---

## Dependencies to Add

```bash
# backend/requirements.txt or pyproject.toml
cryptography>=41.0.0  # For Fernet encryption
```

```bash
pip install cryptography
# or
uv add cryptography
```

---

## Environment Variables

Add to `backend/.env`:

```bash
# Agent Account Encryption
# Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
ENCRYPTION_MASTER_KEY=your_generated_key_here

# Optional: Custom salt for key derivation
ENCRYPTION_SALT=tuxedo-agent-accounts-v1
```

---

## Timeline & Effort Estimate

| Phase       | Tasks                                            | Time          | Priority |
| ----------- | ------------------------------------------------ | ------------- | -------- |
| **Phase 1** | Database schema, encryption, AgentAccountManager | 2-3 hours     | CRITICAL |
| **Phase 2** | API integration, auth dependencies               | 1-2 hours     | CRITICAL |
| **Phase 3** | Update agent tools with user_id                  | 1-2 hours     | CRITICAL |
| **Phase 4** | Testing, migration, deployment                   | 2-3 hours     | CRITICAL |
| **TOTAL**   |                                                  | **6-9 hours** |          |

---

## Success Criteria

✅ **User Isolation:** Users can only access their own agent accounts
✅ **Encryption:** Private keys encrypted at rest in database
✅ **Access Control:** Permission checks on every account operation
✅ **Audit Trail:** All operations logged to database
✅ **Recovery:** User passkey recovery works with agent accounts
✅ **Testing:** All security tests pass
✅ **Migration:** Existing accounts migrated successfully
✅ **Zero Regressions:** All existing functionality still works

---

## Related Documents

- `PASSKEY_ARCHITECTURE_V2.md` - Phase 1 (authentication) and Phase 2 (multi-agent, future)
- `AGENT_FIRST_ARCHITECTURE_PLAN.md` - Overall agent-first architecture
- `SIMPLIFIED_AGENT_ARCHITECTURE.md` - Streamlined agent architecture

---

**Document Version:** 1.0
**Created:** 2025-11-07
**Status:** Planning document - Not yet implemented
**Next Action:** Review and approve plan, then begin Phase 1 implementation
