# Blend Pools Dashboard - Implementation Plan

## 🎯 Goal
Create a comprehensive dashboard showing all active Blend pools on testnet with real-time stats for each pool.

## 📊 What We Need to Display

### Per Pool
1. **Pool Identity**
   - Pool name/ID
   - Contract address
   - Pool status (active/paused)

2. **Asset Composition**
   - List of supported assets (USDC, XLM, BLND, etc.)
   - Asset icons/symbols
   - Number of reserves

3. **TVL (Total Value Locked)**
   - Total supplied across all assets
   - Total borrowed across all assets
   - Net TVL (supplied - borrowed)
   - USD values (requires oracle price data)

4. **Interest Rates (Per Asset)**
   - Supply APY (%)
   - Borrow APY (%)
   - Visual indicators (color-coded)

5. **Utilization**
   - Per-asset utilization rate
   - Overall pool utilization
   - Progress bars/charts

6. **Additional Metrics**
   - Collateral factors
   - Liability factors
   - Available liquidity per asset
   - Emission rewards (if any)

---

## 🏗️ Technical Architecture

### Data Layer

#### 1. Pool Discovery
```typescript
// Get all pools from Pool Factory
PoolFactoryContract.deployed(factory_id: string) → string[]

// For each pool address:
PoolV2.load(network, poolAddress) → Pool
```

#### 2. Pool Data Loading
```typescript
interface Pool {
  id: string;                        // Contract address
  metadata: PoolMetadata;            // Pool name, etc.
  reserves: Map<string, Reserve>;    // Asset ID → Reserve data
  timestamp: number;                 // Last update
}

interface Reserve {
  assetId: string;                   // Token contract address
  config: ReserveConfig;             // Collateral/liability factors
  data: ReserveData;                 // Balances, indexes, etc.
  borrowApr: number;                 // Already calculated!
  estBorrowApy: number;             // Already calculated!
  supplyApr: number;                 // Already calculated!
  estSupplyApy: number;             // Already calculated!
  borrowEmissions?: Emissions;       // BLND rewards
  supplyEmissions?: Emissions;       // BLND rewards
}

interface ReserveData {
  b_rate: bigint;                    // Supply rate
  d_rate: bigint;                    // Borrow rate
  b_supply: bigint;                  // Total supplied (scaled)
  d_supply: bigint;                  // Total borrowed (scaled)
  ir_mod: number;                    // Interest rate modifier
  // ... more fields
}
```

#### 3. Data Flow
```
1. Query Pool Factory → Get all pool addresses
2. For each pool:
   a. Load Pool (PoolV2.load) → Gets all reserves automatically
   b. For each reserve in pool.reserves:
      - Asset ID
      - Supply/Borrow amounts
      - APY (already calculated)
      - Utilization
   c. Load token metadata (symbol, decimals, icon)
3. Cache results (5-10 second refresh)
```

---

## 🎨 UI Architecture

### Component Structure

```
<BlendPoolsDashboard>
  ├── <DashboardHeader>
  │   ├── Total TVL across all pools
  │   ├── Number of active pools
  │   └── Refresh button
  │
  ├── <PoolFilters>
  │   ├── Search by name/asset
  │   ├── Sort by (TVL, APY, utilization)
  │   └── Filter by asset type
  │
  └── <PoolsList>
      └── <PoolCard> (repeated for each pool)
          ├── <PoolHeader>
          │   ├── Pool name
          │   ├── Contract address (shortened)
          │   └── Status badge
          │
          ├── <PoolStats>
          │   ├── TVL
          │   ├── Total supplied
          │   ├── Total borrowed
          │   └── # of assets
          │
          └── <ReservesList>
              └── <ReserveRow> (for each asset)
                  ├── Asset icon & symbol
                  ├── Supply APY (green)
                  ├── Borrow APY (orange)
                  ├── Utilization bar
                  └── Available liquidity
```

### Layout Options

**Option A: Grid Layout**
```
┌──────────┬──────────┬──────────┐
│  Pool 1  │  Pool 2  │  Pool 3  │
│  ────────│  ────────│  ────────│
│  Stats   │  Stats   │  Stats   │
│  Assets  │  Assets  │  Assets  │
└──────────┴──────────┴──────────┘
```

**Option B: List Layout** (Recommended for detail)
```
┌─────────────────────────────────┐
│ Pool 1 - Comet (BLND:USDC)      │
│ ─────────────────────────────── │
│ │Asset│ Supply APY│Borrow APY │ │
│ │USDC │   5.2%    │   8.7%    │ │
│ │BLND │   12.3%   │   15.1%   │ │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ Pool 2 - ...                    │
└─────────────────────────────────┘
```

---

## 🔧 Implementation Phases

### Phase 1: Data Fetching Foundation
**Files to create:**
1. `src/hooks/useBlendPools.ts` - Fetch all pools
2. `src/hooks/usePoolData.ts` - Fetch single pool details
3. `src/utils/blend-helpers.ts` - Helper functions for calculations
4. `src/types/blend.ts` - TypeScript interfaces

**Key challenges:**
- Pool Factory query for all pools
- Batch loading multiple pools efficiently
- Token metadata fetching (symbols, decimals)
- Price data from oracle (for USD values)

### Phase 2: Basic Dashboard UI
**Files to create:**
1. `src/components/dashboard/PoolsDashboard.tsx` - Main container
2. `src/components/dashboard/PoolCard.tsx` - Individual pool
3. `src/components/dashboard/ReserveRow.tsx` - Asset row
4. `src/components/dashboard/PoolStats.tsx` - Stats display

**Features:**
- Display pool name and address
- Show reserves with APY
- Basic styling with Stellar Design System

### Phase 3: Advanced Features
**Enhancements:**
1. Real-time price data from oracle
2. USD value calculations
3. Charts (TVL over time, APY history)
4. Sorting and filtering
5. Search functionality
6. User position highlights (if wallet connected)

### Phase 4: Performance & Polish
**Optimizations:**
- Data caching strategy
- Debounced refresh
- Loading skeletons
- Error handling and retry logic
- Responsive design
- Mobile optimization

---

## 📝 Complexity Analysis

### High Complexity Areas

#### 1. **Asset Metadata** ⚠️ MEDIUM-HIGH
- Need to fetch token symbols, decimals, icons
- May require additional contract calls
- **Solution**: Cache token metadata, use lookup table

#### 2. **Price Data** ⚠️ HIGH
- Oracle contract queries for each asset
- Need to convert asset amounts to USD
- Oracle might have different price sources
- **Solution**: Query pool oracle once, batch asset prices

#### 3. **Scaled Values** ⚠️ MEDIUM
- Reserve amounts are scaled by supply/borrow rates
- Need to convert to actual token amounts
- **Formula**: `actual = scaled * rate / SCALAR`
- **Solution**: SDK provides helper methods

#### 4. **Multiple Pools** ⚠️ HIGH
- Loading 5-10 pools = many RPC calls
- Could hit rate limits
- **Solution**:
  - Load sequentially with delays
  - Implement caching
  - Show loading states per pool

#### 5. **Interest Rate Calculations** ✅ LOW
- SDK already calculates APR and APY!
- `reserve.estSupplyApy` and `reserve.estBorrowApy`
- **No extra work needed**

### Low Complexity Areas ✅

1. **Pool Discovery**: Simple factory query
2. **Pool Loading**: SDK provides `PoolV2.load()`
3. **Reserve Data**: Already included in Pool object
4. **APY Display**: Pre-calculated by SDK
5. **Utilization**: SDK provides `getUtilizationFloat()`

---

## 🎯 Minimum Viable Dashboard (MVP)

### Must-Have Features
1. ✅ Display all active pools
2. ✅ Show pool name and address
3. ✅ List assets in each pool
4. ✅ Display Supply/Borrow APY
5. ✅ Show utilization percentage
6. ✅ Loading states
7. ✅ Error handling

### Nice-to-Have (v2)
- USD values
- Charts and graphs
- Historical data
- User positions
- Sorting/filtering
- Real-time updates (websockets)

---

## 🚀 Implementation Checklist

### Step 1: Data Layer
- [ ] Create `useBlendPools` hook to fetch all pools
- [ ] Create `usePoolDetails` hook for single pool
- [ ] Create token metadata cache/lookup
- [ ] Test data fetching with console logs

### Step 2: Basic UI
- [ ] Create `PoolsDashboard` component
- [ ] Create `PoolCard` component
- [ ] Create `ReserveRow` component
- [ ] Display pool data (no styling yet)

### Step 3: Styling
- [ ] Apply Stellar Design System
- [ ] Add responsive grid/list layout
- [ ] Color-code APY values
- [ ] Add loading skeletons
- [ ] Add error states

### Step 4: Advanced Features
- [ ] Add oracle price queries
- [ ] Calculate USD values
- [ ] Add sorting
- [ ] Add filtering
- [ ] Add search

### Step 5: Polish
- [ ] Performance optimization
- [ ] Mobile responsive
- [ ] Accessibility
- [ ] Documentation
- [ ] User testing

---

## ⏱️ Estimated Timeline

- **Phase 1 (Data)**: 2-3 hours
- **Phase 2 (Basic UI)**: 2-3 hours
- **Phase 3 (Advanced)**: 3-4 hours
- **Phase 4 (Polish)**: 2-3 hours

**Total**: 9-13 hours for full implementation

**MVP Only**: 4-6 hours (Phase 1 + Phase 2 + basic Phase 3)

---

## 🤔 Key Decisions Needed

1. **Layout**: Grid or List view? (Recommend: List for mobile, Grid option for desktop)
2. **Refresh Rate**: Manual button or auto-refresh? (Recommend: Manual + 30s auto)
3. **Price Data**: Show USD values or just token amounts? (Recommend: Start without USD, add later)
4. **Pools to Show**: All pools or only active ones? (Recommend: Filter to active by default)
5. **Default Sort**: By TVL, APY, or name? (Recommend: TVL descending)

---

## 📚 Resources & References

- **Blend SDK Docs**: https://github.com/blend-capital/blend-sdk-js
- **Pool Loading**: `PoolV2.load(network, poolAddress)`
- **Reserve Interface**: Already has APY calculated
- **Network Config**: Use existing `network` from `src/contracts/util.ts`

---

## 🐛 Potential Issues & Solutions

### Issue 1: RPC Rate Limiting
**Solution**: Add delays between pool loads, implement exponential backoff

### Issue 2: Large Data Volume
**Solution**: Pagination, lazy loading, virtual scrolling

### Issue 3: Stale Data
**Solution**: Add timestamp display, refresh button, optional auto-refresh

### Issue 4: Missing Token Metadata
**Solution**: Fallback to contract address, community token list

### Issue 5: Oracle Price Failures
**Solution**: Graceful degradation, show "Price unavailable"

---

## 🎉 Success Criteria

1. Dashboard loads all pools within 10 seconds
2. APY displayed accurately for all assets
3. Responsive on mobile and desktop
4. No crashes or unhandled errors
5. User can understand pool composition at a glance
6. Clear visual hierarchy
7. Accessible to screen readers

---

**Ready to start implementation?** Let me know which phase you'd like to tackle first!
