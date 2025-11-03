# Tuxedo Code Reorganization Plan

**Vision**: Transform Tuxedo into a clean, scalable agent-first DeFi interface that can integrate with broader ecosystems like Choir.

**Context**: This plan supports both immediate hackathon success and long-term evolution toward multi-agent social DeFi experiences.

## 🎯 Objectives

### Immediate (Hackathon Week)
1. **Remove wallet dependencies** and establish agent-first paradigm
2. **Clean up project structure** for professional presentation
3. **Fix testing organization** (move tests out of root)
4. **Remove TUX farming code** and focus on real protocols

### Medium-term (Post-Hackathon)
1. **Modular architecture** supporting multiple agents
2. **Clean separation** between web app and agent core
3. **Extensible protocol integration** framework
4. **Production-ready security** and configuration

### Long-term (Choir Integration)
1. **Multi-agent architecture** supporting social features
2. **API-first design** for mobile/web client support
3. **Plugin system** for different agent capabilities
4. **Cross-protocol abstraction** for multi-chain support

## 📊 Current State Analysis

### Critical Issues
- **Backend main.py**: 2000+ lines, agent logic mixed with API
- **Frontend wallet dependencies**: WalletProvider throughout component tree
- **Test files in root**: test_*.py files at project root (unprofessional)
- **TUX farming mock code**: Entire mock system needs removal
- **Configuration scattered**: Hardcoded values in 15+ locations
- **Monolithic structure**: Difficult to extend or modify

### Files Needing Immediate Attention
- `backend/main.py` - Split into agent core, API, and tools
- `src/providers/WalletProvider.tsx` - Remove entirely
- `src/components/` - Remove wallet dependencies from all components
- `test_*.py` (root) - Move to `tests/` directory
- `backend/tux_farming.py` - Remove entire module
- Configuration files - Centralize and standardize

## 🏗️ Target Architecture

### Project Structure
```
tuxedo/
├── README.md                     # Main project overview
├── HACKATHON_FINAL_PLAN.md       # Current hackathon strategy
├── CLAUDE.md                     # AI assistant development guide
├── ENVIRONMENT_SETUP.md          # Environment configuration
├── SECURITY.md                   # Security considerations
├── PHALA_DEPLOYMENT.md           # Phala deployment guide
├── CODE_REORGANIZATION_PLAN.md   # This document
├── .env.example                  # Environment template
├── .env.backend.example          # Backend env template
├── .env.frontend.example         # Frontend env template
├── render.yaml                   # Render deployment config
├── docker-compose.yaml           # Local development
├── scripts/                      # Development tools
│   ├── dev.sh                    # Development launcher
│   └── dev-improved.sh           # Improved dev launcher
├── contracts/                    # Smart contracts
│   └── (Soroban contracts)
├── backend/                      # FastAPI backend
│   ├── README.md
│   ├── main.py                   # Entry point (simplified)
│   ├── app.py                    # FastAPI app setup
│   ├── .env.example              # Backend env template
│   ├── .env.production.template  # Production template
│   ├── agent/                    # AI agent core
│   │   ├── __init__.py
│   │   ├── core.py               # Main agent logic
│   │   ├── conversation.py       # Chat management
│   │   ├── tools.py              # Tool orchestration
│   │   ├── memory.py             # Context management
│   │   └── prompts.py            # Agent prompts
│   ├── tools/                    # Agent tools
│   │   ├── __init__.py
│   │   ├── base.py               # Base tool interface
│   │   ├── stellar/              # Stellar ecosystem tools
│   │   │   ├── __init__.py
│   │   │   ├── account_manager.py
│   │   │   ├── trading.py
│   │   │   ├── market_data.py
│   │   │   ├── blend_protocol.py
│   │   │   ├── defindex_vaults.py
│   │   │   └── utilities.py
│   │   └── agent/                # Agent management tools
│   │       ├── __init__.py
│   │       ├── account_management.py
│   │       └── security.py
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py           # Pydantic settings
│   │   ├── networks.py           # Network configurations
│   │   ├── contracts.py          # Contract addresses
│   │   └── security.py           # Security parameters
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py           # Chat endpoints
│   │   │   ├── agent.py           # Agent management
│   │   │   ├── health.py         # Health checks
│   │   │   └── tools.py          # Tool execution
│   │   ├── middleware.py         # CORS, auth, logging
│   │   └── schemas.py            # Pydantic models
│   ├── services/                 # Business services
│   │   ├── __init__.py
│   │   ├── stellar_client.py     # Stellar SDK wrapper
│   │   ├── llm_client.py         # LLM abstraction
│   │   ├── cache.py              # Caching service
│   │   └── key_manager.py        # Agent key management
│   ├── database/                 # Database management
│   │   ├── __init__.py
│   │   ├── models.py             # Database models
│   │   └── migrations/           # Database migrations
│   └── tests/                    # Backend tests
│       ├── __init__.py
│       ├── conftest.py           # Test configuration
│       ├── test_agent.py
│       ├── test_tools/
│       │   ├── test_stellar.py
│       │   └── test_agent_management.py
│       ├── test_api/
│       │   ├── test_chat.py
│       │   └── test_agent.py
│       └── integration/
│           └── test_workflows.py
├── src/                          # Frontend (React/TypeScript)
│   ├── main.tsx                  # App entry point
│   ├── App.tsx                   # Main app component
│   ├── .env.example              # Frontend env template
│   ├── components/               # React components
│   │   ├── common/               # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── index.ts
│   │   ├── agent/                # Agent management UI
│   │   │   ├── AgentProvider.tsx  # Replace WalletProvider
│   │   │   ├── AccountManager.tsx # Account management
│   │   │   ├── AccountList.tsx    # Account list
│   │   │   ├── CreateAccount.tsx  # Account creation
│   │   │   └── index.ts
│   │   ├── chat/                 # Chat functionality
│   │   │   ├── ChatInterface.tsx  # Main chat UI
│   │   │   ├── MessageList.tsx    # Message display
│   │   │   ├── MessageInput.tsx   # Input handling
│   │   │   ├── ToolIndicator.tsx  # Tool execution status
│   │   │   └── index.ts
│   │   ├── dashboard/            # Dashboard components
│   │   │   ├── Dashboard.tsx      # Main dashboard
│   │   │   ├── PoolDashboard.tsx  # Blend pools
│   │   │   ├── VaultDashboard.tsx # DeFindex vaults
│   │   │   ├── PortfolioView.tsx  # Portfolio overview
│   │   │   └── index.ts
│   │   └── layout/               # Layout components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       ├── Footer.tsx
│   │       └── index.ts
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAgent.ts           # Agent state management
│   │   ├── useChat.ts            # Chat functionality
│   │   ├── useAccounts.ts        # Account management
│   │   ├── useApi.ts             # API client
│   │   ├── useBlendPools.ts      # Blend pool data
│   │   └── index.ts
│   ├── services/                 # Frontend services
│   │   ├── agentService.ts       # Agent API client
│   │   ├── chatService.ts        # Chat API client
│   │   ├── poolService.ts        # Pool data service
│   │   └── index.ts
│   ├── stores/                   # State management
│   │   ├── agentStore.ts         # Agent state
│   │   ├── chatStore.ts          # Chat state
│   │   ├── accountStore.ts       # Account state
│   │   └── index.ts
│   ├── config/                   # Frontend configuration
│   │   ├── constants.ts          # App constants
│   │   ├── networks.ts           # Network config
│   │   ├── endpoints.ts          # API endpoints
│   │   └── environment.ts        # Environment handling
│   ├── types/                    # TypeScript definitions
│   │   ├── agent.ts              # Agent types
│   │   ├── chat.ts               # Chat types
│   │   ├── stellar.ts            # Stellar types
│   │   ├── api.ts                # API types
│   │   └── index.ts
│   ├── utils/                    # Utility functions
│   │   ├── format.ts             # Data formatting
│   │   ├── validation.ts         # Input validation
│   │   ├── helpers.ts            # Helper functions
│   │   └── index.ts
│   └── tests/                    # Frontend tests
│       ├── setup.ts              # Test setup
│       ├── __mocks__/            # Mock files
│       ├── components/
│       │   ├── agent/
│       │   ├── chat/
│       │   └── dashboard/
│       ├── hooks/
│       └── utils/
├── tests/                        # Integration and E2E tests
│   ├── integration/              # Integration tests
│   │   ├── test_agent_workflows.py
│   │   ├── test_chat_flows.py
│   │   └── test_transaction_flows.py
│   ├── e2e/                      # End-to-end tests
│   │   ├── test_user_journeys.py
│   │   └── test_critical_paths.py
│   └── fixtures/                 # Test data
│       ├── accounts.json
│       ├── transactions.json
│       └── conversations.json
└── docs/                        # Additional documentation
    ├── API.md                     # API documentation
    ├── DEPLOYMENT.md              # Deployment guides
    └── DEVELOPMENT.md             # Development setup
```

## 📋 Implementation Plan

### Phase 1: Critical Cleanup (Hackathon Day 1)

#### 1.1 Remove Wallet Dependencies
**Priority**: CRITICAL for hackathon success

**Actions**:
```bash
# Remove wallet provider system
rm src/providers/WalletProvider.tsx
rm src/components/WalletButton.tsx
rm src/util/wallet.ts

# Create agent provider
# src/providers/AgentProvider.tsx
export const AgentProvider = ({ children }: { children: React.ReactNode }) => {
  const [accounts, setAccounts] = useState<string[]>([]);
  const [activeAccount, setActiveAccount] = useState<string>("");

  const createAccount = async () => {
    const response = await fetch('/api/agent/create-account', { method: 'POST' });
    const newAccount = await response.json();
    setAccounts(prev => [...prev, newAccount.address]);
    return newAccount.address;
  };

  return (
    <AgentContext.Provider value={{ accounts, activeAccount, setActiveAccount, createAccount }}>
      {children}
    </AgentContext.Provider>
  );
};
```

#### 1.2 Fix Testing Structure
**Priority**: HIGH for professional appearance

**Actions**:
```bash
# Create proper test structure
mkdir -p tests/{integration,e2e,fixtures}

# Move root test files to appropriate locations
mv test_agent.py backend/tests/
mv test_agent_with_tools.py backend/tests/test_tools/
mv test_multiturn.py backend/tests/test_chat/
mv test_multiturn_with_tools.py backend/tests/test_chat/
mv test_wallet_fix.py backend/tests/test_agent_management/
```

#### 1.3 Remove TUX Farming System
**Priority**: HIGH for hackathon focus

**Actions**:
```bash
# Remove TUX farming components
rm -rf src/components/tux_farming/
rm src/hooks/useTuxFarming.ts
rm src/components/dashboard/TuxMiningDashboard.tsx

# Remove TUX farming backend
rm backend/tux_farming.py
rm backend/tux_farming_transactions.py

# Remove TUX farming tests
rm test_mock_farming.py
rm test_tux_farming.py
```

### Phase 2: Backend Refactoring (Hackathon Day 1-2)

#### 2.1 Split main.py into Focused Modules
**Target**: Reduce from 2000+ lines to ~200 lines

**Current structure issues**:
- Agent logic mixed with FastAPI setup
- Tool definitions scattered throughout
- Configuration hardcoded
- No clear separation of concerns

**New structure**:
```python
# backend/main.py - Simplified entry point
from app import create_app
from config.settings import settings
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

# backend/app.py - FastAPI application setup
from fastapi import FastAPI
from api.routes import chat, agent, health, tools
from api.middleware import setup_middleware
from config.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="Tuxedo AI Agent",
        description="Agent-first DeFi interface for Stellar ecosystem",
        version="1.0.0"
    )

    # Setup middleware
    setup_middleware(app)

    # Include routers
    app.include_router(chat.router, prefix="/chat")
    app.include_router(agent.router, prefix="/agent")
    app.include_router(health.router, prefix="/health")
    app.include_router(tools.router, prefix="/tools")

    return app
```

#### 2.2 Extract Agent Core Logic
**Target**: Clean agent module focused on AI reasoning

```python
# backend/agent/core.py
from typing import List, Dict, Optional, Any
from langchain_core.messages import HumanMessage, AIMessage
from services.llm_client import LLMClient
from tools.tool_orchestrator import ToolOrchestrator
from agent.conversation import ConversationManager
from agent.memory import MemoryManager

class TuxedoAgent:
    """Main AI agent for DeFi operations"""

    def __init__(self, llm_client: LLMClient, tools: List):
        self.llm_client = llm_client
        self.tools = tools
        self.conversation_manager = ConversationManager()
        self.tool_orchestrator = ToolOrchestrator(tools)
        self.memory_manager = MemoryManager()

    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        agent_account: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process user message and generate response"""

        # Load conversation context
        conversation = await self.conversation_manager.get_or_create(
            conversation_id, agent_account
        )

        # Add human message
        conversation.add_message(HumanMessage(content=message))

        # Get relevant memory
        relevant_memory = await self.memory_manager.get_relevant_context(
            message, agent_account
        )

        # Build agent context
        agent_context = {
            "agent_account": agent_account,
            "conversation_history": conversation.messages,
            "relevant_memory": relevant_memory,
            "current_context": context or {}
        }

        # Process with LLM and tools
        response = await self.llm_client.process_with_tools(
            message,
            self.tools,
            agent_context
        )

        # Add AI response to conversation
        conversation.add_message(AIMessage(content=response["content"]))

        # Save conversation
        await self.conversation_manager.save(conversation)

        # Update memory if needed
        await self.memory_manager.update_memory(
            message, response, agent_account
        )

        return response
```

#### 2.3 Create Agent Management Tools
**Target**: Tools for agent-controlled account management

```python
# backend/tools/agent/account_management.py
from typing import Dict, Optional
from services.key_manager import KeyManager
from services.stellar_client import StellarClient
from tools.base import BaseTool

class AccountManagementTool(BaseTool):
    """Agent-controlled account management"""

    def __init__(self, key_manager: KeyManager, stellar_client: StellarClient):
        self.key_manager = key_manager
        self.stellar_client = stellar_client

    async def create_account(
        self,
        account_name: Optional[str] = None,
        initial_funding: bool = True
    ) -> Dict[str, str]:
        """Create new agent-controlled account"""

        # Generate new keypair
        keypair = self.key_manager.create_random_keypair()

        # Store with metadata
        account_data = {
            "address": keypair.public_key,
            "name": account_name or f"Account {len(self.list_accounts()) + 1}",
            "created_at": datetime.utcnow().isoformat(),
            "initial_funding": initial_funding
        }

        self.key_manager.store_account(keypair.public_key, keypair.secret, account_data)

        # Fund with testnet lumens if requested
        if initial_funding:
            await self.stellar_client.fund_account(keypair.public_key)

        return {
            "address": keypair.public_key,
            "name": account_data["name"],
            "funded": initial_funding,
            "network": "testnet"
        }

    async def list_accounts(self) -> List[Dict[str, str]]:
        """List all agent-controlled accounts"""
        return self.key_manager.list_accounts_with_metadata()

    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get detailed account information"""
        if not self.key_manager.has_account(address):
            raise ValueError(f"Account {address} not found")

        # Get stellar account data
        account_data = await self.stellar_client.get_account(address)
        stored_metadata = self.key_manager.get_account_metadata(address)

        return {
            "address": address,
            "balance": account_data.get("balance", 0),
            "sequence": account_data.get("sequence", 0),
            "metadata": stored_metadata,
            "network": "testnet"
        }
```

### Phase 3: Frontend Refactoring (Hackathon Day 2-3)

#### 3.1 Create Agent-First UI Components
**Target**: Replace wallet UI with agent management UI

```typescript
// src/components/agent/AccountManager.tsx
import React, { useState, useEffect } from 'react';
import { useAgent } from '../../hooks/useAgent';
import { CreateAccount } from './CreateAccount';
import { AccountList } from './AccountList';

export const AccountManager: React.FC = () => {
  const { accounts, activeAccount, createAccount, setActiveAccount } = useAgent();
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateAccount = async (name?: string) => {
    setIsCreating(true);
    try {
      const newAddress = await createAccount(name);
      setActiveAccount(newAddress);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="account-manager">
      <div className="account-manager-header">
        <h3>Agent Accounts</h3>
        <button
          onClick={() => setIsCreating(true)}
          disabled={isCreating}
          className="create-account-btn"
        >
          {isCreating ? 'Creating...' : 'Create Account'}
        </button>
      </div>

      <AccountList
        accounts={accounts}
        activeAccount={activeAccount}
        onSelectAccount={setActiveAccount}
      />

      {isCreating && (
        <CreateAccount
          onCreate={handleCreateAccount}
          onCancel={() => setIsCreating(false)}
        />
      )}
    </div>
  );
};
```

#### 3.2 Create Agent State Management Hook
**Target**: Replace wallet hooks with agent hooks

```typescript
// src/hooks/useAgent.ts
import { useState, useEffect, useCallback } from 'react';
import { agentService } from '../services/agentService';

export interface AgentAccount {
  address: string;
  name: string;
  balance: number;
  network: string;
  created_at: string;
}

export const useAgent = () => {
  const [accounts, setAccounts] = useState<AgentAccount[]>([]);
  const [activeAccount, setActiveAccount] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load accounts on mount
  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const accountList = await agentService.getAccounts();
      setAccounts(accountList);

      // Set active account if none selected
      if (!activeAccount && accountList.length > 0) {
        setActiveAccount(accountList[0].address);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load accounts');
    } finally {
      setIsLoading(false);
    }
  }, [activeAccount]);

  const createAccount = useCallback(async (name?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const newAccount = await agentService.createAccount(name);
      setAccounts(prev => [...prev, newAccount]);
      setActiveAccount(newAccount.address);
      return newAccount.address;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create account');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    accounts,
    activeAccount,
    setActiveAccount,
    createAccount,
    isLoading,
    error,
    refreshAccounts: loadAccounts
  };
};
```

### Phase 4: Configuration Management (Hackathon Day 3)

#### 4.1 Centralize Configuration
**Target**: Single source of truth for all settings

```python
# backend/config/settings.py
from pydantic import BaseSettings, validator
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: str
    openai_base_url: str = "https://openrouter.ai/api/v1"
    primary_model: str = "openai/gpt-oss-120b:exacto"

    # Stellar Configuration
    stellar_network: str = "testnet"
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    friendbot_url: str = "https://friendbot.stellar.org"

    # Agent Configuration
    max_accounts_per_agent: int = 10
    default_account_funding: float = 10000  # stroops
    agent_conversation_limit: int = 100

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]

    # Security Configuration
    encryption_key_path: str = ".encryption_key"
    keystore_path: str = ".agent_keystore.json"

    # External Services
    defindex_api_key: Optional[str] = None

    @validator('stellar_network')
    def validate_network(cls, v):
        if v not in ['testnet', 'mainnet', 'futurenet', 'local']:
            raise ValueError('Invalid network')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

```typescript
// src/config/constants.ts
export const NETWORK_CONFIG = {
  testnet: {
    horizon: 'https://horizon-testnet.stellar.org',
    rpc: 'https://soroban-testnet.stellar.org',
    network: 'Test SDF Network ; September 2015',
    friendbot: 'https://friendbot.stellar.org'
  },
  mainnet: {
    horizon: 'https://horizon.stellar.org',
    rpc: 'https://soroban.stellar.org',
    network: 'Public Global Stellar Network ; September 2015',
    friendbot: null
  }
};

export const API_ENDPOINTS = {
  chat: '/api/chat',
  agent: '/api/agent',
  health: '/api/health',
  tools: '/api/tools'
};

export const AGENT_CONFIG = {
  maxAccounts: 10,
  conversationLimit: 100,
  defaultFunding: 10000,
  messageTimeout: 30000
};

export const UI_CONFIG = {
  maxMessages: 100,
  typingIndicatorDelay: 500,
  toolExecutionTimeout: 30000,
  refreshInterval: 30000
};
```

### Phase 5: Testing Infrastructure (Post-Hackathon)

#### 5.1 Comprehensive Test Structure
**Target**: Professional testing setup with proper organization

```python
# backend/tests/conftest.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from agent.core import TuxedoAgent
from services.llm_client import LLMClient
from tools.stellar.account_manager import AccountManagerTool
from services.key_manager import KeyManager

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_key_manager():
    """Mock key manager for testing"""
    manager = Mock(spec=KeyManager)
    manager.create_random_keypair = Mock()
    manager.store_account = Mock()
    manager.list_accounts = Mock(return_value=[])
    return manager

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing"""
    client = AsyncMock(spec=LLMClient)
    client.process_with_tools = AsyncMock(return_value={
        "content": "Test response",
        "tools_used": [],
        "success": True
    })
    return client

@pytest.fixture
def test_agent(mock_llm_client):
    """Test agent with mocked dependencies"""
    tools = [Mock()]
    return TuxedoAgent(mock_llm_client, tools)
```

#### 5.2 Integration Test Framework
**Target**: Test complete user workflows

```python
# tests/integration/test_agent_workflows.py
import pytest
from fastapi.testclient import TestClient
from app import create_app

app = create_app()
client = TestClient(app)

class TestAgentWorkflows:
    """Integration tests for complete agent workflows"""

    def test_account_creation_workflow(self):
        """Test complete account creation flow"""

        # Create account via API
        response = client.post("/api/agent/create-account", json={
            "name": "Test Account",
            "initial_funding": True
        })

        assert response.status_code == 200
        account_data = response.json()
        assert "address" in account_data
        assert account_data["name"] == "Test Account"

        # Verify account appears in list
        list_response = client.get("/api/agent/accounts")
        assert list_response.status_code == 200
        accounts = list_response.json()
        assert len(accounts) > 0
        assert any(acc["address"] == account_data["address"] for acc in accounts)

    def test_chat_with_agent_workflow(self):
        """Test complete chat interaction flow"""

        # Create account first
        account_response = client.post("/api/agent/create-account")
        account_address = account_response.json()["address"]

        # Send chat message
        chat_response = client.post("/api/chat", json={
            "message": "What is my account balance?",
            "agent_account": account_address
        })

        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        assert "response" in chat_data
        assert "success" in chat_data
        assert chat_data["success"] is True
```

## 🗓️ Implementation Timeline

### Hackathon Week (Days 1-5)
- **Day 1**: Critical cleanup, wallet removal, testing structure
- **Day 2**: Backend refactoring, agent core extraction
- **Day 3**: Frontend agent UI, configuration management
- **Day 4**: Polish and optimization, bug fixes
- **Day 5**: Demo preparation, testing, documentation

### Week 2-3: Production Readiness
- **Backend**: Complete modularization, comprehensive testing
- **Frontend**: Component optimization, state management refinement
- **Configuration**: Environment management, deployment setup

### Week 4-6: Advanced Features
- **Multi-agent support**: Foundation for Choir integration
- **Protocol expansion**: More DeFi protocols
- **Advanced security**: TEE preparation, encryption

### Month 2-3: Choir Integration
- **API abstraction**: Multi-client support (web/mobile)
- **Social features**: Agent sharing and collaboration
- **Cross-chain preparation**: Multi-network support

## 📈 Expected Benefits

### Immediate Benefits (Hackathon)
- **Professional appearance**: Proper file organization, no root-level tests
- **Clear innovation**: Agent-first paradigm immediately obvious
- **Focused demo**: No wallet distractions, pure agent experience
- **Clean codebase**: Easy to explain and demonstrate

### Medium-term Benefits (Production)
- **Maintainability**: Clear separation of concerns, modular architecture
- **Extensibility**: Easy to add new protocols and features
- **Testability**: Comprehensive test coverage, reliable deployment
- **Developer experience**: Intuitive structure, easy onboarding

### Long-term Benefits (Choir Integration)
- **Multi-agent architecture**: Foundation for social agent interactions
- **API-first design**: Support for web, mobile, and future clients
- **Scalable security**: Ready for TEE and advanced encryption
- **Protocol flexibility**: Easy cross-chain and protocol expansion

## 🎯 Success Metrics

### Hackathon Success Criteria
- [ ] Wallet dependencies completely removed
- [ ] Agent account management working seamlessly
- [ ] Professional project structure (no root tests)
- [ ] Clean, impressive demo showcasing innovation
- [ ] Clear differentiation from wallet-dependent projects

### Code Quality Metrics
- [ ] Average file size: < 300 lines
- [ ] Test coverage: > 80% for critical components
- [ ] Configuration: Centralized, environment-specific
- [ ] Documentation: Clear, up-to-date, comprehensive

### Developer Experience Metrics
- [ ] New developer onboarding: < 2 hours
- [ ] Feature implementation time: Reduced by 50%
- [ ] Bug fix time: Reduced by 60%
- [ ] Code review time: Reduced by 40%

## 🔄 Migration Strategy

### Incremental Approach
1. **Critical path first**: Focus on hackathon-winning features
2. **Parallel development**: New structure alongside existing code
3. **Gradual migration**: Move functionality piece by piece
4. **Continuous testing**: Test at each step to prevent regressions
5. **Documentation updates**: Keep docs in sync with changes

### Risk Mitigation
- **Backup strategy**: Git branches for each major change
- **Rollback plan**: Quick revert to working state
- **Testing pipeline**: Automated tests prevent breaking changes
- **Code review**: All changes require review
- **Feature flags**: Switch between old/new implementations safely

## 📝 Next Steps

### Immediate (This Week)
1. **Start with wallet removal** - Highest impact for hackathon
2. **Fix testing structure** - Professional appearance
3. **Extract agent core** - Clean separation of concerns
4. **Create agent UI** - Replace wallet interface

### Post-Hackathon
1. **Complete modularization** - Full backend refactoring
2. **Add comprehensive testing** - Production readiness
3. **Optimize for deployment** - Phala/cloud preparation
4. **Plan Choir integration** - Multi-agent architecture

This reorganization transforms Tuxedo into a professional, scalable, agent-first DeFi interface ready for hackathon success and future ecosystem integration.