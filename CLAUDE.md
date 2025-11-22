# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Choir** (formerly Tuxedo) is a **Sovereign Cloud Personal Banking Agent** — NOT a DApp, NOT a wallet. It's a secure, private computer running in a Trusted Execution Environment (TEE) that manages your financial assets across multiple blockchains.

**The Core Metaphor**: Users authenticate into a TEE filesystem (running on Phala Network) containing:
- `keys.json` - Multi-chain keys (EVM, Stellar, Solana, Bitcoin, Zcash)
- `context.db` - User preferences, risk tolerance, chat history
- `agent_logic.py` - AI brain orchestrating cross-chain yield optimization

**Current State**: Production financial platform, migrating from Stellar-only to multichain architecture

**🏛️ Sovereign Cloud Architecture**:

- **TEE Compute**: Phala Network provides hardware-isolated execution for agent logic
- **Multi-Chain Capital**: EVM (Base, Arbitrum), Stellar, Solana, Bitcoin — chains are commodity infrastructure
- **Non-Custodial Vaults**: Users deposit assets, receive tradeable vault shares (ERC-4626 / Soroban)
- **Cross-Chain Routing**: AI moves capital to highest risk-adjusted yields, handling bridges invisibly
- **Realistic Yields**: 10-15% APY via blue-chip DeFi (Aave/Morpho on Base, Blend on Stellar)
- **Dual-Authority Security**: Agent executes strategies, only users withdraw
- **CHIP Token Economics**: Base yield (10-15%) + network equity (CHIP appreciation)

**⚠️ Important**:

- ALWAYS use web-search-prime to search the web. NEVER use built in web search
- **Not a DApp**: We're a Sovereign Cloud computer, not a wallet connector
- **Chain Agnostic**: EVM (Base) as primary, Stellar maintained, Solana/Bitcoin planned
- **Passkey Auth**: WebAuthn/biometrics only — no MetaMask required (though supported)
- **Python Development**: Use UV for virtual environment management. See backend commands below.
- **Realistic Economics**: 10-15% APY base yields, not 50% hallucinations

## Development Commands

### Frontend Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Lint and format
npm run lint
npm run format

# Install dependencies
npm install
```

### Backend Development

```bash
# Setup virtual environment (from project root)
cd backend

# Use UV for environment management
# UV creates and manages the virtual environment automatically
uv sync  # Creates .venv and installs all dependencies

# Always activate environment before working
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start backend server
python main.py

# Test AI agent functionality
python3 test_agent.py
python3 test_agent_with_tools.py

# Reinstall dependencies if needed
uv sync  # Updates and installs all packages from pyproject.toml + uv.lock
```

### Starting Both Services

```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend (from backend directory)
source .venv/bin/activate && python main.py
```

### UV Environment Management

```bash
# Install new dependencies:
uv add package_name  # Adds to pyproject.toml and installs

# Remove dependencies:
uv remove package_name

# Check installed packages:
uv pip list

# Update all dependencies:
uv sync --upgrade

# Reinstall/refresh environment:
uv sync  # Recreates environment with correct dependencies
```

### Service URLs (Development)

- Frontend: http://localhost:5173/
- Backend: http://localhost:8000/
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

## High-Level Architecture

### System Components

1. **TEE Runtime** (Phala Network) - Hardware-isolated execution environment for agent logic
2. **AI Agent Backend** (`backend/main.py`) - FastAPI with LangChain integration and multi-step reasoning
3. **Multi-Chain Integrations**:
   - `backend/chains/evm.py` - EVM chains (Base, Arbitrum, Ethereum)
   - `backend/stellar_tools.py` - Stellar blockchain (maintained for legacy)
   - `backend/chains/solana.py` - Solana integration (planned)
   - `backend/chains/bitcoin.py` - Bitcoin integration (planned)
4. **DeFi Protocol Adapters**:
   - `backend/protocols/aave_tools.py` - Aave V3 on Base/EVM
   - `backend/protocols/morpho_tools.py` - Morpho optimized lending
   - `backend/blend_pool_tools.py` - Blend Capital on Stellar
   - `backend/protocols/uniswap_tools.py` - Uniswap V3 swaps
5. **Vault System** (`backend/vault_manager.py`) - Multi-chain vault coordination
6. **Passkey Auth** (`backend/api/routes/passkey_auth.py`) - WebAuthn authentication
7. **Chat Interface** (`src/components/ChatInterface.tsx`) - Conversational AI (Thought Bank)
8. **Vault Dashboard** (`src/components/vault/VaultDashboard.tsx`) - Multi-chain vault interface
9. **API Layer** (`src/lib/api.ts`) - HTTP client with session management

### Data Flow

```
User (Passkey Auth) → TEE Filesystem → AI Agent → Cross-Chain Router → DeFi Protocols → Blockchains → Research Report → UI
```

**Multi-Chain Vault Flow:**

```
User Deposit (USDC)
    ↓
Vault Contract (ERC-4626 on Base or Soroban on Stellar)
    ↓
Agent Analyzes Yields Across Chains
    ↓
Routes to Best Opportunity (e.g., Morpho 14.2% on Base)
    ↓
Bridges + Supplies Assets (invisible to user)
    ↓
Yield Accrues → Fee Distribution → Share Value Increases
    ↓
User Withdraws (anytime) → Burns Shares → Receives USDC + Yield
```

## Key Configuration

### Environment Variables

**Frontend (.env.local)**:

```bash
# API Configuration
PUBLIC_API_URL=http://localhost:8000

# EVM Configuration (Primary)
PUBLIC_BASE_RPC_URL=https://mainnet.base.org
PUBLIC_ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
PUBLIC_ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY

# Stellar Configuration (Maintained)
PUBLIC_STELLAR_NETWORK=PUBLIC
PUBLIC_STELLAR_HORIZON_URL=https://horizon.stellar.org
PUBLIC_STELLAR_RPC_URL=https://rpc.ankr.com/stellar_soroban

# Wallet Configuration
PUBLIC_ENABLE_PASSKEY_AUTH=true
PUBLIC_ENABLE_EVM_WALLETS=true  # MetaMask, Coinbase Wallet (optional)
PUBLIC_ENABLE_STELLAR_WALLETS=true  # Freighter (optional)
```

**Backend (.env)**:

```bash
# AI/LLM Configuration
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.redpill.ai/v1
ANTHROPIC_API_KEY=your_anthropic_key
ENABLE_CLAUDE_SDK=true

# EVM Configuration
BASE_RPC_URL=https://mainnet.base.org
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY

# EVM Vault Contracts (Base mainnet)
BASE_VAULT_ADDRESS=0x...  # TUX0 ERC-4626 vault on Base
CHIP_TOKEN_ADDRESS=0x...  # CHIP ERC-20 token
PLATFORM_FEE_ADDRESS=0x...
AGENT_EOA_ADDRESS=0x...  # Agent's authorized address

# Stellar Configuration (Legacy support)
STELLAR_NETWORK=mainnet
STELLAR_HORIZON_URL=https://horizon.stellar.org
STELLAR_RPC_URL=https://rpc.ankr.com/stellar_soroban
STELLAR_VAULT_ID=C...  # Soroban vault (if deployed)

# Phala TEE Configuration (Future)
PHALA_ENDPOINT=https://api.phala.network
PHALA_CLUSTER_ID=0x...
TEE_ATTESTATION_ENABLED=false  # Set true after Phala deployment

# Authentication
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=no-reply@choir.chat
SESSION_SECRET=your_random_secret

# Security
ENABLE_RATE_LIMITING=true
MAX_RECOVERY_ATTEMPTS=5
```

### Critical Architecture Notes

**Sovereign Cloud Model**:
- **TEE Compute**: Agent logic runs in Phala Network's trusted execution environment (planned Q4 2026)
- **Multi-Chain**: EVM (Base) as primary, Stellar maintained, Solana/Bitcoin planned
- **Non-Custodial**: Users own vault shares (ERC-4626), not raw keys
- **Dual-Authority**: Agent executes strategies (within vault), users withdraw (burn shares)
- **Passkey Auth**: WebAuthn/biometrics for authentication (no seed phrases)
- **No Wallet Connect Required**: Direct account creation, though external wallets supported

**Migration Status**:
- Current: Stellar-native implementation (functional)
- Target: EVM-first with multichain support (Q1-Q2 2026)
- Approach: Parallel implementation, gradual user migration
- Contracts: Soroban vaults built (not deployed), ERC-4626 vaults in development

## AI Agent System

### Hybrid Architecture (LangChain + Claude SDK)

Tuxedo now features a **hybrid agent system**:

- **LangChain** (`backend/agent/core.py`) - Blockchain tool execution (19 tools)
- **Claude SDK** (`backend/agent/claude_sdk_wrapper.py`) - Research & analysis

**LangChain** for:
- Stellar blockchain operations
- Blend Capital yield farming
- Vault management
- Real-time DeFi execution

**Claude SDK** for:
- Strategy research and analysis
- Yield opportunity research
- Performance report generation
- Market insights and trends

See [docs/CLAUDE_SDK_INTEGRATION.md](docs/CLAUDE_SDK_INTEGRATION.md) for complete documentation.

### Core Implementation

- **Multi-step reasoning**: Up to 25 iterations with tool selection
- **LangChain v2+ compatible**: Uses new `tools` format
- **Claude SDK v0.1.8**: Advanced research and reasoning
- **Context management**: Conversation history + wallet address injection
- **Error handling**: Graceful failures with user feedback

### Integrated AI Agent Tools

**Multi-Chain Tool Architecture**:
- Current: 19 Stellar-focused tools (functional)
- Target: ~50+ tools across all chains (Q1-Q2 2026)
- Approach: Modular protocol adapters, agent selects best chain/protocol

**EVM Chain Tools (18 tools) - IN DEVELOPMENT:**

1. **Account Manager**: Create accounts, get balances, transaction history, gas estimates
2. **Aave V3**: Supply, borrow, withdraw, repay, get APY, check health factor
3. **Morpho**: Optimize supply, withdraw, check positions, compare vs Aave
4. **Compound V3**: Supply, withdraw, borrow, check positions
5. **Uniswap V3**: Swap tokens, add liquidity, remove liquidity, get quotes
6. **Cross-Chain Bridge**: Estimate costs, execute bridges (LayerZero, native)

**Stellar Tools (19 tools) - CURRENT IMPLEMENTATION:**

1. **Account Manager**: `create`, `fund`, `get`, `transactions`, `list`, `export`, `import`
2. **Market Data**: `orderbook`, `trades`, `ticker`, `pairs`
3. **Trading**: `create_offer`, `manage_offer`, `delete_offer`, `offers`
4. **Trustline Manager**: `create`, `delete`, `allow_trust`, `trustlines`
5. **Utilities**: `status`, `fees`, `ledgers`, `network`
6. **Soroban**: `get_data`, `simulate`, `invoke`, `get_events`, `get_ledger_entries`
7. **Blend Capital**: Pool discovery, APY queries, supply, withdraw, positions (6 tools)

**Multi-Chain Vault Tools (7 tools) - PROTOCOL-AGNOSTIC:**

1. **deposit_to_vault**: Deposit USDC to any chain, receive vault shares
2. **withdraw_from_vault**: Burn shares, receive USDC on any chain
3. **get_vault_performance**: Check TVL, APY, share value across all chains
4. **get_my_vault_position**: View shares and earned yield (aggregated)
5. **vault_agent_optimize**: Agent routes capital to best cross-chain opportunity
6. **vault_get_opportunities**: List current yields across all chains/protocols
7. **vault_distribute_yield**: Distribute fees to share holders

**Solana Tools (12 tools) - PLANNED Q2 2026:**

1. **Kamino Finance**: Supply, withdraw, check APY
2. **Drift Protocol**: Perps trading, positions
3. **Jupiter Aggregator**: Optimal swaps

**Bitcoin/Zcash Tools (6 tools) - PLANNED Q3 2026:**

1. **Wrapped BTC**: Wrap/unwrap, check balances
2. **Privacy Operations**: Zcash shielded transactions

**Total Tools**:
- Current: 19 (Stellar-focused)
- Q1 2026: 37 (+ EVM)
- Q2 2026: 49 (+ Solana)
- Q3 2026: 55 (+ Bitcoin/Zcash)

## Frontend Architecture

### Key Components

- `ChatInterface.tsx` - Main AI chat interface with tool indicators
- `VaultDashboard.tsx` - Non-custodial TUX0 vault interface with deposit/withdraw
- `PoolsDashboard.tsx` - Blend pool visualization
- `api.ts` - HTTP client with wallet address integration
- `useBlendPools.ts` - Pool data fetching hook
- `useVaultStats.ts` - Real-time vault statistics hook
- `useWallet.ts` - Stellar wallet connection
- `WalletContext.tsx` - Dual-mode wallet management (agent/external)

### Tech Stack

- Vite 7.1 + React 19 + TypeScript 5.9
- **wagmi + viem** - EVM wallet connections (MetaMask, Coinbase Wallet)
- **ConnectKit** or **RainbowKit** - Wallet UI components
- Stellar Wallets Kit - Freighter wallet (optional, legacy support)
- TanStack React Query - Server state management
- Axios - HTTP communication with backend
- **ethers.js / web3.js** - EVM blockchain interactions

## Backend Architecture

### Key Files

**Core Infrastructure:**

- `main.py` - FastAPI app with AI agent loop
- `stellar_tools.py` - All 6 Stellar tools implementation
- `stellar_soroban.py` - Smart contract support with async operations
- `account_manager.py` - Multi-user account management (Quantum Leap)
- `agent/tool_factory.py` - Per-request tool creation with user isolation

**TUX0 Vault Integration (NON-CUSTODIAL):**

- `vault_manager.py` - Complete vault contract interface (404 lines)
- `vault_tools.py` - 7 LangChain tools for AI agent vault operations
- `VaultDashboard.tsx` - Full vault interface (627 lines)
- `useVaultStats.ts` - Real-time vault statistics hook
- Smart contracts: Vault, TUX token, Farming (built, deployment pending)
- Dual-authority security: agent strategies, user-only withdrawals

**Blend Capital Integration (MAINNET-ONLY):**

- `blend_pool_tools.py` - Core Blend pool operations (discovery, APY, supply, withdraw, positions)
- `blend_account_tools.py` - LangChain tool wrappers for AI agent (mainnet defaults)
- Supports 3 mainnet pools: Comet, Fixed, YieldBlox
- Real-time on-chain APY calculation

### Tech Stack

- FastAPI + Pydantic - REST API framework
- LangChain + OpenAI gpt-oss 120b (via Redpill AI or openrouter exacto) - Agent orchestration
- **web3.py** - EVM chain interactions (Base, Arbitrum, Ethereum)
- Stellar SDK 13.1.0+ - Stellar blockchain (maintained)
- **solana-py** - Solana integration (planned)
- uvicorn ASGI server - ASGI web server
- python-dotenv - Environment management
- **Phala SDK** - TEE integration (planned Q4 2026)

## Testing

### AI Agent Testing

```bash
# From project root
python3 test_agent.py                    # Basic agent functionality
python3 test_agent_with_tools.py         # Comprehensive tool testing

# Frontend: Test chat interface in browser
# 1. Connect wallet
# 2. Try queries like:
#    - "What is the network status?"
#    - "Create a new account and fund it"
#    - "Show me the XLM/USDC orderbook"
#    - "What's in my wallet?" (requires connected wallet)
```

### Test Files Available

- `test_agent.py` - Basic AI agent functionality tests
- `test_agent_with_tools.py` - Comprehensive Stellar tools validation
- `test_wallet_fix.py` - Wallet integration testing
- `test_blend_integration.py` - Blend protocol integration tests

### TUX0 Vault Integration Testing

```bash
# From backend directory
cd backend
source .venv/bin/activate

# Run vault manager tests (requires deployed contracts)
python3 test_vault_integration.py

# Test vault tools
python3 test_vault_tools.py
```

**Note:** Vault testing requires deployed contracts (pending deployment).

### Blend Capital Integration Testing

```bash
# From backend directory
cd backend
source .venv/bin/activate

# Run Blend integration tests (read-only, no accounts needed)
python3 test_blend_integration.py
```

**Tests included:**

1. Pool discovery from Backstop contract
2. Real-time APY query for USDC in Comet pool
3. Best yield finder across all pools

**Expected results:** All 3 tests should pass, demonstrating:

- Connection to Blend protocol contracts
- On-chain data retrieval via Soroban RPC
- APY calculation from reserve data

### Common Test Scenarios

**Stellar Operations (Mainnet):**

- Network status queries: "What is the current Stellar network status?"
- Account creation: "Create a new account" (user must fund with real XLM)
- Balance queries: "Check the balance for account [ADDRESS]"
- Market data: "Show me the XLM/USDC orderbook"
- Trading operations: "Create an offer to buy 100 XLM for USDC" ⚠️ REAL FUNDS
- Trustline management: "Create a USDC trustline" ⚠️ REAL FUNDS
- Soroban contracts: "Get contract data for [CONTRACT_ID]"

**TUX0 Vault Operations (Non-Custodial - Mainnet):**

- Deposit: "Deposit 100 USDC to the vault" ⚠️ REAL FUNDS, receive TUX0 shares
- Withdraw: "Withdraw 50 shares from the vault" ⚠️ REAL FUNDS, burn shares
- Check performance: "What's the vault's current APY and TVL?"
- Position tracking: "How much yield have I earned on my vault shares?"
- Agent strategies: "Have the agent supply vault funds to the best Blend pool"
- Yield distribution: "Distribute accumulated yield to vault users"

**Blend Capital Yield Farming (Mainnet - Real Funds):**

- Find yield: "What's the best APY for USDC on mainnet?"
- Pool discovery: "Show me all Blend pools" (returns Comet, Fixed, YieldBlox)
- Supply assets: "Supply 100 USDC to the Comet pool" ⚠️ REAL FUNDS
- Check positions: "What are my positions in the Comet pool?"
- Withdraw: "Withdraw 50 USDC from the Comet pool" ⚠️ REAL FUNDS
- APY queries: "What's the current APY for USDC in Comet pool?" (live on-chain data)

## Important Patterns

### Tool Integration Pattern

All Stellar tools follow consistent patterns:

- Async function definitions
- Proper error handling with user-friendly messages
- Type-safe input/output validation
- Consistent response formatting

### Frontend Data Flow

- React hooks for state management
- TanStack Query for server state
- Wallet address passed to all AI calls
- Visual indicators for tool execution

### Error Handling

- Frontend: Graceful degradation with user notifications
- Backend: Try/catch blocks with structured error responses
- AI Agent: Error context preservation for recovery

## Development Notes

### Virtual Environment Management

**UV Environment Best Practices**:

```bash
# ✅ RECOMMENDED - Let UV manage everything
uv sync       # UV creates proper .venv with correct structure
source .venv/bin/activate
```

**Why UV works well**:

- UV creates virtual environments with optimized structure
- UV handles both environment creation AND package management consistently
- Automatic dependency resolution from pyproject.toml and uv.lock
- Faster installation and better caching than standard pip

### Port Configuration

- Frontend: 5173 (configurable via Vite)
- Backend: 8000 (standardized port)
- API fallback: Attempts 8001, 8002 if 8000 unavailable

### Network Configuration

- **Multi-chain mainnet** - All operations use production chains (Base, Stellar, etc.)
- **Primary chain**: Base (Ethereum L2) - Low fees, fast, Coinbase-backed
- **Secondary chains**: Ethereum mainnet, Arbitrum, Stellar
- **Future chains**: Solana, Bitcoin, Zcash
- Contract addresses:
  - EVM: `src/contracts/evm.ts` (Base, Arbitrum, Ethereum)
  - Stellar: `src/contracts/stellar.ts` (Blend protocol)
- Network URLs: Centralized in `backend/config/settings.py`
- RPC providers: Alchemy (EVM), Ankr (Stellar), configurable via environment variables

### Authentication & Wallet Integration

**Primary Auth**: Passkey/WebAuthn (biometric)
- No seed phrases, no passwords
- Hardware-backed security (TouchID, FaceID, Windows Hello)
- Recovery via email + recovery codes
- Session management with sliding expiration

**Optional External Wallets** (for advanced users):
- **EVM**: wagmi + viem (MetaMask, Coinbase Wallet, WalletConnect)
- **Stellar**: Stellar Wallets Kit (Freighter)
- Dual-mode operation: Passkey-created accounts OR external wallet connection
- Transaction signing support for vault operations

**Non-Custodial Model**:
- Users own vault shares (ERC-4626 or Soroban), not raw keys
- Agent operates within vault (can execute strategies, cannot withdraw)
- Users withdraw by burning shares (requires signature)

### API Communication

- Frontend → Backend: HTTP POST to `/chat` endpoint
- Request format: `{ message, history, wallet_address? }`
- Response format: `{ response, success, error? }`
- Health checks: GET `/health` endpoint every 30 seconds

## Production Status

**Sovereign Cloud Migration** (Q4 2025 - Q4 2026):

### Current State (Stellar-Native)

**✅ Fully Functional**:
1. **Passkey Authentication**: WebAuthn/biometric login, recovery codes, email recovery
2. **AI Agent**: 19 Stellar tools, LangChain orchestration, Claude SDK research
3. **Non-Custodial Vaults**: Dual-authority security model
4. **Blend Capital Integration**: 3 mainnet pools (Comet, Fixed, YieldBlox)
5. **User Isolation**: Per-user accounts, encrypted keys, session management
6. **Chat Interface**: Real-time conversational UI, vault dashboard

**⚠️ Not Deployed**:
- Soroban vault contracts (built, not deployed)
- TUX token on Stellar (built, not deployed)

### Target State (Multichain Sovereign Cloud)

**Q1 2026 - Base (EVM) Integration**:
- [ ] ERC-4626 vault contracts on Base mainnet
- [ ] Aave V3, Morpho, Compound integrations
- [ ] 18 EVM tools (parallel to Stellar tools)
- [ ] wagmi + viem wallet connections
- [ ] Realistic 10-15% APY yields

**Q2 2026 - Cross-Chain Routing**:
- [ ] LayerZero bridge integration
- [ ] Automatic yield optimization across chains
- [ ] Solana tools (Kamino, Drift, Jupiter)
- [ ] CHIP token launch (ERC-20 on Base)

**Q3 2026 - Bitcoin & Privacy**:
- [ ] Wrapped BTC integrations (wBTC, tBTC)
- [ ] Zcash privacy layer
- [ ] Tax-aware rebalancing
- [ ] Advanced governance features

**Q4 2026 - Phala TEE Deployment**:
- [ ] Agent logic migrated to Phala Network
- [ ] Encrypted filesystem (keys.json, context.db)
- [ ] Cryptographic attestation UI
- [ ] True "Can't Be Evil" architecture

### Migration Approach

- **Parallel Implementation**: Build EVM alongside Stellar (non-breaking)
- **Gradual User Migration**: 12-month transition period
- **Maintain Stellar**: Keep functional during migration, eventual deprecation TBD
- **User Choice**: Let users choose when to migrate

### Key Metrics

**Current (Stellar)**:
- 19 tools operational
- 0 deployed contracts
- 0 TVL
- Development/testnet only

**Target Q4 2026 (Multichain)**:
- 55+ tools across 6 chains
- $50M+ TVL
- 200,000+ users
- 10-15% base APY
- Full Phala TEE deployment

## File Locations for Common Tasks

### AI Agent Modifications

- **Core logic**: `backend/main.py` - Agent loop, LangChain integration
- **Stellar tools**: `backend/stellar_tools.py` - All 6 Stellar tools
- **Vault tools**: `backend/vault_tools.py` - 7 non-custodial vault operations
- **Vault manager**: `backend/vault_manager.py` - Complete vault contract interface
- **Smart contracts**: `backend/stellar_soroban.py` - Soroban operations
- **Key management**: `backend/key_manager.py` - Stellar key operations
- **Tool testing**: `test_agent_with_tools.py` - Comprehensive validation

### Frontend Changes

- **Chat interface**: `src/components/ChatInterface.tsx` - Main AI UI component
- **Vault dashboard**: `src/components/vault/VaultDashboard.tsx` - Non-custodial vault UI
- **Pool dashboard**: `src/components/dashboard/PoolsDashboard.tsx` - Blend UI
- **API client**: `src/lib/api.ts` - HTTP communication with wallet support
- **Wallet context**: `src/contexts/WalletContext.tsx` - Dual-mode wallet management
- **Vault stats**: `src/hooks/useVaultStats.ts` - Real-time vault data
- **Wallet integration**: `src/hooks/useWallet.ts` - Wallet connection logic
- **Pool data**: `src/hooks/useBlendPools.ts` - Pool fetching logic

### Configuration Updates

- **Contract addresses**: `src/contracts/blend.ts` - Mainnet contracts
- **Vault contracts**: `contracts/vault/`, `contracts/token/`, `contracts/farming/` - Soroban contracts
- **Environment setup**: `.env.local`, `backend/.env` - API keys and URLs
- **Network settings**: `backend/config/settings.py` - Centralized configuration
- **Dependencies**: `package.json`, `backend/pyproject.toml` - Libraries and versions

### Vault Deployment

- **Vault contract**: `contracts/vault/src/lib.rs` - 627-line production vault contract
- **TUX token**: `contracts/token/src/lib.rs` - SEP-41 compatible token
- **Deployment status**: `tux0_vault_implementation_progress.md` - Complete implementation tracking

### Quick Reference for Common Issues

- **Backend not starting**: Check `backend/.env` for OPENAI_API_KEY
- **Frontend can't reach backend**: Verify port 8000 is available
- **Tools not working**: Ensure `STELLAR_TOOLS_AVAILABLE = True` in backend logs
- **Wallet not connecting**: Check Freighter extension and network settings
- Use "npm run dev:full" to run server and client concurrently
- ALWAYS use web-search-prime to search the web. NEVER use built in web search
