# Code Reorganization Plan

This document outlines a systematic plan to reorganize the Tuxedo codebase for better maintainability, scalability, and developer experience.

## 🎯 Objectives

1. **Improve maintainability** by splitting large files into focused modules
2. **Reduce complexity** through clear separation of concerns
3. **Enhance developer experience** with better code organization
4. **Support scaling** by creating extensible architecture
5. **Standardize patterns** across frontend and backend

## 📊 Current State Analysis

### Issues Identified
- **Backend main.py**: 2000+ lines, multiple responsibilities
- **Frontend components**: Mixed concerns, inconsistent patterns
- **Configuration scattered**: Multiple env files, hardcoded values
- **Testing gaps**: Missing comprehensive test coverage
- **Documentation**: Outdated file references

### Files Needing Immediate Attention
- `backend/main.py` - Split into 8+ focused modules
- `src/components/ChatInterface.tsx` - Extract AI logic
- `src/lib/api.ts` - Split into focused API clients
- `src/contracts/` - Standardize contract interfaces
- Configuration files - Centralize and standardize

## 🏗️ Target Architecture

### Backend Structure
```
backend/
├── app.py                    # FastAPI app setup (200 lines)
├── config/
│   ├── __init__.py
│   ├── settings.py           # Environment & configuration
│   ├── logging.py            # Logging configuration
│   └── constants.py          # App constants
├── agent/
│   ├── __init__.py
│   ├── core.py               # Main AI agent logic (300 lines)
│   ├── conversation.py       # Chat management
│   ├── tools.py              # Tool orchestration
│   └── memory.py             # Context management
├── tools/
│   ├── __init__.py
│   ├── stellar/
│   │   ├── __init__.py
│   │   ├── account_manager.py    # 200 lines
│   │   ├── trading.py             # 150 lines
│   │   ├── trustline_manager.py   # 100 lines
│   │   ├── market_data.py         # 100 lines
│   │   ├── utilities.py           # 80 lines
│   │   └── soroban_operations.py  # 200 lines
│   └── base.py               # Base tool interface
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py           # Chat endpoints
│   │   ├── health.py         # Health check
│   │   └── tools.py          # Tool endpoints
│   ├── middleware.py         # CORS, auth, logging
│   └── schemas.py            # Pydantic models
├── services/
│   ├── __init__.py
│   ├── stellar_client.py     # Stellar SDK wrapper
│   ├── openai_client.py      # OpenAI API wrapper
│   └── cache.py              # Caching service
├── utils/
│   ├── __init__.py
│   ├── key_manager.py        # Key management
│   ├── errors.py             # Error definitions
│   └── helpers.py            # Utility functions
└── tests/
    ├── __init__.py
    ├── test_agent.py
    ├── test_tools.py
    ├── test_api.py
    └── conftest.py           # Test configuration
```

### Frontend Structure
```
src/
├── App.tsx                   # Main app component (100 lines)
├── main.tsx                  # App entry point
├── components/
│   ├── common/               # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── index.ts
│   ├── chat/                 # Chat functionality
│   │   ├── ChatInterface.tsx     # Main chat UI (200 lines)
│   │   ├── MessageList.tsx       # Message display
│   │   ├── MessageInput.tsx      # Input handling
│   │   ├── ToolIndicator.tsx     # Tool execution status
│   │   └── index.ts
│   ├── dashboard/            # Dashboard components
│   │   ├── PoolsDashboard.tsx
│   │   ├── PoolCard.tsx
│   │   ├── MetricsPanel.tsx
│   │   └── index.ts
│   └── layout/               # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       ├── Footer.tsx
│       └── index.ts
├── hooks/                    # Custom React hooks
│   ├── useChat.ts            # Chat state management
│   ├── useWallet.ts          # Wallet integration
│   ├── useApi.ts             # API client hook
│   ├── useBlendPools.ts      # Pool data
│   └── index.ts
├── services/                 # Business logic
│   ├── chatService.ts        # Chat API client
│   ├── stellarService.ts     # Stellar operations
│   ├── poolService.ts        # Pool data management
│   └── index.ts
├── stores/                   # State management
│   ├── chatStore.ts          # Chat state
│   ├── walletStore.ts        # Wallet state
│   ├── appStore.ts           # Global app state
│   └── index.ts
├── utils/                    # Utility functions
│   ├── format.ts             # Data formatting
│   ├── validation.ts         # Input validation
│   ├── constants.ts          # App constants
│   └── index.ts
├── types/                    # TypeScript definitions
│   ├── chat.ts               # Chat-related types
│   ├── stellar.ts            # Stellar types
│   ├── api.ts                # API response types
│   └── index.ts
├── styles/                   # Styling
│   ├── globals.css
│   ├── components.css
│   └── variables.css
└── tests/                    # Frontend tests
    ├── __tests__/
    ├── components/
    ├── hooks/
    └── utils/
```

## 📋 Implementation Plan

### Phase 1: Backend Refactoring (Priority: High)

#### 1.1 Configuration Management
**Target**: `backend/config/`

**Actions**:
```python
# backend/config/settings.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: str
    openai_base_url: str = "https://api.redpill.ai/v1"
    primary_model: str = "gpt-4"

    # Stellar Configuration
    stellar_network: str = "testnet"
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    class Config:
        env_file = ".env"
```

**Benefits**:
- Centralized configuration
- Type safety with Pydantic
- Environment-specific settings
- Easy validation

#### 1.2 Split main.py
**Target**: Reduce from 2000+ lines to ~200 lines

**Actions**:
```python
# backend/app.py - New main file
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api.routes import chat, health, tools
from api.middleware import setup_middleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="Tuxedo AI Agent",
        description="Stellar-focused AI agent with DeFi tools",
        version="1.0.0"
    )

    # Setup middleware
    setup_middleware(app)

    # Include routers
    app.include_router(chat.router, prefix="/chat")
    app.include_router(health.router, prefix="/health")
    app.include_router(tools.router, prefix="/tools")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
```

#### 1.3 Extract AI Agent Logic
**Target**: `backend/agent/core.py`

**Actions**:
```python
# backend/agent/core.py
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from .conversation import ConversationManager
from .tools import ToolOrchestrator

class TuxedoAgent:
    def __init__(self, llm: ChatOpenAI, tools: List):
        self.llm = llm
        self.tools = tools
        self.conversation_manager = ConversationManager()
        self.tool_orchestrator = ToolOrchestrator(tools)

    async def process_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        wallet_address: Optional[str] = None
    ) -> str:
        # Main agent logic (extracted from main.py)
        pass
```

#### 1.4 Modularize Tools
**Target**: `backend/tools/stellar/`

**Actions**:
```python
# backend/tools/stellar/account_manager.py
from typing import Dict, List, Optional
from stellar_sdk import Server
from ..base import BaseTool

class AccountManagerTool(BaseTool):
    name = "account_manager"
    description = "Manage Stellar accounts"

    def __init__(self, server: Server):
        self.server = server

    async def create_account(self) -> Dict:
        # Account creation logic
        pass

    async def fund_account(self, address: str) -> Dict:
        # Account funding logic
        pass

    # ... other methods
```

### Phase 2: Frontend Refactoring (Priority: Medium)

#### 2.1 Extract Chat Logic
**Target**: Split `ChatInterface.tsx` (500+ lines) into focused components

**Actions**:
```typescript
// src/components/chat/ChatInterface.tsx - Reduced to ~200 lines
import { useState, useCallback } from 'react'
import { useChat } from '../../hooks/useChat'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { ToolIndicator } from './ToolIndicator'

export const ChatInterface: React.FC = () => {
  const { messages, isLoading, sendMessage, activeTools } = useChat()

  const handleSendMessage = useCallback((message: string) => {
    sendMessage(message)
  }, [sendMessage])

  return (
    <div className="chat-interface">
      <MessageList messages={messages} />
      {activeTools.length > 0 && (
        <ToolIndicator tools={activeTools} />
      )}
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  )
}
```

#### 2.2 Create Custom Hooks
**Target**: `src/hooks/useChat.ts`

**Actions**:
```typescript
// src/hooks/useChat.ts
import { useState, useCallback } from 'react'
import { chatService } from '../services/chatService'
import type { ChatMessage, ChatState } from '../types/chat'

export const useChat = () => {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    activeTools: []
  })

  const sendMessage = useCallback(async (message: string) => {
    setState(prev => ({ ...prev, isLoading: true }))

    try {
      const response = await chatService.sendMessage(message)
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, response.message],
        isLoading: false,
        activeTools: response.activeTools
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error.message,
        isLoading: false
      }))
    }
  }, [])

  return {
    ...state,
    sendMessage,
    clearError: () => setState(prev => ({ ...prev, error: null }))
  }
}
```

#### 2.3 API Service Layer
**Target**: `src/services/`

**Actions**:
```typescript
// src/services/chatService.ts
import { apiClient } from './apiClient'
import type { ChatRequest, ChatResponse } from '../types/api'

class ChatService {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post('/chat', request)
    return response.data
  }

  async getConversationHistory(): Promise<ChatMessage[]> {
    const response = await apiClient.get('/chat/history')
    return response.data
  }
}

export const chatService = new ChatService()
```

### Phase 3: Configuration Management (Priority: High)

#### 3.1 Centralize Configuration
**Target**: Single source of truth for all configuration

**Actions**:
```typescript
// src/config/constants.ts
export const NETWORK_CONFIG = {
  testnet: {
    horizon: 'https://horizon-testnet.stellar.org',
    rpc: 'https://soroban-testnet.stellar.org',
    network: 'TESTNET'
  },
  mainnet: {
    horizon: 'https://horizon.stellar.org',
    rpc: 'https://soroban.stellar.org',
    network: 'PUBLIC'
  }
}

export const API_ENDPOINTS = {
  chat: '/api/chat',
  health: '/api/health',
  tools: '/api/tools'
}

export const UI_CONFIG = {
  maxMessages: 100,
  typingIndicatorDelay: 500,
  toolExecutionTimeout: 30000
}
```

#### 3.2 Environment Variables
**Target**: Standardized environment configuration

**Actions**:
```typescript
// src/config/environment.ts
interface Environment {
  VITE_STELLAR_NETWORK: 'testnet' | 'mainnet'
  VITE_API_URL: string
  VITE_ENABLE_DEBUG: boolean
}

export const env: Environment = {
  VITE_STELLAR_NETWORK: import.meta.env.VITE_STELLAR_NETWORK || 'testnet',
  VITE_API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  VITE_ENABLE_DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true'
}
```

### Phase 4: Testing Infrastructure (Priority: Medium)

#### 4.1 Backend Testing
**Target**: Comprehensive test coverage

**Actions**:
```python
# backend/tests/test_agent.py
import pytest
from unittest.mock import Mock, patch
from agent.core import TuxedoAgent

@pytest.fixture
def mock_llm():
    return Mock()

@pytest.fixture
def agent(mock_llm):
    tools = [Mock()]
    return TuxedoAgent(mock_llm, tools)

@pytest.mark.asyncio
async def test_process_message(agent):
    with patch.object(agent, 'tool_orchestrator') as mock_tools:
        mock_tools.execute.return_value = {"result": "success"}

        response = await agent.process_message("Create account")

        assert response is not None
        mock_tools.execute.assert_called_once()
```

#### 4.2 Frontend Testing
**Target**: Component and integration tests

**Actions**:
```typescript
// src/components/chat/__tests__/ChatInterface.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { ChatInterface } from '../ChatInterface'

jest.mock('../../hooks/useChat')

describe('ChatInterface', () => {
  const mockUseChat = useChat as jest.MockedFunction<typeof useChat>

  beforeEach(() => {
    mockUseChat.mockReturnValue({
      messages: [],
      isLoading: false,
      error: null,
      activeTools: [],
      sendMessage: jest.fn()
    })
  })

  it('renders message input', () => {
    render(<ChatInterface />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('calls sendMessage when form is submitted', () => {
    const mockSendMessage = jest.fn()
    mockUseChat.mockReturnValue({
      messages: [],
      isLoading: false,
      error: null,
      activeTools: [],
      sendMessage: mockSendMessage
    })

    render(<ChatInterface />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'Hello' } })
    fireEvent.submit(screen.getByRole('form'))

    expect(mockSendMessage).toHaveBeenCalledWith('Hello')
  })
})
```

### Phase 5: Documentation & Standards (Priority: Low)

#### 5.1 Code Standards
**Target**: Consistent patterns and practices

**Actions**:
```typescript
// Component template
// src/components/template/ComponentTemplate.tsx
import React from 'react'
import type { ComponentProps } from './types'

export const ComponentTemplate: React.FC<ComponentProps> = ({
  prop1,
  prop2,
  ...props
}) => {
  // Component logic

  return (
    <div className="component-template" {...props}>
      {/* Component JSX */}
    </div>
  )
}

export default ComponentTemplate
```

#### 5.2 Documentation Standards
**Target**: Clear, maintainable documentation

**Actions**:
```python
# backend/tools/stellar/account_manager.py
"""
Stellar Account Management Tool

This module provides functionality for managing Stellar accounts including:
- Creating new accounts
- Funding accounts with testnet lumens
- Retrieving account information
- Managing account operations

Example:
    >>> account_manager = AccountManagerTool(server)
    >>> result = await account_manager.create_account()
    >>> print(result['address'])
"""

class AccountManagerTool(BaseTool):
    """Manage Stellar accounts with testnet support."""

    async def create_account(self) -> Dict[str, str]:
        """
        Create a new Stellar account.

        Returns:
            Dict containing:
            - address: The new account address
            - secret: The account secret key
            - funded: Boolean indicating if account was funded

        Raises:
            StellarAccountError: If account creation fails
        """
```

## 🗓️ Implementation Timeline

### Week 1: Backend Core Refactoring
- Day 1-2: Configuration management system
- Day 3-4: Split main.py into focused modules
- Day 5: Extract AI agent logic

### Week 2: Backend Tools & API
- Day 1-2: Modularize Stellar tools
- Day 3-4: API routes and middleware
- Day 5: Services layer implementation

### Week 3: Frontend Refactoring
- Day 1-2: Extract chat logic into components
- Day 3-4: Create custom hooks
- Day 5: API service layer

### Week 4: Configuration & Testing
- Day 1-2: Frontend configuration management
- Day 3-4: Testing infrastructure setup
- Day 5: Documentation updates

## 📈 Expected Benefits

### Immediate Benefits
- **Reduced complexity**: Files under 300 lines
- **Better maintainability**: Clear separation of concerns
- **Easier testing**: Focused, testable units
- **Improved developer experience**: Intuitive file organization

### Long-term Benefits
- **Scalability**: Easy to add new features
- **Team collaboration**: Clear ownership boundaries
- **Code quality**: Consistent patterns and standards
- **Faster development**: Predictable structure

## 🎯 Success Metrics

### Code Quality Metrics
- Average file size: < 300 lines
- Cyclomatic complexity: < 10 per function
- Test coverage: > 80%
- ESLint warnings: < 50

### Developer Experience Metrics
- Time to locate relevant code: < 30 seconds
- New developer onboarding time: < 2 hours
- Feature implementation time: Reduced by 30%
- Bug fix time: Reduced by 40%

## 🔄 Migration Strategy

### Incremental Approach
1. **Parallel development**: Create new structure alongside existing code
2. **Feature flags**: Use feature flags to switch between old/new implementations
3. **Gradual migration**: Move functionality piece by piece
4. **Testing**: Comprehensive testing at each step
5. **Documentation**: Update documentation continuously

### Risk Mitigation
- **Backup strategy**: Git branches for each major change
- **Rollback plan**: Quick revert capabilities
- **Testing pipeline**: Automated tests prevent regressions
- **Code review**: All changes require review
- **Monitoring**: Track performance and error rates

## 📝 Next Steps

1. **Approve this plan** with the development team
2. **Set up branching strategy** for parallel development
3. **Create detailed implementation tickets** for each phase
4. **Set up CI/CD pipeline** to enforce new standards
5. **Begin Phase 1 implementation** with backend core refactoring

This reorganization will transform the codebase into a maintainable, scalable, and developer-friendly foundation for future development.