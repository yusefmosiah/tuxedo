# Security Improvements Roadmap

**Date:** November 8, 2025
**Status:** Planned Improvements for Production Hardening
**Priority Levels:** Critical (deploy now), High (1-2 weeks), Medium (2-4 weeks)

---

## Executive Summary

The Tuxedo system has a solid security foundation from the Quantum Leap migration. This document outlines targeted improvements to harden the system for production scale, focusing on:

1. **Per-user salt** implementation (encryption improvement)
2. **API Security** hardening (CORS, rate limiting, validation)
3. **Configuration management** (centralize non-secrets)
4. **Tool standardization** (async/sync consistency)

**Note:** Database security is adequate for current scale; improvements planned as we grow to first cohort of users.

---

## Part 1: Per-User Salt Implementation 🔐

### Current State

**File:** `backend/encryption.py:30-42`

```python
# CURRENT: Fixed salt for all users
self.salt = os.getenv('ENCRYPTION_SALT', 'tuxedo-agent-accounts').encode()

def _derive_key(self, user_id: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=self.salt + user_id.encode(),  # Fixed salt + user_id
        iterations=100000,
    )
```

**Issue:** Fixed salt reduces entropy when master key is compromised. If attacker has master_key + salt, they can derive all user keys.

### Improvement: Per-User Salt

**Approach:**
1. Generate random salt per user at account creation
2. Store salt in database (NOT secret - can be public)
3. Use salt only for key derivation, not for authentication
4. Rotate salt when password changes (future: passkey rotation)

**Implementation:**

#### Step 1: Update Database Schema

```sql
-- Add salt column to wallet_accounts or users table
ALTER TABLE wallet_accounts ADD COLUMN encryption_salt TEXT;
-- OR if users table exists:
ALTER TABLE users ADD COLUMN encryption_salt TEXT NOT NULL;
```

#### Step 2: Update EncryptionManager

```python
# backend/encryption.py
import secrets

class EncryptionManager:
    """Manages encryption/decryption with per-user salt"""

    def __init__(self):
        # Master key from environment (from Render/staging)
        self.master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if not self.master_key:
            raise ValueError(
                "ENCRYPTION_MASTER_KEY required in environment. "
                "Set in Render environment variables."
            )
        # No default salt - use per-user salt from database

    def _derive_key(self, user_id: str, user_salt: str) -> bytes:
        """
        Derive encryption key from master key + per-user salt + user_id

        Args:
            user_id: User identifier
            user_salt: Per-user salt from database (base64 encoded)
        """
        # Decode stored salt
        salt_bytes = base64.b64decode(user_salt)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes + user_id.encode(),  # Per-user salt + user_id
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return key

    def encrypt(self, plaintext: str, user_id: str, user_salt: str) -> str:
        """Encrypt private key for storage"""
        key = self._derive_key(user_id, user_salt)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, encrypted: str, user_id: str, user_salt: str) -> str:
        """Decrypt private key for use"""
        key = self._derive_key(user_id, user_salt)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted.encode())
        return decrypted.decode()

    @staticmethod
    def generate_user_salt() -> str:
        """Generate random salt for new user"""
        random_bytes = secrets.token_bytes(32)
        return base64.b64encode(random_bytes).decode()
```

#### Step 3: Update AccountManager

```python
# backend/account_manager.py
from encryption import EncryptionManager

class AccountManager:
    def generate_account(self, user_id: str, chain: str, ...):
        try:
            # ... existing code ...

            # Get or create user's encryption salt
            user_salt = self._get_or_create_user_salt(user_id)

            # Encrypt with per-user salt
            encrypted_private_key = self.encryption.encrypt(
                keypair.private_key,
                user_id,
                user_salt  # NEW: per-user salt
            )

            # Store in database
            cursor.execute('''
                INSERT INTO wallet_accounts
                (id, user_id, chain, public_key, encrypted_private_key,
                 name, source, metadata, encryption_salt, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                account_id,
                user_id,
                chain,
                keypair.public_key,
                encrypted_private_key,
                name,
                "generated",
                json.dumps(metadata),
                user_salt,  # NEW: store salt with account
                ...
            ))

    def _get_or_create_user_salt(self, user_id: str) -> str:
        """Get user's salt or create if doesn't exist"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Check if user has salt
            cursor.execute('SELECT encryption_salt FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()

            if result and result[0]:
                return result[0]

            # Generate new salt
            new_salt = EncryptionManager.generate_user_salt()

            # Store it
            cursor.execute(
                'UPDATE users SET encryption_salt = ? WHERE id = ?',
                (new_salt, user_id)
            )
            conn.commit()

            return new_salt
```

#### Step 4: Migration Script

```python
# backend/migrations/add_per_user_salt.py
"""
Migration: Add per-user salt for encryption improvement
Generates per-user salt for all existing users
"""

import sqlite3
import base64
import secrets
from encryption import EncryptionManager

def migrate():
    """Add per-user salt to all users"""
    conn = sqlite3.connect('tuxedo_passkeys.db')
    cursor = conn.cursor()

    # Get all users
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()

    for (user_id,) in users:
        # Generate salt
        salt = EncryptionManager.generate_user_salt()

        # Store salt
        cursor.execute(
            'UPDATE users SET encryption_salt = ? WHERE id = ?',
            (salt, user_id)
        )

        print(f"✅ Generated salt for user {user_id}")

    conn.commit()
    conn.close()
    print(f"✅ Migration complete: {len(users)} users updated")

if __name__ == '__main__':
    migrate()
```

### Security Benefits

| Attack Scenario | Before | After |
|---|---|---|
| Master key compromised | Attacker can derive all user keys | Attacker needs per-user salt (stored in DB) |
| Database compromised | Salts are fixed, predictable | Salts are random, unique per user |
| Timing attacks | All users use same salt | Per-user salt prevents pattern analysis |

**Timeline:** 1-2 days implementation + testing

---

## Part 2: API Security Hardening 🔒

### 2.1 CORS Configuration Issues

**Current State - app.py:58-70**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://tuxedo.onrender.com",
        "https://tuxedo-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],              # ⚠️ TOO PERMISSIVE
    allow_headers=["*"],              # ⚠️ TOO PERMISSIVE
)
```

**Issues:**
1. `allow_methods=["*"]` allows DELETE, PATCH, OPTIONS unnecessarily
2. `allow_headers=["*"]` allows any header
3. CORS origins hardcoded instead of using config
4. No distinction between development and production

### Fix: Restrict CORS

**Step 1: Update config/settings.py**

```python
# backend/config/settings.py

class Settings:
    def __init__(self):
        # ... existing config ...

        # CORS Configuration (from environment, different by stage)
        env = os.getenv("ENVIRONMENT", "development")

        if env == "production":
            self.cors_origins = [
                "https://tuxedo.onrender.com",
                "https://tuxedo-frontend.onrender.com"
            ]
            self.cors_allow_methods = ["GET", "POST", "OPTIONS"]
            self.cors_allow_headers = ["Content-Type", "Authorization"]
            self.cors_allow_credentials = True

        elif env == "staging":
            self.cors_origins = [
                "https://tuxedo-staging.onrender.com",
                "https://tuxedo-frontend-staging.onrender.com"
            ]
            self.cors_allow_methods = ["GET", "POST", "PUT", "OPTIONS"]
            self.cors_allow_headers = ["Content-Type", "Authorization"]
            self.cors_allow_credentials = True

        else:  # development
            self.cors_origins = [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://localhost:8080"
            ]
            self.cors_allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            self.cors_allow_headers = ["*"]  # Development can be permissive
            self.cors_allow_credentials = True
```

**Step 2: Update app.py**

```python
# backend/app.py
from config.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(...)

    # Setup CORS with environment-specific config
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
```

**Environment Variables:**

```bash
# .env.development
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# .env.staging (in Render)
ENVIRONMENT=staging
CORS_ORIGINS=https://tuxedo-staging.onrender.com,https://tuxedo-frontend-staging.onrender.com

# .env.production (future)
ENVIRONMENT=production
CORS_ORIGINS=https://tuxedo.io,https://app.tuxedo.io
```

### 2.2 Rate Limiting Implementation

**Current State:** No rate limiting

**Issue:** API endpoints can be hammered by bots, consuming resources

### Fix: Add Rate Limiting

**Step 1: Install dependency**

```bash
pip install slowapi
```

**Step 2: Create rate limit middleware - backend/middleware/rate_limit.py**

```python
"""Rate limiting middleware"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

# Define limit strategies
LIMITS = {
    "default": "100/minute",           # General endpoints
    "chat": "10/minute",               # Chat is expensive
    "auth": "5/minute",                # Auth attempts
    "tool": "30/minute",               # Tool calls
    "health": "60/minute",             # Health checks
}

# Per-user limits (for authenticated endpoints)
USER_LIMITS = {
    "chat": "50/hour",                 # Authenticated users
    "trade": "20/hour",                # Trading operations
    "account_create": "5/day",         # Account creation
}

@limiter.error_handler
async def rate_limit_error_handler(request: Request, exc: RateLimitExceeded):
    """Custom error handler for rate limit exceeded"""
    logger.warning(f"Rate limit exceeded: {request.url.path} - {exc.detail}")
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded. Try again in {exc.detail.split('after ')[1] if 'after' in exc.detail else '1 minute'}"
    )
```

**Step 3: Apply limits to endpoints**

```python
# backend/api/routes/chat.py
from middleware.rate_limit import limiter, LIMITS

@router.post("/chat")
@limiter.limit(LIMITS["chat"])  # 10 requests per minute
async def chat_endpoint(request: ChatRequest, current_user = Depends(get_optional_user)):
    ...

# backend/api/routes/agent.py
@router.post("/api/agent/accounts")
@limiter.limit(USER_LIMITS["account_create"])  # 5 per day
async def create_agent_account(...):
    ...

# backend/stellar_tools.py
# For tools called via API
from middleware.rate_limit import USER_LIMITS
@tool
def stellar_trading(...):
    # Rate limit is on the endpoint that calls this
    ...
```

**Step 4: Configure in settings**

```python
# backend/config/settings.py
class Settings:
    def __init__(self):
        # ... existing ...

        # Rate Limiting
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_chat = os.getenv("RATE_LIMIT_CHAT", "10/minute")
        self.rate_limit_auth = os.getenv("RATE_LIMIT_AUTH", "5/minute")
        self.rate_limit_tool = os.getenv("RATE_LIMIT_TOOL", "30/minute")
```

### 2.3 Request Validation

**Current State:** Minimal input validation

**Issue:** Tool parameters not validated before execution

### Fix: Add Pydantic Validation

**Step 1: Create validation schemas - backend/api/schemas/tools.py**

```python
"""Tool request validation schemas"""
from pydantic import BaseModel, Field, validator
from typing import Optional

class AccountManagerRequest(BaseModel):
    """Validate account_manager tool input"""
    action: str = Field(..., pattern="^(create|fund|get|transactions|list|export|import)$")
    account_id: Optional[str] = Field(None, max_length=128)
    secret_key: Optional[str] = Field(None, max_length=256)
    limit: int = Field(10, ge=1, le=100)  # Prevent huge requests

class TradingRequest(BaseModel):
    """Validate trading tool input"""
    action: str = Field(..., pattern="^(buy|sell|cancel_order|get_orders)$")
    account_id: str = Field(..., max_length=128)
    buying_asset: Optional[str] = Field(None, max_length=12)
    selling_asset: Optional[str] = Field(None, max_length=12)
    amount: Optional[str] = Field(None, regex="^[0-9]+\.?[0-9]*$")
    price: Optional[str] = Field(None, regex="^[0-9]+\.?[0-9]*$")

    @validator('amount', 'price')
    def validate_numbers(cls, v):
        if v:
            num = float(v)
            if num <= 0:
                raise ValueError('Must be positive number')
            if num > 1000000000:
                raise ValueError('Amount too large')
        return v

class MarketDataRequest(BaseModel):
    """Validate market_data tool input"""
    action: str = Field(..., pattern="^orderbook$")
    base_asset: str = Field("XLM", max_length=12)
    quote_asset: Optional[str] = Field(None, max_length=12)
    quote_issuer: Optional[str] = Field(None, max_length=56)
    limit: int = Field(20, ge=1, le=200)
```

**Step 2: Use in tools**

```python
# backend/stellar_tools.py
from api.schemas.tools import AccountManagerRequest, TradingRequest

def account_manager(action: str, user_id: str, ...):
    """Validate input before processing"""
    # Validate using Pydantic
    validated = AccountManagerRequest(
        action=action,
        account_id=account_id,
        limit=limit
    )

    # Use validated data
    action = validated.action
    ...
```

**Timeline:** 2-3 days implementation + testing

---

## Part 3: Configuration Management 📋

### Current State

**Issues:**
1. Network URLs hardcoded in multiple places
2. CORS origins duplicated
3. Friendbot URL hardcoded in stellar_tools.py
4. No central configuration for non-secrets

**Files with hardcoding:**
- `backend/stellar_tools.py:22` - FRIENDBOT_URL
- `backend/stellar_tools.py:21` - TESTNET_NETWORK_PASSPHRASE
- `backend/app.py:61-66` - CORS origins
- `backend/config/settings.py:34-39` - CORS origins (duplicate)

### Fix: Centralized Config

**Step 1: Expand config/settings.py**

```python
# backend/config/settings.py
from enum import Enum

class NetworkType(str, Enum):
    TESTNET = "testnet"
    MAINNET = "mainnet"
    PUBLIC = "public"

class Network(BaseModel):
    """Network configuration"""
    name: str
    network_passphrase: str
    horizon_url: str
    soroban_rpc_url: str
    friendbot_url: Optional[str] = None  # Only for testnet

NETWORKS = {
    "testnet": Network(
        name="Stellar Test Network",
        network_passphrase="Test SDF Network ; September 2015",
        horizon_url="https://horizon-testnet.stellar.org",
        soroban_rpc_url="https://soroban-testnet.stellar.org",
        friendbot_url="https://friendbot.stellar.org"
    ),
    "mainnet": Network(
        name="Stellar Public Network",
        network_passphrase="Public Global Stellar Network ; September 2015",
        horizon_url="https://horizon.stellar.org",
        soroban_rpc_url="https://mainnet.soroban.stellar.org",
        friendbot_url=None
    )
}

class Settings:
    def __init__(self):
        # ... existing config ...

        # Network Configuration
        stellar_network = os.getenv("STELLAR_NETWORK", "testnet")
        if stellar_network not in NETWORKS:
            raise ValueError(f"Unknown network: {stellar_network}")

        self.stellar_network_name = stellar_network
        self.stellar_network = NETWORKS[stellar_network]

        # Contract Addresses (by network)
        if stellar_network == "testnet":
            self.contracts = {
                "blend": "CAAAA...",  # Testnet address
                "usdc": "GBUQ...",
                # ... other contracts ...
            }
        else:  # mainnet
            self.contracts = {
                "blend": "CBLEND...",  # Mainnet address
                "usdc": "CBBD...",
                # ... other contracts ...
            }

        # Tool Spending Limits (by network)
        self.spending_limits = {
            "testnet": {
                "XLM": {"max_per_transaction": 100000},
                "USDC": {"max_per_transaction": 100000}
            },
            "mainnet": {
                "XLM": {"max_per_transaction": 1000},
                "USDC": {"max_per_transaction": 10000}
            }
        }

settings = Settings()
```

**Step 2: Use centralized config in stellar_tools.py**

```python
# backend/stellar_tools.py
from config.settings import settings

# Remove hardcoded values:
# - TESTNET_NETWORK_PASSPHRASE
# - FRIENDBOT_URL

# Use settings instead:
def account_manager(action: str, user_id: str, ...):
    network_passphrase = settings.stellar_network.network_passphrase
    horizon_url = settings.stellar_network.horizon_url
    friendbot_url = settings.stellar_network.friendbot_url

    if action == "fund":
        if not friendbot_url:
            return {"error": "Friendbot not available on this network"}
        # Fund account using friendbot_url
```

**Step 3: Contract address management**

```python
# backend/contracts/__init__.py
from config.settings import settings

class ContractAddresses:
    """Get contract addresses for current network"""

    @staticmethod
    def blend():
        return settings.contracts["blend"]

    @staticmethod
    def usdc():
        return settings.contracts["usdc"]

    @staticmethod
    def all():
        return settings.contracts

# Usage throughout codebase:
# OLD: from src.contracts.blend import BLEND_CONTRACT
# NEW: from contracts import ContractAddresses
#      address = ContractAddresses.blend()
```

**Benefits:**
- ✅ Single source of truth for configuration
- ✅ Easy network switching (testnet ↔ mainnet)
- ✅ No hardcoded values in code
- ✅ Environment-based configuration
- ✅ Support for contract upgrades

**Timeline:** 1-2 days implementation

---

## Part 4: Tool Sync/Async Standardization ⚙️

### Current State

**Issue:** Inconsistent async/sync implementation

**stellar_tools.py:** All functions are **sync** (`def`)
**tool_factory.py:** Wraps with `@tool` decorator
**core.py:** Tries to call with `ainvoke` (expects async)

**Files involved:**
- `backend/stellar_tools.py:256-789` - All sync functions
- `backend/agent/core.py:300-327` - Tool execution (tries both async and sync)
- `backend/agent/tool_factory.py:60-256` - Tool wrapping

### Why This Matters

1. **Performance:** Async allows concurrent tool calls
2. **Consistency:** All tools should follow same pattern
3. **Maintainability:** Developers know what to expect
4. **Scalability:** Blocking calls prevent serving multiple requests

### Fix: Standardize to Async

**Step 1: Convert stellar_tools.py to async**

```python
# backend/stellar_tools.py

# BEFORE:
def account_manager(action: str, user_id: str, account_manager, horizon, ...):
    # Sync implementation
    if action == "create":
        keypair = adapter.generate_keypair()
    ...

# AFTER:
async def account_manager(action: str, user_id: str, account_manager, horizon, ...):
    """Stellar account management operations (async)"""
    if action == "create":
        keypair = await adapter.generate_keypair_async()
    # Use await for all I/O operations
    ...

async def trading(action: str, user_id: str, account_id: str, ...):
    """Unified SDEX trading tool (async)"""
    # All I/O operations with await
    horizon_server = await get_horizon_server()
    ...

async def market_data(action: str, user_id: str, horizon, ...):
    """Query SDEX market data (async, read-only)"""
    data = await horizon.orderbook(...)
    ...
```

**Step 2: Update tool_factory.py to wrap async functions**

```python
# backend/agent/tool_factory.py

from agent.stellar_tools import (
    account_manager as _account_manager,  # Now async
    trading as _trading,                  # Now async
    # ... etc ...
)

def create_user_tools(user_id: str) -> List:
    """Create async tools for authenticated user"""

    @tool
    async def stellar_account_manager(  # async tool
        action: str,
        account_id: Optional[str] = None,
        ...
    ):
        """Stellar account management (async)"""
        return await _account_manager(
            action=action,
            user_id=user_id,
            account_manager=account_mgr,
            ...
        )

    @tool
    async def stellar_trading(action: str, account_id: str, ...):
        """Unified SDEX trading (async)"""
        return await _trading(
            action=action,
            user_id=user_id,
            account_id=account_id,
            account_manager=account_mgr,
            ...
        )

    return [stellar_account_manager, stellar_trading, ...]
```

**Step 3: Update core.py tool execution**

```python
# backend/agent/core.py

# SIMPLIFIED: Since all tools are now async, use single execution path
if tool_func:
    try:
        # All tools are async now - single execution path
        result = await tool_func.ainvoke(tool_args)

        logger.info(f"Tool {tool_name} executed successfully")

        yield {
            "type": "tool_result",
            "content": str(result),
            "tool_name": tool_name,
            "success": True
        }
```

**Benefits:**
- ✅ Consistent async pattern throughout
- ✅ Better performance (concurrent tool calls)
- ✅ Single execution path in core.py
- ✅ Easier debugging and testing
- ✅ Supports future streaming responses

**Migration Strategy:**

```bash
# Phase 1: Convert core tools
- account_manager (critical path)
- market_data (read-only, safe)
- utilities (read-only, safe)

# Phase 2: Convert complex tools
- trading (transaction signing)
- trustline_manager (multi-step)

# Phase 3: Convert advanced tools
- stellar_soroban
- defindex_tools
```

**Timeline:** 2-3 days (all tools) or 1 day (core tools only)

---

## Implementation Roadmap 📅

### Week 1: Critical Improvements
- [ ] **Rate limiting** (High priority) - Prevent abuse
  - Install slowapi
  - Create rate limit middleware
  - Apply to chat and auth endpoints
  - Test with load testing

- [ ] **CORS security** (High priority) - Restrict access
  - Move CORS config to settings.py
  - Use environment variables
  - Test with multiple origins

### Week 2: Database & Encryption
- [ ] **Per-user salt** (High priority) - Encryption improvement
  - Add salt column to database
  - Update EncryptionManager
  - Update AccountManager
  - Create migration script
  - Test decryption of old accounts (backward compat)

### Week 3: Configuration & Tooling
- [ ] **Centralized config** (Medium priority) - Non-secrets management
  - Expand settings.py with network configs
  - Move hardcoded values to config
  - Update stellar_tools.py to use settings
  - Update contract address management

- [ ] **Tool standardization** (Medium priority) - Async consistency
  - Convert stellar_tools.py to async
  - Update tool_factory.py
  - Simplify core.py execution
  - Comprehensive testing

### Week 4: Request Validation
- [ ] **Input validation** (Medium priority) - Security & robustness
  - Create validation schemas
  - Apply to tool endpoints
  - Test with invalid inputs
  - Document expected formats

---

## Deployment Strategy

### Phase 1: Rate Limiting (Immediate)
```bash
# 1. Implement and test locally
# 2. Deploy to staging (Render)
# 3. Monitor for false positives
# 4. Adjust limits based on usage
# 5. Deploy to production
```

**Risk:** Low (non-breaking change)

### Phase 2: Per-User Salt (After Phase 1)
```bash
# 1. Add database column
# 2. Run migration script (generates salts for all users)
# 3. Update EncryptionManager
# 4. Test decryption works
# 5. Deploy with backward compatibility
```

**Risk:** Medium (database change + encryption)
**Rollback:** Have old salt available for decryption if needed

### Phase 3: Config & Tools (After Phase 2)
```bash
# 1. Expand settings.py
# 2. Convert tools to async
# 3. Extensive testing
# 4. Gradual rollout
```

**Risk:** Medium (breaking changes to tool execution)
**Testing:** Unit tests + integration tests required

---

## Testing & Validation

### Rate Limiting Tests
```python
# backend/tests/test_rate_limiting.py
def test_rate_limit_chat():
    """Verify chat endpoint rate limiting"""
    for i in range(11):  # Exceed 10/minute limit
        response = client.post("/chat", ...)
        if i < 10:
            assert response.status_code == 200
        else:
            assert response.status_code == 429  # Too Many Requests

def test_rate_limit_per_user():
    """Verify per-user limits work correctly"""
    user1_response = client.post("/chat", headers={"user-id": "user1"})
    user2_response = client.post("/chat", headers={"user-id": "user2"})
    # Both should work (different users)
```

### Per-User Salt Tests
```python
# backend/tests/test_encryption.py
def test_per_user_salt():
    """Verify per-user salt works correctly"""
    enc_mgr = EncryptionManager()

    salt1 = EncryptionManager.generate_user_salt()
    salt2 = EncryptionManager.generate_user_salt()

    # Different salts for different users
    assert salt1 != salt2

    # Same user_id + different salt = different encrypted keys
    user_id = "test_user"
    plaintext = "secret_key"

    encrypted1 = enc_mgr.encrypt(plaintext, user_id, salt1)
    encrypted2 = enc_mgr.encrypt(plaintext, user_id, salt2)

    assert encrypted1 != encrypted2  # Different salts produce different ciphertexts

    # But both decrypt correctly
    assert enc_mgr.decrypt(encrypted1, user_id, salt1) == plaintext
    assert enc_mgr.decrypt(encrypted2, user_id, salt2) == plaintext

def test_backward_compatibility():
    """Verify old accounts without salt can still be accessed"""
    # Create account with old fixed salt
    # Ensure it can still be decrypted with new system
```

### Tool Async Tests
```python
# backend/tests/test_tools_async.py
@pytest.mark.asyncio
async def test_tool_execution_async():
    """Verify all tools execute async"""
    user_id = "test_user"
    tools = create_user_tools(user_id)

    for tool in tools:
        # All tools should have ainvoke
        assert hasattr(tool, 'ainvoke'), f"{tool.name} is not async"

        # Call with ainvoke
        result = await tool.ainvoke({"action": "list"})
        assert result is not None
```

---

## Success Metrics

### Rate Limiting
- ✅ No request storms in logs
- ✅ Error rate stable at < 1%
- ✅ Valid users don't hit limits under normal usage

### Per-User Salt
- ✅ All users have unique salt
- ✅ Old accounts decrypt correctly
- ✅ New accounts use per-user salt
- ✅ Security audit confirms improvement

### Configuration Management
- ✅ No hardcoded URLs in production code
- ✅ Easy to switch between testnet/mainnet
- ✅ All contract addresses centralized
- ✅ Network switching requires only env var change

### Tool Standardization
- ✅ All tools are async
- ✅ Concurrent tool calls work
- ✅ Response times improved
- ✅ Single execution path in core.py

---

## Notes & Decisions

### Master Key Management
- ✅ Master key in Render environment (staging)
- ✅ Per-user salt improves security without changing master key
- ✅ Salt rotation planned for future (when password changes)
- ✅ No need to create a new master key - use existing

### Database Security
- ✅ Good enough for current scale
- ✅ SQLite with file-based encryption (future: move to Postgres)
- ✅ Improvements planned for first cohort (audit logging, backups, replication)

### Rate Limiting Strategy
- Development: Permissive (no limits)
- Staging: Conservative (prevent resource exhaustion)
- Production: Balanced (prevent abuse, allow legitimate use)

### Tool Execution
- All tools should be async for consistency
- Blocking calls prevent concurrent request handling
- Async tools enable future streaming responses

---

## References

- `backend/encryption.py` - Current encryption implementation
- `backend/config/settings.py` - Configuration management
- `backend/app.py` - CORS configuration
- `backend/stellar_tools.py` - Tool implementations
- `backend/agent/tool_factory.py` - Tool creation
- `backend/agent/core.py` - Tool execution

---

## Sign-Off

This security improvements roadmap is ready for implementation. Prioritize based on:

1. **Critical:** Rate limiting (prevent abuse)
2. **High:** Per-user salt (encryption improvement)
3. **High:** CORS security (restrict access)
4. **Medium:** Tool standardization (consistency & performance)
5. **Medium:** Configuration management (maintainability)
6. **Medium:** Request validation (robustness)

**Next Step:** Begin implementation with rate limiting (Week 1)

---

**Document Version:** 1.0
**Last Updated:** November 8, 2025
**Maintained By:** Claude Code
**Status:** Ready for Implementation
