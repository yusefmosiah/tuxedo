# Agent Account Migration: Quantum Leap Strategy

**Complete Replacement of KeyManager with AccountManager**

---

## Executive Summary

**Approach:** Complete architectural replacement, no gradual migration, no backward compatibility.

**Rationale:**

- No valuable data exists (testnet accounts only, recreatable from faucet)
- Gradual migration adds complexity without benefit
- Clean break enables simpler, more secure architecture
- Future-proof from day one

**Timeline:** 4-6 hours of focused work

**Outcome:** Production-ready multi-user agent system with complete user isolation

---

## Current State: Single-User Insecure

```
User Chat → Agent → Stellar Tools → KeyManager (global) → .stellar_keystore.json
                                                          ↓
                                                     Plain text keys
                                                     No user isolation
                                                     Single file for all users
```

**Files to Delete:**

- `backend/key_manager.py` - Entire class removed
- `.stellar_keystore.json` - Deleted (backed up if paranoid)

**Critical Issue:** Any authenticated user can access ANY account. Unacceptable for production.

---

## Target State: Multi-User Secure

```
User Chat → Auth Middleware (user_id) → Agent → Stellar Tools (user_id) → AccountManager → Database
                                                                                            ↓
                                                                                   Encrypted keys
                                                                                   User-isolated rows
                                                                                   Permission checks
```

**Core Principle:** `user_id` flows through every layer, enforced at every boundary.

---

## Architecture Changes

### 1. Tool Signatures: `user_id` is Mandatory Second Parameter

**Pattern:** Every tool function accepts `user_id` as the second parameter after `action`.

```python
# OLD (KeyManager era):
def account_manager(action: str, key_manager, horizon: Server, account_id: Optional[str] = None):
    """Manage accounts globally"""
    keypair = key_manager.get_keypair(account_id)  # No permission check!
    ...

# NEW (AccountManager era):
def account_manager(
    action: str,
    user_id: str,           # MANDATORY: enforces user isolation
    account_manager,        # Replaces key_manager
    horizon: Server,
    account_id: Optional[str] = None
):
    """Manage accounts with user isolation"""
    # Permission check built into AccountManager
    keypair = account_manager.get_keypair_for_signing(user_id, account_id)
    ...
```

**All Stellar Tools Updated:**

- `account_manager(action, user_id, ...)`
- `trading(action, user_id, account_id, ...)`
- `trustline_manager(action, user_id, account_id, ...)`
- `market_data(action, user_id, ...)` - read-only but logged
- `utilities(action, user_id, ...)` - read-only but logged

### 2. Agent Tool Registration: Inject `user_id` via Lambda

**Pattern:** Lambda wrapper injects `user_id` from auth context, user can't fake it.

```python
# backend/main.py

@app.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Chat endpoint with mandatory user context

    Security flow:
    1. get_current_user extracts user_id from session token
    2. user_id injected into all tool calls via lambda
    3. Tools enforce ownership before any operation
    """
    user_id = current_user['id']  # From auth middleware (trusted)

    # Initialize components
    account_mgr = AccountManager()
    horizon = Server("https://horizon-testnet.stellar.org")

    # Create tools with user_id injection
    tools = [
        Tool(
            name="account_manager",
            func=lambda action, **kwargs: stellar_tools.account_manager(
                action=action,
                user_id=user_id,        # INJECTED from auth, not from LLM
                account_manager=account_mgr,
                horizon=horizon,
                **kwargs
            ),
            description="Manage Stellar accounts: create, fund, get balances, list, export, import"
        ),
        Tool(
            name="trading",
            func=lambda action, account_id, **kwargs: stellar_tools.trading(
                action=action,
                user_id=user_id,        # INJECTED
                account_id=account_id,
                account_manager=account_mgr,
                horizon=horizon,
                **kwargs
            ),
            description="Trade on Stellar DEX: buy, sell, cancel orders, view orders"
        ),
        Tool(
            name="trustline_manager",
            func=lambda action, account_id, asset_code, asset_issuer, **kwargs: stellar_tools.trustline_manager(
                action=action,
                user_id=user_id,        # INJECTED
                account_id=account_id,
                asset_code=asset_code,
                asset_issuer=asset_issuer,
                account_manager=account_mgr,
                horizon=horizon,
                **kwargs
            ),
            description="Manage trustlines: establish, remove"
        ),
        Tool(
            name="market_data",
            func=lambda action, **kwargs: stellar_tools.market_data(
                action=action,
                user_id=user_id,        # INJECTED (for logging)
                horizon=horizon,
                **kwargs
            ),
            description="Query market data: orderbook, trades, ticker"
        ),
        Tool(
            name="utilities",
            func=lambda action, **kwargs: stellar_tools.utilities(
                action=action,
                user_id=user_id,        # INJECTED (for logging)
                horizon=horizon,
                **kwargs
            ),
            description="Network utilities: status, fees"
        )
    ]

    # Create agent with user-isolated tools
    agent = create_agent(tools=tools)

    # Execute
    response = await agent.arun(request.message)

    return {"response": response, "success": True}
```

**Key Security Properties:**

- `user_id` comes from `get_current_user(session_token)` - verified by auth system
- LLM cannot provide `user_id` parameter (lambda injects it)
- Even if LLM hallucinates account IDs, permission check catches it
- Tools fail closed: if `user_id` missing, operation rejected

### 3. Tool Implementation: Permission Checks First

**Pattern:** Every tool verifies ownership before any operation.

```python
# backend/stellar_tools.py

def account_manager(
    action: str,
    user_id: str,
    account_manager: AccountManager,
    horizon: Server,
    account_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Unified account management with mandatory user isolation

    Args:
        action: Operation to perform
        user_id: User identifier (MANDATORY - injected by auth layer)
        account_manager: AccountManager instance
        horizon: Horizon server instance
        account_id: Account ID (for get/export/delete actions)
        secret_key: Secret key (for import action)
        limit: Transaction limit (for transactions action)
    """
    try:
        if action == "create":
            # Generate new account for THIS user
            result = account_manager.generate_account(
                user_id=user_id,
                chain="stellar",
                name="Stellar Account"
            )
            return result

        elif action == "fund":
            # PERMISSION CHECK: verify user owns this account
            if not account_id:
                return {"error": "account_id required", "success": False}

            account = account_manager._get_account_by_id(account_id)
            if not account or account['user_id'] != user_id:
                return {
                    "error": f"Permission denied: account not owned by user",
                    "success": False
                }

            # Proceed with funding
            public_key = account['public_key']
            response = requests.get(f"{FRIENDBOT_URL}?addr={public_key}")
            response.raise_for_status()

            return {"success": True, "message": "Account funded"}

        elif action == "get":
            # PERMISSION CHECK
            if not account_id:
                return {"error": "account_id required", "success": False}

            account = account_manager._get_account_by_id(account_id)
            if not account or account['user_id'] != user_id:
                return {"error": "Permission denied", "success": False}

            # Fetch on-chain data
            public_key = account['public_key']
            chain_account = horizon.accounts().account_id(public_key).call()

            return {
                "account_id": account_id,
                "public_key": public_key,
                "balances": chain_account["balances"],
                "sequence": chain_account["sequence"],
                "success": True
            }

        elif action == "list":
            # List THIS user's accounts only
            accounts = account_manager.get_user_accounts(user_id, chain="stellar")
            return {
                "accounts": accounts,
                "count": len(accounts),
                "success": True
            }

        elif action == "export":
            # PERMISSION CHECK built into export_account
            if not account_id:
                return {"error": "account_id required", "success": False}

            result = account_manager.export_account(user_id, account_id)
            return result

        elif action == "import":
            # Import to THIS user's account list
            if not secret_key:
                return {"error": "secret_key required", "success": False}

            result = account_manager.import_account(
                user_id=user_id,
                chain="stellar",
                private_key=secret_key,
                name="Imported Account"
            )
            return result

        elif action == "transactions":
            # PERMISSION CHECK
            if not account_id:
                return {"error": "account_id required", "success": False}

            account = account_manager._get_account_by_id(account_id)
            if not account or account['user_id'] != user_id:
                return {"error": "Permission denied", "success": False}

            public_key = account['public_key']
            transactions = horizon.transactions().for_account(public_key).limit(limit).order(desc=True).call()

            return {
                "transactions": [
                    {
                        "hash": tx["hash"],
                        "ledger": tx["ledger"],
                        "created_at": tx["created_at"],
                        "successful": tx["successful"]
                    }
                    for tx in transactions["_embedded"]["records"]
                ],
                "success": True
            }

        else:
            return {
                "error": f"Unknown action: {action}",
                "valid_actions": ["create", "fund", "get", "list", "export", "import", "transactions"]
            }

    except Exception as e:
        return {"error": str(e), "success": False}


def trading(
    action: str,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    horizon: Server,
    buying_asset: Optional[str] = None,
    selling_asset: Optional[str] = None,
    buying_issuer: Optional[str] = None,
    selling_issuer: Optional[str] = None,
    amount: Optional[str] = None,
    price: Optional[str] = None,
    order_type: str = "limit",
    offer_id: Optional[str] = None,
    max_slippage: float = 0.05
) -> Dict[str, Any]:
    """
    Trading with mandatory user isolation

    EVERY action requires permission check before signing transactions
    """
    try:
        # PERMISSION CHECK: verify user owns this account
        if not account_manager.user_owns_account(user_id, account_id):
            return {
                "error": "Permission denied: account not owned by user",
                "success": False
            }

        # Get signing keypair (permission checked again inside)
        keypair = account_manager.get_keypair_for_signing(user_id, account_id)

        # Proceed with trading operations...
        if action == "buy":
            # ... implementation
            pass
        elif action == "sell":
            # ... implementation
            pass
        elif action == "cancel_order":
            # ... implementation
            pass
        elif action == "get_orders":
            # Read-only but still permission-checked
            account = account_manager._get_account_by_id(account_id)
            public_key = account['public_key']
            offers = horizon.offers().for_account(public_key).call()
            return {"offers": offers["_embedded"]["records"], "success": True}

    except PermissionError as e:
        return {"error": str(e), "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}
```

---

## Implementation Steps: Quantum Leap

### **Step 1: Delete Old System** (15 minutes)

```bash
# Backup (paranoia only)
cp backend/key_manager.py backend/key_manager.py.backup
cp .stellar_keystore.json .stellar_keystore.json.backup 2>/dev/null || true

# Delete
git rm backend/key_manager.py
rm -f .stellar_keystore.json

# Commit
git commit -m "Remove KeyManager: quantum leap to AccountManager"
```

### **Step 2: Update Tool Signatures** (1-2 hours)

**File:** `backend/stellar_tools.py`

- Add `user_id: str` as second parameter to all tool functions
- Replace `key_manager` parameter with `account_manager`
- Add permission checks at start of every function
- Use `account_manager.get_keypair_for_signing(user_id, account_id)` for transactions

**Pattern for ALL tools:**

```python
def tool_name(action: str, user_id: str, account_manager: AccountManager, ...):
    # 1. Validate user_id present
    if not user_id:
        return {"error": "user_id required", "success": False}

    # 2. Permission check if operating on specific account
    if account_id:
        if not account_manager.user_owns_account(user_id, account_id):
            return {"error": "Permission denied", "success": False}

    # 3. Proceed with operation
    ...
```

### **Step 3: Update Agent Tool Registration** (1 hour)

**File:** `backend/main.py`

- Import `AccountManager` instead of `KeyManager`
- Create `AccountManager()` instance
- Wrap all tool registrations with lambda to inject `user_id`
- Ensure `current_user` extracted from auth middleware

**Template:**

```python
account_mgr = AccountManager()

tools = [
    Tool(
        name="tool_name",
        func=lambda **kwargs: stellar_tools.tool_name(
            user_id=current_user['id'],  # From auth
            account_manager=account_mgr,
            **kwargs
        ),
        description="..."
    ),
    # ... repeat for all tools
]
```

### **Step 4: Test User Isolation** (1-2 hours)

**Test Script:** `backend/test_user_isolation.py`

```python
"""
Test that user isolation works correctly
"""
from account_manager import AccountManager
from database_passkeys import PasskeyDatabaseManager
import pytest

def test_cross_user_account_access():
    """User A cannot access User B's accounts"""
    db = PasskeyDatabaseManager()
    account_mgr = AccountManager()

    # Create two users
    user_a = db.create_user("user_a@test.com")
    user_b = db.create_user("user_b@test.com")

    # User A creates account
    result_a = account_mgr.generate_account(
        user_id=user_a['id'],
        chain="stellar",
        name="User A Account"
    )
    assert result_a['success']
    account_a_id = result_a['account_id']

    # User B tries to export User A's account
    result = account_mgr.export_account(
        user_id=user_b['id'],
        account_id=account_a_id
    )
    assert not result['success']
    assert "Permission denied" in result['error']

    print("✅ User isolation test passed")

def test_user_can_access_own_accounts():
    """User can access their own accounts"""
    db = PasskeyDatabaseManager()
    account_mgr = AccountManager()

    user = db.create_user("user_test@test.com")

    # Create account
    result = account_mgr.generate_account(
        user_id=user['id'],
        chain="stellar"
    )
    assert result['success']
    account_id = result['account_id']

    # Export own account
    result = account_mgr.export_account(
        user_id=user['id'],
        account_id=account_id
    )
    assert result['success']
    assert 'private_key' in result

    print("✅ User can access own accounts")

def test_list_accounts_user_isolated():
    """List accounts returns only user's accounts"""
    db = PasskeyDatabaseManager()
    account_mgr = AccountManager()

    user_a = db.create_user("list_a@test.com")
    user_b = db.create_user("list_b@test.com")

    # User A creates 2 accounts
    account_mgr.generate_account(user_a['id'], "stellar")
    account_mgr.generate_account(user_a['id'], "stellar")

    # User B creates 1 account
    account_mgr.generate_account(user_b['id'], "stellar")

    # User A sees only their 2 accounts
    accounts_a = account_mgr.get_user_accounts(user_a['id'])
    assert len(accounts_a) == 2

    # User B sees only their 1 account
    accounts_b = account_mgr.get_user_accounts(user_b['id'])
    assert len(accounts_b) == 1

    print("✅ List accounts properly isolated")

if __name__ == "__main__":
    test_cross_user_account_access()
    test_user_can_access_own_accounts()
    test_list_accounts_user_isolated()
    print("\n✅ All isolation tests passed!")
```

**Run:**

```bash
cd backend
source .venv/bin/activate
python test_user_isolation.py
```

### **Step 5: Update Environment** (5 minutes)

**File:** `backend/.env`

```bash
# Add encryption keys if not present
ENCRYPTION_MASTER_KEY=<generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'>
ENCRYPTION_SALT=tuxedo-agent-accounts-v1

# Existing vars
OPENAI_API_KEY=your_key
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
```

### **Step 6: Clean Up References** (30 minutes)

**Search and replace across codebase:**

```bash
# Find all KeyManager references
grep -r "KeyManager" backend/ --exclude-dir=.venv

# Find all key_manager parameter references
grep -r "key_manager" backend/ --exclude-dir=.venv

# Update imports
sed -i 's/from key_manager import KeyManager/from account_manager import AccountManager/g' backend/*.py

# Update variable names
sed -i 's/key_manager/account_manager/g' backend/stellar_tools.py
sed -i 's/KeyManager()/AccountManager()/g' backend/*.py
```

---

## Verification Checklist

**Before Quantum Leap:**

- [ ] All changes reviewed and understood
- [ ] `ENCRYPTION_MASTER_KEY` generated and set in `.env`
- [ ] Database schema includes `wallet_accounts` table
- [ ] `AccountManager` class tested in isolation

**During Quantum Leap:**

- [ ] `KeyManager` class deleted
- [ ] `.stellar_keystore.json` deleted (backed up)
- [ ] All tool signatures updated with `user_id` parameter
- [ ] All tools use `AccountManager` instead of `KeyManager`
- [ ] `main.py` injects `user_id` via lambda wrappers
- [ ] No references to `KeyManager` remain in codebase

**After Quantum Leap:**

- [ ] User isolation tests pass
- [ ] Agent can create accounts (testnet)
- [ ] Agent can fund accounts via Friendbot
- [ ] Agent can query balances
- [ ] Cross-user access blocked (test fails as expected)
- [ ] Production ready for multi-user deployment

---

## Rollback Plan

**If quantum leap fails catastrophically:**

```bash
# Restore KeyManager
git checkout HEAD~1 -- backend/key_manager.py

# Restore keystore
cp .stellar_keystore.json.backup .stellar_keystore.json

# Revert changes
git reset --hard HEAD~1

# Debug and retry
```

**But honestly:** With no valuable data, easier to just fix forward.

---

## Success Metrics

**Post-Migration:**

- ✅ No `KeyManager` in codebase
- ✅ All accounts stored in database (encrypted)
- ✅ User A cannot access User B's accounts
- ✅ Agent creates accounts scoped to authenticated user
- ✅ All tools enforce permission checks
- ✅ System ready for production deployment

**Production Readiness Score:** 8/10

- Security: ✅ User isolated, encrypted at rest
- Scalability: ✅ Database-backed, multi-chain ready
- Maintainability: ✅ Clean architecture, no legacy code
- Missing: Audit logging (-1), TEE deployment (-1)

---

## Timeline

**Total:** 4-6 hours

- Delete old system: 15 min
- Update tool signatures: 1-2 hours
- Update agent registration: 1 hour
- Test user isolation: 1-2 hours
- Update environment: 5 min
- Clean up references: 30 min

**Recommended Approach:** Block out 4 hours, execute in one sitting, ship it.

---

**Status:** Design Complete
**Next Action:** Execute quantum leap
**Risk Level:** Low (no valuable data to lose)
**Reward:** Production-ready multi-user agent architecture

**Related Documents:**

- `AGENT_ACCOUNT_SECURITY_PLAN.md` - Overall security architecture
- `AGENT_FILESYSTEM_ISOLATION.md` - Layered security strategy
- `PASSKEY_ARCHITECTURE_V2.md` - User authentication system
