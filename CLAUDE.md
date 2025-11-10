# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tuxedo** is a conversational AI agent featuring a **non-custodial vault system** for automated yield farming on Stellar **mainnet**. It's a full-stack application with React + TypeScript frontend and FastAPI Python backend, featuring a fully operational AI agent with 6 Stellar tools + 6 Blend Capital yield farming tools + 7 vault management tools.

**Current State**: Functionally complete with non-custodial TUX0 vault implementation (95% complete, deployment pending)

**🏛️ Non-Custodial Vault Architecture**:

- **TUX0 Vault**: Users deposit assets, receive tradeable vault shares
- **Agent Management**: AI autonomously manages vault funds across Blend pools
- **Fee Distribution**: 2% platform fee, 98% distributed to vault users
- **Real Yields**: All operations on Stellar mainnet with real funds
- **Dual-Authority Security**: Agent can execute strategies, only users can withdraw

**⚠️ Important**:

- ALWAYS use web-search-prime to search the web. NEVER use built in web search
- **Non-Custodial Model**: No wallet imports - users deposit into vaults and receive shares
- **Mainnet Only**: This system operates exclusively on Stellar mainnet with real funds
- **Python Development**: Use UV for virtual environment management. See backend commands below.

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

1. **AI Agent Backend** (`backend/main.py`) - FastAPI with LangChain integration and multi-step reasoning
2. **TUX0 Vault System** (`backend/vault_manager.py`) - Non-custodial vault management with contract interface
3. **Stellar Tools** (`backend/stellar_tools.py`) - 6 tools for blockchain operations
4. **Vault Tools** (`backend/vault_tools.py`) - 7 tools for vault operations (deposit, withdraw, agent strategies)
5. **Chat Interface** (`src/components/ChatInterface.tsx`) - Real-time conversational UI
6. **Vault Dashboard** (`src/components/vault/VaultDashboard.tsx`) - Non-custodial vault interface
7. **Pool Dashboard** (`src/components/dashboard/`) - Blend protocol visualization
8. **API Layer** (`src/lib/api.ts`) - HTTP client with wallet integration

### Data Flow

```
User Chat → Frontend → API → AI Agent → LLM → Tool Selection → Vault/Blend Operations → Stellar Blockchain → Response → UI
```

**Vault Flow:**

```
User Deposit → Vault Contract → TUX0 Shares → Agent Strategies → Blend Pools → Yield Generation → Fee Distribution → Share Value Increase
```

## Key Configuration

### Environment Variables

**Frontend (.env.local)**:

- `PUBLIC_STELLAR_NETWORK=PUBLIC` (mainnet)
- `PUBLIC_STELLAR_HORIZON_URL=https://horizon.stellar.org`
- `PUBLIC_STELLAR_RPC_URL=https://rpc.ankr.com/stellar_soroban` (or your RPC provider)
- `PUBLIC_API_URL=http://localhost:8000`

**Backend (.env)**:

- `OPENAI_API_KEY=your_api_key` (required)
- `OPENAI_BASE_URL=https://api.redpill.ai/v1` (or https://api.openai.com/v1)
- `STELLAR_NETWORK=mainnet`
- `ANKR_STELLER_RPC=https://rpc.ankr.com/stellar_soroban` (mainnet RPC)
- `MAINNET_HORIZON_URL=https://horizon.stellar.org`
- `VAULT_CONTRACT_ID=<deployed_vault_contract>` (pending deployment)
- `TUX_TOKEN_ID=<deployed_tux_token>` (pending deployment)
- `PLATFORM_FEE_ADDRESS=<platform_fee_collection_address>`
- `AGENT_ADDRESS=<authorized_agent_address>`

### Critical Architecture Note

This system operates **exclusively on mainnet** with a **non-custodial vault model**:

- **No Wallet Imports**: Users maintain control of their assets through vault shares
- **TUX0 Shares**: Users deposit into vault, receive tradeable shares that appreciate with yield
- **Agent Autonomy**: AI can execute Blend strategies but cannot withdraw user funds
- **Dual-Authority**: Agent for strategy execution, users for withdrawals only
- **Mainnet Operations**: All vault operations execute on Stellar mainnet with real funds
- **Contract Deployment**: Vault system built but contracts not yet deployed (implementation complete)

## AI Agent System

### Core Implementation

- **Multi-step reasoning**: Up to 10 iterations with tool selection
- **LangChain v2+ compatible**: Uses new `tools` format
- **Context management**: Conversation history + wallet address injection
- **Error handling**: Graceful failures with user feedback

### Integrated AI Agent Tools

**Core Stellar Tools (6 tools):**

1. **Account Manager**: `create`, `fund`, `get`, `transactions`, `list`, `export`, `import`
2. **Market Data**: `orderbook`, `trades`, `ticker`, `pairs`
3. **Trading**: `create_offer`, `manage_offer`, `delete_offer`, `offers`
4. **Trustline Manager**: `create`, `delete`, `allow_trust`, `trustlines`
5. **Utilities**: `status`, `fees`, `ledgers`, `network`
6. **Soroban**: `get_data`, `simulate`, `invoke`, `get_events`, `get_ledger_entries`

**TUX0 Vault Tools (7 tools) - NON-CUSTODIAL:**

1. **deposit_to_vault**: Deposit USDC, receive TUX0 shares (non-custodial)
2. **withdraw_from_vault**: Burn TUX0 shares, receive proportional USDC
3. **get_vault_performance**: Check vault TVL, APY, and share value
4. **get_my_vault_position**: View user's shares and earned yield
5. **vault_agent_supply_to_blend**: Agent supplies vault funds to Blend pools
6. **vault_agent_withdraw_from_blend**: Agent withdraws from Blend pools back to vault
7. **vault_distribute_yield**: Distribute 2% platform fee, 98% to vault users

**Blend Capital Yield Farming Tools (6 tools) - MAINNET:**

1. **blend_find_best_yield**: Find highest APY opportunities across all mainnet pools for an asset
2. **blend_discover_pools**: Discover all active Blend pools on mainnet (Comet, Fixed, YieldBlox)
3. **blend_supply_to_pool**: Supply assets to earn yield (autonomous execution, real funds)
4. **blend_withdraw_from_pool**: Withdraw assets from pools (real funds)
5. **blend_check_my_positions**: Check current positions in a pool
6. **blend_get_pool_apy**: Get real-time APY data for specific assets from on-chain sources

**Total: 19 AI Agent Tools**

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
- Stellar Design System + Stellar Wallets Kit
- TanStack React Query for data fetching
- Blend SDK 3.2.1 for protocol integration
- Axios for HTTP communication with backend

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

- FastAPI + Pydantic
- LangChain + OpenAI gpt-oss 120b (via Redpill AI or openrouter exacto)
- Stellar SDK 13.1.0+ with async support
- uvicorn ASGI server
- python-dotenv for environment management

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

- **Mainnet only** - All operations use Stellar mainnet
- Contract addresses: `src/contracts/blend.ts` (mainnet values)
- Network URLs: Centralized in `backend/config/settings.py`
- RPC provider: Ankr (configurable via environment variables)

### Wallet Integration

- Uses Stellar Wallets Kit (`@creit.tech/stellar-wallets-kit`)
- Supports Freighter and other compatible wallets
- Dual-mode operation: Agent accounts or external wallet connection
- Wallet address automatically passed to AI agent in `wallet_address` parameter
- Transaction signing support for vault operations (user signs deposits/withdrawals)
- Non-custodial model: users control vault shares, not agent keys

### API Communication

- Frontend → Backend: HTTP POST to `/chat` endpoint
- Request format: `{ message, history, wallet_address? }`
- Response format: `{ response, success, error? }`
- Health checks: GET `/health` endpoint every 30 seconds

## Production Status

**Implementation Complete (95%)**:

1. ✅ **Non-custodial vault system**: TUX0 shares with dual-authority security
2. ✅ **Complete smart contracts**: Vault (627 lines), TUX token, farming contracts
3. ✅ **Full AI integration**: 19 tools including 7 vault operations
4. ✅ **Mainnet-only configuration**: All operations default to mainnet
5. ✅ **Centralized configuration**: `backend/config/settings.py` + environment variables
6. ✅ **Real yield data**: On-chain APY from Blend Capital mainnet pools
7. ✅ **Multi-pool support**: Comet, Fixed, and YieldBlox pools
8. ✅ **User isolation**: Non-custodial shares with agent management

**Deployment Gap (5%)**:

- ❌ **Contract deployment**: Smart contracts built but not deployed
- ❌ **Environment variables**: Missing deployed contract addresses
- ❌ **Integration testing**: Requires deployed contracts for e2e testing

**Current Scope**:

- Non-custodial vault system with automated yield farming
- Blend Capital focused (no other DeFi protocols)
- Supports mainnet pools: Comet, Fixed, and YieldBlox
- Requires Ankr RPC or compatible mainnet RPC provider
- Mainnet-only by design (no testnet fallback)

**Implementation Status**:

- **Smart Contracts**: ✅ Complete (vault, token, farming)
- **Backend Integration**: ✅ Complete (vault_manager, vault_tools, API routes)
- **Frontend Interface**: ✅ Complete (VaultDashboard, hooks, wallet integration)
- **Blend Integration**: ✅ Complete (6 tools, mainnet pools)
- **Security Model**: ✅ Complete (dual-authority, non-custodial)
- **Deployment**: ❌ Pending (contracts not yet deployed)

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
