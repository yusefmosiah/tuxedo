# Tuxedo AI - Implementation Plan

**Goal**: Add conversational AI interface for discovering and understanding Blend pools
**Approach**: TypeScript-only, lean MVP focused on conversational money market exploration
**Timeline**: 1 day for core demo
**Status**: Ready to implement

---

## Table of Contents
1. [Overview](#overview)
2. [Phase 1: Setup & Dependencies](#phase-1-setup--dependencies)
3. [Phase 2: AI Agent & Blend Tools](#phase-2-ai-agent--blend-tools)
4. [Phase 3: Chat UI](#phase-3-chat-ui)
5. [Phase 4: Integration & Testing](#phase-4-integration--testing)
6. [Future Phases](#future-phases)
7. [Deployment](#deployment)

---

## Overview

### What We're Building (MVP)

A conversational interface that allows users to:
- 💬 Ask about Blend pool opportunities ("What's the best USDC yield?")
- 📊 Get current APY rates, utilization, and TVL explained in plain English
- 🎓 Understand DeFi risks without jargon
- 💡 Discover lending/borrowing opportunities across all Blend pools

**Not in MVP** (deferred to future phases):
- ❌ XLM → USDC trading
- ❌ Pool deposits
- ❌ Conversation persistence (Supabase)
- ❌ Reward token system & protocol fees

**Note**: Wallet connection is already live (Scaffold Stellar + Freighter integration)

### Technology Stack (MVP)

```
Frontend (Browser)
├── React Components
│   └── ChatInterface.tsx (local state only)
├── API Client
│   └── FastAPI backend communication
└── Existing Infrastructure (from Scaffold Stellar)
    ├── WalletProvider + useWallet hook ✅
    ├── Freighter integration ✅
    ├── useBlendPools hook ✅
    └── Blend SDK integration ✅

Backend (FastAPI Server)
├── FastAPI Application
│   ├── Chat endpoint (/chat)
│   └── Health check (/health)
├── AI Integration
│   ├── LangChain Python + OpenAI/RedPill
│   └── MCP Client for py-stellar-mcp
└── MCP Server Integration
    └── py-stellar-mcp (existing repo)
        ├── Account management tools
        ├── Blend pool queries
        ├── Stellar operations
        └── Soroban contract interactions

External Services
├── OpenAI GPT or RedPill Qwen3-VL via API
└── Stellar Network (via py-stellar-mcp)
```

### Why This Approach?

**Why FastAPI + MCP Server Approach:**
- ✅ **Security**: API keys stay server-side, never exposed to browsers
- ✅ **Rich Tools**: py-stellar-mcp provides comprehensive Stellar operations
- ✅ **Future-Proof**: Easy to add more MCP servers and complex agent workflows
- ✅ **Python Ecosystem**: Better LangChain/LangGraph support for agentic systems
- ✅ **Type Safety**: End-to-end type safety from MCP server to frontend

**Focus on Core Value First:**
- ✅ Get conversational pool discovery working in hours, not days
- ✅ Prove AI + DeFi UX value before adding complexity
- ✅ No database setup/management until it adds value
- ✅ No transaction signing flow until core chat works

**Add Later When Valuable:**
- 🔮 Trading tools (once users trust pool recommendations)
- 🔮 Supabase (once users want conversation history)
- 🔮 Portfolio tracking (once users have positions)
- 🔮 LangGraph workflows (once users need complex multi-step operations)

---

## Phase 1: Setup & Dependencies

### 1.1 Backend Setup (FastAPI)

Create backend directory and install Python dependencies:

```bash
# Create backend directory
mkdir backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install fastapi uvicorn python-multipart \
  langchain langchain-openai langchain-community \
  pydantic python-dotenv httpx mcp

# Create requirements.txt for future reference
pip freeze > requirements.txt
```

### 1.2 Frontend Dependencies

```bash
npm install --save \
  axios
```

**Note**: No LangChain.js needed - AI logic moved to FastAPI backend!

### 1.3 Environment Variables

**Backend (.env):**
```bash
# OpenAI/RedPill Configuration
OPENAI_API_KEY=sk-rp-34c7daeea1dcb00cab5acab8014b7efeb87b819cbee6b41f6d15a64d8f8dca86
OPENAI_BASE_URL=https://api.redpill.ai/v1

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001  # py-stellar-mcp server address
MCP_SERVER_TIMEOUT=30
```

**Frontend (.env - already exists):**
```bash
# Existing Stellar Config (no changes needed)
PUBLIC_STELLAR_NETWORK="TESTNET"
PUBLIC_STELLAR_RPC_URL="https://soroban-testnet.stellar.org"
PUBLIC_STELLAR_HORIZON_URL="https://horizon-testnet.stellar.org"

# Backend API URL
PUBLIC_API_URL=http://localhost:8000
```

### 1.4 RedPill API Setup (Phala Cloud)

**Get API Key**:
1. Go to https://www.redpill.ai/
2. Sign up and create an account
3. Navigate to your API settings to get an API key
4. Add it to your backend `.env` file (already done above!)

### 1.5 Start py-stellar-mcp Server

Clone and start your existing MCP server:

```bash
# Clone your repository (if not already done)
git clone https://github.com/yusefmosiah/py-stellar-mcp.git
cd py-stellar-mcp

# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the MCP server
python -m mcp.server.stdio stellar_mcp.server --port 8001
```

**Note**: This server should run continuously on port 8001, providing Stellar tools to your FastAPI backend.

**About Phala Cloud GPU TEE**:
- **Privacy**: All AI requests run in Trusted Execution Environments (TEEs)
- **Security**: Your data and prompts never leave the secure enclave
- **Performance**: GPU-accelerated inference with low latency
- **Open Source**: Uses Qwen3-VL, a powerful open-source multimodal model

**Model Details**:
- **Model**: Qwen3-VL-235B-A22B-Instruct
- **Architecture**: 235B parameter multimodal model
- **Context Window**: 131K tokens
- **Capabilities**:
  - Text generation with visual understanding (images and video)
  - Agentic interaction and tool use
  - Complex multi-image dialogues
  - Visual coding workflows
  - Document AI and multilingual OCR
  - Software/UI assistance
  - Spatial and embodied tasks
- **Technology**: GPU TEE protected with strong text performance comparable to flagship Qwen3 language models
- **Features**: 2D/3D grounding and long-form visual comprehension
- **Pricing**: $0.30/M input tokens, $1.49/M output tokens
- **Benchmark Performance**: Competitive with leading models on perception and reasoning tasks

---

## Phase 2: FastAPI Backend & MCP Integration

### 2.1 Create FastAPI Server

**File**: `backend/main.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
from contextlib import asynccontextmanager

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str

# Global MCP client session
mcp_session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mcp_session
    print("Connecting to MCP server...")

    # Connect to py-stellar-mcp server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp.server.stdio", "stellar_mcp.server"],
        env=None
    )

    try:
        mcp_session = await stdio_client(server_params)
        print("Connected to MCP server successfully!")
    except Exception as e:
        print(f"Failed to connect to MCP server: {e}")
        mcp_session = None

    yield

    # Shutdown
    if mcp_session:
        try:
            await mcp_session[0].close()
        except:
            pass

app = FastAPI(
    title="Tuxedo AI Backend",
    description="FastAPI backend for Tuxedo AI with MCP integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt for the AI
SYSTEM_PROMPT = """You are Tuxedo, an AI assistant that helps users discover and understand lending opportunities on Stellar through the Blend Protocol.

**Your Capabilities:**
- Query all active Blend pools to find current APY rates
- Access Stellar account information and balances
- Perform Stellar operations via MCP tools
- Explain DeFi lending concepts in simple, clear language
- Compare different pools and assets
- Assess risk based on utilization rates and pool metrics

**Key Principles:**
1. **Plain language first** - Avoid DeFi jargon unless the user asks for technical details
2. **Always explain risks** - High APY usually means higher risk (utilization, volatility, liquidity)
3. **Be transparent** - Yields come from borrowers paying interest to lenders
4. **Never promise returns** - Always say "current rate" or "estimated APY based on today's data"
5. **Show your work** - When comparing pools, show the numbers (APY, utilization, TVL)

**Available Tools:**
- All tools provided by py-stellar-mcp server (account management, pool queries, trading, etc.)
- Use these tools to get real-time Stellar data for accurate responses

**Current Context:**
- User is exploring Blend pools on Stellar testnet
- This is for educational/informational purposes
- Focus on helping users understand opportunities and risks"""

# Initialize OpenAI client
model = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model="gpt-4",  # or "qwen/qwen3-vl-235b-a22b-instruct" for RedPill
    temperature=0.7,
    max_tokens=2000,
)

@app.get("/")
async def root():
    return {"message": "Tuxedo AI Backend is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mcp_connected": mcp_session is not None,
        "openai_configured": bool(OPENAI_API_KEY)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message with AI and MCP tools"""
    try:
        # Build message history
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *[HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)
              for msg in request.history],
            HumanMessage(content=request.message),
        ]

        # For now, simple chat without MCP tools
        # TODO: Integrate MCP tools in Phase 2.2
        response = await model.ainvoke(messages)

        return ChatResponse(response=response.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2.2 MCP Client Integration

**File**: `backend/mcp_client.py`

```python
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class StellarMCPClient:
    """Client for interacting with py-stellar-mcp server"""

    def __init__(self):
        self.session = None
        self._tools = []

    async def connect(self, server_url: str = "http://localhost:8001"):
        """Connect to MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "mcp.server.stdio", "stellar_mcp.server"],
                env=None
            )

            self.session = await stdio_client(server_params)
            await self.session[0].initialize()

            # List available tools
            tools_result = await self.session[0].list_tools()
            self._tools = tools_result.tools

            print(f"Connected to MCP server. Available tools: {len(self._tools)}")
            return True

        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            return False

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the MCP server"""
        if not self.session:
            raise Exception("Not connected to MCP server")

        try:
            result = await self.session[0].call_tool(tool_name, arguments)
            return result.content[0].text if result.content else "No content returned"
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [tool.name for tool in self._tools] if self._tools else []

# Global MCP client instance
mcp_client = StellarMCPClient()
```

---

## Phase 3: Frontend Chat UI

### 3.1 Create API Client

**File**: `src/lib/api.ts`

```typescript
import axios from 'axios';

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  response: string;
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request/response interceptors for debugging
api.interceptors.request.use((config) => {
  console.log('API Request:', config.method?.toUpperCase(), config.url);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/chat', request);
    return response.data;
  },

  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },
};
```

### 3.2 Create Chat Interface Component

**File**: `src/components/ChatInterface.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react';
import { Button, Text, Loader } from '@stellar/design-system';
import { chatApi, type ChatMessage } from '../lib/api';
import { useWallet } from '../hooks/useWallet';

export const ChatInterface: React.FC = () => {
  const { data: wallet } = useWallet();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await chatApi.healthCheck();
        setApiStatus('connected');
      } catch (error) {
        console.error('Backend health check failed:', error);
        setApiStatus('disconnected');
      }
    };

    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || apiStatus === 'disconnected') return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: input,
        history: messages,
      });

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please check if the backend is running and try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIndicator = () => {
    switch (apiStatus) {
      case 'connected':
        return '🟢';
      case 'disconnected':
        return '🔴';
      case 'checking':
        return '🟡';
    }
  };

  const getStatusText = () => {
    switch (apiStatus) {
      case 'connected':
        return 'Connected to backend';
      case 'disconnected':
        return 'Backend offline - Start FastAPI server';
      case 'checking':
        return 'Checking connection...';
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '600px',
        border: '1px solid #e0e0e0',
        borderRadius: '12px',
        overflow: 'hidden',
        backgroundColor: '#fff',
      }}
    >
      {/* Header with status */}
      <div
        style={{
          padding: '16px 20px',
          backgroundColor: '#f8f9fa',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Text as="h3" size="md" weight="semi-bold">
          💬 Tuxedo AI Assistant
        </Text>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px' }}>{getStatusIndicator()}</span>
          <Text as="p" size="sm" style={{ color: '#666' }}>
            {getStatusText()}
          </Text>
        </div>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <Text as="p" size="lg" style={{ marginBottom: '16px' }}>
              👋 Hi! I'm Tuxedo
            </Text>
            <Text as="p" size="md" style={{ color: '#666' }}>
              Ask me about Blend lending pools, yields, and DeFi opportunities on Stellar
            </Text>
            {wallet?.address && (
              <Text as="p" size="sm" style={{ color: '#999', marginTop: '8px' }}>
                Connected: {wallet.address.slice(0, 8)}...{wallet.address.slice(-4)}
              </Text>
            )}

            {apiStatus === 'disconnected' && (
              <div style={{
                marginTop: '24px',
                padding: '12px 16px',
                backgroundColor: '#fff3cd',
                border: '1px solid #ffeaa7',
                borderRadius: '8px',
                color: '#856404',
              }}>
                <Text as="p" size="sm">
                  <strong>Backend not connected!</strong><br/>
                  Run: <code style={{ backgroundColor: '#f8f9fa', padding: '2px 4px', borderRadius: '4px' }}>
                    cd backend && python main.py
                  </code>
                </Text>
              </div>
            )}

            <div
              style={{
                marginTop: '24px',
                fontSize: '14px',
                color: '#999',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <p style={{ fontWeight: '600', marginBottom: '4px' }}>Try asking:</p>
              <p>"What yields are available for USDC?"</p>
              <p>"Which pool has the best APY?"</p>
              <p>"Explain how Blend lending works"</p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '12px',
                backgroundColor: msg.role === 'user' ? '#667eea' : '#f0f0f0',
                color: msg.role === 'user' ? '#fff' : '#000',
              }}
            >
              <Text as="p" size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                {msg.content}
              </Text>
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div
              style={{
                padding: '12px 16px',
                borderRadius: '12px',
                backgroundColor: '#f0f0f0',
              }}
            >
              <Loader size="sm" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid #e0e0e0',
          backgroundColor: '#fafafa',
        }}
      >
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={
              apiStatus === 'disconnected'
                ? "Backend offline - check console"
                : "Ask about yields, pools, or DeFi concepts..."
            }
            disabled={isLoading || apiStatus === 'disconnected'}
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              fontSize: '14px',
              backgroundColor: apiStatus === 'disconnected' ? '#f8f9fa' : '#fff',
              cursor: apiStatus === 'disconnected' ? 'not-allowed' : 'text',
            }}
          />
          <Button
            variant="primary"
            size="md"
            onClick={handleSend}
            disabled={isLoading || !input.trim() || apiStatus === 'disconnected'}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
```

### 3.2 Add to Home Page

**File**: `src/pages/Home.tsx` (update)

```typescript
import { PoolsDashboard } from '../components/dashboard/PoolsDashboard';
import { ChatInterface } from '../components/ChatInterface';
import { Text } from '@stellar/design-system';

export default function Home() {
  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
      {/* Hero Section */}
      <section style={{ marginBottom: '48px', textAlign: 'center' }}>
        <Text as="h1" size="xl" style={{ marginBottom: '8px' }}>
          Tuxedo AI
        </Text>
        <Text as="p" size="md" style={{ color: '#666' }}>
          Your conversational guide to DeFi lending on Stellar
        </Text>
      </section>

      {/* Chat Interface */}
      <section style={{ marginBottom: '48px' }}>
        <Text as="h2" size="lg" style={{ marginBottom: '16px' }}>
          Ask Tuxedo
        </Text>
        <ChatInterface />
      </section>

      {/* Pool Dashboard */}
      <section>
        <Text as="h2" size="lg" style={{ marginBottom: '16px' }}>
          All Blend Pools
        </Text>
        <PoolsDashboard />
      </section>
    </div>
  );
}
```

---

## Phase 4: Integration & Testing

### 4.1 Development Setup

**Start all services in order:**

```bash
# 1. Start MCP server (Terminal 1)
cd py-stellar-mcp
source venv/bin/activate
python -m mcp.server.stdio stellar_mcp.server --port 8001

# 2. Start FastAPI backend (Terminal 2)
cd backend
source venv/bin/activate
python main.py

# 3. Start frontend (Terminal 3)
npm run dev
# Visit http://localhost:5173
```

### 4.2 Test Checklist

- [ ] **System Health**
  - [ ] All three services start without errors
  - [ ] FastAPI health check passes (`GET http://localhost:8000/health`)
  - [ ] Frontend shows green "Connected to backend" status
  - [ ] No CORS errors in browser console

- [ ] **AI Chat Basics**
  - [ ] Chat interface renders on home page with status indicator
  - [ ] Can send message and get response from backend
  - [ ] Loading state shows while waiting
  - [ ] Messages display in correct bubbles (user right, AI left)
  - [ ] Response time is reasonable (2-5 seconds)

- [ ] **Error Handling**
  - [ ] Stop FastAPI backend → Frontend shows "Backend offline"
  - [ ] Restart backend → Connection restores automatically
  - [ ] Test with empty messages (should be disabled)
  - [ ] Check browser console for API errors

- [ ] **MCP Integration** (Phase 2.2 milestone)
  - [ ] FastAPI connects to py-stellar-mcp server on startup
  - [ ] Can call basic Stellar tools (account info, balances)
  - [ ] AI has access to real-time Stellar data

### 4.3 Manual Testing Script

```
1. Start all services (MCP, FastAPI, frontend)
2. Open http://localhost:5173
3. Verify green status "Connected to backend"
4. Type: "Hello, what can you help me with?"
5. Should get friendly response about Blend pools and DeFi
6. Type: "What yields are available for USDC?"
7. Wait 2-5 seconds (loading indicator should show)
8. Expect response with current market information
9. Test error case: Stop FastAPI, try to send message
10. Verify "Backend offline" warning appears
11. Restart FastAPI, verify connection auto-recovers
```

---

## Future Phases

### Phase 5: Trading Tools (Deferred)

**When to add**: After users trust pool recommendations and want to act on them.

**What to add**:
- `src/lib/stellar-trading.ts` - XLM→USDC swap builder
- `swap_xlm_to_usdc` tool for LangChain
- `create_usdc_trustline` tool
- Transaction signing flow in ChatInterface
- Integration with existing `useSubmitRpcTx` hook

**Estimated time**: 3-4 hours

### Phase 6: Supabase Persistence (Deferred)

**When to add**: After users request conversation history or want to resume chats.

**What to add**:
- Supabase project setup
- Database schema (users, conversations, messages)
- `src/lib/supabase.ts` client
- Update ChatInterface to save/load conversations
- Conversation list UI (sidebar or separate page)

**Estimated time**: 2-3 hours

### Phase 7: Advanced Features (Deferred)

- Portfolio tracking (if user has deposits)
- USD pricing via oracles
- Historical APY charts
- Mobile responsive design
- Dark mode

### Phase 8: Tokenomics & Revenue Model (Future)

**When to add**: After achieving user scale and validating product-market fit.

**Goals**:
- Monetize the platform sustainably
- Reward early users and active participants
- Create network effects through token utility

**What to build**:

1. **Reward Token Smart Contract** (Soroban)
   - Deploy ERC20-style token on Stellar
   - Mint rewards to users based on activity:
     - Depositing into Blend pools via Tuxedo
     - Holding balances over time
     - Referrals/social sharing
   - Token distribution schedule (vesting, caps)

2. **Protocol Fee System**
   - Take small percentage of user yields (research: 5-15% is typical)
   - Examples from DeFi:
     - Aave: 10% protocol reserve fee
     - Compound: 10% reserve factor
     - Yearn: 2% management + 20% performance
   - **Start at 0%**, increase gradually as value is proven
   - Fees collected in treasury contract

3. **Token Utility & Staking**
   - Stake tokens → reduce/eliminate protocol fees
   - Governance rights (protocol parameters, fee rates)
   - Liquidity mining incentives
   - Potential: Revenue sharing with stakers

4. **Competitive Analysis Needed**
   - Research what Blend Protocol charges (if anything)
   - Check what users expect in DeFi aggregators
   - Consider user retention vs. revenue tradeoff

**Technical Implementation**:
```rust
// Soroban smart contract (pseudo-code)
contract TuxedoRewards {
    // Mint rewards based on user deposits
    fn calculate_rewards(user: Address, deposit_amount: i128, duration: u64) -> i128;

    // Staking for fee discounts
    fn stake_tokens(user: Address, amount: i128);
    fn get_fee_discount(user: Address) -> u32; // Returns discount % (0-100)

    // Protocol fee collection
    fn collect_fee(pool: Address, yield_earned: i128) -> i128;
}
```

**AI Chat Integration**:
- Explain token rewards when suggesting deposits
- "You'd earn 12% APY on USDC, plus 50 TUX tokens per month"
- Show staking benefits: "Stake 1000 TUX to reduce fees from 5% to 0%"

**Revenue Projections** (hypothetical):
```
Assumptions:
- 100 users with avg $10k deposited = $1M TVL
- Average yield: 10% APY
- Protocol fee: 5%

Annual revenue = $1M × 10% × 5% = $5,000/year

At scale (10,000 users, $100M TVL):
Annual revenue = $100M × 10% × 5% = $500,000/year
```

**Estimated time**: 1-2 weeks
- Smart contract development: 3-4 days
- Testing & auditing: 3-4 days
- Frontend integration: 2-3 days
- Token distribution strategy: 1-2 days

**Important**: DO NOT implement fees until:
1. Product has proven value (users actually use it)
2. Competitive analysis complete
3. Token economics designed properly
4. Legal review (token regulation varies by jurisdiction)

---

## Deployment

### Local Development
```bash
# Terminal 1: Start MCP server
cd py-stellar-mcp
source venv/bin/activate
python -m mcp.server.stdio stellar_mcp.server --port 8001

# Terminal 2: Start FastAPI backend
cd backend
source venv/bin/activate
python main.py

# Terminal 3: Start frontend
npm run dev
# Visit http://localhost:5173
```

### Production Deployment Options

**Option 1: Separate Services (Recommended)**
```bash
# Frontend: Deploy to Vercel/Netlify
npm run build
vercel deploy

# Backend: Deploy to Railway/Render/Heroku
# Deploy backend/main.py as a web service

# MCP Server: Deploy as separate service
# Or bundle with FastAPI backend for simplicity
```

**Option 2: All-in-One FastAPI**
- Bundle frontend build into FastAPI static files
- Run both from single server instance
- Easier for small deployments

### Environment Variables (Production)

**Frontend Environment:**
- `PUBLIC_API_URL` (your FastAPI backend URL)

**Backend Environment:**
- `OPENAI_API_KEY` (your RedPill API key)
- `OPENAI_BASE_URL` (set to `https://api.redpill.ai/v1`)
- `MCP_SERVER_URL` (internal MCP server address)
- `CORS_ORIGINS` (your frontend domain)

### Production Considerations

**Security:**
- Use HTTPS for all API communication
- Set proper CORS origins in production
- Consider rate limiting on FastAPI endpoints
- Use environment variables for all secrets

**Performance:**
- Deploy FastAPI with Gunicorn/Uvicorn workers
- Consider Redis for caching if scaling
- Monitor MCP server connection health
- Set up proper logging and monitoring

**Reliability:**
- Auto-restart scripts for MCP server
- Health checks for all services
- Load balancing if scaling backend
- Error monitoring (Sentry, etc.)

---

## Success Criteria

✅ **MVP Complete When:**
1. User can open app and see chat interface
2. User can ask about Blend pools and get AI responses
3. AI can query live pool data and explain it clearly
4. Conversation flows naturally with context retention
5. Error handling works gracefully

🎯 **Demo-Ready When:**
1. All MVP features working smoothly
2. Can complete full demo in 2 minutes:
   - "What yields are available?"
   - "Which is best for low risk?"
   - "Explain how this works"
3. UI is clean and intuitive
4. No console errors during happy path

---

## Timeline Estimate

- **Phase 1**: 30 minutes (backend setup, Python env, dependencies)
- **Phase 2**: 3 hours (FastAPI server + MCP integration)
- **Phase 3**: 1.5 hours (updated chat UI with API client)
- **Phase 4**: 1 hour (testing three-service setup + polish)

**Total**: ~5.5-6.5 hours (slightly longer due to backend complexity)

**Why Slightly Longer Than Original:**
- Added security and robustness with server-side LLM calls
- MCP server integration provides much richer Stellar functionality
- Architecture is more scalable and future-proof
- Better separation of concerns for long-term maintenance

---

## Next Steps

### Phase 1 - Backend Foundation (Start Here)
1. ✅ Set up Python backend environment
2. ✅ Install FastAPI + LangChain + MCP dependencies
3. ✅ Configure environment variables for API access
4. ✅ Clone and start py-stellar-mcp server

### Phase 2 - AI Integration (Core Work)
5. ✅ Create `backend/main.py` with FastAPI server
6. ✅ Create `backend/mcp_client.py` for Stellar integration
7. ✅ Test basic chat functionality without MCP tools
8. ✅ Integrate MCP tools for real-time Stellar data

### Phase 3 - Frontend Updates
9. ✅ Create `src/lib/api.ts` for HTTP client
10. ✅ Update `src/components/ChatInterface.tsx` for backend communication
11. ✅ Add connection status indicators and error handling
12. ✅ Test end-to-end flow: Frontend → FastAPI → LLM

### Phase 4 - Integration & Polish
13. ✅ Three-service setup: MCP server + FastAPI + Frontend
14. ✅ Health checks and connection monitoring
15. ✅ Error handling and recovery scenarios
16. ✅ Performance testing and optimization
17. 🎉 Demo with full architecture!

**Then Later** (Future Phases):
- Phase 5: Add LangGraph workflows for complex multi-step operations
- Phase 6: Supabase integration for conversation persistence
- Phase 7: Advanced features (trading, portfolio tracking)

Ready to build a secure, scalable AI × DeFi platform! 🚀

**Key Architectural Benefits:**
- 🔒 API keys never exposed to browsers
- 🛠️ Rich Stellar tools via py-stellar-mcp
- 🚀 Easy to add more MCP servers and AI capabilities
- 🔧 Python ecosystem for advanced agentic workflows
- 📈 Future-proof for LangGraph and complex multi-agent systems
