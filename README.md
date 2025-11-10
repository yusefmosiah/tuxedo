# 🎩 Tuxedo: Agentic DeFi for Everyone

**Part of the [Choir](./CHOIR_WHITEPAPER.md) ecosystem | Building the future of AI-managed yield optimization**

> "DeFi agents are inevitable. By 2027, everyone will have one. The only question is: will they be secure enough to trust with your capital?"

**Current Status:** 🚀 **Live on Mainnet** | Transitioning to Vault Architecture
**Network:** Stellar Mainnet (Real Yields, Real Capital)
**Vision:** Non-custodial AI agents with transparent vault management

---

## 🎯 What is Tuxedo?

Tuxedo is a **conversational AI agent** that manages DeFi yield strategies on Stellar mainnet. It's named Tuxedo because yield farming requires dressing up—making complex DeFi operations accessible through natural conversation while maintaining the security and sophistication the ecosystem demands.

### The Evolution: Wallet Import → Vault Collateral

**Phase 1 (Current):** Wallet Import Model ⚠️
- Users import private keys for agent management
- Agent executes yield strategies autonomously
- Works, but feels wrong (and it is!)
- Violates DeFi best practice: "not your keys, not your crypto"

**Phase 2 (In Development):** Vault-Based Collateral ✨
- Users **deposit** assets into transparent vaults
- Receive **tradeable vault shares** representing position
- Agents manage vault assets without holding user keys
- Multiple vault types: Conservative, Aggressive, Research-backed
- Performance tracked via vault token prices on DEX
- Users maintain custody, agents demonstrate performance

**Why this matters:** We're transitioning from custodial agent control to non-custodial agent coordination. The vault model enables true DeFi composability: your agent's performance becomes a tradeable asset.

### The Core Thesis

**Everyone will have a DeFi agent by 2030.** The technology is inevitable. The critical question isn't *if*, but **how do we make it secure enough to trust?**

**Our Approach:**

1. **Radical transparency** - Open source, documented architecture, live on mainnet
2. **Iterative security** - Start with working system, improve continuously
3. **Vault evolution** - Move from key custody to deposit-based collateral
4. **Token incentives** - Reward researchers who make us better
5. **User sovereignty** - Always maintain exit options

**We're not just building an agent. We're building the architectural patterns for an entire category of secure AI-managed DeFi.**

---

## 🏗️ Architecture: Current + Future State

### Current Architecture: Wallet Import Model (Mainnet Live)

```
┌─────────────────────────────────────────────────────┐
│  USER                                                │
│  - Imports wallet via private key                   │
│  - Converses with AI agent                          │
│  - Agent manages assets autonomously                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  AI AGENT (Mainnet Operations)                      │
│  - Holds encrypted user keys                        │
│  - Executes yield strategies                        │
│  - Blend Capital: Lending/borrowing                 │
│  - Soroban: Smart contract operations               │
│  - Stellar DEX: Trading operations                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  STELLAR MAINNET                                     │
│  Real assets, real yields, real transactions        │
└─────────────────────────────────────────────────────┘
```

**Current Tools (12 mainnet operations):**
- 6 Stellar tools: Account, market data, trading, trustlines, utilities, Soroban
- 6 Blend Capital tools: Pool discovery, APY tracking, supply, withdraw, positions

**Security:** Encrypted keys, user isolation, per-request tool instantiation

### Future Architecture: Vault-Based Collateral (In Development)

```
┌─────────────────────────────────────────────────────┐
│  USER                                                │
│  - Keeps private keys (non-custodial)              │
│  - Deposits assets to vault                         │
│  - Receives tradeable vault share tokens            │
│  - Trades vault tokens on DEX                       │
└──────────────────┬──────────────────────────────────┘
                   │ Deposits USDC
                   ↓
┌─────────────────────────────────────────────────────┐
│  VAULT SMART CONTRACT (TUX-CORE, TUX-AGGRESSIVE...)│
│  - Holds deposited assets                           │
│  - Mints share tokens to users                      │
│  - Enforces risk limits                             │
│  - Enables agent operations                         │
└──────────────────┬──────────────────────────────────┘
                   │ Agent manages
                   ↓
┌─────────────────────────────────────────────────────┐
│  AI AGENT (Vault Manager)                           │
│  - Executes yield strategies WITHIN vault           │
│  - NO custody of user keys                          │
│  - Transparent operations (on-chain audit trail)    │
│  - Generates research reports for decisions         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  STELLAR MAINNET DEFI                                │
│  Blend, DeFindex, Soroswap, Aquarius                │
└─────────────────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  SECONDARY MARKETS                                   │
│  Vault tokens (TUX-CORE, etc.) trade on DEX         │
│  Price reflects agent performance                   │
│  Users can exit without withdrawing from vault      │
└─────────────────────────────────────────────────────┘
```

**Vault Types (Planned):**
- **TUX-CORE**: Conservative diversified (8-12% APY)
- **TUX-AGGRESSIVE**: High-yield seeking (15-30% APY)
- **TUX-RESEARCH**: Citation-backed strategies (10-20% APY + CHOIR rewards)
- **TUX-STABLE**: Stablecoin only (5-8% APY)
- **TUX-{USER}**: Personal custom agents

**See:** `docs/VAULT_COLLATERAL_ARCHITECTURE.md` and `docs/VAULT_IMPLEMENTATION_PLAN.md`

---

## 🔐 Security Status: Mainnet Live with Vault Upgrade Path

### ✅ Current Security (Wallet Import Model)

**User Isolation:**
- Database-level account isolation per user
- Encrypted private keys at rest (Fernet symmetric encryption)
- User-specific key derivation (PBKDF2 + user_id salt)
- Permission checks on every operation
- Per-request tool instantiation

**Key Management:**
- `AccountManager` architecture for multi-user support
- Wallet import/export for user sovereignty
- Encrypted storage with master key derivation
- Multi-chain abstraction (Stellar mainnet, others planned)

**Authentication:**
- Passkey-based authentication (WebAuthn)
- Session-based authorization
- No passwords, no phishing vectors

**Mainnet Operations:**
- All operations on Stellar mainnet (real funds)
- Blend Capital integration (Comet, Fixed, YieldBlox pools)
- Real-time on-chain APY data
- Soroban smart contract support

### ⚠️ Current Limitations (Why Vault Upgrade Matters)

**The Fundamental Issue:**
- Users must trust agent with private keys
- Violates DeFi best practice: "not your keys, not your crypto"
- No transparent performance tracking across users
- Difficult to compare agent strategies

**Known Risks:**
- Agent has full custody (encrypted, but still custodial)
- No independent verification of agent operations
- Limited audit trail visibility
- Recovery requires key backup

### 🚀 Vault Architecture Security Improvements (In Development)

**What Changes:**
- ✅ Users keep private keys (non-custodial)
- ✅ Agents manage vault assets (no key custody)
- ✅ On-chain audit trail (transparent operations)
- ✅ Tradeable performance tracking (vault token prices)
- ✅ Risk limits enforced by smart contract
- ✅ Emergency withdrawal mechanisms
- ✅ Multiple agent strategies to choose from

**Smart Contract Security:**
- Risk limit enforcement (asset concentration, liquidity reserves)
- Emergency pause functionality
- Time-locked parameter changes
- Governance-controlled upgrades

**Timeline:** See `docs/VAULT_IMPLEMENTATION_PLAN.md` (16-week phased approach)

### 💡 Security Philosophy

**We believe:**
1. **Transparency over obscurity** - Open source, documented risks
2. **Iteration over perfection** - Ship, learn, improve
3. **User sovereignty over convenience** - Vault model prioritizes custody
4. **Community validation** - Security researchers earn TUX tokens

**Current Status:** Mainnet live with wallet import. Actively developing vault architecture to eliminate key custody requirement.

---

## 💰 Token Incentives: Security as Community Effort

### TUX Token Economics

**Supply:** 100M tokens (Sui blockchain per Choir whitepaper)
**Distribution:**

- 40% - Testnet depositors & beta users
- 20% - Security researchers & auditors
- 20% - Development team
- 20% - Treasury (governance)

### Security Bounty Program

**Found a vulnerability?** We reward responsible disclosure.

**Severity Tiers:**

- 🔴 **Critical** (private key exposure, user fund theft): 50,000 TUX
- 🟠 **High** (cross-user access, authorization bypass): 25,000 TUX
- 🟡 **Medium** (data leakage, DoS vectors): 10,000 TUX
- 🟢 **Low** (information disclosure, edge cases): 2,500 TUX

**Contact:** security@choir.chat
**PGP Key:** [Coming Soon]

**Requirements:**

- Responsible disclosure (give us time to patch)
- Testnet demonstration (we provide test accounts)
- Clear reproduction steps
- Suggested mitigation

### Beta Tester Rewards

**Testnet participants earn TUX tokens for:**

- Depositing capital on testnet (simulated risk)
- Testing import/export workflows
- Reporting bugs and UX issues
- Contributing to documentation
- Helping others in community Discord

**Mainnet launch timeline depends on community validation.**

---

## 🚀 Quick Start

### Prerequisites

```bash
# Backend
- Python 3.11+
- uv (or pip)
- OpenAI-compatible API key (Redpill AI, OpenRouter, etc.)

# Frontend
- Node.js 18+
- npm or pnpm
```

### 1. Backend Setup

```bash
cd backend

# Create virtual environment with UV (recommended)
uv sync  # Creates .venv and installs all dependencies
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend
python main.py
# Backend runs on http://localhost:8000
```

**Required Environment Variables:**

```bash
# OpenAI-compatible API
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.redpill.ai/v1  # or https://api.openai.com/v1

# Stellar Network (MAINNET)
STELLAR_NETWORK=mainnet
MAINNET_HORIZON_URL=https://horizon.stellar.org
ANKR_STELLER_RPC=https://rpc.ankr.com/stellar_soroban

# Encryption (generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
ENCRYPTION_MASTER_KEY=your_generated_key
ENCRYPTION_SALT=tuxedo-agent-accounts-v1
```

**⚠️ Mainnet Configuration:**
- All operations use real Stellar mainnet
- Real funds, real yields, real risks
- Contract addresses in `backend/blend_pool_tools.py`
- RPC provider: Ankr (or your preferred mainnet RPC)

### 2. Frontend Setup

```bash
# From project root
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:5173
```

### 3. Access the Application

1. Open http://localhost:5173
2. Create account with passkey (no password needed)
3. Connect existing Stellar wallet or import private key
4. Chat with agent: "What's my wallet balance?" or "Find best USDC yield"
5. Explore Blend Protocol pools (mainnet: Comet, Fixed, YieldBlox)
6. Try yield strategies: "Supply 100 USDC to Comet pool"

**⚠️ Mainnet Warning:** You're operating with real funds. Start small, test carefully.

---

## 🎯 Core Features

### 🤖 Conversational AI

- Natural language blockchain interaction
- Multi-step reasoning with LangChain
- Context-aware conversation history
- Tool execution with real-time feedback

### 🔑 User Sovereignty (Current → Future)

**Current (Wallet Import):**
- Import existing wallets via private key
- Export private keys anytime
- Agent holds encrypted keys for operations
- ⚠️ Custodial during active management

**Future (Vault Model):**
- Users deposit to vault, keep keys
- Receive tradeable vault share tokens
- Agent manages vault, never touches keys
- ✅ True non-custodial architecture

### 🏦 DeFi Integration (Mainnet Live)

- **Blend Protocol**: Lending/borrowing on Stellar mainnet
  - Comet Pool: Diversified stablecoin lending
  - Fixed Pool: Fixed-rate lending strategies
  - YieldBlox Pool: Historical yield farming
- **Soroban**: Smart contract operations
- **Stellar DEX**: Trading and liquidity
- **Future**: DeFindex, multi-chain (Solana, EVM, Sui)

### 📊 Yield Strategies

**Current (Mainnet):**
- Blend Capital pool discovery and APY tracking
- Automated supply to highest-yield opportunities
- Multi-pool position management
- Real-time on-chain data

**Future (Vault Model):**
- Multiple vault strategies (Conservative, Aggressive, Research)
- AI-driven rebalancing across protocols
- Citation-backed decision making with research reports
- Tradeable performance via vault token prices

### 🛡️ Security Features

- Hardware TEE for key custody
- Encrypted keys at rest
- User isolation by default
- Passkey authentication (no passwords)

---

## 🧪 Development

### Run Full Stack Concurrently

```bash
npm run dev:full
# Starts both backend (8000) and frontend (5173)
```

### Test AI Agent

```bash
cd backend
python test_agent.py                    # Basic agent functionality
python test_agent_with_tools.py         # Comprehensive tool testing
```

### Test Mainnet Integration

```bash
cd backend
source .venv/bin/activate

# Test Blend integration (mainnet, read-only)
python test_blend_integration.py       # Pool discovery, APY queries

# Test user isolation
python test_user_isolation.py          # Verify cross-user access blocked
```

### Available Tools

**Account Management:**

- `create` - Generate new testnet account
- `fund` - Request testnet XLM from Friendbot
- `get` - Query account balances
- `list` - Show all user accounts
- `import` - Import existing wallet
- `export` - Export private keys

**Trading:**

- `buy` - Create buy order on Stellar DEX
- `sell` - Create sell order
- `cancel_order` - Cancel existing order
- `get_orders` - View active orders

**Market Data:**

- `orderbook` - View liquidity depth
- `trades` - Recent trade history
- `ticker` - Current prices

**DeFindex (Yield Farming):**

- `get_strategies` - Available yield strategies
- `deploy_capital` - Deposit into strategy
- `withdraw` - Remove capital

---

## 📁 Project Structure

```
tuxedo/
├── backend/
│   ├── main.py                    # FastAPI app + agent orchestration
│   ├── app.py                     # App factory pattern
│   ├── stellar_tools.py           # 6 Stellar blockchain tools
│   ├── defindex_tools.py          # DeFindex yield farming tools
│   ├── account_manager.py         # Multi-chain account management
│   ├── encryption.py              # Private key encryption
│   ├── database_passkeys.py       # User authentication & storage
│   ├── chains/                    # Chain-specific adapters
│   │   ├── base.py                # Abstract chain interface
│   │   └── stellar.py             # Stellar implementation
│   └── .env                       # Configuration (not in git)
│
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx      # Main AI chat UI
│   │   ├── TuxFarmingDashboard.tsx # DeFindex interface
│   │   └── dashboard/
│   │       └── PoolsDashboard.tsx # Blend Protocol pools
│   ├── lib/
│   │   └── api.ts                 # Backend API client
│   ├── hooks/
│   │   ├── useWallet.ts           # Wallet connection
│   │   └── useBlendPools.ts       # Pool data fetching
│   └── contracts/
│       └── blend.ts               # Contract addresses (testnet)
│
├── docs/
│   ├── VAULT_COLLATERAL_ARCHITECTURE.md  # Future vault system design
│   ├── VAULT_IMPLEMENTATION_PLAN.md      # 16-week roadmap to vaults
│   └── DEFINDEX_RESTORATION_GUIDE.md     # DeFindex integration guide
├── CHOIR_WHITEPAPER.md                   # Vision & tokenomics
├── AGENT_ACCOUNT_SECURITY_PLAN.md        # Security architecture
└── CLAUDE.md                             # Development guide
```

### Key Implementation Files

**Security Architecture:**

- `backend/account_manager.py:549-833` - Core user isolation logic
- `backend/encryption.py:474-528` - Key encryption/decryption
- `backend/database_passkeys.py` - User database schema

**AI Agent:**

- `backend/main.py:20-65` - Agent initialization & tool registration
- `backend/stellar_tools.py:1-100` - Tool implementations

**Frontend:**

- `src/components/ChatInterface.tsx` - Conversational UI
- `src/lib/api.ts` - HTTP client with auth

---

## 🔬 Research Directions (Post-Hackathon)

### Code Mode Paradigm (Cloudflare/Anthropic)

Instead of JSON tool calling, give agents code execution environments:

```typescript
// Agent writes TypeScript code that executes in sandbox
const account = await stellar.accounts.create();
await stellar.accounts.fund(account.id);
const balance = await stellar.accounts.getBalance(account.id);
const offers = await stellar.market.getOrderbook("USDC", "XLM");
return { account, balance, offers };
```

**Benefits:**

- 98.7% token reduction (150K → 2K tokens)
- Intermediate results stay in sandbox
- LLMs are trained on real code, not synthetic tool formats

**Status:** Research phase, POC planned

### Extended Thinking (Anthropic Claude 4)

Platform agent with deep reasoning capabilities:

- Budget control: `"thinking": {"type": "enabled", "budget_tokens": 16000}`
- Interleaved reasoning between tool calls
- Dynamic workflow adjustment based on intermediate results

**Use Case:** Multi-step DeFi research with citation generation

### Live Data Streams (Somnia)

Real-time event subscriptions for platform agent:

- Subscribe to Blend pool APY changes
- Monitor DeFindex rebalancing events
- Track cross-chain arbitrage opportunities
- Generate research reports on market movements

**Status:** Evaluating Somnia Data Streams hackathon (Nov 4-15)

---

## 🎓 Documentation

### For Developers

- [CLAUDE.md](./CLAUDE.md) - Complete development guide
- [docs/playful_path_to_vaults.md](./docs/playful_path_to_vaults.md) - 🚀 **1.6-hour vault sprint guide** (START HERE)
- [docs/VAULT_COLLATERAL_ARCHITECTURE.md](./docs/VAULT_COLLATERAL_ARCHITECTURE.md) - Full vault system design
- [docs/VAULT_IMPLEMENTATION_PLAN.md](./docs/VAULT_IMPLEMENTATION_PLAN.md) - Detailed 16-week roadmap
- [AGENT_ACCOUNT_SECURITY_PLAN.md](./AGENT_ACCOUNT_SECURITY_PLAN.md) - Current security architecture

### For Users

- [CHOIR_WHITEPAPER.md](./CHOIR_WHITEPAPER.md) - Vision, tokenomics, roadmap
- **Vault FAQ** (coming soon) - Understanding vault-based collateral

### API Documentation

- Backend API: http://localhost:8000/docs (when running)
- OpenAPI spec: http://localhost:8000/openapi.json

---

## 🛣️ Roadmap

### Q4 2024: Mainnet Launch ✅

- [x] Core agent functionality on mainnet
- [x] Passkey authentication
- [x] Blend Protocol integration (Comet, Fixed, YieldBlox)
- [x] Wallet import/export
- [x] Multi-user isolation with AccountManager
- [x] Real-time APY data from mainnet

### Q1 2025: Vault Architecture Transition

**Phase 1: Smart Contracts (Weeks 1-3)**
- [ ] TuxedoVault smart contract development
- [ ] Deposit/withdraw functions
- [ ] Share token minting/burning
- [ ] Risk limit enforcement
- [ ] Testnet deployment and testing

**Phase 2: Backend Integration (Weeks 4-5)**
- [ ] Vault state management
- [ ] Agent vault manager
- [ ] Database schema for vault tracking
- [ ] API endpoints for vault operations

**Phase 3: Frontend (Weeks 6-7)**
- [ ] Vault dashboard UI
- [ ] Deposit/withdraw modals
- [ ] Performance charts
- [ ] Activity feed for agent operations

**Phase 4: Multi-Vault Launch (Week 8)**
- [ ] Deploy TUX-CORE (conservative)
- [ ] Deploy TUX-AGGRESSIVE (high-yield)
- [ ] Deploy TUX-STABLE (stablecoin only)
- [ ] Deploy TUX-RESEARCH (citation-backed)

### Q2 2025: Migration & Growth

**Phase 5: User Migration (Weeks 9-10)**
- [ ] Migration tool from wallet import to vaults
- [ ] Incentive program (TUX token bonuses)
- [ ] User education campaign
- [ ] Graceful deprecation of wallet import

**Phase 6: DEX Integration (Week 11)**
- [ ] Vault token liquidity pools
- [ ] Market making bots
- [ ] Price discovery mechanisms
- [ ] Trading interface for vault tokens

**Phase 7: Governance (Weeks 12-13)**
- [ ] TUX governance token launch
- [ ] Staking and tier system
- [ ] Vault parameter voting
- [ ] Revenue sharing for stakers

### Q3 2025: Mainnet Vault Launch

**Phase 8: Security & Launch (Weeks 14-16)**
- [ ] Professional smart contract audit
- [ ] Bug bounty program
- [ ] Mainnet vault deployment
- [ ] Marketing and community growth

### Q4 2025: Ecosystem Expansion

- [ ] Cross-chain vaults (Solana, EVM)
- [ ] Personal agent vault creation
- [ ] Research vault with CHOIR integration
- [ ] Advanced analytics and reporting

**See:** `docs/VAULT_IMPLEMENTATION_PLAN.md` for detailed 16-week roadmap

---

## 🤝 Contributing

We welcome contributions, especially in security:

**Security Research:**

1. Test user isolation on testnet
2. Report vulnerabilities via security@choir.chat
3. Review code for potential exploits
4. Suggest architectural improvements

**Development:**

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

**Documentation:**

1. Improve setup instructions
2. Add architecture diagrams
3. Write tutorials for common tasks
4. Translate documentation

**Community:**

1. Help other users in Discord
2. Share testnet experiences
3. Provide UX feedback
4. Test on different platforms

**All contributors are eligible for TUX token rewards.**

---

## 🌐 Community

**Discord:** [Coming Soon]
**Twitter:** [@ChoirTech](https://twitter.com/ChoirTech)
**GitHub:** [Issues](https://github.com/yusefmosiah/tuxedo/issues) | [Discussions](https://github.com/yusefmosiah/tuxedo/discussions)
**Email:** hello@choir.chat

---

## ⚖️ License

MIT License - See [LICENSE](./LICENSE) for details

---

## 🙏 Acknowledgments

**Built with:**

- [Stellar](https://stellar.org) - Blockchain infrastructure
- [Blend Protocol](https://blend.capital) - Lending protocol
- [DeFindex](https://defindex.io) - Yield optimization
- [Anthropic Claude](https://anthropic.com) - AI reasoning
- [Phala Network](https://phala.network) - TEE infrastructure
- [LangChain](https://langchain.com) - Agent framework

**Hackathon Wins:**

- 🎃 Harvard Hack-o-Ween 2024
- 🏆 [Add your hackathon wins here]

---

## ⚠️ Disclaimer

**Mainnet Software - Use at Your Own Risk**

Tuxedo is experimental software operating on Stellar mainnet with real funds. While functional, it is in active development and security improvements are ongoing.

**Current Architecture (Wallet Import):**
- Agent holds encrypted user keys during operations
- Custodial model during active management
- User can export keys and exit anytime
- Transitioning to non-custodial vault architecture

**Understand the Risks:**

- **Smart contracts can have bugs** - DeFi protocols may fail
- **Agent operations can fail** - AI is not infallible
- **Key custody matters** - Current model requires trust in agent
- **Mainnet means real money** - Start small, test carefully
- **No guarantees** - Software provided "as is"

**Before Using:**

1. Review the code (open source)
2. Understand wallet import implications
3. Start with small amounts
4. Know that vault architecture (non-custodial) is coming
5. Accept full responsibility for your funds

**Legal:**

- No warranties of any kind
- You are responsible for your own funds
- Not financial advice
- Review security documentation thoroughly

**The vault architecture transition will eliminate key custody concerns. Until then, use with appropriate caution.**

**DeFi is risky. AI agents are experimental. Mainnet operations are irreversible. Proceed carefully.**

---

**Built for the future of agentic finance. Secured by the community.**

🎩 **Tuxedo** | Making yield farming look good
