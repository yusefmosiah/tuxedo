# ⚡ Quick Start - Pool Discovery

## 30 Second Setup

### 1. Ensure Dev Server is Running
```bash
npm run dev
# Should show: http://localhost:5173/ (or 5174)
```

### 2. Open in Browser
http://localhost:5173/

### 3. Click Button
"🔍 Discover All Pools & Tokens"

### 4. Wait & View Results
Wait 10-30 seconds, then see:
- All pool addresses found
- All tokens in each pool
- Total token count

---

## What You'll See

### Console (F12 → Console tab)
Real-time discovery progress:
```
🔍 [Strategy 1] Loading pools from Backstop reward zone...
  ✅ Discovered 3 pool(s)
📦 Loading tokens for pool 1...
  ✅ Found 5 tokens
📦 Loading tokens for pool 2...
  ✅ Found 4 tokens
📦 Loading tokens for pool 3...
  ✅ Found 3 tokens
✅ Total: 3 pools, 12 unique tokens
```

### Web Page
**Pools Section**: List of all discovered pools with token count
**Tokens Section**: Grid of all unique token addresses

---

## Expected Output

### Pools Found
- **Comet Pool**: `CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4...` (5 tokens)
- **Pool 2**: `CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX...` (4 tokens)
- **Pool 3**: `CYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY...` (3 tokens)

### Tokens (Examples)
- `CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU` (USDC)
- `CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK6A2JN3HEX56T2EDAFO7QF` (BLND)
- `CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC` (XLM)
- ... (9 more)

---

## Copy Token List for Next Phase

After discovery completes, you have the exhaustive list of all testnet tokens:

1. Copy all token addresses from the page
2. Use for next phase: **Create comprehensive token metadata**
3. Map each address to proper symbol, name, decimals, icon

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Page blank | Wait 5-10 seconds, refresh browser |
| Button doesn't work | Check console (F12) for errors |
| Takes >30 seconds | Normal (network latency), be patient |
| Shows 0 pools | Check network status, try again |
| Shows only 1 pool | Check Backstop has only 1 active |
| Console errors | See POOL_DISCOVERY_GUIDE.md |

---

## What's Next?

After discovery completes:

### Phase 1: Token Metadata
Map all discovered tokens to proper names:
```
CAQCFVLOBK5G... → USDC (6 decimals)
CB22KRA3YZVC... → BLND (7 decimals)
...
```

### Phase 2: USD Pricing
Show values in USD instead of units:
```
Total Supplied: 1,234,567.89 USDC → $1,234,567.89
```

### Phase 3: Full Dashboard
Display all pools with complete stats

---

## Detailed Docs

- **Full Guide**: [POOL_DISCOVERY_GUIDE.md](./POOL_DISCOVERY_GUIDE.md)
- **Implementation**: [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Project Status**: [DASHBOARD_STATUS.md](./DASHBOARD_STATUS.md)

---

## Key Files

| File | Purpose |
|------|---------|
| `src/utils/poolDiscovery.ts` | Discovery engine |
| `src/pages/PoolDiscoveryDebug.tsx` | Discovery UI |
| `src/hooks/useBlendPools.ts` | Pool loading hook |

---

**Time to Run Discovery**: 10-30 seconds ⏱️
**Complexity**: Simple - one button click ✨
**Result**: Exhaustive list of all pools and tokens 🎉
