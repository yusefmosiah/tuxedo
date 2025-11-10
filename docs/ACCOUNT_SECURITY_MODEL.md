# Account Security Model

## Overview

Tuxedo uses a **dual-authority** architecture where the agent can operate on behalf of both its own operational account and user-specific accounts, with strict security boundaries.

---

## Account Types

### 1. System Agent Account

**Ownership:** `user_id = "system_agent"`

**Purpose:**
- Agent's own funded mainnet wallet
- Used for agent-initiated operations (e.g., providing liquidity, testing)
- Never exposed to users

**Security:**
- ❌ **NOT shown in user UI**
- ❌ **NOT exportable by users**
- ❌ **NOT accessible via `/api/agent/accounts`**
- ✅ **Only accessible when `AgentContext.user_id = "system_agent"`**

**Storage:**
```sql
INSERT INTO wallet_accounts (user_id, ...)
VALUES ("system_agent", ...)
```

### 2. User-Managed Accounts

**Ownership:** `user_id = <authenticated_user_id>`

**Purpose:**
- User's personal accounts managed by the agent
- Agent operates these autonomously in "agent mode"
- User has full export/import capabilities

**Security:**
- ✅ **Shown in user UI** (WalletSelector)
- ✅ **Exportable by owning user only**
- ✅ **Accessible via `/api/agent/accounts`** (user-scoped)
- ✅ **Permission checked by `AgentContext`**

**Storage:**
```sql
INSERT INTO wallet_accounts (user_id, ...)
VALUES ("user_abc123", ...)
```

### 3. External Wallet (Not Stored)

**Ownership:** User's external wallet (Freighter, xBull, etc.)

**Purpose:**
- User maintains custody via browser extension
- Agent prepares transactions, user approves
- Private key NEVER touches backend

**Security:**
- ✅ **User maintains full custody**
- ✅ **No private key storage**
- ✅ **Address only passed as `wallet_address` parameter**
- ✅ **Transactions signed in browser**

---

## Permission Model

### AgentContext Authority

```python
class AgentContext:
    def __init__(self, user_id: str, wallet_mode: str = "agent"):
        self.user_id = user_id              # Current user
        self.agent_user_id = "system_agent" # Agent's identity
        self.wallet_mode = wallet_mode

    def get_authorized_user_ids(self) -> List[str]:
        """Agent has authority over both system_agent and current user"""
        return [self.agent_user_id, self.user_id]

    def has_permission(self, account_user_id: str) -> bool:
        """Check if agent can access this account"""
        return account_user_id in self.get_authorized_user_ids()
```

### Permission Check Flow

**Example 1: User tries to export their own account**
```python
agent_context = AgentContext(user_id="user_abc123")
account = {user_id: "user_abc123", ...}

agent_context.has_permission("user_abc123")  # ✅ True
# Authorized: ["system_agent", "user_abc123"]
```

**Example 2: User tries to export system_agent account**
```python
agent_context = AgentContext(user_id="user_abc123")
account = {user_id: "system_agent", ...}

agent_context.has_permission("system_agent")  # ❌ False
# Authorized: ["system_agent", "user_abc123"]
# Account owner: "system_agent"
# ❌ Permission denied!
```

**Example 3: Agent operating on its own behalf**
```python
agent_context = AgentContext(user_id="system_agent")
account = {user_id: "system_agent", ...}

agent_context.has_permission("system_agent")  # ✅ True
# Authorized: ["system_agent", "system_agent"]
```

---

## API Security

### `/api/agent/accounts` (GET)

**Security:**
- ✅ Requires authentication (`get_current_user`)
- ✅ Returns only `user_id = current_user['id']`
- ❌ System agent accounts NEVER returned

```python
@router.get("/accounts")
async def list_accounts(current_user: Dict = Depends(get_current_user)):
    user_id = current_user['id']
    # Only returns accounts WHERE user_id = user_id
    accounts = list_agent_accounts(user_id=user_id)
    return accounts
```

### `/api/agent/export-account` (POST)

**Security:**
- ✅ Requires authentication
- ✅ Permission check via `AgentContext`
- ❌ Cannot export system_agent accounts

```python
@router.post("/export-account")
async def export_account(
    account_id: str,
    current_user: Dict = Depends(get_current_user)
):
    agent_context = AgentContext(user_id=current_user['id'])

    # Get account (returns None if not found)
    account = account_manager._get_account_by_id(account_id)

    # Permission check
    if not agent_context.has_permission(account['user_id']):
        raise PermissionError("Not authorized")

    # Export (only if user owns it)
    return account_manager.export_account(agent_context, account_id)
```

---

## Database Schema

### wallet_accounts Table

```sql
CREATE TABLE wallet_accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,              -- "system_agent" or user ID
    chain TEXT NOT NULL,                -- "stellar", "solana", etc.
    public_key TEXT NOT NULL,           -- Wallet address
    encrypted_private_key TEXT NOT NULL,-- Encrypted with user-specific key
    name TEXT,
    source TEXT,                        -- "generated", "imported"
    network TEXT DEFAULT 'mainnet',
    metadata TEXT,                      -- JSON metadata
    created_at TIMESTAMP,
    last_used_at TIMESTAMP
);

-- Security indexes
CREATE INDEX idx_user_accounts ON wallet_accounts(user_id);
CREATE INDEX idx_user_chain ON wallet_accounts(user_id, chain);
```

**Query Patterns:**

```sql
-- User's accounts only
SELECT * FROM wallet_accounts WHERE user_id = ?;

-- System agent's accounts (internal only)
SELECT * FROM wallet_accounts WHERE user_id = 'system_agent';

-- NEVER mix user accounts with system accounts
```

---

## Wallet Mode Security

### Agent Mode (Default)

**Flow:**
```
User Chat → Agent → AccountManager.get_keypair_for_signing()
  → Sign with user's account → Submit to blockchain
```

**Security:**
- ✅ Agent has custody (encrypted storage)
- ✅ User can export at any time
- ✅ Permission checks on all operations
- ✅ User-specific encryption keys

### External Mode

**Flow:**
```
User Chat → Agent → Prepare unsigned XDR
  → Return to frontend → stellar-wallets-kit
  → User approves in Freighter → Submit to blockchain
```

**Security:**
- ✅ User maintains custody (never stored)
- ✅ Private key never touches backend
- ✅ Only wallet address passed to backend
- ✅ User approves every transaction

### Imported Mode

**Flow:**
```
User imports Freighter wallet → Store in AccountManager
  → Agent operates like agent mode (with custody)
```

**Security:**
- ✅ User explicitly grants custody
- ⚠️ Private key stored (encrypted)
- ✅ User can export at any time
- ✅ Same permission model as generated accounts

---

## Security Guarantees

### ✅ What Users CAN Do

1. **View their own accounts** - `/api/agent/accounts`
2. **Export their own accounts** - Full private key access
3. **Import external wallets** - Grant agent custody
4. **Connect external wallets** - Maintain custody
5. **Create new accounts** - Agent-managed or external
6. **Switch between modes** - Agent vs External
7. **Delete their own accounts** (future)

### ❌ What Users CANNOT Do

1. **View system_agent accounts** - Not in API responses
2. **Export system_agent accounts** - Permission denied
3. **Sign with system_agent key** - Permission denied
4. **Access other users' accounts** - User-scoped queries
5. **Bypass wallet_mode** - Injected server-side
6. **Spoof AgentContext** - Created in backend only
7. **See other users' private keys** - User-specific encryption

### 🔒 System Protections

1. **Encryption at rest** - All private keys encrypted
2. **User-specific encryption** - Keys encrypted with user ID
3. **Permission checks** - Every sensitive operation
4. **Authentication required** - All account endpoints
5. **Audit logging** - Sensitive operations logged
6. **SQL injection protection** - Parameterized queries
7. **Context injection** - AgentContext created server-side

---

## Threat Model

### Threats Mitigated

- ✅ **User accessing system_agent account** - Permission checks
- ✅ **User accessing other user's accounts** - User-scoped queries
- ✅ **LLM spoofing user context** - Server-side context injection
- ✅ **Private key exposure** - Encrypted at rest
- ✅ **Unauthorized export** - Permission checks
- ✅ **SQL injection** - Parameterized queries

### Threats Requiring Vigilance

- ⚠️ **Backend compromise** - Would expose encrypted keys
- ⚠️ **Encryption key compromise** - Would allow decryption
- ⚠️ **User credential theft** - Would grant account access
- ⚠️ **Man-in-the-middle** - Requires HTTPS enforcement
- ⚠️ **Browser extension compromise** - External wallet risk

---

## Best Practices

### For Development

1. **Never log private keys** - Even in debug mode
2. **Always check permissions** - Before sensitive operations
3. **User-scoped queries** - Include `WHERE user_id = ?`
4. **Context injection** - Create AgentContext server-side
5. **Validate input** - Sanitize all user input
6. **Rate limiting** - On sensitive endpoints
7. **Audit logging** - Track export/import operations

### For Deployment

1. **HTTPS required** - All production traffic
2. **Secure key storage** - Environment variables
3. **Database backups** - Encrypted backups
4. **Access control** - Principle of least privilege
5. **Security audits** - Regular penetration testing
6. **Monitoring** - Alert on suspicious activity
7. **Incident response** - Plan for breach scenarios

---

## Naming Conventions

### Current Terminology (Confusing)

- ❌ "agent accounts" - Could mean system_agent or user accounts
- ❌ "agent wallet" - Unclear whose wallet
- ❌ "system accounts" - Too generic

### Recommended Terminology (Clear)

- ✅ **"My Accounts"** - User's agent-managed accounts
- ✅ **"Managed Accounts"** - User accounts under agent custody
- ✅ **"External Wallet"** - User's Freighter/xBull wallet
- ✅ **"System Agent Account"** - Agent's operational wallet
- ✅ **"Imported Wallet"** - External wallet imported to agent custody

### UI Language

```typescript
// ❌ Confusing
"Agent Accounts"
"Agent Wallet"

// ✅ Clear
"My Accounts (Agent-Managed)"
"External Wallet (My Custody)"
"Connected: Freighter"
```

---

## Example Scenarios

### Scenario 1: User Creates Account

```
1. User clicks "Create Account" in UI
2. Frontend calls POST /api/agent/create-account
3. Backend creates account with user_id = current_user['id']
4. Private key encrypted with user's encryption key
5. Account stored in database
6. Account appears in user's account list
7. User can export this account anytime
```

### Scenario 2: User Connects Freighter

```
1. User clicks "Connect Wallet"
2. stellar-wallets-kit opens Freighter modal
3. User approves in Freighter
4. Frontend receives wallet address (no private key)
5. Frontend stores address in WalletContext
6. When user chats, wallet_address sent to backend
7. Agent prepares unsigned XDR
8. Frontend signs via Freighter
9. Frontend submits signed transaction
```

### Scenario 3: User Tries to Export System Account

```
1. User somehow gets system_agent account_id
2. User calls POST /api/agent/export-account
3. Backend creates AgentContext(user_id=user_id)
4. Backend loads account: user_id = "system_agent"
5. Permission check: agent_context.has_permission("system_agent")
6. ❌ DENIED: "system_agent" not in ["system_agent", "user_id"]
7. Return 403 Forbidden
```

---

**Last Updated:** 2025-11-10
**Version:** 1.0
**Status:** Current Architecture
