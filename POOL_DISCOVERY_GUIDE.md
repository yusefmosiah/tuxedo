# 🔍 Pool Discovery Guide

## Overview

The pool discovery system exhaustively searches for all Blend pools on Stellar Testnet and catalogues all tokens used across them.

## How It Works

### Architecture

There are **3 discovery strategies** (in priority order):

1. **Backstop Reward Zone** (Primary)
   - Queries `Backstop.config.rewardZone` to get all active pools
   - Most reliable and matches official blend-ui approach
   - Single RPC call, no event pagination issues

2. **Pool Factory Events** (Disabled - Use for Research)
   - Scans Pool Factory deployment events
   - Finds all historically deployed pools
   - Slower and has ledger retention limitations
   - Can be re-enabled once fully tested

3. **Known Hardcoded Pools** (Fallback)
   - Comet pool (always available)
   - Add more as discovered

### Implementation Files

| File | Purpose |
|------|---------|
| `src/utils/poolDiscovery.ts` | Core discovery engine with multiple strategies |
| `src/pages/PoolDiscoveryDebug.tsx` | UI for running discovery and viewing results |
| `src/hooks/useBlendPools.ts` | React hook for loading pools in dashboard |

## Using the Discovery Tool

### Method 1: Web UI (Easiest)

1. **Open the app**: http://localhost:5174/
2. **Click button**: "🔍 Discover All Pools & Tokens"
3. **Wait**: Processing will take 10-30 seconds
4. **View results**:
   - Pool count and addresses
   - Tokens in each pool
   - Total unique tokens
   - Detailed console logs (F12)

### Method 2: Programmatic

```typescript
// Import the discovery utilities
import {
  discoverAllPools,
  generatePoolTokenReport,
  logPoolStats,
} from "../utils/poolDiscovery";

// In your code:
const pools = await discoverAllPools();
const report = await generatePoolTokenReport();
await logPoolStats();
```

## Output

### Console Output Example

```
🌊 === COMPREHENSIVE POOL DISCOVERY ===

🔍 [Strategy 1] Loading pools from Backstop reward zone...
  📊 Backstop loaded successfully
  📊 Backstop config: { rewardZoneCount: 3 }
  🏊 Pool 1: CCQ74HN...
  🏊 Pool 2: CXXXX...
  🏊 Pool 3: Cyyyy...
  ✅ Discovered 3 pool(s) from Backstop

📊 === DISCOVERY SUMMARY ===
  Backstop pools: 3
  Factory pools: 0 (disabled)
  Known pools: 1
  Total unique: 3

🎫 === TOKEN DISCOVERY ===

📦 Loading tokens for pool: CCQ74HN...
  ✅ Found 5 tokens:
    💰 CAQCFVLO... (USDC)
    💰 CB22KRA3... (BLND)
    ...

💰 TOKENS (All unique tokens across all pools)
Total unique tokens across all pools: 12
  1. CAQCFVLOBK5G...
  2. CB22KRA3YZV...
  ...
```

### Web UI Output

**Pool List**:
- Pool address and name
- Number of tokens per pool
- Token addresses

**Token Summary**:
- Grid of all unique token addresses
- Total count

## Common Issues

### Issue: Only 1 Pool Shows (Backstop Issue)

**Reason**: Backstop's reward zone contains only active earning pools

**Solution**:
1. This is expected if Blend only has 1 active pool
2. Check console logs to confirm Backstop is loading
3. Look for any pools in "paused" or "frozen" status

### Issue: Slow Discovery (20-30 seconds)

**Reason**: Loading multiple pools from network

**Solutions**:
1. This is normal - network latency + multiple RPC calls
2. Discovery only needs to run once
3. Results can be cached (future enhancement)

### Issue: Network Errors

**Possible Causes**:
- Stellar testnet RPC timeout
- Rate limiting
- Network connectivity

**Solutions**:
1. Check browser console (F12) for detailed error messages
2. Verify RPC URL in `src/contracts/util.ts` is correct
3. Try again after a few seconds
4. Check Stellar network status

## Data Structure

### PoolDiscoveryResult

```typescript
interface PoolDiscoveryResult {
  backstopPools: string[];     // From Backstop reward zone
  factoryPools: string[];      // From Pool Factory events
  knownPools: string[];        // Hardcoded fallback pools
  allPoolsUnique: string[];    // Deduplicated list of all pools
}
```

### PoolTokenReport

```typescript
interface PoolTokenReport {
  poolAddress: string;         // Pool contract address
  poolName: string;           // Pool display name
  tokens: TokenInfo[];        // Tokens in this pool
  tokenCount: number;         // Number of tokens
}
```

### TokenInfo

```typescript
interface TokenInfo {
  address: string;            // Token contract address
  symbol: string;             // Token symbol (inferred)
  decimals: number;           // Token decimals (default 7)
}
```

## Next Steps

### Phase 1: Expand Token Metadata ⚠️

Currently token metadata is minimal (only symbol = short address):

```typescript
// Current (bad)
symbol: "CAQCF"  // Just first 5 chars

// Needed (good)
symbol: "USDC"
name: "USD Coin"
decimals: 6
icon: "https://..."
```

**Action**:
1. Use discovery to get all token addresses
2. Create comprehensive token metadata lookup
3. Update `src/utils/tokenMetadata.ts`

### Phase 2: Add USD Pricing 💵

Display TVL and amounts in USD instead of raw units:

```typescript
// Current
totalSupplied: 1000000n units

// Needed
totalSupplied: "1,000,000.00 USDC"
totalSuppliedUSD: "$1,000,000.00"
```

**Action**:
1. Query pool oracle for token prices
2. Calculate USD values: `(amount / 10^decimals) * price`
3. Update dashboard UI to display $USD

### Phase 3: Update Dashboard 📊

Currently dashboard only shows Comet pool. Update to show all discovered pools:

```typescript
// In PoolsDashboard.tsx
// Replace:
const { pools } = useBlendPools();  // Currently shows only 1

// With logic to load all discovered pools
// Or enhance useBlendPools to use discovery utility
```

## Debugging

### Enable Detailed Logging

1. Open browser console (F12)
2. Click "🔍 Discover All Pools & Tokens"
3. Watch console output in real-time
4. Look for:
   - ✅ Success messages
   - ❌ Error messages with details
   - ⏳ Loading/waiting messages

### Check Raw Network Data

```typescript
// In poolDiscovery.ts, add:
console.log("Raw Backstop config:", backstop.config);
console.log("All reserves:", pool.reserves);
```

### Test Individual Functions

```javascript
// In browser console:
import { discoverAllPools } from './utils/poolDiscovery.js';
const result = await discoverAllPools();
console.log(result);
```

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Backstop load | 1-2s | Single RPC call |
| Load 1 pool | 2-3s | Multiple RPC calls per pool |
| Load 3-5 pools | 10-15s | Parallel loading |
| Load 10+ pools | 30-60s | Potential rate limiting |

**Optimization**:
- Results cached for 5-10 minutes
- Only re-query when specifically requested
- Show pools as they load (incremental UI)

## Files Modified

```
src/
├── utils/
│   └── poolDiscovery.ts              ← NEW: Discovery engine
├── pages/
│   └── PoolDiscoveryDebug.tsx         ← NEW: Discovery UI
├── hooks/
│   └── useBlendPools.ts               ← UPDATED: Added discovery
├── App.tsx                            ← UPDATED: Added route
└── pages/Home.tsx                     ← UPDATED: Added button
```

## Troubleshooting Checklist

- [ ] Browser console open (F12) before clicking discovery
- [ ] RPC URL is correct: `https://soroban-testnet.stellar.org`
- [ ] Stellar testnet is accessible
- [ ] No rate limiting errors in console
- [ ] Wait 10-30 seconds for discovery to complete
- [ ] Check console for specific error messages
- [ ] Try refreshing page and running again
- [ ] Check Stellar network status page

## Future Enhancements

1. **Caching**: Store results in localStorage with TTL
2. **Incremental Loading**: Show pools as they load
3. **Real-time Updates**: WebSocket connection for live data
4. **Export**: Download pool/token list as CSV/JSON
5. **Filtering**: Search, sort, filter by name/assets
6. **Historical Tracking**: Track pool/token changes over time

---

**Last Updated**: October 25, 2025
**Status**: Discovery system complete, token metadata incomplete
