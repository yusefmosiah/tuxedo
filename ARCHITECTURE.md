# Blend Pools Dashboard - Architecture Documentation

**Project**: Tuxedo - AI-Powered Blend Pools Discovery Dashboard
**Last Updated**: October 25, 2025
**Status**: Phase 1 Complete (Dashboard), Phase 2 In Progress (AI Chat)

---

## Overview

Tuxedo is a conversational interface for discovering and interacting with Blend Protocol lending pools on Stellar. Users can:
- View all active Blend pools with real-time APY rates
- Ask an AI assistant about yield opportunities and risks
- Execute trades (XLM → USDC) and deposits through natural language
- Track their positions and conversation history

---

## Technology Stack

### Frontend
- **Framework**: Vite 7.1 + React 19 + TypeScript 5.9
- **UI Library**: Stellar Design System 3.1
- **Routing**: React Router DOM 7.9
- **State Management**: React Query (TanStack Query) 5.90
- **Styling**: CSS Modules + Inline Styles

### Blockchain Integration
- **Stellar SDK**: @stellar/stellar-sdk 14.2.0
- **Blend SDK**: @blend-capital/blend-sdk 3.2.1
- **Wallet**: @creit.tech/stellar-wallets-kit 1.9.5 (Freighter support)

### AI & Backend Services (Planned)
- **LLM**: AWS Bedrock (Claude 3.5 Sonnet via @langchain/aws)
- **Framework**: LangChain.js (@langchain/core)
- **Database**: Supabase Cloud (PostgreSQL + Auth)
- **Schema Validation**: Zod 4.1

### Network Configuration
- **Primary Network**: Stellar Testnet (for transactions)
- **Display Data**: Mainnet pools (accurate APY rates)
- **RPC URL**: https://soroban-testnet.stellar.org
- **Horizon URL**: https://horizon-testnet.stellar.org

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (User)                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Vite + React Frontend                                │  │
│  │  ┌─────────────────┐  ┌──────────────────────────┐   │  │
│  │  │ Pool Dashboard  │  │  Chat Interface          │   │  │
│  │  │ (Phase 1 ✅)    │  │  (Phase 2 - In Progress) │   │  │
│  │  └─────────────────┘  └──────────────────────────┘   │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  Wallet Provider (Freighter)                    │ │  │
│  │  │  - signTransaction()                            │ │  │
│  │  │  - getAddress()                                 │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────┬──────────────────┬────────┘
               │                  │                  │
               │                  │                  │
       ┌───────▼──────┐   ┌──────▼─────────┐  ┌────▼────────┐
       │   Stellar    │   │  AWS Bedrock   │  │  Supabase   │
       │   Network    │   │  (Claude API)  │  │  Cloud      │
       │              │   │                │  │             │
       │ - Horizon    │   │ - LangChain    │  │ - Users     │
       │ - Soroban    │   │   Integration  │  │ - Convos    │
       │ - Blend SDK  │   │ - Tool Calling │  │ - Deposits  │
       └──────────────┘   └────────────────┘  └─────────────┘
```

---

## Core Components

### 1. Pool Discovery System

**File**: `src/hooks/useBlendPools.ts`

**How It Works**:
1. Load Backstop contract (`Backstop.load()`)
2. Query `config.rewardZone` array for active pool addresses
3. Load each pool with `PoolV2.load(network, address)`
4. Transform reserve data into UI-friendly format
5. Return pools with loading/error states

**Key Insight**: Uses Backstop.rewardZone instead of Pool Factory events (simpler, more reliable, matches official blend-ui approach)

```typescript
// Discovery Flow
const backstop = await Backstop.load(network, BLEND_CONTRACTS.backstop);
const poolAddresses = backstop.config.rewardZone; // Array of pool contract IDs

const pools = await Promise.all(
  poolAddresses.map(addr => PoolV2.load(network, addr))
);
```

**Data Structure**:
```typescript
interface BlendPoolData {
  id: string;                    // Pool contract address
  name: string;                  // Pool name (e.g., "Comet")
  metadata: PoolMetadata;        // Admin, oracle, status, etc.
  reserves: PoolReserve[];       // Array of assets in pool
  timestamp: number;             // Last update time
  totalReserves: number;         // Count of reserves
  status: 'active' | 'paused' | 'unknown';
}

interface PoolReserve {
  assetId: string;               // Contract address of asset
  config: ReserveConfig;         // Collateral factors, caps
  data: ReserveData;             // Balances, rates (scaled values)

  // Pre-calculated by Blend SDK (no math needed!)
  borrowApr: number;
  estBorrowApy: number;
  supplyApr: number;
  estSupplyApy: number;

  // Calculated values
  totalSupplied: bigint;         // Actual token amount
  totalBorrowed: bigint;
  availableLiquidity: bigint;
  utilization: number;           // 0-1 float

  // Optional emissions
  borrowEmissions?: Emissions;
  supplyEmissions?: Emissions;
}
```

### 2. Dashboard UI

**Main Components**:
- `PoolsDashboard.tsx` - Container with summary stats and refresh
- `PoolCard.tsx` - Individual pool display (expandable)
- `ReserveRow.tsx` - Asset row with APY, utilization, liquidity

**Features**:
- ✅ Real-time pool data from Backstop
- ✅ Expandable reserve details
- ✅ Color-coded APY (green=supply, orange/red=borrow)
- ✅ Utilization bars with dynamic colors
- ✅ Loading/error/empty states
- ✅ Refresh functionality
- ✅ Copy contract address to clipboard

### 3. Wallet Integration

**File**: `src/providers/WalletProvider.tsx`

**Capabilities**:
- Connect wallet (Freighter modal)
- Get user address and network
- Sign transactions (`signTransaction()`)
- Persistent connection (polls every 1s)
- Network detection (testnet/mainnet)

**Context API**:
```typescript
interface WalletContextType {
  address?: string;
  network?: string;
  networkPassphrase?: string;
  isPending: boolean;
  signTransaction?: (xdr: string, opts: SignOpts) => Promise<string>;
}
```

### 4. Token Metadata

**File**: `src/utils/tokenMetadata.ts`

**Provides**:
- Token lookup by contract address
- Amount formatting with decimals
- Compact number formatting (K/M/B)
- APY percentage formatting
- Color coding for APY and utilization

**Current Tokens**:
```typescript
const TOKEN_METADATA = {
  [BLEND_CONTRACTS.blndToken]: { symbol: "BLND", name: "Blend Token", decimals: 7 },
  [BLEND_CONTRACTS.usdcToken]: { symbol: "USDC", name: "USD Coin", decimals: 7 },
  [BLEND_CONTRACTS.xlmToken]: { symbol: "XLM", name: "Stellar Lumens", decimals: 7 },
};
```

---

## Blend Protocol Contracts (Testnet)

```typescript
export const BLEND_CONTRACTS = {
  // Core Protocol
  poolFactory: "CDSMKKCWEAYQW4DAUSH3XGRMIVIJB44TZ3UA5YCRHT6MP4LWEWR4GYV6",
  backstop:    "CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X",
  emitter:     "CCS5ACKIDOIVW2QMWBF7H3ZM4ZIH2Q2NP7I3P3GH7YXXGN7I3WND3D6G",

  // Tokens
  blndToken:   "CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK6A2JN3HEX56T2EDAFO7QF",
  usdcToken:   "CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU",
  xlmToken:    "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC",

  // Pools
  cometPool:   "CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF",
};
```

---

## Data Flow Examples

### Pool Discovery Flow
```
1. User loads dashboard
   ↓
2. useBlendPools() hook triggers
   ↓
3. Backstop.load(network, backstop_address)
   ↓
4. Extract backstop.config.rewardZone (array of pool addresses)
   ↓
5. Promise.all(addresses.map(addr => PoolV2.load(network, addr)))
   ↓
6. Transform each pool's reserves
   ↓
7. Update React state with pool data
   ↓
8. PoolsDashboard renders PoolCard components
   ↓
9. Each PoolCard renders ReserveRow components
```

### Transaction Signing Flow (Planned)
```
1. User: "Swap 10 XLM for USDC"
   ↓
2. LangChain receives message
   ↓
3. Claude decides to call swap_xlm_to_usdc tool
   ↓
4. Tool builds transaction using Stellar SDK
   ↓
5. Returns XDR to LangChain
   ↓
6. LangChain returns message: "Ready to sign [transaction details]"
   ↓
7. UI shows "Sign Transaction" button
   ↓
8. User clicks → signTransaction(xdr)
   ↓
9. Freighter wallet popup appears
   ↓
10. User approves → Signed XDR returned
   ↓
11. Frontend submits to Stellar network
   ↓
12. Poll for transaction status
   ↓
13. Show success message with transaction hash
```

---

## Key Technical Decisions

### ✅ Why Vite instead of Next.js?
- Faster dev server and HMR
- Simpler deployment (static site)
- No need for server-side rendering
- Better for blockchain apps (wallet signing happens client-side)

### ✅ Why No MCP Server?
**Original Plan**: Use Python MCP server for Stellar operations
**Problem**: Stdio transport doesn't work in browser
**Solution**: Use Stellar SDK + Blend SDK directly in TypeScript

**Benefits**:
- Simpler architecture (no bridge server needed)
- Better UX (direct wallet integration)
- Fewer failure points
- Easier to debug (single language)
- Faster execution (no IPC overhead)

### ✅ Why Backstop for Pool Discovery?
**Alternative Considered**: Query Pool Factory events
**Problem**: Event retention limited to 7 days, pagination complexity
**Solution**: Use Backstop.config.rewardZone

**Benefits**:
- Single RPC call instead of paginated event queries
- Always up-to-date with active pools
- Matches official blend-ui architecture
- No ledger range limitations

### ✅ Why Mainnet Display + Testnet Transactions?
- Mainnet has real liquidity and accurate APY rates
- Testnet has test assets for safe demos
- Show mainnet data but only allow testnet transactions
- Clear banner: "Demo Mode - Testnet Transactions Only"

---

## Project Structure

```
blend-pools/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── PoolsDashboard.tsx    # Main dashboard container
│   │   │   ├── PoolCard.tsx          # Individual pool display
│   │   │   └── ReserveRow.tsx        # Asset row in pool
│   │   ├── layout/
│   │   │   └── Box.tsx               # Layout utility
│   │   ├── ConnectAccount.tsx        # Wallet connection button
│   │   ├── WalletButton.tsx          # Wallet UI
│   │   ├── NetworkPill.tsx           # Network indicator
│   │   └── BlendPoolViewer.tsx       # Contract debugger
│   │
│   ├── hooks/
│   │   ├── useBlendPools.ts          # Fetch all pools (MAIN HOOK)
│   │   ├── useBlendPool.ts           # Fetch single pool
│   │   ├── useWallet.ts              # Wallet context hook
│   │   ├── useWalletBalance.ts       # Fetch user balances
│   │   └── useNotification.ts        # Toast notifications
│   │
│   ├── providers/
│   │   ├── WalletProvider.tsx        # Wallet context provider
│   │   └── NotificationProvider.tsx  # Notification context
│   │
│   ├── pages/
│   │   ├── Home.tsx                  # Main page (dashboard)
│   │   ├── Debugger.tsx              # Contract debugger
│   │   └── PoolDiscoveryDebug.tsx    # Pool discovery testing
│   │
│   ├── types/
│   │   └── blend.ts                  # TypeScript interfaces
│   │
│   ├── utils/
│   │   └── tokenMetadata.ts          # Token formatting utilities
│   │
│   ├── contracts/
│   │   ├── blend.ts                  # Contract addresses
│   │   └── util.ts                   # Network config
│   │
│   ├── util/
│   │   ├── wallet.ts                 # Wallet utilities
│   │   └── storage.ts                # LocalStorage helpers
│   │
│   ├── App.tsx                       # Main app component
│   └── main.tsx                      # Entry point
│
├── docs/
│   └── archive/                      # Historical documentation
│       ├── DASHBOARD_STATUS.md       # Phase 1 completion notes
│       ├── BLEND_INTEGRATION.md      # Original integration guide
│       └── QUICK_START.md            # Original quick start
│
├── ARCHITECTURE.md                   # This file
├── IMPLEMENTATION_PLAN.md            # Phase 2 implementation plan
├── README.md                         # Project overview
├── package.json                      # Dependencies
├── vite.config.ts                    # Vite configuration
└── tsconfig.json                     # TypeScript configuration
```

---

## Current Status

### ✅ Phase 1: Pool Dashboard (Complete)
- [x] Pool discovery via Backstop
- [x] Load multiple pools in parallel
- [x] Display pool metadata and reserves
- [x] Show APY rates (supply/borrow)
- [x] Utilization bars with color coding
- [x] Available liquidity display
- [x] Expandable pool cards
- [x] Loading/error/empty states
- [x] Refresh functionality

### 🚧 Phase 2: AI Chat Interface (In Progress)
- [ ] Install AI dependencies (LangChain, AWS Bedrock, Supabase)
- [ ] Setup Supabase schema (users, conversations, deposits)
- [ ] Create Stellar trading utilities (XLM→USDC swaps)
- [ ] Build LangChain tools (pool queries, trading, risk analysis)
- [ ] Implement chat UI component
- [ ] Add transaction signing flow
- [ ] Persist conversation history
- [ ] Create system prompt for Tuxedo AI

### 📋 Phase 3: Advanced Features (Planned)
- [ ] Add USD pricing (query Blend oracles)
- [ ] Complete token metadata for all assets
- [ ] Implement sorting and filtering
- [ ] Add historical APY charts
- [ ] Mobile responsive design
- [ ] Dark mode support

---

## Known Issues & Limitations

### 🟡 Medium Priority
1. **Token Metadata Incomplete**: Only 3 tokens (BLND, USDC, XLM) have metadata
2. **No USD Pricing**: Shows raw token amounts instead of USD values
3. **Performance with Many Pools**: Not yet tested with 10+ pools

### 🟢 Low Priority
4. **No Historical Data**: Only current snapshot, no trends
5. **No Search/Filter**: Can't search pools by name or asset
6. **Desktop-Only UI**: Mobile layout not optimized

### ✅ Resolved
- ~~Pool discovery failing~~ - Fixed by using Backstop.rewardZone
- ~~Status detection broken~~ - Fixed by using pool.metadata.status

---

## Development Guide

### Local Development
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Open browser to http://localhost:5173
```

### Build for Production
```bash
# Build static site
npm run build

# Preview production build
npm run preview
```

### Deploy
```bash
# Deploy to Vercel, Netlify, or any static host
npm run build
# Upload dist/ folder
```

### Environment Variables
```bash
# .env.local
VITE_STELLAR_NETWORK=testnet
VITE_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_RPC_URL=https://soroban-testnet.stellar.org

# Phase 2 (AI features)
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_AWS_REGION=us-east-1
VITE_AWS_ACCESS_KEY_ID=AKIA...
VITE_AWS_SECRET_ACCESS_KEY=...
```

---

## References

### Blend Protocol
- **Blend SDK**: https://github.com/blend-capital/blend-sdk-js
- **Pool Integration**: https://docs.blend.capital/tech-docs/integrations/integrate-pool
- **Official UI**: https://github.com/blend-capital/blend-ui

### Stellar
- **Stellar SDK**: https://github.com/stellar/js-stellar-sdk
- **Soroban Docs**: https://developers.stellar.org/docs/build/smart-contracts
- **RPC Docs**: https://developers.stellar.org/docs/data/rpc

### Frontend
- **Vite**: https://vitejs.dev
- **React Query**: https://tanstack.com/query/latest
- **Stellar Design System**: https://github.com/stellar/design-system

---

**Last Updated**: October 25, 2025
**Maintained By**: Development Team
**Status**: Living Document
