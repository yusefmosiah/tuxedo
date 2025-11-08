# 🎩 Tuxedo: Agentic DeFi for Everyone

**Part of the [Choir](./CHOIR_WHITEPAPER.md) ecosystem | Building the future of AI-managed yield optimization**

> "DeFi agents are inevitable. By 2027, everyone will have one. The only question is: will they be secure enough to trust with your capital?"

**Current Status:** 🧪 **Beta Testnet** | Actively seeking security researchers
**Network:** Stellar Testnet → Mainnet (Community Security Required)
**Vision:** Agentic finance with user sovereignty

---

## 🎯 What is Tuxedo?

Tuxedo is a **conversational AI agent** that manages DeFi strategies on your behalf. It's named Tuxedo because yield farming requires dressing up—making complex DeFi operations accessible through natural conversation.

### The Core Thesis

**Everyone will have a DeFi agent by 2030.** The technology is inevitable. But today, the critical blocker is **security**. Why would you trust AI with your capital when:

- Smart contracts have vulnerabilities
- AI agents are built with coding assistants (yes, this very codebase)
- Key management is notoriously difficult
- Multi-user isolation is complex

**Our Approach:**

1. **Build in the open** - Transparent architecture, documented security model
2. **Testnet first** - Experiment safely before mainnet deployment
3. **Token incentives** - Reward security researchers who make us better
4. **Community effort** - Mainnet launch requires collective security validation

**We're not just building an agent. We're building the security foundation for an entire category.**

---

## 🏗️ Architecture: Two Agent Types

### 👤 User Agents (Privacy-First Execution)

**What:** Personal AI agents that execute DeFi operations on behalf of individual users
**Runtime:** Phala TEE (Trusted Execution Environment) GPU cloud
**API:** OpenAI-compatible models via OpenRouter/LangChain
**Security:** Private keys isolated in hardware TEE, encrypted at rest
**Purpose:**

- Execute yield strategies (Blend Protocol, DeFindex)
- Manage portfolio across multiple chains
- Respond to user instructions in natural language
- Sign and submit blockchain transactions

**Status:** ✅ Core functionality working on testnet

### 🔬 Platform Agent (Always-On Research)

**What:** Continuously running research agent analyzing DeFi markets
**Runtime:** Tuxedo backend infrastructure (future: distributed)
**API:** Anthropic Claude API with extended thinking
**Tools:** Code execution mode with live data feeds
**Purpose:**

- Monitor real-time market conditions (Somnia Data Streams)
- Write research reports on yield opportunities
- Populate vector database with analysis
- Generate citations for user agent decisions

**Status:** 🚧 Design phase (post-hackathon)

### How They Work Together

```
┌─────────────────────────────────────────────────────┐
│  Platform Agent (Always Running)                    │
│  - Monitors live DeFi data streams                  │
│  - Analyzes yield opportunities                     │
│  - Writes research reports                          │
│  - Populates vector database                        │
└──────────────────┬──────────────────────────────────┘
                   │ Research Reports
                   │ (Cited in decisions)
                   ↓
┌─────────────────────────────────────────────────────┐
│  User Agent (On-Demand, Private)                    │
│  - Reads platform research                          │
│  - Executes user-specific strategies                │
│  - Signs transactions in TEE                        │
│  - Manages private keys securely                    │
└─────────────────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  Multi-Chain DeFi Protocols                         │
│  Stellar | Solana | EVM | Sui                       │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 Security Status: Transparent & Evolving

### ✅ What's Implemented

**User Isolation:**

- Database-level account isolation per user
- Encrypted private keys at rest (Fernet symmetric encryption)
- User-specific key derivation (PBKDF2 + user_id salt)
- Permission checks on every operation

**Key Management:**

- `AccountManager` architecture (replaces legacy `KeyManager`)
- Wallet import/export for user sovereignty
- Multi-chain abstraction layer (Stellar, future: Solana/EVM/Sui)
- TEE deployment for private key custody

**Authentication:**

- Passkey-based authentication (WebAuthn)
- Session-based authorization
- No passwords, no phishing vectors

### ⚠️ What's In Progress

**Current Migration:** "Quantum Leap" from KeyManager to AccountManager

- See: `AGENT_MIGRATION_QUANTUM_LEAP.md`
- Target: Complete user isolation with encrypted accounts
- Status: Partially implemented, needs final migration steps

**Known Limitations:**

- Testnet only (hardcoded contract addresses)
- Limited audit trail logging
- No rate limiting on sensitive operations
- TEE deployment not yet configured

### ❌ NOT Production-Ready For Mainnet

**Do NOT deploy mainnet capital until:**

- [ ] Third-party security audit completed
- [ ] Community security testing campaign finished
- [ ] TEE infrastructure validated in production
- [ ] Comprehensive audit logging implemented
- [ ] Rate limiting and abuse prevention deployed
- [ ] Recovery mechanisms tested thoroughly
- [ ] Multi-signature support for high-value operations

**We are explicit about this because user trust requires honesty.**

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

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv sync  # Or: pip install -r requirements.txt

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
OPENAI_BASE_URL=https://api.redpill.ai/v1  # or https://openrouter.ai/api/v1

# Stellar Network
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
SOROBAN_RPC_URL=https://soroban-testnet.stellar.org

# Encryption (generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
ENCRYPTION_MASTER_KEY=your_generated_key
ENCRYPTION_SALT=tuxedo-agent-accounts-v1
```

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
3. Chat with agent: "Create a testnet account and fund it"
4. Explore Blend Protocol pools
5. Test DeFindex yield strategies

---

## 🎯 Core Features

### 🤖 Conversational AI

- Natural language blockchain interaction
- Multi-step reasoning with LangChain
- Context-aware conversation history
- Tool execution with real-time feedback

### 🔑 User Sovereignty

- **Import existing wallets** (Freighter, Phantom, MetaMask)
- **Export private keys** anytime (you own your funds)
- Non-custodial architecture
- "Not your keys, not your crypto" respected

### 🏦 DeFi Integration

- **Blend Protocol**: Lending/borrowing on Stellar
- **DeFindex**: Multi-protocol yield optimization
- **Soroban**: Smart contract interaction
- **Multi-chain** (future): Solana, EVM, Sui

### 📊 Yield Strategies

- Automated rebalancing across protocols
- AI-driven strategy selection
- Research-backed decision making
- Transparent execution reports

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

### Test User Isolation

```bash
cd backend
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
├── CHOIR_WHITEPAPER.md            # Vision & tokenomics
├── AGENT_ACCOUNT_SECURITY_PLAN.md # Security architecture
├── AGENT_MIGRATION_QUANTUM_LEAP.md # Current migration status
└── CLAUDE.md                      # Development guide
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
- [AGENT_MIGRATION_QUANTUM_LEAP.md](./AGENT_MIGRATION_QUANTUM_LEAP.md) - Current migration status
- [AGENT_ACCOUNT_SECURITY_PLAN.md](./AGENT_ACCOUNT_SECURITY_PLAN.md) - Security architecture

### For Users

- [CHOIR_WHITEPAPER.md](./CHOIR_WHITEPAPER.md) - Vision, tokenomics, roadmap

### API Documentation

- Backend API: http://localhost:8000/docs (when running)
- OpenAPI spec: http://localhost:8000/openapi.json

---

## 🛣️ Roadmap

### Q4 2025: Testnet Beta

- [x] Core agent functionality
- [x] Passkey authentication
- [x] Blend Protocol integration
- [ ] Complete AccountManager migration (quantum leap)
- [ ] TEE deployment on Phala
- [ ] Security bounty program launch
- [ ] Community testing campaign

### Q1 2026: Mainnet Preparation

- [ ] Third-party security audit
- [ ] Audit logging & monitoring
- [ ] Rate limiting & abuse prevention
- [ ] Multi-chain support (Solana, EVM)
- [ ] Platform agent (research capabilities)
- [ ] Live data stream integration

### Q2 2026: Mainnet Launch

- [ ] Security validation complete
- [ ] Mainnet deployment (community approved)
- [ ] TUX token distribution
- [ ] Mobile apps (iOS, Android)
- [ ] Governance transition

### Q3-Q4 2026: Ecosystem Growth

- [ ] Code mode implementation
- [ ] Advanced tax optimization
- [ ] Multi-signature support
- [ ] Institutional features
- [ ] Academic partnerships

**Timeline depends on security validation. We will not rush mainnet.**

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

**Testnet Software - Use at Your Own Risk**

Tuxedo is experimental software in active development. This is a testnet deployment for security research and community testing.

**Do not:**

- Deploy mainnet capital
- Use for production purposes
- Rely on this software for critical operations
- Expect stability or backwards compatibility

**Legal:**

- No warranties of any kind
- You are responsible for your own funds
- Software provided "as is"
- Review code before trusting with value

**DeFi is risky. Agents are new. Security is hard. Proceed carefully.**

---

**Built for the future of agentic finance. Secured by the community.**

🎩 **Tuxedo** | Making yield farming look good
