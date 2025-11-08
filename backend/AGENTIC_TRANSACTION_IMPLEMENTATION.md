# Agentic Transaction Implementation Plan

## Overview

Enable autonomous "deposit 1000 XLM to vault" transactions by integrating DeFindex tools into the established tool_factory pattern with user_id injection and AccountManager integration.

## Current State Analysis

### ✅ What Works

- **tool_factory.py**: Established pattern for user_id injection from auth middleware
- **AccountManager**: Encrypted private key storage with user isolation
- **Agent Core**: Multi-step reasoning with LangChain tool selection
- **DeFindex Tools**: Basic functions exist but are DISABLED and NOT integrated

### 🚨 Current Problems

1. **Global Tool Loading**: DeFindex tools loaded globally in `agent/core.py` without user_id
2. **Disabled Execution**: `execute_defindex_deposit()` returns error message
3. **Missing Integration**: DeFindex tools not in tool_factory pattern
4. **Wrong Parameters**: Tools expect `user_address` instead of using AccountManager

## Implementation Plan

### Step 1: Integrate DeFindex Tools into Tool Factory

**File**: `backend/agent/tool_factory.py`

**Current Issue**:

```python
# WRONG - Global loading in agent/core.py
from defindex_tools import execute_defindex_deposit
```

**Solution**: Add DeFindex tools to `create_user_tools()` function:

```python
@tool
def defindex_discover_vaults(min_apy: Optional[float] = 0.0):
    """Discover DeFindex vaults sorted by APY"""
    return _defindex_discover_vaults(
        min_apy=min_apy,
        user_id=user_id  # INJECTED from auth
    )

@tool
def defindex_get_vault_details(vault_address: str):
    """Get detailed information about a DeFindex vault"""
    return _defindex_get_vault_details(
        vault_address=vault_address,
        user_id=user_id  # INJECTED from auth
    )

@tool
def defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    account_id: str  # User's account ID from AccountManager
):
    """Execute autonomous deposit to DeFindex vault using user's account"""
    return _defindex_deposit(
        vault_address=vault_address,
        amount_xlm=amount_xlm,
        user_id=user_id,  # INJECTED from auth
        account_id=account_id,
        account_manager=account_mgr
    )
```

### Step 2: Create Backend Functions with AccountManager Integration

**File**: `backend/defindex_account_tools.py` (new file)

Create new backend functions that work with AccountManager:

```python
async def _defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_id: str,
    account_id: str,
    account_manager: AccountManager
) -> str:
    """Execute deposit using user's account from AccountManager"""
    try:
        # 1. Get user's account (private key access)
        user_account = account_manager.get_account(user_id, account_id)

        # 2. Build transaction via DeFindex API
        client = get_defindex_client(network='testnet')
        amount_stroops = int(amount_xlm * 10_000_000)

        tx_data = client.build_deposit_transaction(
            vault_address=vault_address,
            amount_stroops=amount_stroops,
            caller=user_account['public_key'],
            invest=True
        )

        # 3. Sign with user's private key
        unsigned_xdr = tx_data.get('xdr')
        signed_tx = account_manager.sign_transaction(
            user_id=user_id,
            account_id=account_id,
            transaction_xdr=unsigned_xdr
        )

        # 4. Submit transaction
        result = client.submit_transaction(signed_tx)

        return f"✅ **Deposit Successful**\nHash: {result['hash']}\nAmount: {amount_xlm} XLM"

    except Exception as e:
        return f"❌ **Deposit Failed**: {str(e)}"
```

### Step 3: Remove Global DeFindex Tool Loading

**File**: `backend/agent/core.py`

**Remove**:

```python
# REMOVE - Lines 96-118
from defindex_tools import (
    discover_high_yield_vaults,
    get_defindex_vault_details,
    prepare_defindex_deposit,
    execute_defindex_deposit,
    execute_defindex_withdrawal
)
```

**Replace with**: Load from tool_factory in authenticated routes only

### Step 4: Update Tool Factory to Include DeFindex Tools

**File**: `backend/agent/tool_factory.py`

Add to `create_user_tools()` return value:

```python
# Return list of tools with user_id injected
tools = [
    stellar_account_manager,
    stellar_trading,
    stellar_trustline_manager,
    stellar_market_data,
    stellar_utilities,
    # NEW - DeFindex tools with user_id injection
    defindex_discover_vaults,
    defindex_get_vault_details,
    defindex_deposit
]
```

### Step 5: Test Implementation

**Test Strategy**:

1. **Unit Tests**: Test each DeFindex tool function individually
2. **Integration Tests**: Test tool factory creates tools correctly
3. **End-to-End Test**: Full "deposit to vault" conversation flow
4. **Security Test**: Verify user isolation works correctly

**Test File**: `backend/test_agentic_transactions.py`

```python
async def test_defindex_tool_factory_integration():
    """Test DeFindex tools in tool_factory pattern"""
    from agent.tool_factory import create_user_tools

    tools = create_user_tools("test_user_123")

    # Verify tools were created
    tool_names = [t.name for t in tools]
    assert "defindex_discover_vaults" in tool_names
    assert "defindex_deposit" in tool_names

    # Test actual tool execution
    result = await tools[-1].ainvoke({
        "vault_address": TESTNET_VAULTS['XLM_HODL_1'],
        "amount_xlm": 10.0,
        "account_id": "test_account_1"
    })

    print("Tool execution result:", result)
```

## Security Considerations

### ✅ Built-in Security

- **User Isolation**: user_id from auth middleware, not from LLM
- **TEE Protection**: Private keys in AccountManager with TEE encryption
- **Permission Boundaries**: Tools can only access authenticated user's accounts
- **Audit Trail**: All actions logged with user_id context

### 🛡️ Additional Safeguards

- **Transaction Limits**: Consider implementing max deposit amounts
- **Error Handling**: Graceful failure modes for insufficient funds
- **Validation**: Vault address validation against known testnet vaults
- **Rate Limiting**: Prevent rapid successive transactions

## Implementation Files

### Files to Modify:

1. `backend/agent/tool_factory.py` - Add DeFindex tools
2. `backend/agent/core.py` - Remove global DeFindex loading
3. `backend/defindex_tools.py` - Remove old disabled code (optional)

### Files to Create:

1. `backend/defindex_account_tools.py` - New AccountManager-integrated functions
2. `backend/test_agentic_transactions.py` - Comprehensive tests

## Expected Outcome

After implementation, users will be able to have conversations like:

```
User: "Deposit 100 XLM to vault CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"

Agent Flow:
1. Use defindex_get_vault_details to verify vault
2. Use stellar_account_manager to check user balance
3. Use defindex_deposit to execute transaction
4. Return transaction hash and confirmation
```

## Deployment Notes

### Phala Deployment Ready

- ✅ TEE-compatible encryption
- ✅ User isolation pattern
- ✅ Auth middleware integration
- ✅ No hardcoded credentials

### Rollback Plan

If issues arise, can quickly revert by:

1. Restoring global tool loading in agent/core.py
2. Commenting out DeFindex tools in tool_factory
3. No database changes required (safe deployment)

## Success Metrics

1. ✅ **Tool Integration**: DeFindex tools appear in authenticated tool sets
2. ✅ **Transaction Success**: Real deposits execute successfully
3. ✅ **User Isolation**: Each user can only access their own accounts
4. ✅ **Error Handling**: Graceful failures for insufficient funds, invalid vaults
5. ✅ **Performance**: Tool response time < 5 seconds

## Timeline

- **Phase 1** (Today): Integration and enablement
- **Phase 2** (Today): Testing and validation
- **Phase 3** (Tomorrow): Phala deployment with working agentic transactions

This implementation provides the foundation for autonomous DeFi transactions while maintaining security and user isolation appropriate for Phala Network deployment.
