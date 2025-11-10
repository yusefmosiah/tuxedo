# Blend Query Fix - Implementation Summary

**Date**: 2025-11-10
**Branch**: `claude/work-in-progress-011CUygQekUW7DXN93rXkinT`
**Status**: ✅ Fixed and Ready for Testing

---

## Problem Statement

Blend query functionality was returning 0% APY for all reserves. Analysis of two experimental branches (`experimental/blend-query` and `claude/implement-blend-query-toolkit-011CUyfQDrttdJkVeGdAzDLh`) revealed the root causes.

## Root Causes

### 1. Incorrect Decimal Scaling (CRITICAL)
**Location**: `backend/blend_pool_tools.py:500, 506`

- **Problem**: Code was using 7 decimals (1e7) for rate conversion
- **Reality**: Blend v2 contracts use **12 decimals (1e12)** for b_rate and d_rate
- **Source**: [Blend v2 contracts - storage.rs](https://github.com/blend-capital/blend-contracts-v2/blob/main/pool/src/storage.rs)

```rust
// From Blend v2 source code:
pub struct ReserveData {
    pub d_rate: i128,  // 12 decimals - conversion rate from dToken to underlying
    pub b_rate: i128,  // 12 decimals - conversion rate from bToken to underlying
    ...
}
```

### 2. Account Creation Bug
**Location**: `backend/blend_pool_tools.py:471`

- **Problem**: `create_result['account']['id']` - incorrect nested access
- **Fix**: Changed to `create_result['account_id']` - matches AccountManager return structure

### 3. APY Calculation Logic
**Location**: `backend/blend_pool_tools.py:502, 508`

- **Problem**: b_rate/d_rate are cumulative exchange rates, not direct APR values
- **Fix**: Subtract 1 from the rate to get the interest component before calculating APY
- **Example**: If b_rate = 1.05e12, then actual APR = 0.05 (5%)

## Changes Made

### File: `backend/blend_pool_tools.py`

```python
# BEFORE (Incorrect - 7 decimals):
b_rate = reserve_data.get('b_rate', 0)
supply_rate = b_rate / 1e7
supply_apr = supply_rate
supply_apy = ((1 + supply_apr / 365) ** 365 - 1) * 100

# AFTER (Correct - 12 decimals with cumulative rate handling):
b_rate = reserve_data.get('b_rate', 0)
supply_rate = b_rate / 1e12
supply_apr = supply_rate - 1 if supply_rate > 1 else 0  # Extract interest component
supply_apy = ((1 + supply_apr / 365) ** 365 - 1) * 100
```

Same fix applied to d_rate (borrow rate).

### Account Creation Fix

```python
# BEFORE:
account_id = create_result['account']['id']

# AFTER:
account_id = create_result['account_id']
```

## Testing Status

### Test File Created
- `/home/user/tuxedo/backend/test_blend_query_fix.py`

### Current Limitation
Testing requires a **funded mainnet account** because:
1. `get_reserve()` is called via `simulate` action
2. Simulation requires loading account from Stellar network
3. Unfunded accounts don't exist on-chain yet

### Solution Options

**Option A** (Current): Use funded account for testing
- Simplest approach
- Works with production users who have funded accounts
- Just need to test with real funded account

**Option B** (Future): Implement `get_ledger_entries` approach
- No account required (read-only ledger queries)
- Requires discovering correct storage key patterns
- Attempted in experimental branch but storage keys were unclear

## Contract Function Verified

**Correct Function**: `get_reserve(asset: Address) -> Reserve`

- **Source**: [pool/src/contract.rs](https://github.com/blend-capital/blend-contracts-v2/blob/main/pool/src/contract.rs)
- **Returns**: Composite `Reserve` structure with `data` and `config` fields
- **Parameters**: Asset contract address

```rust
fn get_reserve(e: Env, asset: Address) -> Reserve {
    let pool_config = storage::get_pool_config(&e);
    Reserve::load(&e, &pool_config, &asset)
}
```

## Expected Impact

With these fixes:
1. ✅ APY queries should return **realistic positive values** (e.g., 5-15% for USDC)
2. ✅ best_yield finder will work correctly
3. ✅ Position tracking already works (uses `get_positions()`)
4. ✅ All Blend query toolkit features functional

## Next Steps

### For Testing
1. Use existing funded account OR fund a test account with minimum XLM (1 XLM)
2. Run: `python test_blend_query_fix.py`
3. Verify positive APY values returned

### For Production
1. Test with real user accounts (which are funded)
2. Monitor APY values for reasonableness (should match mainnet.blend.capital)
3. If issues persist, consider implementing get_ledger_entries approach

## References

- **Blend v2 Contracts**: https://github.com/blend-capital/blend-contracts-v2
- **Blend SDK**: https://github.com/blend-capital/blend-sdk-js
- **Blend Docs**: https://docs.blend.capital/tech-docs/integrations/integrate-pool
- **Experimental Branch Issues**: `origin/experimental/blend-query:docs/blend_query_issues.md`

## Key Learnings

1. **Always verify decimal scaling** - Different contracts use different precision (7 vs 12 decimals)
2. **Understand rate semantics** - Cumulative vs instantaneous rates require different calculations
3. **Contract source is truth** - When docs are unclear, read the contract source code
4. **Testing requires mainnet resources** - Simulations need on-chain accounts

---

**Status**: ✅ **Implementation Complete - Ready for Testing with Funded Account**
