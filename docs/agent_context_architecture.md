# Agent Context Architecture: Dual Authority Pattern

## Overview

This document describes the architectural redesign to support **dual authority** for the Tuxedo AI agent, allowing it to seamlessly access both its own funded accounts and user-specific accounts without tool duplication.

## Problem Statement

### Current Architecture Issues

The agent has a pre-funded mainnet account (`GA4KBIWEVNXJPT545A6YYZPZUFYHCG4LBDGN437PDRTBLGOE3KIW5KBZ`) imported at startup under `user_id="system_agent"`, but cannot access it during user interactions because:

1. **Account Import**: On startup, `AGENT_STELLAR_SECRET` is imported into `AccountManager` with `user_id="system_agent"` (see `agent/core.py:65-126`)

2. **System Prompt**: The agent is told about its funded account in the system prompt (see `agent/core.py:705-734`)

3. **Per-Request Tools**: When a user chats, tools are created with that **user's** `user_id` via `tool_factory.create_user_tools(user_id)` (see `tool_factory.py:35-534`)

4. **Permission Mismatch**: When the agent calls `stellar_account_manager(action="list")`, it queries accounts for the current user, not for `"system_agent"`, so it cannot see its own funded account

5. **Permission Denied**: Even if the agent gets the `account_id` of its funded account, permission checks fail because tools are scoped to a different user:

```python
# account_manager.py:366-390
def get_keypair_for_signing(self, user_id: str, account_id: str):
    if account['user_id'] != user_id:
        raise PermissionError("Permission denied")
```

### Why Not Duplicate Tools?

We could create separate `agent_*` tools for agent operations and `stellar_*` tools for user operations, but this:
- Violates DRY principle
- Creates maintenance burden
- Makes the tool set confusing
- Doesn't scale to future contexts

## Solution: Delegated Authority Pattern

### Core Concept

Replace single-context user isolation with **dual authority**:

```
Before:
user_id (single context) → tools → permission checks

After:
agent_context (dual authority) → tools → permission checks
   ├─ system_agent (agent's own accounts)
   └─ user_id (current user's accounts)
```

The agent operates with explicit authority over multiple user contexts simultaneously.

## Architecture Components

### 1. AgentContext Object

**New File**: `backend/agent/context.py`

```python
"""
Agent Context - Delegated Authority Pattern
Provides dual authority for agent operations over both system and user accounts.
"""

from typing import List, Optional


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
```

### 2. AccountManager Updates

**File**: `backend/account_manager.py`

Update all permission-checking methods to accept `authorized_user_ids`:

#### get_keypair_for_signing()

```python
def get_keypair_for_signing(
    self,
    user_id: str,
    account_id: str,
    authorized_user_ids: Optional[List[str]] = None
):
    """
    Get decrypted keypair for transaction signing.

    Supports delegated authority - agent can sign for accounts
    owned by any of the authorized user IDs.

    Args:
        user_id: Primary user ID (for backward compatibility)
        account_id: Account to access
        authorized_user_ids: List of all authorized user IDs
                             (enables delegated authority)
                             If None, defaults to [user_id]

    Returns:
        Keypair object for signing

    Raises:
        ValueError: If account not found
        PermissionError: If user not authorized for this account
    """
    # Get account
    account = self._get_account_by_id(account_id)
    if not account:
        raise ValueError("Account not found")

    # Support delegated authority
    if authorized_user_ids is None:
        authorized_user_ids = [user_id]

    # Check permission against all authorized user IDs
    if account['user_id'] not in authorized_user_ids:
        raise PermissionError(
            f"Permission denied: account owned by {account['user_id']}, "
            f"but only authorized for {authorized_user_ids}"
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
```

#### export_account()

```python
def export_account(
    self,
    user_id: str,
    account_id: str,
    authorized_user_ids: Optional[List[str]] = None
) -> Dict:
    """
    Export wallet private key with delegated authority support.

    Args:
        user_id: Primary user ID
        account_id: Account to export
        authorized_user_ids: List of authorized user IDs
    """
    try:
        # Get account
        account = self._get_account_by_id(account_id)
        if not account:
            return {
                "error": "Account not found",
                "success": False
            }

        # Support delegated authority
        if authorized_user_ids is None:
            authorized_user_ids = [user_id]

        # Verify ownership
        if account['user_id'] not in authorized_user_ids:
            return {
                "error": f"Permission denied: account not owned by authorized users",
                "success": False
            }

        # Decrypt private key using actual owner
        private_key = self.encryption.decrypt(
            account['encrypted_private_key'],
            account['user_id']  # Use actual owner for decryption
        )

        # ... rest of export logic
```

#### delete_account()

```python
def delete_account(
    self,
    user_id: str,
    account_id: str,
    authorized_user_ids: Optional[List[str]] = None
) -> Dict:
    """
    Delete an account with delegated authority support.

    Args:
        user_id: Primary user ID
        account_id: Account to delete
        authorized_user_ids: List of authorized user IDs
    """
    try:
        # Get account
        account = self._get_account_by_id(account_id)
        if not account:
            return {
                "error": "Account not found",
                "success": False
            }

        # Support delegated authority
        if authorized_user_ids is None:
            authorized_user_ids = [user_id]

        # Verify ownership
        if account['user_id'] not in authorized_user_ids:
            return {
                "error": "Permission denied: account not owned by authorized users",
                "success": False
            }

        # ... rest of delete logic
```

#### user_owns_account()

```python
def user_owns_account(
    self,
    user_id: str,
    account_id: str,
    authorized_user_ids: Optional[List[str]] = None
) -> bool:
    """
    Check if user owns account with delegated authority support.

    Args:
        user_id: Primary user ID
        account_id: Account to check
        authorized_user_ids: List of authorized user IDs
    """
    if authorized_user_ids is None:
        authorized_user_ids = [user_id]

    account = self._get_account_by_id(account_id)
    return account is not None and account['user_id'] in authorized_user_ids
```

### 3. Stellar Tools Updates

**File**: `backend/stellar_tools.py`

Update each tool function to accept and use `authorized_user_ids`:

#### account_manager()

```python
def account_manager(
    action: str,
    user_id: str,
    account_manager: AccountManager,
    horizon: Server,
    account_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    limit: int = 10,
    authorized_user_ids: Optional[List[str]] = None  # NEW
) -> Dict:
    """
    Stellar account management operations with delegated authority.

    Args:
        action: Operation to perform
        user_id: Primary user ID (for logging/defaults)
        account_manager: AccountManager instance
        horizon: Horizon server instance
        account_id: Account ID for operations
        secret_key: Secret key for import
        limit: Transaction limit
        authorized_user_ids: List of authorized user IDs (for dual authority)
    """
    if authorized_user_ids is None:
        authorized_user_ids = [user_id]

    if action == "list":
        # Return accounts from ALL authorized user IDs
        all_accounts = []
        for auth_user_id in authorized_user_ids:
            accounts = account_manager.get_user_accounts(
                user_id=auth_user_id,
                chain="stellar"
            )
            # Tag each account with ownership context
            for acc in accounts:
                acc['owner_context'] = (
                    'agent' if auth_user_id == "system_agent"
                    else 'user'
                )
                acc['owner_user_id'] = auth_user_id
            all_accounts.extend(accounts)

        return {
            "accounts": all_accounts,
            "count": len(all_accounts),
            "success": True
        }

    elif action == "get":
        # account_id required
        if not account_id:
            return {"error": "account_id required", "success": False}

        # Verify permission
        if not account_manager.user_owns_account(
            user_id=user_id,
            account_id=account_id,
            authorized_user_ids=authorized_user_ids
        ):
            return {"error": "Permission denied", "success": False}

        # ... rest of get logic

    elif action == "export":
        return account_manager.export_account(
            user_id=user_id,
            account_id=account_id,
            authorized_user_ids=authorized_user_ids
        )

    # ... similar updates for other actions
```

#### trading()

```python
def trading(
    action: str,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    horizon: Server,
    buying_asset: Optional[str] = None,
    selling_asset: Optional[str] = None,
    # ... other params
    authorized_user_ids: Optional[List[str]] = None  # NEW
):
    """
    Trading operations with delegated authority support.
    """
    if authorized_user_ids is None:
        authorized_user_ids = [user_id]

    # Verify permission
    if not account_manager.user_owns_account(
        user_id=user_id,
        account_id=account_id,
        authorized_user_ids=authorized_user_ids
    ):
        return {"error": "Permission denied", "success": False}

    # Get keypair for signing
    keypair = account_manager.get_keypair_for_signing(
        user_id=user_id,
        account_id=account_id,
        authorized_user_ids=authorized_user_ids
    )

    # ... rest of trading logic
```

#### trustline_manager()

```python
def trustline_manager(
    action: str,
    user_id: str,
    account_id: str,
    asset_code: str,
    asset_issuer: str,
    account_manager: AccountManager,
    horizon: Server,
    limit: Optional[str] = None,
    authorized_user_ids: Optional[List[str]] = None  # NEW
):
    """
    Trustline operations with delegated authority support.
    """
    if authorized_user_ids is None:
        authorized_user_ids = [user_id]

    # Verify permission
    if not account_manager.user_owns_account(
        user_id=user_id,
        account_id=account_id,
        authorized_user_ids=authorized_user_ids
    ):
        return {"error": "Permission denied", "success": False}

    # Get keypair for signing
    keypair = account_manager.get_keypair_for_signing(
        user_id=user_id,
        account_id=account_id,
        authorized_user_ids=authorized_user_ids
    )

    # ... rest of trustline logic
```

Apply similar pattern to `market_data()` and `utilities()` (though these are read-only and may not need authorization checks).

### 4. Tool Factory Updates

**File**: `backend/agent/tool_factory.py`

Change function signature and tool implementations:

#### create_user_tools()

```python
from agent.context import AgentContext  # NEW import

def create_user_tools(agent_context: AgentContext) -> List:
    """
    Create tools for agent with delegated authority context.

    The agent can operate on:
    - Its own system accounts (system_agent)
    - Current user's accounts (user_id)

    Args:
        agent_context: Agent execution context with dual authority

    Returns:
        List of LangChain tools with agent context injected

    Security:
        - agent_context encapsulates authorized user IDs
        - LLM cannot access or modify authorization context
        - Each tool enforces permission checks using authorized_user_ids
        - Tools fail closed: no authorization = operation rejected
    """
    logger.info(f"Creating tools for {agent_context}")

    # Initialize shared dependencies
    horizon = Server(HORIZON_URL)
    account_mgr = AccountManager()

    # Extract values from context
    user_id = agent_context.user_id
    authorized_user_ids = agent_context.get_authorized_user_ids()

    # Create tools with agent_context injected via closure

    @tool
    def stellar_account_manager(
        action: str,
        account_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        limit: int = 10
    ):
        """
        Stellar account management operations (MAINNET ONLY).

        With dual authority, this tool can access:
        - Agent's own funded mainnet account
        - Current user's accounts (if authenticated)

        Actions:
            - "create": Generate new mainnet account (requires manual funding)
            - "get": Get account details (balances, sequence, trustlines)
            - "transactions": Get transaction history
            - "list": List all accessible accounts (agent + user)
            - "export": Export secret key (⚠️ dangerous!)
            - "import": Import existing keypair

        Args:
            action: Operation to perform
            account_id: Account ID (internal ID, required for most actions)
            secret_key: Secret key (required only for "import")
            limit: Transaction limit (for "transactions" action)

        Returns:
            Action-specific response dict. For "list", returns accounts
            tagged with owner_context: "agent" or "user"
        """
        return _account_manager(
            action=action,
            user_id=user_id,  # Primary user ID
            authorized_user_ids=authorized_user_ids,  # Dual authority
            account_manager=account_mgr,
            horizon=horizon,
            account_id=account_id,
            secret_key=secret_key,
            limit=limit
        )

    @tool
    def stellar_trading(
        action: str,
        account_id: str,
        buying_asset: Optional[str] = None,
        selling_asset: Optional[str] = None,
        # ... other params
    ):
        """
        Unified SDEX trading tool with dual authority.

        Can execute trades from:
        - Agent's funded account
        - User's accounts
        """
        return _trading(
            action=action,
            user_id=user_id,
            authorized_user_ids=authorized_user_ids,  # Dual authority
            account_id=account_id,
            account_manager=account_mgr,
            horizon=horizon,
            # ... other params
        )

    @tool
    def stellar_trustline_manager(
        action: str,
        account_id: str,
        asset_code: str,
        asset_issuer: str,
        limit: Optional[str] = None
    ):
        """
        Manage trustlines with dual authority.
        """
        return _trustline_manager(
            action=action,
            user_id=user_id,
            authorized_user_ids=authorized_user_ids,  # Dual authority
            account_id=account_id,
            asset_code=asset_code,
            asset_issuer=asset_issuer,
            account_manager=account_mgr,
            horizon=horizon,
            limit=limit
        )

    # ... similar updates for market_data, utilities, blend tools

    # Return list of tools
    tools = [
        stellar_account_manager,
        stellar_trading,
        stellar_trustline_manager,
        stellar_market_data,
        stellar_utilities,
        # Blend Capital tools
        blend_find_best_yield,
        blend_discover_pools,
        blend_supply_to_pool,
        blend_withdraw_from_pool,
        blend_check_my_positions,
        blend_get_pool_apy
    ]

    logger.info(f"Created {len(tools)} tools with dual authority for {agent_context}")
    return tools
```

#### create_anonymous_tools()

```python
def create_anonymous_tools() -> List:
    """
    Create read-only tools for anonymous (unauthenticated) users.

    Returns:
        List of read-only LangChain tools
    """
    logger.info("Creating anonymous (read-only) tools")

    # Anonymous users get an agent context too
    agent_context = AgentContext(user_id="anonymous")

    # Initialize shared dependencies
    horizon = Server(HORIZON_URL)

    # Only include read-only tools for anonymous users
    # (market_data and utilities don't need account access)

    @tool
    def stellar_market_data(
        action: str,
        base_asset: str = "XLM",
        quote_asset: Optional[str] = None,
        quote_issuer: Optional[str] = None,
        limit: int = 20
    ):
        """Query SDEX market data (read-only, no authentication required)."""
        return _market_data(
            action=action,
            user_id=agent_context.user_id,
            horizon=horizon,
            base_asset=base_asset,
            quote_asset=quote_asset,
            quote_issuer=quote_issuer,
            limit=limit
        )

    @tool
    def stellar_utilities(action: str):
        """Network utilities (read-only, no authentication required)."""
        return _utilities(
            action=action,
            user_id=agent_context.user_id,
            horizon=horizon
        )

    tools = [
        stellar_market_data,
        stellar_utilities
    ]

    logger.info(f"Created {len(tools)} anonymous tools")
    return tools
```

### 5. Route Handler Updates

**File**: `backend/api/routes/chat.py` (or wherever tools are created)

Update the route that creates tools:

```python
from agent.context import AgentContext  # NEW import
from agent.tool_factory import create_user_tools

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with AI agent.
    """
    # Get current user ID from auth (or "anonymous")
    current_user_id = get_current_user_id_from_auth()  # Your auth logic

    # Create agent context with dual authority
    agent_context = AgentContext(user_id=current_user_id)

    # Create tools with dual authority
    tools = create_user_tools(agent_context=agent_context)

    # ... rest of chat logic with tools
```

### 6. Blend Tools Updates

**File**: `backend/blend_account_tools.py`

Update Blend tool implementations to accept and use `authorized_user_ids`:

```python
async def _blend_supply_to_pool(
    pool_address: str,
    asset_address: str,
    amount: float,
    account_id: str,
    user_id: str,
    account_manager: AccountManager,
    authorized_user_ids: Optional[List[str]] = None  # NEW
):
    """Supply to Blend pool with delegated authority."""
    if authorized_user_ids is None:
        authorized_user_ids = [user_id]

    # Verify permission
    if not account_manager.user_owns_account(
        user_id=user_id,
        account_id=account_id,
        authorized_user_ids=authorized_user_ids
    ):
        return {"error": "Permission denied", "success": False}

    # Get keypair for signing
    keypair = account_manager.get_keypair_for_signing(
        user_id=user_id,
        account_id=account_id,
        authorized_user_ids=authorized_user_ids
    )

    # ... rest of supply logic
```

Apply to all Blend tool functions:
- `_blend_supply_to_pool()`
- `_blend_withdraw_from_pool()`
- `_blend_check_my_positions()`
- etc.

Then update the tool wrappers in `tool_factory.py`:

```python
@tool
def blend_supply_to_pool(
    pool_address: str,
    asset_address: str,
    amount: float,
    account_id: str
):
    """Supply assets to Blend pool with dual authority."""
    # ... executor logic with authorized_user_ids injected
    return asyncio.run(
        _blend_supply_to_pool(
            pool_address=pool_address,
            asset_address=asset_address,
            amount=amount,
            account_id=account_id,
            user_id=user_id,
            authorized_user_ids=authorized_user_ids,  # Dual authority
            account_manager=account_mgr
        )
    )
```

## Expected Behavior After Implementation

### Agent Lists Accounts

When the agent runs:
```python
stellar_account_manager(action="list")
```

Result:
```json
{
  "accounts": [
    {
      "id": "account_xyz123",
      "address": "GA4KBIWEVNXJPT545A6YYZPZUFYHCG4LBDGN437PDRTBLGOE3KIW5KBZ",
      "balance": 1.285703,
      "owner_context": "agent",
      "owner_user_id": "system_agent",
      "name": "System Agent Account"
    },
    {
      "id": "account_abc456",
      "address": "GBUXXMSYQ43HAM5HVHXI5RKSO4UWWVSATODGE534QLHYKOI3CXK2WNSM",
      "balance": 0,
      "owner_context": "user",
      "owner_user_id": "user_789",
      "name": "User's Account"
    }
  ],
  "count": 2,
  "success": true
}
```

### Agent Uses Its Own Account

The agent can now:
```python
# Use agent's funded account for trading
stellar_trading(
    action="buy",
    account_id="account_xyz123",  # Agent's account
    buying_asset="USDC",
    selling_asset="XLM",
    amount="10",
    price="0.1"
)
```

Permission check passes because:
- Account `account_xyz123` belongs to `user_id="system_agent"`
- Agent context has `authorized_user_ids=["system_agent", "user_789"]`
- `"system_agent" in authorized_user_ids` → ✅ Permission granted

### Agent Uses User Account

The agent can also:
```python
# Use user's account
stellar_account_manager(
    action="get",
    account_id="account_abc456"  # User's account
)
```

Permission check passes because:
- Account `account_abc456` belongs to `user_id="user_789"`
- Agent context has `authorized_user_ids=["system_agent", "user_789"]`
- `"user_789" in authorized_user_ids` → ✅ Permission granted

### Clear Visibility

The `owner_context` field helps the agent (and logs) understand ownership:
- `"agent"`: This is the AI agent's own account
- `"user"`: This is the current user's account

## Benefits

1. **No Tool Duplication**: Single set of tools works for both agent and user accounts
2. **Explicit Authority**: `AgentContext` makes dual authority explicit and auditable
3. **Backward Compatible**: Existing single-user code still works (defaults to `[user_id]`)
4. **Granular Control**: Each operation validates permissions against authorized list
5. **Clear Ownership**: Accounts tagged with context for transparency
6. **Secure**: Permission checks validate against authorized list, no bypass possible
7. **Extensible**: Easy to add more authority contexts in future (e.g., team accounts)
8. **Agent Autonomy**: Agent can discover and use its own funded account seamlessly

## Implementation Checklist

- [ ] 1. Create `backend/agent/context.py` with `AgentContext` class
- [ ] 2. Update `backend/account_manager.py`:
  - [ ] Add `authorized_user_ids` parameter to `get_keypair_for_signing()`
  - [ ] Add `authorized_user_ids` parameter to `export_account()`
  - [ ] Add `authorized_user_ids` parameter to `delete_account()`
  - [ ] Add `authorized_user_ids` parameter to `user_owns_account()`
- [ ] 3. Update `backend/stellar_tools.py`:
  - [ ] Add `authorized_user_ids` parameter to `account_manager()`
  - [ ] Implement multi-user account listing in `action="list"`
  - [ ] Add `authorized_user_ids` parameter to `trading()`
  - [ ] Add `authorized_user_ids` parameter to `trustline_manager()`
  - [ ] Update permission checks in all functions
- [ ] 4. Update `backend/blend_account_tools.py`:
  - [ ] Add `authorized_user_ids` to all async functions
  - [ ] Update permission checks to use authorized list
- [ ] 5. Update `backend/agent/tool_factory.py`:
  - [ ] Change `create_user_tools()` signature to accept `AgentContext`
  - [ ] Update all tool wrappers to pass `authorized_user_ids`
  - [ ] Update `create_anonymous_tools()` to use `AgentContext`
- [ ] 6. Update route handlers (e.g., `backend/api/routes/chat.py`):
  - [ ] Create `AgentContext` from current user
  - [ ] Pass `AgentContext` to `create_user_tools()`
- [ ] 7. Test dual authority:
  - [ ] Agent can list and see both agent and user accounts
  - [ ] Agent can use its own funded account for operations
  - [ ] Agent can use user accounts for operations
  - [ ] Permission checks work correctly
  - [ ] `owner_context` tagging is correct

## Testing Strategy

### Unit Tests

```python
# test_agent_context.py
def test_agent_context_authorized_users():
    ctx = AgentContext(user_id="user_123")
    assert ctx.get_authorized_user_ids() == ["system_agent", "user_123"]

def test_agent_context_has_permission():
    ctx = AgentContext(user_id="user_123")
    assert ctx.has_permission("system_agent") == True
    assert ctx.has_permission("user_123") == True
    assert ctx.has_permission("user_456") == False

def test_agent_context_account_types():
    ctx = AgentContext(user_id="user_123")
    assert ctx.is_agent_account("system_agent") == True
    assert ctx.is_user_account("user_123") == True
    assert ctx.is_user_account("system_agent") == False
```

### Integration Tests

```python
# test_dual_authority_integration.py
async def test_agent_can_list_both_accounts():
    """Agent should see both agent and user accounts"""
    agent_context = AgentContext(user_id="test_user")
    tools = create_user_tools(agent_context)

    # Find account manager tool
    account_tool = next(t for t in tools if t.name == "stellar_account_manager")

    # List accounts
    result = account_tool.invoke({"action": "list"})

    # Should include both agent and user accounts
    assert result["success"] == True
    assert result["count"] >= 1  # At least agent's account

    # Check for agent account
    agent_accounts = [a for a in result["accounts"] if a["owner_context"] == "agent"]
    assert len(agent_accounts) >= 1
    assert agent_accounts[0]["address"] == "GA4KBIWEVNXJPT545A6YYZPZUFYHCG4LBDGN437PDRTBLGOE3KIW5KBZ"

async def test_agent_can_use_agent_account():
    """Agent should be able to operate on its own account"""
    agent_context = AgentContext(user_id="test_user")
    # ... test agent operations on system_agent account

async def test_agent_can_use_user_account():
    """Agent should be able to operate on user account"""
    agent_context = AgentContext(user_id="test_user")
    # ... test agent operations on user account

async def test_permission_denied_for_unauthorized():
    """Agent should NOT be able to access other users' accounts"""
    agent_context = AgentContext(user_id="user_123")
    # ... attempt to access account owned by user_456
    # ... should get PermissionError
```

### Manual Testing

1. **Start backend** with `AGENT_STELLAR_SECRET` set
2. **Check logs** for agent account import:
   ```
   ✅ Agent account imported successfully: GA4KBIW...
   ```
3. **Chat with agent**: "List all your accounts"
4. **Verify response** includes agent's funded account with `owner_context: "agent"`
5. **Test operation**: "Check the balance of your funded account"
6. **Test trade**: "Use your funded account to buy USDC"

## Migration Path

### Phase 1: Add Dual Authority Support (Backward Compatible)

1. Create `AgentContext` class
2. Add `authorized_user_ids` parameters with defaults to `None`
3. Default behavior: `if authorized_user_ids is None: authorized_user_ids = [user_id]`
4. Test with existing routes (should work unchanged)

### Phase 2: Update Tool Factory

1. Update `create_user_tools()` to accept `AgentContext`
2. Keep backward compatibility wrapper:
   ```python
   def create_user_tools_legacy(user_id: str) -> List:
       """Backward compatible wrapper"""
       return create_user_tools(AgentContext(user_id=user_id))
   ```

### Phase 3: Update Route Handlers

1. Update routes to use `AgentContext`
2. Remove legacy wrappers

### Phase 4: Cleanup

1. Remove `authorized_user_ids=None` defaults (make required)
2. Remove legacy compatibility code

## Security Considerations

1. **Encryption Context**: Private keys are encrypted using the account's **owner** user_id, not the requester's user_id. When agent accesses a system_agent account, decryption uses `"system_agent"` as the key.

2. **Authorization is Explicit**: The `authorized_user_ids` list is created by trusted backend code (not by LLM or user input). The LLM cannot manipulate or expand its authority.

3. **Fail Closed**: If `authorized_user_ids` is somehow None or empty, permission checks fail.

4. **Audit Trail**: All operations log which user_id performed action on which account, making ownership clear.

5. **No Privilege Escalation**: User cannot gain access to other users' accounts through agent. Agent context is scoped per-request to that user.

## Future Extensions

### Multi-User Teams

Could extend to support team accounts:
```python
class TeamAgentContext(AgentContext):
    def __init__(self, user_id: str, team_id: Optional[str] = None):
        super().__init__(user_id)
        self.team_id = team_id

    def get_authorized_user_ids(self) -> List[str]:
        base = super().get_authorized_user_ids()
        if self.team_id:
            # Add all team members
            team_members = get_team_members(self.team_id)
            base.extend(team_members)
        return base
```

### Delegated Authority Scopes

Could add granular permissions:
```python
class ScopedAgentContext(AgentContext):
    def __init__(self, user_id: str, scopes: List[str]):
        super().__init__(user_id)
        self.scopes = scopes  # e.g., ["read", "trade", "admin"]

    def can_perform_action(self, action: str) -> bool:
        # Check if action is allowed by scopes
        pass
```

## References

- **Original Issue**: Agent cannot access pre-funded account (`GA4KBIW...`)
- **Root Cause**: User isolation prevents agent from seeing `system_agent` accounts
- **Solution**: Delegated authority pattern with `AgentContext`
- **Implementation**: See checklist above

## Questions & Answers

**Q: Why not just make the agent account a special global account?**
A: That would bypass the security model and make it hard to audit. Explicit authority via `AgentContext` is clearer and more secure.

**Q: What happens if two users are chatting at the same time?**
A: Each request gets its own `AgentContext` scoped to that user. No cross-contamination.

**Q: Can a user access another user's accounts through the agent?**
A: No. The `AgentContext` is created server-side with only `["system_agent", current_user_id]`. The LLM cannot modify this list.

**Q: Why tag accounts with `owner_context`?**
A: Makes it clear to the agent (and in logs) which accounts belong to whom. Helps with transparency and debugging.

**Q: Does this break existing code?**
A: No. The `authorized_user_ids` parameter defaults to `None`, which falls back to single-user behavior: `[user_id]`.

---

**Status**: Ready for implementation
**Priority**: High (blocks agent from using its funded account)
**Effort**: Medium (requires updates across multiple layers)
**Risk**: Low (backward compatible with gradual migration path)
