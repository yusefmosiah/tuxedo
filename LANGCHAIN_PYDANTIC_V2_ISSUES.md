# LangChain Pydantic v2 Compatibility Issues

## Problem Summary

The agent-first architecture implementation is failing due to Pydantic v2 JSON schema generation errors when LangChain tries to convert Stellar tools to OpenAI function format.

## Error Details

### Primary Error

```
Cannot generate a JsonSchema for core_schema.IsInstanceSchema (<class 'key_manager.KeyManager'>)

For further information visit https://errors.pydantic.dev/2.12/u/invalid-for-json-schema
```

### Secondary Error

```
Arg key_manager in docstring not found in function signature.
```

## Root Cause Analysis

### 1. Custom Class Type Annotations

The Stellar tools use `KeyManager` as a parameter type in function signatures:

```python
def account_manager(
    action: str,
    horizon: Server,
    key_manager: KeyManager,  # ← This causes the schema generation error
    ...
) -> Dict[str, Any]:
```

LangChain's `convert_to_openai_function` uses Pydantic to generate JSON schemas from function signatures. Pydantic v2 cannot serialize custom classes like `KeyManager` that are not Pydantic models.

### 2. Docstring Parameter Mismatch

The function docstrings have parameter descriptions that don't match the actual function signature order, causing validation errors:

```python
# Function signature:
def account_manager(action, key_manager, horizon, ...)

# Docstring expects:
Args:
    action: Operation to perform
    key_manager: KeyManager instance
    horizon: Horizon server instance
    # But the parsing is failing due to the KeyManager type issue
```

### 3. LangChain Architecture Pattern

The current system attempts to directly import and use existing Stellar functions as LangChain tools:

```python
# In agent/core.py line 68:
from stellar_tools import account_manager, trading, trustline_manager, market_data, utilities
agent_tools.extend([account_manager, trading, trustline_manager, market_data, utilities])
```

This approach works for simple functions but fails when:

- Functions have custom class type annotations
- Functions have complex parameter dependencies
- Docstrings don't perfectly match signatures

## Current Status

### Working Components

- ✅ Agent-first frontend architecture (ChatInterface, Dashboard, AgentProvider)
- ✅ Backend agent initialization and LLM setup
- ✅ Agent account management tools (properly wrapped with @tool decorator)
- ✅ DeFindex vault tools (properly wrapped with @tool decorator)
- ✅ Health endpoints and basic API functionality
- ✅ 25 pre-existing agent accounts available

### Failing Components

- ❌ Stellar tools (account_manager, trading, trustline_manager, market_data, utilities)
- ❌ Soroban operations tool
- ❌ Chat endpoint functionality due to tool loading failure

## Files Affected

### Backend Files

- `backend/stellar_tools.py` - Contains 5 composite tools with KeyManager dependencies
- `backend/stellar_soroban.py` - Soroban operations tool with KeyManager dependency
- `backend/agent/core.py` - Tool loading and conversion logic
- `backend/key_manager.py` - Custom class causing schema generation issues

### attempted Fixes Applied

1. **Removed KeyManager type annotations** - Fixed primary error but revealed secondary docstring mismatch error
2. **Fixed docstring parameter order** - Still encountering validation issues
3. **Syntax corrections** - Fixed indentation errors during editing

## Architectural Considerations

### Current Architecture Issues

1. **Tight Coupling**: Stellar tools are tightly coupled to KeyManager class
2. **Mixed Responsibilities**: Tools handle both business logic and key management
3. **Schema Generation Complexity**: Complex function signatures with custom types
4. **Documentation Mismatch**: Docstrings not aligned with actual function signatures

### Design Principles to Consider

1. **Single Responsibility**: Tools should focus on their specific domain
2. **Dependency Injection**: Dependencies should be injected, not passed as parameters
3. **Schema-First Design**: Function signatures should be schema-compatible from the start
4. **Proper Abstractions**: Clean separation between LangChain tools and Stellar operations

## Potential Solutions (Research Needed)

### Option 1: Proper LangChain Tool Wrappers

Create dedicated @tool decorated wrappers that handle KeyManager internally:

```python
@tool
def stellar_account_manager(action: str, account_id: Optional[str] = None, ...) -> Dict[str, Any]:
    """Stellar account management operations."""
    key_manager = KeyManager()  # Instantiate internally
    horizon = Server(HORIZON_URL)
    return account_manager(action, key_manager, horizon, account_id, ...)
```

**Pros**: Clean separation, proper schema generation
**Cons**: Code duplication, maintenance overhead

### Option 2: Refactor Stellar Functions

Make KeyManager a global singleton or inject it differently:

```python
# Instead of passing as parameter, use global or context
key_manager = KeyManager()  # Global instance

def account_manager(action: str, horizon: Server, ...):  # No key_manager parameter
    # Use global key_manager
```

**Pros**: Cleaner function signatures
**Cons**: Global state, testing complexity

### Option 3: Pydantic Model Integration

Convert KeyManager to a proper Pydantic model or create Pydantic schemas for tool parameters:

```python
class ToolParameters(BaseModel):
    action: str
    account_id: Optional[str] = None
    # ... other parameters
```

**Pros**: Proper schema generation
**Cons**: Major refactoring effort

### Option 4: Alternative LangChain Patterns

Research if LangChain has other patterns for handling complex dependencies or if there are better ways to integrate existing functions.

## Next Steps

1. **Research Phase**: Investigate LangChain best practices for complex tool integration
2. **Architecture Review**: Evaluate which solution aligns best with system architecture
3. **Implementation**: Apply chosen solution with proper testing
4. **Documentation**: Update architectural documentation

## Technical Debt

This issue reveals underlying technical debt in the Stellar tools layer:

- Functions were designed for direct use, not for AI agent integration
- Key management is mixed with business logic
- Lack of schema-first design consideration

Addressing this properly will improve maintainability and enable better AI agent capabilities.

## Impact Assessment

### High Priority

- Chat functionality completely broken
- Agent cannot access Stellar blockchain features
- Core value proposition of AI agent + Stellar integration unavailable

### Medium Priority

- Frontend agent-first architecture complete but unusable
- Agent account management works but limited without Stellar tools

### Low Priority

- Non-Stellar features (DeFindex, agent account creation) still functional
