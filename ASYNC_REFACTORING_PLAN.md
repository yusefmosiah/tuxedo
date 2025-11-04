# Async Refactoring Plan for DeFindex Tools

## Problem Statement

Currently, the `discover_high_yield_vaults` tool works but uses synchronous operations, which violates architectural best practices for a FastAPI async application and could cause blocking issues under load.

## Root Cause Analysis

The real issue is **not** that we need sync operations - it's that our tool execution logic in `agent/core.py` doesn't properly handle LangChain `StructuredTool` objects where `.func` is `None`.

## Architectural Best Practices

### 1. **Keep Async Operations** ✅
- Soroban operations should remain async
- Network calls should be non-blocking
- All tool execution should be async-native
- FastAPI applications should be fully async to prevent blocking

### 2. **Fix the Real Problem: Tool Execution Logic**
The issue is in `agent/core.py` lines 274-277. Instead of accessing `tool.func` directly, we should use LangChain's proper invocation methods.

### 3. **Proper Async Tool Invocation Pattern**

From the LangChain documentation, the correct pattern is:
```python
# For async tools - use ainvoke
result = await tool.ainvoke(tool_args)

# For sync tools - use invoke
result = tool.invoke(tool_args)
```

## Current State Analysis

### What Works Now
- ✅ `discover_high_yield_vaults` tool executes successfully
- ✅ Returns real vault data with APYs and TVL
- ✅ Integrates with SSE streaming system
- ✅ No functional errors

### What's Architecturally Wrong
- ❌ Uses sync `SorobanServer` instead of async `SorobanServerAsync`
- ❌ Blocks the event loop during network calls
- ❌ Goes against FastAPI async best practices
- ❌ Could cause performance issues under load

## Implementation Plan

### Phase 1: Restore Async Foundation
1. **Revert `defindex_soroban.py`** to use async `create_soroban_client_with_ssl`
2. **Import async dependencies** properly
3. **Update class initialization** to handle async clients

### Phase 2: Fix Tool Execution Logic
1. **Update `agent/core.py`** tool execution logic
2. **Prioritize `tool.ainvoke()`** for async tools
3. **Fallback to `tool.invoke()`** for sync tools
4. **Remove direct `.func` access** pattern

### Phase 3: Ensure Proper Async Tool Design
1. **Verify all DeFindex tools** are properly async
2. **Update tool functions** to use async/await
3. **Handle async context managers** correctly
4. **Test async tool execution**

### Phase 4: Testing & Validation
1. **Test same query**: "Call the discover_high_yield_vaults tool with min_apy parameter set to 30"
2. **Verify functionality** remains identical
3. **Check performance** under load
4. **Validate no blocking** occurs

## Technical Implementation Details

### Step 1: Restore Async Soroban Client
```python
# defindex_soroban.py
from stellar_ssl import create_soroban_client_with_ssl

class DeFindexSoroban:
    def __init__(self, network: str = "mainnet"):
        if network == "mainnet":
            self.soroban = create_soroban_client_with_ssl("https://mainnet.stellar.expert/explorer/rpc")
        else:
            self.soroban = create_soroban_client_with_ssl("https://soroban-testnet.stellar.org")
```

### Step 2: Fix Tool Execution Logic
```python
# agent/core.py
if hasattr(tool_func, 'ainvoke') and callable(tool_func.ainvoke):
    # Modern LangChain async tool
    result = await tool_func.ainvoke(tool_args)
elif hasattr(tool_func, 'invoke') and callable(tool_func.invoke):
    # Modern LangChain sync tool
    result = tool_func.invoke(tool_args)
elif hasattr(tool_func, 'func') and tool_func.func is not None:
    # Legacy tool with func attribute
    if asyncio.iscoroutinefunction(tool_func.func):
        result = await tool_func.func(**tool_args)
    else:
        result = tool_func.func(**tool_args)
```

### Step 3: Update Tool Functions
```python
# defindex_tools.py
@tool
async def discover_high_yield_vaults(min_apy: Optional[float] = 30.0) -> str:
    defindex = get_defindex_soroban(network='mainnet')
    vaults_data = await defindex.get_available_vaults(min_apy=min_apy)
    # ... rest of implementation
```

## Success Criteria

1. ✅ **Functionality**: Tool works exactly as it does now
2. ✅ **Performance**: No blocking of event loop
3. ✅ **Architecture**: Follows FastAPI async best practices
4. ✅ **Maintainability**: Clean, readable async code
5. ✅ **Reliability**: No race conditions or async issues

## Risk Mitigation

### Low Risk
- Changes are well-understood async patterns
- LangChain has robust async support
- Current functionality is preserved

### Rollback Plan
- If issues arise, revert to current sync implementation
- Current sync version works as a safety net
- No breaking changes to external APIs

## Next Steps

1. **Commit current working state** to git
2. **Implement Phase 1**: Restore async foundation
3. **Implement Phase 2**: Fix tool execution logic
4. **Implement Phase 3**: Update tool functions
5. **Implement Phase 4**: Test and validate
6. **Deploy and monitor** performance

---

**Date**: November 4, 2025
**Author**: AI Assistant
**Status**: Planning Complete