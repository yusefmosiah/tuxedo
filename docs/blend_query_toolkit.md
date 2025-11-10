# Blend Query Toolkit: Comprehensive Implementation Guide

**Status**: Research Complete
**Date**: 2025-11-10
**Goal**: Enable efficient querying of Blend Capital pools using direct Soroban RPC calls

---

## Executive Summary

### The Problem

Our agent can discover Blend pools but **cannot retrieve yield data** (APY, reserves, positions). When querying the `get_reserve()` contract function via simulation, we receive "Account not found" errors, resulting in all APY queries returning 0%.

**Error Example from Chat Logs**:
```
❌ Error getting APY: Failed to get reserve APY: Failed to get reserve data: Account not found
⚠️ No yield opportunities found for XLM with APY above 0.0% on mainnet
```

### The Root Cause

We're using **contract function simulation** (`simulate` action in `stellar_soroban.py`) which requires building and simulating a transaction. This approach:
- Requires a funded account for simulation
- Is slower (multiple RPC calls)
- Less reliable for read-only queries
- Not how the official Blend SDK works

### The Solution

Implement **direct ledger entry queries** using `getLedgerEntries` RPC method, matching the Blend SDK's approach:
1. Construct ledger keys for reserve data
2. Fetch multiple entries in a single RPC call
3. Parse reserve configuration and data directly
4. Calculate APY from on-chain rates

**Benefits**:
- No account required for queries
- Single RPC call for multiple reserves
- Faster and more efficient
- Matches official SDK patterns

---

## Current State Analysis

### What Works ✅

1. **Pool Discovery** (`blend_discover_pools`):
   - Hardcoded pool addresses (Comet, Fixed, YieldBlox)
   - Returns active pool information

2. **Account Management**:
   - Agent has its own mainnet account
   - Can view its XLM balance
   - AccountManager integration working

3. **Transaction Operations** (Untested but implemented):
   - Supply collateral framework
   - Withdraw collateral framework
   - Position checking framework

### What's Broken ❌

1. **Reserve APY Queries**:
   - `blend_get_reserve_apy` fails with "Account not found"
   - Uses `simulate` action which requires funded accounts
   - Returns 0% APY for all assets

2. **Best Yield Finder**:
   - Depends on APY queries
   - Returns "No yield opportunities found"
   - Can't provide meaningful recommendations

3. **Position Checking**:
   - May work for funded accounts but untested
   - Also uses `simulate` which is suboptimal

### Technical Debt

**File**: `backend/blend_pool_tools.py:415-536`

```python
# Current broken approach
result = await soroban_operations(
    action="simulate",  # ❌ This is the problem
    contract_id=pool_address,
    function_name="get_reserve",
    parameters=parameters,
    account_id=account_id,  # ❌ Requires account
    ...
)
```

**Issues**:
1. Creates temporary read-only accounts unnecessarily
2. Simulates a transaction that will never be submitted
3. Prone to "Account not found" errors
4. Not aligned with Blend SDK patterns

---

## How Blend SDK Works (The Right Way)

### Architecture Overview

The official Blend SDK ([blend-sdk-js](https://github.com/blend-capital/blend-sdk-js)) uses **direct ledger queries** via `getLedgerEntries`:

```typescript
// From: blend-sdk-js/src/pool/pool_metadata.ts
static async load(network, poolId) {
  // Construct ledger keys for contract instance and reserve list
  const ledgerKeys = [
    contractInstance.ledgerKey(),
    reserveListKey(poolId, 'ResList')
  ];

  // Single RPC call to fetch multiple entries
  const response = await network.getLedgerEntries(...ledgerKeys);

  // Parse entries and return metadata
  return new PoolMetadata(...);
}
```

### Ledger Entry Types

Blend stores data in **CONTRACT_DATA** ledger entries with specific keys:

1. **Pool Configuration**:
   - Key: `SCV_LEDGER_KEY_CONTRACT_INSTANCE`
   - Contains: Pool admin, backstop rate, oracle, max positions

2. **Reserve List** (`ResList`):
   - Key: `Symbol("ResList")`
   - Contains: Array of reserve asset addresses

3. **Reserve Configuration** (`ResConfig`):
   - Key: `Symbol("ResConfig")` + asset address
   - Contains: c_factor, l_factor, util, decimals, etc.

4. **Reserve Data** (`ResData`):
   - Key: `Symbol("ResData")` + asset address
   - Contains: **b_rate**, **d_rate**, b_supply, d_supply, interest rates

### Reserve Loading Process

```typescript
// From: blend-sdk-js/src/pool/reserve.ts
static async load(network, poolId, assetId) {
  const ledgerKeys = [
    ReserveConfig.ledgerKey(poolId, assetId),  // ResConfig
    ReserveData.ledgerKey(poolId, assetId),    // ResData
    // ... emission configs
  ];

  const response = await network.getLedgerEntries(...ledgerKeys);

  // Parse each entry by decoding its key type
  response.entries.forEach(entry => {
    const keyType = decodeEntryKey(entry.key);
    switch(keyType) {
      case 'ResConfig': config = ReserveConfig.fromLedgerEntryData(entry);
      case 'ResData': data = ReserveData.fromLedgerEntryData(entry);
      // ...
    }
  });

  return new Reserve(config, data, ...);
}
```

### APY Calculation

**From Reserve Data**:
```typescript
// b_rate = supply rate (what suppliers earn)
// d_rate = borrow rate (what borrowers pay)

const supplyRate = reserve.data.bRate / 1e7;  // Stellar uses 7 decimals
const supplyAPR = supplyRate;
const supplyAPY = ((1 + supplyAPR / 365) ** 365 - 1) * 100;

const borrowRate = reserve.data.dRate / 1e7;
const borrowAPR = borrowRate;
const borrowAPY = ((1 + borrowAPR / 365) ** 365 - 1) * 100;
```

**Key Fields**:
- `b_supply`: Total supplied in protocol tokens
- `d_supply`: Total borrowed in protocol tokens
- `b_rate`: Conversion rate for bTokens (supply/collateral)
- `d_rate`: Conversion rate for dTokens (liabilities)
- Interest accrual adjusts these rates over time

---

## Technical Deep Dive: getLedgerEntries vs Contract Calls

### Method Comparison

| Aspect | getLedgerEntries (SDK Way) | Contract Simulation (Current) |
|--------|---------------------------|------------------------------|
| **Speed** | Single RPC call | Multiple calls (load account, simulate, parse) |
| **Account Required** | No | Yes (even for reads) |
| **Efficiency** | Batch fetch multiple entries | One query at a time |
| **Reliability** | Direct storage access | Prone to simulation errors |
| **SDK Pattern** | ✅ Matches official SDK | ❌ Custom approach |
| **Cost** | Minimal | Higher (account state queries) |

### Stellar Python SDK: getLedgerEntries

**Method Signature**:
```python
from stellar_sdk.soroban_server_async import SorobanServerAsync

async def get_ledger_entries(
    self,
    keys: List[stellar_xdr.LedgerKey]
) -> GetLedgerEntriesResponse
```

**Return Type**:
```python
class GetLedgerEntriesResponse:
    entries: List[LedgerEntryResult]  # Optional
    latest_ledger: int

class LedgerEntryResult:
    key: str          # XDR string of the ledger key
    xdr: str          # XDR string of the ledger entry data
    last_modified_ledger_seq: int
    live_until_ledger_seq: int  # TTL
```

### Constructing Ledger Keys in Python

**Contract Instance Key**:
```python
from stellar_sdk import xdr, Address

def make_contract_instance_key(contract_id: str) -> xdr.LedgerKey:
    return xdr.LedgerKey(
        type=xdr.LedgerEntryType.CONTRACT_DATA,
        contract_data=xdr.LedgerKeyContractData(
            contract=Address(contract_id).to_xdr_sc_address(),
            key=xdr.SCVal(xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
            durability=xdr.ContractDataDurability.PERSISTENT
        )
    )
```

**Symbol Key (for ResConfig, ResData, ResList)**:
```python
from stellar_sdk import scval

def make_contract_data_key(
    contract_id: str,
    symbol: str,
    durability: str = "PERSISTENT"
) -> xdr.LedgerKey:
    return xdr.LedgerKey(
        type=xdr.LedgerEntryType.CONTRACT_DATA,
        contract_data=xdr.LedgerKeyContractData(
            contract=Address(contract_id).to_xdr_sc_address(),
            key=scval.to_symbol(symbol),
            durability=getattr(xdr.ContractDataDurability, durability)
        )
    )
```

**Usage Example**:
```python
# Fetch reserve list and multiple reserves
ledger_keys = [
    make_contract_data_key(pool_id, "ResList"),
    make_contract_data_key(pool_id, "ResConfig_USDC"),  # Example key pattern
    make_contract_data_key(pool_id, "ResData_USDC"),
]

response = await soroban_server.get_ledger_entries(ledger_keys)

for entry in response.entries:
    # Parse XDR data
    entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
    value = entry_data.contract_data.val
    native_value = scval.to_native(value)
    # ... process native_value
```

---

## Python Implementation Guide

### Step 1: Add New Soroban Action

**File**: `backend/stellar_soroban.py`

Add a new action called `get_ledger_entries`:

```python
async def soroban_operations(
    action: str,
    # ... existing params
    ledger_keys: Optional[List] = None,  # NEW PARAMETER
) -> Dict[str, Any]:
    """
    Actions:
        - "get_ledger_entries": Query multiple ledger entries (NEW)
        - "get_data": Query contract storage
        - "simulate": Simulate contract call
        - "invoke": Execute contract function
        - "get_events": Query contract events
    """
    try:
        if action == "get_ledger_entries":
            # NEW ACTION: Direct ledger entry queries
            if not ledger_keys:
                return {"error": "ledger_keys required for get_ledger_entries"}

            # Convert ledger keys from dict format to XDR LedgerKey objects
            xdr_keys = []
            for key_spec in ledger_keys:
                if key_spec["type"] == "contract_instance":
                    xdr_keys.append(
                        xdr.LedgerKey(
                            type=xdr.LedgerEntryType.CONTRACT_DATA,
                            contract_data=xdr.LedgerKeyContractData(
                                contract=Address(key_spec["contract_id"]).to_xdr_sc_address(),
                                key=xdr.SCVal(xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
                                durability=xdr.ContractDataDurability.PERSISTENT
                            )
                        )
                    )
                elif key_spec["type"] == "contract_data":
                    xdr_keys.append(
                        xdr.LedgerKey(
                            type=xdr.LedgerEntryType.CONTRACT_DATA,
                            contract_data=xdr.LedgerKeyContractData(
                                contract=Address(key_spec["contract_id"]).to_xdr_sc_address(),
                                key=scval.to_symbol(key_spec["key"]),
                                durability=getattr(
                                    xdr.ContractDataDurability,
                                    key_spec.get("durability", "PERSISTENT")
                                )
                            )
                        )
                    )

            # Execute query
            response = await soroban_server.get_ledger_entries(xdr_keys)

            # Parse results
            entries = []
            for entry_result in response.entries:
                entry_data = xdr.LedgerEntryData.from_xdr(entry_result.xdr)

                entries.append({
                    "key_xdr": entry_result.key,
                    "value": scval.to_native(entry_data.contract_data.val),
                    "last_modified_ledger": entry_result.last_modified_ledger_seq,
                    "live_until_ledger": entry_result.live_until_ledger_seq
                })

            return {
                "success": True,
                "entries": entries,
                "latest_ledger": response.latest_ledger,
                "count": len(entries)
            }

        # ... existing actions (get_data, simulate, invoke, get_events)
```

### Step 2: Create Ledger Key Helper Functions

**File**: `backend/blend_pool_tools.py` (add new section)

```python
from stellar_sdk import xdr, Address, scval
from typing import Dict, Any, List

# ============================================================================
# LEDGER KEY CONSTRUCTION HELPERS
# ============================================================================

def make_reserve_config_key(pool_address: str, asset_address: str) -> Dict[str, Any]:
    """
    Construct ledger key for Reserve Configuration.

    Storage key pattern: Symbol("ResConfig") with asset context
    Note: The actual key structure may need verification from contract code
    """
    return {
        "type": "contract_data",
        "contract_id": pool_address,
        "key": f"ResConfig_{asset_address}",  # May need adjustment
        "durability": "PERSISTENT"
    }


def make_reserve_data_key(pool_address: str, asset_address: str) -> Dict[str, Any]:
    """
    Construct ledger key for Reserve Data (includes b_rate, d_rate).

    Storage key pattern: Symbol("ResData") with asset context
    """
    return {
        "type": "contract_data",
        "contract_id": pool_address,
        "key": f"ResData_{asset_address}",  # May need adjustment
        "durability": "PERSISTENT"
    }


def make_reserve_list_key(pool_address: str) -> Dict[str, Any]:
    """
    Construct ledger key for Reserve List (all assets in pool).

    Storage key: Symbol("ResList")
    """
    return {
        "type": "contract_data",
        "contract_id": pool_address,
        "key": "ResList",
        "durability": "PERSISTENT"
    }


def make_pool_config_key(pool_address: str) -> Dict[str, Any]:
    """
    Construct ledger key for Pool Configuration.

    Uses contract instance key.
    """
    return {
        "type": "contract_instance",
        "contract_id": pool_address
    }
```

### Step 3: Rewrite Reserve APY Query

**File**: `backend/blend_pool_tools.py:415-536`

Replace the broken `blend_get_reserve_apy` function:

```python
async def blend_get_reserve_apy(
    pool_address: str,
    asset_address: str,
    user_id: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Get real APY data for a reserve using direct ledger entry queries.

    NEW APPROACH: Uses getLedgerEntries instead of contract simulation.
    No account required, single RPC call, matches Blend SDK pattern.
    """
    try:
        logger.info(f"Fetching reserve data for {asset_address[:8]}... from pool {pool_address[:8]}...")

        # Construct ledger keys for this reserve
        ledger_keys = [
            make_reserve_data_key(pool_address, asset_address),
            make_reserve_config_key(pool_address, asset_address),
        ]

        # Query ledger entries directly (NO ACCOUNT NEEDED!)
        result = await soroban_operations(
            action="get_ledger_entries",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            ledger_keys=ledger_keys,
            network_passphrase=NETWORK_CONFIG['passphrase']
        )

        if not result.get('success') or not result.get('entries'):
            raise ValueError(f"Failed to get reserve data: {result.get('error', 'No entries returned')}")

        # Parse entries by key pattern
        reserve_data = None
        reserve_config = None

        for entry in result['entries']:
            value = entry['value']
            # The key information is in entry['key_xdr'] but we can infer from structure
            if 'b_rate' in value and 'd_rate' in value:
                reserve_data = value
            elif 'c_factor' in value or 'l_factor' in value:
                reserve_config = value

        if not reserve_data:
            raise ValueError("Reserve data not found in ledger entries")

        # Extract rates (Stellar uses 7 decimals = 1e7 scale)
        b_rate = reserve_data.get('b_rate', 0)
        d_rate = reserve_data.get('d_rate', 0)

        # Calculate APY from rates
        supply_rate = b_rate / 1e7
        supply_apr = supply_rate
        supply_apy = ((1 + supply_apr / 365) ** 365 - 1) * 100

        borrow_rate = d_rate / 1e7
        borrow_apr = borrow_rate
        borrow_apy = ((1 + borrow_apr / 365) ** 365 - 1) * 100

        # Calculate metrics
        total_supplied = reserve_data.get('b_supply', 0)
        total_borrowed = reserve_data.get('d_supply', 0)
        available = total_supplied - total_borrowed
        utilization = total_borrowed / total_supplied if total_supplied > 0 else 0

        # Get asset symbol (this can stay as-is or be optimized)
        asset_symbol = await _get_asset_symbol(
            asset_address, soroban_server, account_manager, user_id, network=network
        )

        logger.info(f"✅ Reserve {asset_symbol}: Supply APY = {supply_apy:.2f}%, Utilization = {utilization:.1%}")

        return {
            'asset_address': asset_address,
            'asset_symbol': asset_symbol,
            'supply_apy': round(supply_apy, 2),
            'borrow_apy': round(borrow_apy, 2),
            'total_supplied': total_supplied,
            'total_borrowed': total_borrowed,
            'utilization': round(utilization, 4),
            'available_liquidity': available,
            'data_source': 'ledger_entries',
            'latest_ledger': result.get('latest_ledger')
        }

    except Exception as e:
        logger.error(f"Error in blend_get_reserve_apy: {e}")
        raise ValueError(f"Failed to get reserve APY: {str(e)}")
```

### Step 4: Optimize Reserve List Query

**File**: `backend/blend_pool_tools.py:267-320`

Replace `_get_pool_reserves` to use ledger queries:

```python
async def _get_pool_reserves(
    pool_address: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    user_id: str,
    network: str = "mainnet"
) -> List[Dict[str, Any]]:
    """
    Get list of reserves from pool using direct ledger query.

    NEW APPROACH: Queries ResList storage key directly.
    Falls back to hardcoded reserves if query fails.
    """
    try:
        # Try to query ResList from ledger
        ledger_keys = [make_reserve_list_key(pool_address)]

        result = await soroban_operations(
            action="get_ledger_entries",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            ledger_keys=ledger_keys,
            network_passphrase=NETWORK_CONFIG['passphrase']
        )

        if result.get('success') and result.get('entries'):
            # Parse reserve list
            reserve_addresses = result['entries'][0]['value']

            reserves = []
            for asset_address in reserve_addresses:
                # Get symbol for each asset
                symbol = await _get_asset_symbol(
                    asset_address, soroban_server, account_manager, user_id, network=network
                )
                reserves.append({
                    'address': asset_address,
                    'symbol': symbol
                })

            logger.info(f"✅ Loaded {len(reserves)} reserves from ledger for pool {pool_address[:8]}...")
            return reserves

        # Fallback to hardcoded if query fails
        logger.warning(f"Failed to query ResList, using hardcoded reserves")

    except Exception as e:
        logger.warning(f"Error querying reserve list: {e}, using hardcoded reserves")

    # Fallback: Use hardcoded known reserves
    if pool_address in POOL_KNOWN_RESERVES:
        reserves = []
        for symbol, address in POOL_KNOWN_RESERVES[pool_address]:
            reserves.append({
                'address': address,
                'symbol': symbol
            })
        logger.info(f"Using {len(reserves)} hardcoded reserves for pool {pool_address[:8]}...")
        return reserves

    logger.error(f"No reserve data available for pool {pool_address}")
    return []
```

---

## Implementation Plan

### Phase 1: Core Infrastructure ✅

**Files to Modify**:
1. `backend/stellar_soroban.py` - Add `get_ledger_entries` action
2. `backend/blend_pool_tools.py` - Add ledger key helpers

**Tasks**:
- [x] Research complete
- [ ] Implement `get_ledger_entries` in `stellar_soroban.py`
- [ ] Add ledger key construction helpers
- [ ] Add unit tests for key construction

**Testing**:
```python
# Test ledger key construction
key = make_reserve_data_key(BLEND_MAINNET_CONTRACTS['comet'], BLEND_MAINNET_CONTRACTS['usdc'])
assert key['type'] == 'contract_data'
assert 'ResData' in key['key']
```

### Phase 2: Reserve APY Queries 🎯

**Files to Modify**:
1. `backend/blend_pool_tools.py:415-536` - Rewrite `blend_get_reserve_apy`

**Tasks**:
- [ ] Replace simulation-based query with ledger entry query
- [ ] Verify storage key patterns against actual contract
- [ ] Test APY calculation logic
- [ ] Handle missing/malformed data

**Testing**:
```python
# Test APY query
apy_data = await blend_get_reserve_apy(
    pool_address=BLEND_MAINNET_CONTRACTS['comet'],
    asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
    user_id='test_user',
    soroban_server=server,
    account_manager=manager,
    network='mainnet'
)

assert apy_data['supply_apy'] > 0
assert 'b_rate' in reserve_data
assert 'data_source' == 'ledger_entries'
```

### Phase 3: Reserve List Optimization

**Files to Modify**:
1. `backend/blend_pool_tools.py:267-320` - Optimize `_get_pool_reserves`

**Tasks**:
- [ ] Query ResList from ledger
- [ ] Parse reserve addresses
- [ ] Maintain hardcoded fallback
- [ ] Cache results for efficiency

### Phase 4: Position Queries

**Files to Modify**:
1. `backend/blend_pool_tools.py:761-876` - Optimize `blend_get_my_positions`

**Tasks**:
- [ ] Evaluate if ledger entries can replace simulation
- [ ] Keep simulation if required for user-specific data
- [ ] Document why simulation is needed (if it is)

### Phase 5: Integration Testing

**Create**: `backend/test_blend_ledger_queries.py`

```python
import asyncio
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import (
    blend_get_reserve_apy,
    blend_find_best_yield,
    BLEND_MAINNET_CONTRACTS,
    NETWORK_CONFIG
)

async def test_reserve_apy():
    """Test direct ledger query for reserve APY"""
    server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    manager = AccountManager()

    result = await blend_get_reserve_apy(
        pool_address=BLEND_MAINNET_CONTRACTS['comet'],
        asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
        user_id='system',
        soroban_server=server,
        account_manager=manager,
        network='mainnet'
    )

    print(f"✅ USDC Supply APY: {result['supply_apy']:.2f}%")
    print(f"✅ USDC Borrow APY: {result['borrow_apy']:.2f}%")
    print(f"✅ Utilization: {result['utilization']:.1%}")
    assert result['supply_apy'] > 0, "Supply APY should be positive"
    print("✅ Test passed!")

if __name__ == '__main__':
    asyncio.run(test_reserve_apy())
```

---

## Storage Key Discovery

### Critical Unknown: Exact Storage Key Format

**What We Know**:
- Blend contracts store data with symbol keys
- SDK uses `ResConfig`, `ResData`, `ResList` patterns
- Keys include asset context somehow

**What We Need to Verify**:
- Exact key format for asset-specific data
- Is it `"ResData_" + asset_address`?
- Or `"ResData"` with asset in a separate parameter?
- Or tuple/map structure?

### Discovery Methods

**Method 1: Inspect SDK Source Code**
```bash
# Clone Blend SDK
git clone https://github.com/blend-capital/blend-sdk-js
cd blend-sdk-js

# Find storage key construction
grep -r "ResData" src/
grep -r "ResConfig" src/
grep -r "ledgerKey" src/
```

**Method 2: Query Existing Contracts**
```python
# Try different key patterns
patterns = [
    f"ResData_{asset_address}",
    f"ResData",
    ("ResData", asset_address),  # Tuple
]

for pattern in patterns:
    try:
        result = await query_ledger(pattern)
        if result:
            print(f"✅ Found data with pattern: {pattern}")
            break
    except:
        continue
```

**Method 3: Inspect Contract Source**
```bash
# Check Blend contracts
https://github.com/blend-capital/blend-contracts-v2/blob/main/pool/src/storage.rs
# Look for reserve storage functions
```

### Recommended Approach

1. Start with simple symbol keys: `"ResData"`, `"ResConfig"`
2. If that fails, try asset-qualified keys: `"ResData_{asset}"`
3. Examine contract storage in stellar.expert
4. Use Stellar CLI to inspect ledger entries:
   ```bash
   stellar contract read \
     --id <POOL_ID> \
     --durability persistent \
     --network mainnet
   ```

---

## Code Examples

### Complete Working Example

```python
#!/usr/bin/env python3
"""
Complete example: Query Blend pool reserve APY using ledger entries
"""
import asyncio
from stellar_sdk import xdr, Address, scval
from stellar_sdk.soroban_server_async import SorobanServerAsync

# Configuration
COMET_POOL = "CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM"
USDC_TOKEN = "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75"
RPC_URL = "https://rpc.ankr.com/stellar_soroban"

async def query_reserve_apy():
    server = SorobanServerAsync(RPC_URL)

    # Construct ledger keys
    keys = [
        xdr.LedgerKey(
            type=xdr.LedgerEntryType.CONTRACT_DATA,
            contract_data=xdr.LedgerKeyContractData(
                contract=Address(COMET_POOL).to_xdr_sc_address(),
                key=scval.to_symbol("ResData"),  # Try this first
                durability=xdr.ContractDataDurability.PERSISTENT
            )
        )
    ]

    # Query ledger
    response = await server.get_ledger_entries(keys)

    if not response.entries:
        print("❌ No entries found - need to adjust key pattern")
        return

    # Parse response
    for entry in response.entries:
        entry_data = xdr.LedgerEntryData.from_xdr(entry.xdr)
        value = scval.to_native(entry_data.contract_data.val)

        print(f"✅ Found reserve data:")
        print(f"   b_rate: {value.get('b_rate', 'N/A')}")
        print(f"   d_rate: {value.get('d_rate', 'N/A')}")
        print(f"   b_supply: {value.get('b_supply', 'N/A')}")
        print(f"   d_supply: {value.get('d_supply', 'N/A')}")

        # Calculate APY
        if 'b_rate' in value:
            b_rate = value['b_rate']
            supply_rate = b_rate / 1e7
            supply_apy = ((1 + supply_rate / 365) ** 365 - 1) * 100
            print(f"   📈 Supply APY: {supply_apy:.2f}%")

    await server.close()

if __name__ == '__main__':
    asyncio.run(query_reserve_apy())
```

---

## Testing Strategy

### Unit Tests

**File**: `backend/tests/test_blend_ledger_keys.py`
```python
def test_reserve_data_key_construction():
    key = make_reserve_data_key("POOL123", "ASSET456")
    assert key['type'] == 'contract_data'
    assert key['contract_id'] == "POOL123"
    assert 'ResData' in key['key']

def test_reserve_config_key_construction():
    key = make_reserve_config_key("POOL123", "ASSET456")
    assert key['durability'] == 'PERSISTENT'
```

### Integration Tests

**File**: `backend/tests/test_blend_integration_ledger.py`
```python
@pytest.mark.asyncio
async def test_usdc_apy_query_mainnet():
    """Test real mainnet USDC APY query"""
    result = await blend_get_reserve_apy(
        pool_address=BLEND_MAINNET_CONTRACTS['comet'],
        asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
        user_id='test',
        soroban_server=test_server,
        account_manager=test_manager,
        network='mainnet'
    )

    assert result['success']
    assert result['supply_apy'] > 0
    assert result['data_source'] == 'ledger_entries'
    assert 'latest_ledger' in result
```

### Manual Testing

```bash
# 1. Test new soroban action
cd backend
source .venv/bin/activate
python3 -c "
import asyncio
from stellar_soroban import soroban_operations
# ... test get_ledger_entries
"

# 2. Test APY query
python3 test_blend_ledger_queries.py

# 3. Test in agent
python3 test_agent_with_tools.py
# Ask: "What's the APY for USDC in the Comet pool?"

# 4. Test in UI
npm run dev
# Connect wallet, ask agent about yields
```

---

## Expected Outcomes

### Before (Current State)
```
User: "What's the best APY for USDC?"

Agent: blend_find_best_yield
❌ Error getting APY: Account not found
⚠️ No yield opportunities found for USDC with APY above 0.0%
```

### After (With Ledger Queries)
```
User: "What's the best APY for USDC?"

Agent: blend_find_best_yield
✅ Found reserve data for USDC in Comet Pool
✅ Supply APY: 8.45%
✅ Borrow APY: 12.30%
✅ Utilization: 68.5%

🌟 Found 3 yield opportunities for USDC on Blend Capital:

1. Comet Pool
   💰 APY: 8.45%
   💧 Available Liquidity: 1,234,567 USDC
   📊 Utilization: 68.5%
   ...
```

---

## Troubleshooting

### Issue: "No entries found"

**Possible Causes**:
1. Wrong storage key format
2. Asset not in this pool
3. Contract data expired (TTL)
4. RPC endpoint issues

**Solutions**:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Try alternative key patterns
keys_to_try = [
    scval.to_symbol("ResData"),
    scval.to_symbol(f"ResData:{asset_address}"),
    scval.to_symbol(f"Res_{asset_address}_Data"),
]

for key in keys_to_try:
    result = await query_with_key(key)
    if result: break
```

### Issue: "Invalid XDR"

**Solution**: Verify XDR version compatibility
```python
from stellar_sdk import __version__
print(f"stellar-sdk version: {__version__}")
# Should be >= 13.1.0
```

### Issue: "TTL expired"

**Solution**: Check live_until_ledger
```python
if entry.live_until_ledger_seq < current_ledger:
    print("⚠️ Entry expired, needs restoration")
    # Use contract getter as fallback
```

---

## Next Steps

### Immediate Actions
1. ✅ **Research Complete**: This document
2. **Implement**: `get_ledger_entries` in `stellar_soroban.py`
3. **Discover**: Verify exact storage key patterns
4. **Rewrite**: `blend_get_reserve_apy` function
5. **Test**: Integration tests with mainnet
6. **Deploy**: Update agent tools

### Future Enhancements
1. **Caching**: Cache reserve data with TTL
2. **Batch Queries**: Fetch all reserves in single call
3. **Pool Metadata**: Query pool config from ledger
4. **Emissions**: Add BLND emission APY
5. **Historical**: Track APY changes over time

### Questions to Answer
- [ ] Exact storage key format for ResData/ResConfig?
- [ ] Are positions stored in ledger or computed?
- [ ] How to handle multiple asset indices?
- [ ] TTL management strategy?
- [ ] Error handling for missing data?

---

## References

### Documentation
- [Blend Integration Docs](https://docs.blend.capital/tech-docs/integrations/integrate-pool)
- [Stellar getLedgerEntries](https://developers.stellar.org/network/soroban-rpc/methods/getLedgerEntries)
- [Soroban Storage Guide](https://developers.stellar.org/docs/learn/fundamentals/contract-development/storage/persisting-data)

### Source Code
- [blend-sdk-js](https://github.com/blend-capital/blend-sdk-js)
- [blend-contracts-v2](https://github.com/blend-capital/blend-contracts-v2)
- [stellar-sdk Python](https://github.com/StellarCN/py-stellar-base)

### Related Files
- `backend/stellar_soroban.py` - Soroban operations handler
- `backend/blend_pool_tools.py` - Blend pool operations
- `backend/blend_account_tools.py` - LangChain tool wrappers

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Status**: Ready for Implementation
**Author**: Claude Agent Research Team
