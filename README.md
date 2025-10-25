# Tuxedo - AI-Powered Blend Pools Dashboard

**Conversational interface for discovering and interacting with Blend Protocol on Stellar**

Built with Vite + React + TypeScript | Powered by Blend SDK + AWS Bedrock (Claude)

---

## 🎯 What is Tuxedo?

Tuxedo makes DeFi lending on Stellar accessible through natural language. Users can:

- 💬 **Ask an AI assistant** about yield opportunities and risks
- 📊 **View all Blend pools** with real-time APY rates
- 💱 **Execute trades** (XLM → USDC) through conversation
- 🏊 **Deposit into pools** with guided assistance
- 📝 **Track conversations** and transaction history

**Demo Mode**: Shows mainnet pool data (accurate APYs) but only allows testnet transactions.

---

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- npm or yarn
- Freighter wallet (browser extension)

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd blend-pools

# Install dependencies
npm install

# Start dev server
npm run dev
```

Visit http://localhost:5173 and connect your Freighter wallet!

---

## 📚 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system design and technical overview
- **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** - Step-by-step guide to build AI features
- **[docs/archive/](./docs/archive/)** - Historical documentation

---

## ✅ Current Status

### Phase 1: Pool Dashboard ✅ **Complete**

- [x] Discover all Blend pools via Backstop contract
- [x] Display pool metadata, reserves, and APY rates
- [x] Show utilization metrics and available liquidity
- [x] Color-coded APY visualization
- [x] Expandable pool cards
- [x] Real-time refresh

### Phase 2: AI Chat Interface 🚧 **In Progress**

- [ ] Conversational pool queries
- [ ] XLM → USDC swap via chat
- [ ] Transaction signing flow
- [ ] Conversation history (Supabase)
- [ ] Risk explanations in plain English

### Phase 3: Advanced Features 📋 **Planned**

- [ ] USD pricing (oracle integration)
- [ ] Complete token metadata
- [ ] Historical APY charts
- [ ] Mobile responsive design
- [ ] Dark mode

---

## 🏗️ Tech Stack

**Frontend**
- Vite 7.1 + React 19 + TypeScript 5.9
- Stellar Design System
- React Router + React Query

**Blockchain**
- Stellar SDK 14.2
- Blend SDK 3.2.1
- Freighter Wallet (via Stellar Wallets Kit)

**AI & Backend** *(Phase 2)*
- AWS Bedrock (Claude 3.5 Sonnet)
- LangChain.js
- Supabase Cloud (PostgreSQL)

---

## 🛠️ Development

### Project Structure

```
src/
├── components/
│   ├── dashboard/          # Pool dashboard UI
│   │   ├── PoolsDashboard.tsx
│   │   ├── PoolCard.tsx
│   │   └── ReserveRow.tsx
│   └── ChatInterface.tsx   # AI chat (Phase 2)
├── hooks/
│   └── useBlendPools.ts    # Main data fetching hook
├── lib/                    # Phase 2: AI & trading logic
│   ├── ai-agent.ts
│   ├── ai-tools.ts
│   ├── stellar-trading.ts
│   └── supabase.ts
├── types/
│   └── blend.ts            # TypeScript interfaces
└── utils/
    └── tokenMetadata.ts    # Token formatting
```

### Key Files

- **`src/hooks/useBlendPools.ts`** - Fetches pools from Backstop.rewardZone
- **`src/components/dashboard/PoolsDashboard.tsx`** - Main dashboard component
- **`src/contracts/blend.ts`** - Testnet contract addresses

### Environment Variables

```bash
# .env.local

# Stellar Network
VITE_STELLAR_NETWORK=testnet
VITE_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_RPC_URL=https://soroban-testnet.stellar.org

# Phase 2: AI Features
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_AWS_REGION=us-east-1
VITE_AWS_ACCESS_KEY_ID=AKIA...
VITE_AWS_SECRET_ACCESS_KEY=...
```

---

## 🧪 Testing

### Manual Testing

1. **Connect Wallet**
   - Click "Connect Account"
   - Select Freighter
   - Approve connection

2. **View Pools**
   - Dashboard auto-loads on page load
   - Click pool cards to expand reserves
   - Check APY rates and utilization

3. **Refresh Data**
   - Click refresh button
   - Verify pools reload

### Phase 2 Testing *(Coming Soon)*

4. **Chat with Tuxedo**
   - Ask "What yields are available?"
   - Request "Swap 10 XLM for USDC"
   - Sign transaction in Freighter

---

## 📦 Build & Deploy

### Build for Production

```bash
npm run build
# Outputs to dist/
```

### Deploy

**Vercel** (Recommended)
```bash
vercel deploy
```

**Netlify**
```bash
netlify deploy --prod --dir=dist
```

**Any Static Host**
- Upload `dist/` folder
- No server-side rendering needed
- All environment variables must be set in hosting platform

---

## 🔗 Blend Protocol Contracts (Testnet)

```typescript
Backstop:     CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X
Comet Pool:   CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF

BLND Token:   CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK6A2JN3HEX56T2EDAFO7QF
USDC Token:   CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU
XLM Token:    CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC
```

---

## 🎓 How It Works

### Pool Discovery

1. Load Backstop contract using Blend SDK
2. Query `config.rewardZone` for active pool addresses
3. Load each pool with `PoolV2.load()`
4. Transform reserve data for UI display

**Why Backstop?** More reliable than Pool Factory events, matches official blend-ui architecture.

### AI Chat *(Phase 2)*

1. User sends message to Claude (via AWS Bedrock)
2. Claude decides which tools to call (pool queries, trading, etc.)
3. Tools execute using Stellar SDK directly
4. Claude formats results in plain English
5. If transaction needed, show "Sign" button
6. User signs with Freighter wallet
7. Transaction submitted to Stellar network

**No MCP Server Needed** - We use Stellar SDK + Blend SDK directly in TypeScript instead of Python MCP server.

---

## 🤝 Contributing

This project uses:
- **ESLint** for linting
- **Prettier** for formatting
- **Husky** for git hooks

```bash
# Format code
npm run format

# Lint code
npm run lint
```

---

## 📄 License

Licensed under the [Apache License, Version 2.0](./LICENSE)

---

## 🔗 Links

- **Blend Protocol**: https://blend.capital
- **Blend SDK**: https://github.com/blend-capital/blend-sdk-js
- **Stellar Docs**: https://developers.stellar.org
- **Scaffold Stellar**: https://github.com/AhaLabs/scaffold-stellar

---

## 🙏 Acknowledgments

Built with [Scaffold Stellar](https://github.com/AhaLabs/scaffold-stellar) by Aha Labs

Powered by [Blend Protocol](https://blend.capital) on Stellar

---

**Status**: Active Development | **Version**: 0.1.0 | **Last Updated**: October 25, 2025
