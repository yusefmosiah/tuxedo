# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tuxedo** is a conversational AI agent for discovering and interacting with Blend Protocol on Stellar testnet. It's a full-stack application with React + TypeScript frontend and FastAPI Python backend, featuring a fully operational AI agent with 6 integrated Stellar tools.

**Current State**: Production-ready for educational use on testnet (6.3/10 production readiness score)

**🚀 Active Migration**: Quantum leap from `KeyManager` to `AccountManager` for multi-user security
- See `AGENT_MIGRATION_QUANTUM_LEAP.md` for implementation details
- Architecture shift: user-isolated encrypted accounts in database
- No gradual migration - complete replacement (no valuable data exists)

**⚠️ Important**:
- ALWAYS use web-search-prime to search the web. NEVER use built in web search
- This system contains extensive hardcoded testnet configuration and is not suitable for mainnet deployment without significant refactoring.
- **Python Development**: ALWAYS run `source .venv/bin/activate && uv sync` before starting backend work to ensure dependencies are up to date

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
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync  # Or: pip install -r requirements.txt

# IMPORTANT: Always activate venv and sync dependencies first
# Run this whenever starting work on backend:
source .venv/bin/activate && uv sync

# Start backend server
python main.py

# Test AI agent functionality
python3 test_agent.py
python3 test_agent_with_tools.py
```

### Starting Both Services
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend (from backend directory)
source .venv/bin/activate && python main.py
```

### Service URLs (Development)
- Frontend: http://localhost:5173/
- Backend: http://localhost:8000/
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

## High-Level Architecture

### System Components
1. **AI Agent Backend** (`backend/main.py`) - FastAPI with LangChain integration and multi-step reasoning
2. **Stellar Tools** (`backend/stellar_tools.py`) - 6 tools for blockchain operations
3. **Chat Interface** (`src/components/ChatInterface.tsx`) - Real-time conversational UI
4. **Pool Dashboard** (`src/components/dashboard/`) - Blend protocol visualization
5. **API Layer** (`src/lib/api.ts`) - HTTP client with wallet integration

### Data Flow
```
User Chat → Frontend → API → AI Agent → LLM → Tool Selection → Stellar Blockchain → Response → UI
```

## Key Configuration

### Environment Variables
**Frontend (.env.local)**:
- `VITE_STELLAR_NETWORK=testnet`
- `VITE_HORIZON_URL=https://horizon-testnet.stellar.org`
- `VITE_RPC_URL=https://soroban-testnet.stellar.org`
- `VITE_API_URL=http://localhost:8000` (or `PUBLIC_API_URL`)

**Backend (.env)**:
- `OPENAI_API_KEY=your_api_key` (required)
- `OPENAI_BASE_URL=https://api.redpill.ai/v1` (or https://api.openai.com/v1)
- `STELLAR_NETWORK=testnet`
- `HORIZON_URL=https://horizon-testnet.stellar.org`
- `SOROBAN_RPC_URL=https://soroban-testnet.stellar.org`

### Critical Architecture Note
This system contains **13+ categories of hardcoded values** limiting it to testnet:
- Contract addresses in `src/contracts/blend.ts`
- Network URLs in backend files
- Token metadata in `src/utils/tokenMetadata.ts`
- Port numbers and timeouts

## AI Agent System

### Core Implementation
- **Multi-step reasoning**: Up to 10 iterations with tool selection
- **LangChain v2+ compatible**: Uses new `tools` format
- **Context management**: Conversation history + wallet address injection
- **Error handling**: Graceful failures with user feedback

### 6 Integrated Stellar Tools
1. **Account Manager**: `create`, `fund`, `get`, `transactions`, `list`, `export`, `import`
2. **Market Data**: `orderbook`, `trades`, `ticker`, `pairs`
3. **Trading**: `create_offer`, `manage_offer`, `delete_offer`, `offers`
4. **Trustline Manager**: `create`, `delete`, `allow_trust`, `trustlines`
5. **Utilities**: `status`, `fees`, `ledgers`, `network`
6. **Soroban**: `get_data`, `simulate`, `invoke`, `get_events`, `get_ledger_entries`

## Frontend Architecture

### Key Components
- `ChatInterface.tsx` - Main AI chat interface with tool indicators
- `PoolsDashboard.tsx` - Blend pool visualization
- `api.ts` - HTTP client with wallet address integration
- `useBlendPools.ts` - Pool data fetching hook
- `useWallet.ts` - Stellar wallet connection

### Tech Stack
- Vite 7.1 + React 19 + TypeScript 5.9
- Stellar Design System + Stellar Wallets Kit
- TanStack React Query for data fetching
- Blend SDK 3.2.1 for protocol integration
- Axios for HTTP communication with backend

## Backend Architecture

### Key Files
- `main.py` - FastAPI app with AI agent loop
- `stellar_tools.py` - All 6 Stellar tools implementation
- `stellar_soroban.py` - Smart contract support
- `key_manager.py` - Stellar key management

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
#    - "Create a new testnet account and fund it"
#    - "Show me the XLM/USDC orderbook"
#    - "What's in my wallet?" (requires connected wallet)
```

### Test Files Available
- `test_agent.py` - Basic AI agent functionality tests
- `test_agent_with_tools.py` - Comprehensive Stellar tools validation
- `test_wallet_fix.py` - Wallet integration testing

### Common Test Scenarios
- Network status queries: "What is the current Stellar network status?"
- Account creation: "Create a new testnet account and fund it"
- Balance queries: "Check the balance for account [ADDRESS]"
- Market data: "Show me the XLM/USDC orderbook"
- Trading operations: "Create an offer to buy 100 XLM for USDC"
- Trustline management: "Create a USDC trustline"
- Soroban contracts: "Get contract data for [CONTRACT_ID]"

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

### Port Configuration
- Frontend: 5173 (configurable via Vite)
- Backend: 8000 (standardized port)
- API fallback: Attempts 8001, 8002 if 8000 unavailable

### Network Configuration
- Currently testnet-only (major limitation)
- Contract addresses: `src/contracts/blend.ts` (hardcoded testnet values)
- Network URLs: Scattered across `backend/main.py` and `stellar_tools.py`
- Friendbot URL: Hardcoded to `https://friendbot.stellar.org`

### Wallet Integration
- Uses Stellar Wallets Kit (`@creit.tech/stellar-wallets-kit`)
- Supports Freighter and other compatible wallets
- Wallet address automatically passed to AI agent in `wallet_address` parameter
- Read-only operations (no transaction signing in current implementation)

### API Communication
- Frontend → Backend: HTTP POST to `/chat` endpoint
- Request format: `{ message, history, wallet_address? }`
- Response format: `{ response, success, error? }`
- Health checks: GET `/health` endpoint every 30 seconds

## Production Limitations

**Critical Issues to Address**:
1. **Hardcoded testnet configuration**: Contract addresses, network URLs, friendbot
2. **Scattered configuration**: Settings across multiple files
3. **Limited error context**: Generic error messages to users
4. **No dynamic token discovery**: Cannot support new tokens
5. **Testnet-only deployment**: Cannot work on mainnet or other networks

**Immediate Actions Needed**:
- Create centralized configuration management system
- Add mainnet and multi-network support
- Implement dynamic token/contract discovery
- Enhance error handling and user feedback
- Remove hardcoded values from source code

**Known Hardcoded Locations**:
- `src/contracts/blend.ts`: Testnet contract addresses
- `backend/stellar_tools.py`: Network URLs and friendbot
- `backend/main.py`: OpenAI endpoints and CORS settings
- `src/utils/tokenMetadata.ts`: Token information and UI thresholds

## File Locations for Common Tasks

### AI Agent Modifications
- **Core logic**: `backend/main.py` - Agent loop, LangChain integration
- **Tool implementations**: `backend/stellar_tools.py` - All 6 Stellar tools
- **Smart contracts**: `backend/stellar_soroban.py` - Soroban operations
- **Key management**: `backend/key_manager.py` - Stellar key operations
- **Tool testing**: `test_agent_with_tools.py` - Comprehensive validation

### Frontend Changes
- **Chat interface**: `src/components/ChatInterface.tsx` - Main AI UI component
- **API client**: `src/lib/api.ts` - HTTP communication with wallet support
- **Pool dashboard**: `src/components/dashboard/PoolsDashboard.tsx` - Blend UI
- **Wallet integration**: `src/hooks/useWallet.ts` - Wallet connection logic
- **Pool data**: `src/hooks/useBlendPools.ts` - Pool fetching logic

### Configuration Updates
- **Contract addresses**: `src/contracts/blend.ts` - Testnet contracts (⚠️ hardcoded)
- **Environment setup**: `.env.local`, `backend/.env` - API keys and URLs
- **Network settings**: Multiple backend files (⚠️ needs refactoring)
- **Dependencies**: `package.json`, `backend/pyproject.toml` - Libraries and versions

### Quick Reference for Common Issues
- **Backend not starting**: Check `backend/.env` for OPENAI_API_KEY
- **Frontend can't reach backend**: Verify port 8000 is available
- **Tools not working**: Ensure `STELLAR_TOOLS_AVAILABLE = True` in backend logs
- **Wallet not connecting**: Check Freighter extension and network settings
- **Testnet only**: All contracts and URLs hardcoded to testnet (see Production Limitations)
- note the "npm run dev:full" command to run server and client concurrently
- ALWAYS use web-search-prime to search the web. NEVER use built in web search