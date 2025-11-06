# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tuxedo** is a conversational AI agent for discovering and interacting with Blend Protocol on Stellar testnet. It's a full-stack application with React + TypeScript frontend and FastAPI Python backend, featuring a fully operational AI agent with 6 integrated Stellar tools.

**Current State**: Production-ready for educational use on testnet (8.5/10 production readiness score)

**🔐 NEW: Passkey Authentication**: Complete WebAuthn-based authentication system replacing magic links with:
- **Biometric authentication** (Face ID, Touch ID, Windows Hello)
- **Recovery codes** (8 single-use backup codes per user)
- **Multi-agent key derivation** from master passkey
- **PRF support** with server-side fallback
- **Cross-platform compatibility**

**⚠️ Important**:
- ALWAYS use web-search-prime to search the web. NEVER use built in web search
- This system contains extensive hardcoded testnet configuration and is not suitable for mainnet deployment without significant refactoring.
- **Authentication**: All users must register with the new passkey system (magic links deprecated)

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

# Run database migration (one-time setup)
python migrate_to_passkeys.py

# Start backend server
python main.py

# Test AI agent functionality
python3 test_agent.py
python3 test_agent_with_tools.py

# Test passkey authentication
python -c "import api.routes.passkey; from crypto.key_derivation import KeyDerivation; from auth.recovery import RecoveryCodeService; print('✅ Passkey modules working')"
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
- Passkey Registration: http://localhost:5173/ (Login component handles both registration and authentication)

## High-Level Architecture

### System Components
1. **AI Agent Backend** (`backend/main.py`) - FastAPI with LangChain integration and multi-step reasoning
2. **Passkey Authentication** (`backend/api/routes/passkey.py`) - WebAuthn-based secure authentication
3. **Key Derivation** (`backend/crypto/key_derivation.py`) - Stellar account derivation from passkeys
4. **Recovery System** (`backend/auth/recovery.py`) - Backup code generation and validation
5. **Stellar Tools** (`backend/stellar_tools.py`) - 6 tools for blockchain operations
6. **Passkey Service** (`src/services/passkeyAuth.ts`) - Frontend WebAuthn integration
7. **Auth Context** (`src/contexts/AuthContext.tsx`) - React authentication state management
8. **Chat Interface** (`src/components/ChatInterface.tsx`) - Real-time conversational UI
9. **Login Component** (`src/components/Login.tsx`) - Unified passkey registration/login/recovery
10. **Pool Dashboard** (`src/components/dashboard/`) - Blend protocol visualization
11. **API Layer** (`src/lib/api.ts`) - HTTP client with wallet integration

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
- `TUXEDO_SERVER_SECRET=your_32_byte_server_secret` (required for passkey key derivation)

**Passkey Configuration** (in `backend/api/routes/passkey.py`):
- `RP_ID=localhost` (Production: yourdomain.com)
- `RP_NAME=Tuxedo AI`
- `RP_ORIGIN=http://localhost:5173` (Production: https://yourdomain.com)

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

## 🔐 Authentication System

### Passkey Authentication (NEW)
Tuxedo AI now uses **WebAuthn passkey authentication** replacing deprecated magic links:

#### Features
- **Biometric Authentication**: Face ID, Touch ID, Windows Hello, fingerprint sensors
- **Username-less Login**: Email optional for returning users
- **Recovery Codes**: 8 single-use backup codes per user (format: XXXX-XXXX-XXXX-XXXX)
- **Multi-Agent Key Derivation**: Deterministic Stellar accounts from master passkey
- **PRF Support**: Hardware-backed key derivation with server-side fallback
- **Cross-Platform**: Works on iOS, Android, Windows, macOS, Linux

#### Authentication Flow
1. **Registration**: Email + WebAuthn credential → Stellar keypair derivation → Recovery codes generated
2. **Authentication**: WebAuthn verification → Session creation → Automatic login
3. **Recovery**: Recovery code validation → Temporary session → Setup new passkey required

#### API Endpoints
- `POST /auth/passkey/register/start` - Start registration process
- `POST /auth/passkey/register/verify` - Complete registration
- `POST /auth/passkey/login/start` - Start authentication
- `POST /auth/passkey/login/verify` - Complete authentication
- `POST /auth/passkey/recovery/verify` - Validate recovery code
- `POST /auth/validate-passkey-session` - Validate existing session

#### Frontend Components
- **PasskeyAuthService** (`src/services/passkeyAuth.ts`) - WebAuthn integration
- **AuthContext** (`src/contexts/AuthContext.tsx`) - Authentication state management
- **Login** (`src/components/Login.tsx`) - Unified registration/authenticate/recovery UI
- **ProtectedRoute** (`src/components/ProtectedRoute.tsx`) - Route protection

#### Backend Components
- **Passkey Routes** (`backend/api/routes/passkey.py`) - Authentication endpoints
- **Key Derivation** (`backend/crypto/key_derivation.py`) - Stellar account derivation
- **Recovery Service** (`backend/auth/recovery.py`) - Backup code management
- **Database** (`backend/database.py`) - Passkey schema and session management

#### Security Features
- **Zero-Knowledge**: Private keys never leave user device
- **Hardware Security**: TPM/Secure Enclave protection when available
- **Anti-Replay**: Single-use challenges with 15-minute expiration
- **Domain Binding**: Passkeys bound to specific RP ID/domain
- **Backup Protection**: SHA-256 hashed recovery codes, single-use validation

#### Browser Support
- **Chrome**: 67+ (Android), 108+ (Desktop)
- **Firefox**: 60+ (Android), 114+ (Desktop)
- **Safari**: 14+ (iOS/macOS)
- **Edge**: 108+

#### Migration Notes
- **Magic Links**: Deprecated and removed
- **Database**: Run `python migrate_to_passkeys.py` to update schema
- **Users**: Must re-register with new passkey system
- **Backward Compatibility**: Old components remain but redirect to new system

## Testing

### Passkey Authentication Testing
```bash
# Test passkey modules
python -c "
import api.routes.passkey
from crypto.key_derivation import KeyDerivation
from auth.recovery import RecoveryCodeService
print('✅ All passkey modules working')
"

# Test database schema
python -c "
import database
db = database.DatabaseManager()
print('✅ Database initialized with passkey tables')
"

# Test key derivation
python -c "
from crypto.key_derivation import KeyDerivation
keypair = KeyDerivation.derive_from_server('test', 'cred', b'secret')
print(f'✅ Key derivation works: {keypair.public_key}')
"
```

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