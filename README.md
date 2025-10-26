# Tuxedo - AI-Powered Blend Pools Dashboard

**Conversational AI agent for discovering and interacting with Blend Protocol on Stellar**

Built with Vite + React + TypeScript | Powered by LangChain + FastAPI + Stellar SDK

🤖 **Status**: AI Agent Fully Operational | 🔧 **6 Stellar Tools Integrated** | 🚀 **Testnet Ready**

---

## 🎯 What is Tuxedo?

Tuxedo makes DeFi lending on Stellar accessible through natural language conversation with an AI agent. Users can:

- 🤖 **Chat with Tuxedo AI** about Stellar operations and DeFi opportunities
- 🔧 **Execute Stellar tools** through conversation (6 tools available)
- 👤 **Create and manage testnet accounts** with automatic funding
- 📊 **Query network status** and get real-time blockchain information
- 📈 **Access market data** and DEX orderbooks
- 💱 **Prepare for trading operations** (wallet integration ready)
- 🔮 **Smart contract interaction** (Soroban/Blend Protocol ready)
- 🏊 **Foundation for Blend lending** operations

**Current Status**: Fully functional AI agent with Stellar tool integration on testnet.

---

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- npm or yarn
- Freighter wallet (browser extension, optional for advanced features)

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd blend-pools

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync  # Or: pip install -r requirements.txt
cd ..

# Start both servers (Terminal 1)
npm run dev

# Start backend server (Terminal 2)
cd backend
source .venv/bin/activate
python main.py
```

Visit http://localhost:5173 to chat with Tuxedo AI!

**Services:**
- Frontend: http://localhost:5173/
- Backend: http://localhost:8002/
- Health Check: http://localhost:8002/health

---

## 📚 Documentation

- **[FRONTEND_INTEGRATION_PROGRESS.md](./FRONTEND_INTEGRATION_PROGRESS.md)** - Complete AI agent implementation details
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system design and technical overview
- **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** - Step-by-step guide to build AI features
- **[docs/archive/](./docs/archive/)** - Historical documentation

---

## ✅ Current Status

### 🎯 Phase 1: Pool Dashboard ✅ **Complete**

- [x] Discover all Blend pools via Backstop contract
- [x] Display pool metadata, reserves, and APY rates
- [x] Show utilization metrics and available liquidity
- [x] Color-coded APY visualization
- [x] Expandable pool cards
- [x] Real-time refresh

### 🤖 Phase 2: AI Agent Integration ✅ **COMPLETE**

- [x] **Fully functional AI agent** with multi-step reasoning
- [x] **6 Stellar tools integrated**: Account Manager, Market Data, Trading, Trustline Manager, Utilities, Soroban
- [x] **Frontend chat interface** with real-time communication
- [x] **Wallet address integration** for personalized operations
- [x] **LangChain compatibility** with proper tool binding
- [x] **Visual indicators** for different tool operations
- [x] **Testnet account creation** with automatic funding
- [x] **Network status queries** and market data access
- [x] **Error handling** and graceful failures
- [x] **Comprehensive testing** with validation scripts

### 🚀 Phase 3: Blend Protocol Integration 📋 **Ready for Development**

- [ ] Blend pool discovery via Soroban contracts
- [ ] APY querying and yield optimization
- [ ] Lending/borrowing operations
- [ ] Risk assessment and management
- [ ] Portfolio tracking and analytics

### 🎨 Phase 4: Advanced Features 📋 **Planned**

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

**Backend** ✅ **Fully Implemented**
- FastAPI (Python)
- LangChain with tool integration
- gpt-oss 120b via Redpill AI
- 6 Stellar tools with async support

**Blockchain**
- Stellar SDK 14.2 (Python + TypeScript)
- Blend SDK 3.2.1
- Soroban smart contract support
- Freighter Wallet (via Stellar Wallets Kit)

**AI & Agent System** ✅ **Fully Operational**
- Multi-step reasoning agent
- Tool calling with error handling
- Conversation history management
- Wallet address context injection

---

## 🛠️ Development

### Project Structure

```
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/          # Pool dashboard UI
│   │   │   │   ├── PoolsDashboard.tsx
│   │   │   │   ├── PoolCard.tsx
│   │   │   │   └── ReserveRow.tsx
│   │   │   └── ChatInterface.tsx   # ✅ AI chat interface
│   │   ├── hooks/
│   │   │   └── useBlendPools.ts    # Main data fetching hook
│   │   ├── lib/
│   │   │   └── api.ts              # ✅ API client with wallet support
│   │   ├── types/
│   │   │   └── blend.ts            # TypeScript interfaces
│   │   └── utils/
│   │       └── tokenMetadata.ts    # Token formatting
├── backend/                       # ✅ FastAPI backend
│   ├── main.py                    # ✅ AI agent implementation
│   ├── stellar_tools.py           # ✅ 6 Stellar tools
│   ├── stellar_soroban.py         # ✅ Smart contract support
│   ├── key_manager.py             # ✅ Key management
│   └── pyproject.toml             # Python dependencies
├── test_agent.py                  # ✅ Basic agent testing
├── test_agent_with_tools.py       # ✅ Comprehensive tool testing
└── FRONTEND_INTEGRATION_PROGRESS.md # ✅ Detailed progress documentation
```

### Key Files

**Frontend**
- **`src/components/ChatInterface.tsx`** - ✅ AI chat interface with tool indicators
- **`src/lib/api.ts`** - ✅ API client with wallet address integration
- **`src/hooks/useBlendPools.ts`** - Fetches pools from Backstop.rewardZone
- **`src/components/dashboard/PoolsDashboard.tsx`** - Main dashboard component

**Backend**
- **`backend/main.py`** - ✅ AI agent with LangChain and tool integration
- **`backend/stellar_tools.py`** - ✅ 6 Stellar tools implementation
- **`backend/stellar_soroban.py`** - ✅ Smart contract interaction support
- **`backend/contracts/blend.ts`** - Testnet contract addresses

### Environment Variables

**Frontend (.env.local)**
```bash
# Stellar Network
VITE_STELLAR_NETWORK=testnet
VITE_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_RPC_URL=https://soroban-testnet.stellar.org
VITE_API_URL=http://localhost:8002
```

**Backend (.env)**
```bash
# OpenAI Configuration (for LLM)
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.redpill.ai/v1  # or https://api.openai.com/v1

# Stellar Configuration
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
```

---

## 🧪 Testing

### ✅ AI Agent Testing (Fully Functional)

1. **Start Both Servers**
   ```bash
   # Terminal 1: Frontend
   npm run dev

   # Terminal 2: Backend
   cd backend && source .venv/bin/activate && python main.py
   ```

2. **Test AI Agent Functions**
   - **Network Status**: "What is the current Stellar network status?"
   - **Account Creation**: "Create a new testnet account and fund it"
   - **Balance Queries**: "Check the balance for account [ADDRESS]"
   - **Market Data**: "Show me the XLM/USDC orderbook"
   - **Wallet Integration**: Connect wallet and ask "What's in my wallet?"

3. **Automated Testing**
   ```bash
   # Test basic agent functionality
   python3 test_agent.py

   # Test all Stellar tools
   python3 test_agent_with_tools.py
   ```

### Pool Dashboard Testing

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

### Health Checks

- **Frontend**: Visit http://localhost:5173/
- **Backend**: curl http://localhost:8002/health
- **API Testing**: Use the test scripts provided

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

**Status**: ✅ AI Agent Fully Operational | **Version**: 0.2.0 | **Last Updated**: October 26, 2025

---

## 🎉 **Recent Updates**

### ✅ **October 26, 2025 - Frontend Integration Complete**

- **🤖 AI Agent**: Multi-step reasoning with LangChain integration
- **🔧 6 Stellar Tools**: Account management, market data, trading, trustlines, utilities, soroban
- **💬 Chat Interface**: Real-time frontend-backend communication
- **🔗 Wallet Integration**: Connected wallet addresses passed to agent
- **🎨 Visual Indicators**: Tool execution status indicators
- **🧪 Comprehensive Testing**: Full validation scripts and test coverage
- **📚 Documentation**: Complete progress documentation and API guides

The Tuxedo AI Agent is now **production-ready for educational use** on Stellar testnet!
