# Tuxedo - AI-Powered Blend Pools Dashboard

Conversational AI agent for discovering and interacting with Blend Protocol on Stellar testnet.

**Live Demo:** https://your-demo-url.com
**Explainer Video:** [Watch Project Overview]()
**Block Explorer:** [View Contract on Stellar Explorer]()

---

## 🎥 Demo Video

[Project Demo Video - Coming Soon]

---

## 📸 Screenshots

### Dashboard Interface
*Screenshot of the main Blend pools dashboard showing APY rates and pool metrics*

### AI Chat Interface
*Screenshot of the conversational AI interface with tool execution indicators*

### Wallet Integration
*Screenshot showing connected wallet with account details*

---

## 🔧 How It Works

### Smart Contract Integration
Tuxedo interacts with Blend Protocol's smart contracts on Stellar testnet:

**Core Contracts:**
- **Backstop Contract:** `CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X`
- **Comet Pool Contract:** `CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF`

**Architecture:**
1. **Pool Discovery:** Queries Backstop.contract.rewardZone to discover active lending pools
2. **Data Fetching:** Uses Blend SDK to fetch pool metadata, reserves, and APY rates
3. **AI Agent:** FastAPI backend with LangChain integration processes natural language queries
4. **Tool Execution:** 6 Stellar tools execute blockchain operations (account creation, balance queries, market data, etc.)
5. **Real-time Updates:** Dashboard displays live pool data and utilization metrics

**Technical Flow:**
```
User Query → AI Agent → Tool Selection → Stellar Blockchain → Response → UI Update
```

---

## 🎬 Project Explainer (Video with Audio)

[Detailed Project Walkthrough - Coming Soon]

*In this video, I explain:*
- Project architecture and how components interact
- GitHub repository structure and key files
- Live demo of AI agent and dashboard functionality
- How smart contract integration works
- Step-by-step workflow from user query to blockchain execution

---

## 🚀 Try It Live

**Demo URL:** https://your-demo-url.com

*Features available for judging:*
- Connect Stellar wallet (Freighter)
- Chat with AI agent about Stellar operations
- View real-time Blend pool data and APY rates
- Create testnet accounts with automatic funding
- Query network status and market data

---

## 🔗 Block Explorer Links

**Stellar Testnet Contracts:**
- **Backstop Contract:** [View on Stellar Explorer](https://stellar.expert/explorer/testnet/contract/CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X)
- **Comet Pool Contract:** [View on Stellar Explorer](https://stellar.expert/explorer/testnet/contract/CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF)
- **BLND Token:** [View on Stellar Explorer](https://stellar.expert/explorer/testnet/asset/CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK6A2JN3HEX56T2EDAFO7QF-BLND)
- **USDC Token:** [View on Stellar Explorer](https://stellar.expert/explorer/testnet/asset/CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU-USDC)

---

## 📁 Repository Structure

```
blend-pools/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx      # AI chat UI
│   │   └── dashboard/
│   │       ├── PoolsDashboard.tsx # Pool dashboard
│   │       └── PoolCard.tsx       # Individual pool display
│   ├── lib/
│   │   └── api.ts                 # API client with wallet integration
│   └── hooks/
│       └── useBlendPools.ts       # Pool data fetching
├── backend/
│   ├── main.py                    # FastAPI + AI agent
│   ├── stellar_tools.py           # 6 Stellar blockchain tools
│   └── stellar_soroban.py         # Smart contract interaction
└── contracts/
    └── blend.ts                   # Contract addresses and interfaces
```

**Key Files:**
- `backend/main.py` - AI agent with LangChain integration
- `backend/stellar_tools.py` - Stellar blockchain operations
- `src/components/ChatInterface.tsx` - Conversational AI interface
- `src/lib/api.ts` - Frontend-backend communication

---

## 🛠️ Tech Stack

**Frontend:** React 19 + TypeScript + Vite + Stellar Design System
**Backend:** FastAPI + Python + LangChain + OpenAI
**Blockchain:** Stellar SDK + Blend SDK + Soroban Contracts
**AI:** Multi-step reasoning agent with 6 integrated Stellar tools

---

## 📞 Contact

Built for Blend Protocol on Stellar. Questions? Open an issue or reach out via GitHub.