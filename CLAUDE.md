# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Choir** (formerly Tuxedo) is AI research infrastructure for the learning economy.

**Core Product**: Ghostwriter - An AI agent that helps you research, write, and publish—then pays you in stablecoins when your work gets cited.

**Current Phase**: Ghostwriter Foundation (Q4 2025 - 90% Complete)
**Status**: Research infrastructure implemented, citation economics in development
**Architecture**: Multi-model orchestration + optional yield farming (future)

### What Works Today ✅

1. **Ghostwriter Pipeline** - 8-stage research and writing system
2. **Passkey Authentication** - WebAuthn biometric login (production-proven)
3. **Multi-user Isolation** - Separate accounts and sessions per user
4. **Chat Interface** - Conversational AI with tool execution
5. **WebSearch Integration** - Tavily API for real-time web research

### What's Planned 📋

1. **Citation Economics** - Earn stablecoins when your work gets cited
2. **Multichain Vaults** - Optional DeFi yield farming (Base → EVM chains)
3. **Knowledge Base** - Semantic search and citation graph
4. **Anonymous Publishing** - Merit-based discovery without identity

**Important**: No smart contracts are deployed. Vault system and citation rewards are planned but not yet implemented.

---

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
uv sync  # Creates .venv and installs all dependencies

# Always activate environment before working
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start backend server
python main.py

# Test Ghostwriter pipeline
python test_ghostwriter.py

# Test WebSearch integration
python test_websearch.py
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

---

## High-Level Architecture

### System Components

1. **Ghostwriter Pipeline** (`backend/agent/ghostwriter/`) - 8-stage research and writing system
2. **AI Agent Backend** (`backend/agent/core.py`) - LangChain integration and multi-step reasoning
3. **Passkey Auth** (`backend/database_passkeys.py`) - WebAuthn authentication
4. **Account Manager** (`backend/account_manager.py`) - Multi-user isolation
5. **Chat Interface** (`src/components/ChatInterface.tsx`) - Real-time conversational UI
6. **API Layer** (`src/lib/api.ts`) - HTTP client with session management

### Ghostwriter Pipeline Flow

```
User Request → Conductor → Ghostwriter Agent
    ↓
1. RESEARCH (Multi-model web search + knowledge base)
2. DRAFT (Synthesize into narrative)
3. EXTRACT (Atomic claims + citations)
4. VERIFY (3-layer citation verification)
5. CRITIQUE (Critical analysis)
6. REVISE (Fix unsupported claims)
7. RE-VERIFY (Confirm improvements)
8. STYLE (Apply style guide)
    ↓
Published Article → Citation Graph → Rewards (future)
```

---

## Key Configuration

### Environment Variables

**Frontend (.env.local)**:
```bash
PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env)**:
```bash
# Required for Ghostwriter
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
TAVILY_API_KEY=your_tavily_key

# Optional - for legacy Stellar features
OPENAI_API_KEY=your_api_key  # For basic chat agent
OPENAI_BASE_URL=https://api.redpill.ai/v1  # Or https://api.openai.com/v1

# Database
DATABASE_URL=sqlite:///./choir.db

# Authentication
SESSION_SECRET_KEY=your_random_secret_key_here
```

### Critical Architecture Notes

**What's Implemented**:
- ✅ Ghostwriter 8-stage pipeline (~2000 lines)
- ✅ Passkey authentication (WebAuthn)
- ✅ Multi-user account system
- ✅ Chat interface with AI agent
- ✅ WebSearch integration (Tavily API)
- ✅ Tool execution framework

**What's NOT Implemented (Yet)**:
- ❌ Smart contracts (no deployments)
- ❌ Citation reward system
- ❌ Knowledge base / vector search
- ❌ Vault system
- ❌ DeFi integrations
- ❌ Multichain support

**Legacy Code** (from Stellar hackathon, still present but not core):
- `backend/stellar_tools.py` - Stellar blockchain tools
- `backend/blend_pool_tools.py` - Blend Capital (Stellar DeFi)
- `backend/vault_tools.py` - References undeployed vault contracts

These files exist for reference but are not part of the current Choir vision. See `docs/MULTICHAIN_EVM_MIGRATION_PLAN.md` for future multichain architecture.

---

## Ghostwriter Implementation

### Core Pipeline

**Location**: `backend/agent/ghostwriter/pipeline.py` (708 lines)

**8 Stages**:

1. **Research** - Parallel subagents gather 3-5 sources using Tavily websearch
2. **Draft** - Synthesize research into coherent document
3. **Extract** - Extract atomic claims with citations
4. **Verify** - 3-layer verification (URL → content → Claude validation)
5. **Critique** - Critical analysis of weak arguments
6. **Revise** - Fix unsupported claims and incorporate critique
7. **Re-verify** - Confirm revised claims are properly supported
8. **Style** - Apply user's style guide (technical, academic, conversational, etc.)

**Models Used**:
- **AWS Bedrock Claude 4.5 Haiku** - Fast research and extraction
- **AWS Bedrock Claude 4.5 Sonnet** - Deep reasoning and synthesis

### Configuration

**Setup Guide**: `backend/agent/ghostwriter/OPENHANDS_SDK_BEDROCK_CONFIGURATION.md`

**Key Details**:
- Uses OpenHands SDK (built on LiteLLM)
- Requires AWS Bedrock access (IAM permissions for Claude models)
- Tavily API for web search
- Session-based file management

### Style Guides

**Location**: `backend/agent/ghostwriter/style_guides/`

Available styles:
- `technical.md` - Technical documentation style
- `academic.md` - Academic paper style
- `conversational.md` - Blog/essay style
- `defi_report.md` - DeFi research report style

### Testing Ghostwriter

```bash
# From backend directory
source .venv/bin/activate

# Run full pipeline test
python test_ghostwriter.py

# Test websearch only
python test_websearch.py
```

Expected output:
- Session created in `/tmp/ghostwriter_test_sessions/`
- 8 stages execute sequentially
- Final report generated with verification metrics
- Citations validated and included

---

## Passkey Authentication

### Implementation

**Database**: `backend/database_passkeys.py`
**API Routes**: `backend/api/routes/passkey_auth.py`
**Frontend**: `src/services/passkeyAuth.ts`, `src/contexts/AuthContext.tsx`

### Features

- ✅ WebAuthn biometric authentication (fingerprint, Face ID)
- ✅ Session-based authorization
- ✅ Recovery codes (backup authentication)
- ✅ Email recovery (via SendGrid)
- ✅ Multi-device support
- ✅ Production-tested and working

### Flow

```
User → Register with Passkey → Store credential
    ↓
Login → Biometric challenge → Session token
    ↓
API requests → Bearer token → Authenticated
```

**Security**: Passkeys use public-key cryptography (FIDO2/WebAuthn standard). Private keys never leave the device.

---

## Frontend Architecture

### Key Components

- `ChatInterface.tsx` - Main AI chat interface with Ghostwriter
- `WalletContext.tsx` - Authentication and session management
- `api.ts` - HTTP client with session token injection

### Tech Stack

- Vite 7.1 + React 19 + TypeScript 5.9
- TanStack React Query for server state
- Axios for HTTP communication

### State Management

- React Context for auth state
- TanStack Query for server data
- Local state for UI

---

## Backend Architecture

### Key Files

**Core Infrastructure**:
- `main.py` - FastAPI app entry point
- `app.py` - Application factory pattern
- `agent/core.py` - LangChain agent orchestration
- `agent/tool_factory.py` - Per-request tool creation with user isolation
- `account_manager.py` - Multi-user account management

**Ghostwriter**:
- `agent/ghostwriter/pipeline.py` - 8-stage research pipeline
- `agent/ghostwriter/tool.py` - LangChain tool wrapper
- `agent/ghostwriter/verify.py` - Citation verification engine
- `agent/ghostwriter/websearch_tool.py` - Tavily integration

**Authentication**:
- `database_passkeys.py` - Passkey database schema
- `api/routes/passkey_auth.py` - Auth endpoints
- `services/email.py` - SendGrid email service

**Legacy** (from Stellar hackathon):
- `stellar_tools.py` - Stellar blockchain operations
- `blend_pool_tools.py` - Blend Capital DeFi
- `vault_tools.py` - Undeployed vault contracts

### Tech Stack

- FastAPI + Pydantic
- LangChain + OpenAI (for basic chat agent)
- OpenHands SDK + AWS Bedrock (for Ghostwriter)
- SQLite database
- uvicorn ASGI server

---

## Testing

### Ghostwriter Testing

```bash
# From backend directory
cd backend
source .venv/bin/activate

# Full pipeline test
python test_ghostwriter.py

# WebSearch integration test
python test_websearch.py
```

**Test Output**:
- Session directory created
- 8 stages execute with progress logging
- Verification metrics displayed
- Final report saved to session directory

### Frontend Testing

```bash
# Start both services
# Terminal 1: npm run dev
# Terminal 2: cd backend && source .venv/bin/activate && python main.py

# Test in browser
# 1. Register with passkey
# 2. Try Ghostwriter: "Research yield farming on Base"
# 3. Watch 8-stage pipeline execute
# 4. See final report with citations
```

### Common Test Scenarios

**Ghostwriter**:
- "Research DeFi yield opportunities on Base blockchain"
- "Write a technical analysis of Aave V3 vs Compound V3"
- "Compare Stellar and Ethereum L2s for DeFi applications"

**Authentication**:
- Register with biometric passkey
- Login with passkey
- Test recovery codes
- Multi-device registration

---

## Important Patterns

### Ghostwriter Tool Integration

**Location**: `backend/agent/tool_factory.py`

Ghostwriter is exposed as a LangChain tool that agents can invoke:

```python
from agent.ghostwriter.tool import get_ghostwriter_tool

# Create tool for specific user
ghostwriter_tool = get_ghostwriter_tool(user_id="user_123")

# Agent can now call Ghostwriter
result = await ghostwriter_tool.ainvoke({
    "topic": "DeFi yield farming",
    "style_guide": "defi_report"
})
```

### User Isolation

All tools are created per-request with user context:

```python
# backend/agent/tool_factory.py
def create_user_tools(user_id: str) -> List[Tool]:
    """Create tools with user_id injected for isolation"""
    return [
        get_ghostwriter_tool(user_id),
        # Future: other tools here
    ]
```

### Error Handling

- Frontend: Graceful degradation with user notifications
- Backend: Try/catch blocks with structured error responses
- Ghostwriter: Stage-level error recovery with fallbacks

---

## Development Notes

### Virtual Environment Management

**UV Best Practices**:
```bash
# ✅ RECOMMENDED - Let UV manage everything
uv sync       # UV creates proper .venv with correct structure
source .venv/bin/activate
```

**Why UV**:
- Creates virtual environments with optimized structure
- Handles both environment creation AND package management
- Automatic dependency resolution from pyproject.toml
- Faster than pip, better caching

### Port Configuration

- Frontend: 5173 (Vite default)
- Backend: 8000 (FastAPI)

### API Communication

- Frontend → Backend: HTTP POST to `/chat` endpoint
- Request format: `{ message, history, session_token }`
- Response format: `{ response, success, error? }`
- Health checks: GET `/health` endpoint

---

## Production Status

**Implemented (90%)**:
1. ✅ Ghostwriter 8-stage pipeline
2. ✅ Passkey authentication system
3. ✅ Multi-user isolation
4. ✅ Chat interface with AI agent
5. ✅ WebSearch integration (Tavily)
6. ✅ Session management

**In Development (10%)**:
1. 🚧 Citation economics system
2. 🚧 Knowledge base / vector search
3. 🚧 Semantic citation detection

**Planned (Not Started)**:
1. ❌ Smart contract deployment
2. ❌ Multichain vault system
3. ❌ DeFi yield farming
4. ❌ Cross-chain operations

**Current Scope**:
- Research and writing infrastructure (Ghostwriter)
- Passkey authentication for web apps
- Multi-user AI agent system
- Foundation for future citation economics

---

## File Locations for Common Tasks

### Ghostwriter Modifications

- **Core pipeline**: `backend/agent/ghostwriter/pipeline.py`
- **Verification**: `backend/agent/ghostwriter/verify.py`
- **WebSearch**: `backend/agent/ghostwriter/websearch_tool.py`
- **Tool wrapper**: `backend/agent/ghostwriter/tool.py`
- **Prompts**: `backend/agent/ghostwriter/prompts/`
- **Style guides**: `backend/agent/ghostwriter/style_guides/`

### AI Agent Modifications

- **Core logic**: `backend/agent/core.py`
- **Tool factory**: `backend/agent/tool_factory.py`
- **Tool definitions**: `backend/agent/tools.py`

### Frontend Changes

- **Chat interface**: `src/components/ChatInterface.tsx`
- **Auth context**: `src/contexts/AuthContext.tsx`
- **API client**: `src/lib/api.ts`
- **Passkey service**: `src/services/passkeyAuth.ts`

### Configuration Updates

- **Environment setup**: `.env.local`, `backend/.env`
- **Dependencies**: `package.json`, `backend/pyproject.toml`
- **Database schema**: `backend/database_passkeys.py`

---

## Future Architecture (Multichain)

**See**: `docs/MULTICHAIN_EVM_MIGRATION_PLAN.md` for detailed migration plan

**Vision**: Transition from research-only to research + optional DeFi

**Phases**:
1. ✅ Phase 1: Ghostwriter foundation (current)
2. 📋 Phase 2: Citation economics (Q1 2026)
3. 📋 Phase 3: Knowledge base (Q1 2026)
4. 📋 Phase 4: Multichain vaults (Q2 2026)
5. 📋 Phase 5: DeFi yield farming (Q2-Q3 2026)

**Key Principles**:
- Research infrastructure comes first
- Citation rewards funded by optional DeFi performance fees
- Most users never deploy capital, earn through citations only
- Multichain from day 1 (Base → Arbitrum → Optimism)

---

## Quick Reference for Common Issues

**Backend not starting**:
- Check `backend/.env` for AWS credentials
- Verify `uv sync` completed successfully
- Ensure port 8000 is available

**Frontend can't reach backend**:
- Verify backend is running on port 8000
- Check `PUBLIC_API_URL` in `.env.local`
- Check CORS settings in `backend/app.py`

**Ghostwriter errors**:
- Verify AWS Bedrock access (IAM permissions)
- Check TAVILY_API_KEY in `backend/.env`
- Review `backend/agent/ghostwriter/OPENHANDS_SDK_BEDROCK_CONFIGURATION.md`

**Passkey auth not working**:
- Passkeys require HTTPS (or localhost)
- Check browser compatibility (WebAuthn support)
- Verify database migrations ran

---

## Additional Resources

**Documentation**:
- `README.md` - Project overview (Choir vision)
- `UNIFIED_VISION.md` - Complete vision document
- `docs/MULTICHAIN_EVM_MIGRATION_PLAN.md` - Future architecture
- `docs/CHOIR_WHITEPAPER.md` - Economic model
- `docs/GHOSTWRITER_ARCHITECTURE_OPENHANDS_SDK.md` - Ghostwriter architecture
- `docs/PASSKEY_ARCHITECTURE_V2.md` - Authentication system

**Important Notes**:
- **No deployed smart contracts** - vault system is planned but not live
- **Stellar code is legacy** - from hackathon phase, not core to Choir
- **Ghostwriter is the focus** - research infrastructure, not DeFi (yet)
- **Multichain is planned** - see migration plan for timeline

**Development Philosophy**:
- Research infrastructure first, DeFi second
- Citation economics over attention economics
- Merit-based discovery over identity-based distribution
- Intellectual contribution as productive capital