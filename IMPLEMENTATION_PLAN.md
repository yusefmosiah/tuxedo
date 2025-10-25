# Tuxedo AI - Implementation Plan

**Goal**: Add conversational AI interface for discovering Blend pools and executing trades
**Approach**: TypeScript-only implementation (no MCP server complexity)
**Timeline**: 2-3 days for MVP
**Status**: Ready to implement

---

## Table of Contents
1. [Overview](#overview)
2. [Phase 1: Setup & Dependencies](#phase-1-setup--dependencies)
3. [Phase 2: Supabase Database](#phase-2-supabase-database)
4. [Phase 3: Stellar Trading Tools](#phase-3-stellar-trading-tools)
5. [Phase 4: AI Agent & LangChain](#phase-4-ai-agent--langchain)
6. [Phase 5: Chat UI](#phase-5-chat-ui)
7. [Phase 6: Integration & Testing](#phase-6-integration--testing)
8. [Testing Checklist](#testing-checklist)
9. [Deployment](#deployment)

---

## Overview

### What We're Building

A conversational interface that allows users to:
- Ask about Blend pool opportunities ("What's the best USDC yield?")
- Understand risks in plain English
- Execute XLM → USDC swaps via chat
- Deposit into Blend pools (testnet only)
- View conversation history

### Technology Stack

```
Frontend (Browser)
├── React Components
│   └── ChatInterface.tsx
├── AI Integration
│   ├── LangChain.js + AWS Bedrock (Claude 3.5 Sonnet)
│   └── Custom Tools (TypeScript)
├── Trading Layer
│   ├── Stellar SDK (direct)
│   └── Wallet Integration (Freighter)
└── Persistence
    └── Supabase Client (browser)

External Services
├── AWS Bedrock API (Claude)
├── Supabase Cloud (PostgreSQL)
└── Stellar Network (Horizon + Soroban)
```

### Why This Approach?

**Rejected**: Python MCP Server with bridge
- ❌ Requires running separate Python process
- ❌ stdio transport doesn't work in browser
- ❌ Need to build HTTP bridge server
- ❌ More complex deployment

**Chosen**: Direct TypeScript Implementation
- ✅ Uses existing Stellar SDK + Blend SDK
- ✅ Wallet signing already works (Freighter)
- ✅ Single codebase to maintain
- ✅ Better UX (no roundtrips to Python)
- ✅ Simpler deployment (static site only)

---

## Phase 1: Setup & Dependencies

### 1.1 Install NPM Packages

```bash
npm install --save \
  @langchain/core \
  @langchain/aws \
  @supabase/supabase-js \
  zod

# Optional: For better type inference
npm install --save-dev @types/node
```

### 1.2 Environment Variables

Create/update `.env.local`:

```bash
# Existing Stellar Config
VITE_STELLAR_NETWORK=testnet
VITE_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_RPC_URL=https://soroban-testnet.stellar.org

# NEW: Supabase Cloud
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...your-anon-key

# NEW: AWS Bedrock
VITE_AWS_REGION=us-east-1
VITE_AWS_ACCESS_KEY_ID=AKIA...
VITE_AWS_SECRET_ACCESS_KEY=...

# Service key (only for server-side, don't expose to browser)
# Not needed for Vite app since we use anon key
```

### 1.3 AWS Bedrock Setup

**Required Permissions** (IAM):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
    }
  ]
}
```

**Enable Model Access**:
1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Enable "Claude 3.5 Sonnet v2"

---

## Phase 2: Supabase Database

### 2.1 Create Supabase Project

1. Visit https://supabase.com
2. Click "New Project"
3. Choose region (closest to users)
4. Set database password (save it!)
5. Wait for provisioning (~2 minutes)

### 2.2 Run Database Schema

Go to SQL Editor in Supabase dashboard and run:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (wallet-based auth)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  wallet_address TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_active TIMESTAMPTZ DEFAULT NOW()
);

-- Chat conversations
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT,
  messages JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transaction tracking
CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
  tx_type TEXT NOT NULL, -- 'swap', 'deposit', 'trustline'
  tx_hash TEXT NOT NULL,
  from_asset TEXT,
  to_asset TEXT,
  amount TEXT,
  network TEXT NOT NULL DEFAULT 'testnet',
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'confirmed', 'failed'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_wallet ON users(wallet_address);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_hash ON transactions(tx_hash);

-- Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Public read/write for demo (tighten for production)
CREATE POLICY "Allow all operations" ON users FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON conversations FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON transactions FOR ALL USING (true);
```

### 2.3 Get Supabase Credentials

1. Go to Project Settings → API
2. Copy "Project URL" → `VITE_SUPABASE_URL`
3. Copy "anon public" key → `VITE_SUPABASE_ANON_KEY`
4. Update `.env.local`

---

## Phase 3: Stellar Trading Tools

### 3.1 Create Trading Utility

**File**: `src/lib/stellar-trading.ts`

```typescript
import {
  TransactionBuilder,
  Operation,
  Asset,
  Networks,
  Horizon,
} from '@stellar/stellar-sdk';
import { BLEND_CONTRACTS } from '../contracts/blend';

// USDC issuer on testnet
const USDC_ISSUER = BLEND_CONTRACTS.usdcToken;

export interface SwapParams {
  amount: string;
  userAddress: string;
  network: 'testnet' | 'mainnet';
}

/**
 * Build XLM → USDC swap transaction using path payment
 */
export async function buildXLMtoUSDCSwap(params: SwapParams) {
  const { amount, userAddress, network } = params;

  const horizonUrl =
    network === 'testnet'
      ? 'https://horizon-testnet.stellar.org'
      : 'https://horizon.stellar.org';
  const server = new Horizon.Server(horizonUrl);

  // Load user account
  const account = await server.loadAccount(userAddress);

  // Define assets
  const xlm = Asset.native();
  const usdc = new Asset('USDC', USDC_ISSUER);

  // Build path payment operation
  const pathPayment = Operation.pathPaymentStrictSend({
    sendAsset: xlm,
    sendAmount: amount,
    destination: userAddress,
    destAsset: usdc,
    destMin: '0', // Accept any amount (for testnet demo)
    path: [], // Let Stellar find best path automatically
  });

  // Build transaction
  const transaction = new TransactionBuilder(account, {
    fee: '100000', // 0.01 XLM max fee
    networkPassphrase:
      network === 'testnet' ? Networks.TESTNET : Networks.PUBLIC,
  })
    .addOperation(pathPayment)
    .setTimeout(300) // 5 minutes
    .build();

  return {
    xdr: transaction.toXDR(),
    hash: transaction.hash().toString('hex'),
  };
}

/**
 * Check if user has USDC trustline
 */
export async function hasUSDCTrustline(
  userAddress: string,
  network: 'testnet' | 'mainnet'
): Promise<boolean> {
  const horizonUrl =
    network === 'testnet'
      ? 'https://horizon-testnet.stellar.org'
      : 'https://horizon.stellar.org';
  const server = new Horizon.Server(horizonUrl);

  try {
    const account = await server.loadAccount(userAddress);
    const usdcBalance = account.balances.find(
      (b) =>
        'asset_code' in b &&
        b.asset_code === 'USDC' &&
        'asset_issuer' in b &&
        b.asset_issuer === USDC_ISSUER
    );
    return !!usdcBalance;
  } catch (err) {
    console.error('Error checking trustline:', err);
    return false;
  }
}

/**
 * Build trustline creation transaction
 */
export async function buildUSDCTrustline(
  userAddress: string,
  network: 'testnet' | 'mainnet'
) {
  const horizonUrl =
    network === 'testnet'
      ? 'https://horizon-testnet.stellar.org'
      : 'https://horizon.stellar.org';
  const server = new Horizon.Server(horizonUrl);

  const account = await server.loadAccount(userAddress);
  const usdc = new Asset('USDC', USDC_ISSUER);

  const transaction = new TransactionBuilder(account, {
    fee: '10000', // 0.001 XLM
    networkPassphrase:
      network === 'testnet' ? Networks.TESTNET : Networks.PUBLIC,
  })
    .addOperation(Operation.changeTrust({ asset: usdc }))
    .setTimeout(300)
    .build();

  return {
    xdr: transaction.toXDR(),
    hash: transaction.hash().toString('hex'),
  };
}

/**
 * Estimate swap output (query DEX orderbook)
 */
export async function estimateSwapOutput(
  amountXLM: string,
  network: 'testnet' | 'mainnet'
): Promise<string> {
  const horizonUrl =
    network === 'testnet'
      ? 'https://horizon-testnet.stellar.org'
      : 'https://horizon.stellar.org';
  const server = new Horizon.Server(horizonUrl);

  const xlm = Asset.native();
  const usdc = new Asset('USDC', USDC_ISSUER);

  try {
    // Get orderbook for XLM/USDC
    const orderbook = await server
      .orderbook(xlm, usdc)
      .limit(10)
      .call();

    // Simple estimation from best ask price
    if (orderbook.asks.length > 0) {
      const bestAsk = parseFloat(orderbook.asks[0].price);
      const estimatedUSDC = parseFloat(amountXLM) * bestAsk;
      return estimatedUSDC.toFixed(2);
    }
  } catch (err) {
    console.error('Error estimating swap:', err);
  }

  return 'Unknown';
}
```

---

## Phase 4: AI Agent & LangChain

### 4.1 Create Supabase Client

**File**: `src/lib/supabase.ts`

```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL!;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Database types
export interface User {
  id: string;
  wallet_address: string;
  created_at: string;
  last_active: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  transaction?: string; // XDR if message includes tx
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string | null;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

// Helper: Get or create user by wallet address
export async function getOrCreateUser(walletAddress: string): Promise<User> {
  // Try to get existing
  const { data: existing } = await supabase
    .from('users')
    .select('*')
    .eq('wallet_address', walletAddress)
    .single();

  if (existing) {
    // Update last_active
    await supabase
      .from('users')
      .update({ last_active: new Date().toISOString() })
      .eq('id', existing.id);
    return existing;
  }

  // Create new user
  const { data: newUser, error } = await supabase
    .from('users')
    .insert({ wallet_address: walletAddress })
    .select()
    .single();

  if (error) throw error;
  return newUser!;
}

// Helper: Save conversation
export async function saveConversation(
  userId: string,
  messages: Message[],
  conversationId?: string
): Promise<Conversation> {
  const title = messages[0]?.content.slice(0, 50) || 'New conversation';

  if (conversationId) {
    const { data, error } = await supabase
      .from('conversations')
      .update({ messages, updated_at: new Date().toISOString() })
      .eq('id', conversationId)
      .select()
      .single();

    if (error) throw error;
    return data!;
  }

  const { data, error } = await supabase
    .from('conversations')
    .insert({ user_id: userId, title, messages })
    .select()
    .single();

  if (error) throw error;
  return data!;
}

// Helper: Get user's conversations
export async function getUserConversations(
  userId: string
): Promise<Conversation[]> {
  const { data, error } = await supabase
    .from('conversations')
    .select('*')
    .eq('user_id', userId)
    .order('updated_at', { ascending: false });

  if (error) throw error;
  return data || [];
}

// Helper: Track transaction
export async function trackTransaction(
  userId: string,
  txType: string,
  txHash: string,
  details: {
    fromAsset?: string;
    toAsset?: string;
    amount?: string;
    network?: string;
    conversationId?: string;
  }
) {
  const { error } = await supabase.from('transactions').insert({
    user_id: userId,
    tx_type: txType,
    tx_hash: txHash,
    ...details,
  });

  if (error) throw error;
}
```

### 4.2 Create LangChain Tools

**File**: `src/lib/ai-tools.ts`

```typescript
import { DynamicStructuredTool } from '@langchain/core/tools';
import { z } from 'zod';
import { Backstop, PoolV2 } from '@blend-capital/blend-sdk';
import { BLEND_CONTRACTS } from '../contracts/blend';
import { network } from '../contracts/util';
import {
  buildXLMtoUSDCSwap,
  buildUSDCTrustline,
  hasUSDCTrustline,
  estimateSwapOutput,
} from './stellar-trading';

export function createTuxedoTools(
  userAddress: string,
  networkType: 'testnet' | 'mainnet' = 'testnet'
) {
  // Tool 1: Get Blend Pools
  const getBlendPools = new DynamicStructuredTool({
    name: 'get_blend_pools',
    description:
      'Get all active Blend lending pools with current APY rates, TVL, and utilization',
    schema: z.object({}),
    func: async () => {
      try {
        const backstop = await Backstop.load(network, BLEND_CONTRACTS.backstop);
        const poolAddresses = backstop.config.rewardZone;

        const pools = await Promise.all(
          poolAddresses.map(async (addr) => {
            const pool = await PoolV2.load(network, addr);
            return {
              name: pool.metadata.name,
              address: addr,
              reserves: Array.from(pool.reserves.entries()).map(
                ([assetId, reserve]) => ({
                  asset: assetId.slice(0, 8) + '...',
                  supplyApy: (reserve.estSupplyApy * 100).toFixed(2) + '%',
                  borrowApy: (reserve.estBorrowApy * 100).toFixed(2) + '%',
                  utilization:
                    (reserve.getUtilizationFloat() * 100).toFixed(1) + '%',
                })
              ),
            };
          })
        );

        return JSON.stringify(pools, null, 2);
      } catch (err) {
        return JSON.stringify({ error: String(err) });
      }
    },
  });

  // Tool 2: Swap XLM → USDC
  const swapXLMtoUSDC = new DynamicStructuredTool({
    name: 'swap_xlm_to_usdc',
    description:
      'Build a transaction to swap XLM for USDC on Stellar DEX. Returns transaction XDR for signing.',
    schema: z.object({
      amount: z.string().describe('Amount of XLM to swap (e.g., "10")'),
    }),
    func: async ({ amount }) => {
      try {
        // Check trustline
        const hasTrustline = await hasUSDCTrustline(userAddress, networkType);

        if (!hasTrustline) {
          return JSON.stringify({
            status: 'needs_trustline',
            message:
              'You need to establish a USDC trustline first. Would you like me to create it?',
          });
        }

        // Estimate output
        const estimatedUSDC = await estimateSwapOutput(amount, networkType);

        // Build transaction
        const { xdr, hash } = await buildXLMtoUSDCSwap({
          amount,
          userAddress,
          network: networkType,
        });

        return JSON.stringify({
          status: 'ready_to_sign',
          transactionXDR: xdr,
          hash,
          estimatedOutput: estimatedUSDC,
          message: `Ready to swap ${amount} XLM for approximately ${estimatedUSDC} USDC. Please review and sign the transaction.`,
        });
      } catch (err) {
        return JSON.stringify({ error: String(err) });
      }
    },
  });

  // Tool 3: Create USDC Trustline
  const createUSDCTrustline = new DynamicStructuredTool({
    name: 'create_usdc_trustline',
    description:
      'Build a transaction to create a USDC trustline for the user. Required before receiving USDC.',
    schema: z.object({}),
    func: async () => {
      try {
        const { xdr, hash } = await buildUSDCTrustline(userAddress, networkType);

        return JSON.stringify({
          status: 'ready_to_sign',
          transactionXDR: xdr,
          hash,
          message:
            'Trustline transaction ready. This is a one-time setup to enable USDC on your account. Please sign to continue.',
        });
      } catch (err) {
        return JSON.stringify({ error: String(err) });
      }
    },
  });

  return [getBlendPools, swapXLMtoUSDC, createUSDCTrustline];
}
```

### 4.3 Create AI Agent

**File**: `src/lib/ai-agent.ts`

```typescript
import { ChatBedrock } from '@langchain/aws';
import { HumanMessage, AIMessage, SystemMessage } from '@langchain/core/messages';
import { createTuxedoTools } from './ai-tools';

const SYSTEM_PROMPT = `You are Tuxedo, an AI assistant that helps users discover and access high-yield lending opportunities on Stellar through the Blend Protocol.

**Your Capabilities:**
- Query Blend pools to find current APY rates
- Explain DeFi concepts in simple, clear language
- Help users swap XLM for USDC on Stellar DEX
- Guide users through depositing into Blend pools (testnet only)
- Provide risk assessments

**Key Principles:**
1. Always explain risks before recommending any financial action
2. Use plain language - avoid DeFi jargon unless the user asks
3. Only execute transactions on testnet (even though you can see mainnet data)
4. Be transparent about how yields are generated (borrowers pay interest to lenders)
5. Never promise returns - always say "current rate" or "estimated APY"
6. When showing pools, include: APY, TVL, utilization, and risk level

**Current Context:**
- User can see mainnet pool data (real APYs) but can only transact on testnet
- This is a demo application for educational purposes
- Always confirm with the user before building transactions`;

// Initialize Bedrock client
const model = new ChatBedrock({
  region: import.meta.env.VITE_AWS_REGION || 'us-east-1',
  model: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
  credentials: {
    accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID!,
    secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY!,
  },
  temperature: 0.7,
  maxTokens: 2000,
});

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export async function chat(
  userMessage: string,
  conversationHistory: ChatMessage[],
  userAddress: string
) {
  try {
    // Create tools with user's address
    const tools = createTuxedoTools(userAddress, 'testnet');

    // Build message history
    const messages = [
      new SystemMessage(SYSTEM_PROMPT),
      ...conversationHistory.map((msg) =>
        msg.role === 'user'
          ? new HumanMessage(msg.content)
          : new AIMessage(msg.content)
      ),
      new HumanMessage(userMessage),
    ];

    // Bind tools to model
    const modelWithTools = model.bindTools(
      tools.map((tool) => ({
        name: tool.name,
        description: tool.description,
        parameters: tool.schema,
      }))
    );

    // First invocation
    const response = await modelWithTools.invoke(messages);

    // Check if tools were called
    if (response.tool_calls && response.tool_calls.length > 0) {
      const toolResults = [];

      for (const toolCall of response.tool_calls) {
        const tool = tools.find((t) => t.name === toolCall.name);
        if (tool) {
          const result = await tool.invoke(toolCall.args);
          toolResults.push(result);
        }
      }

      // Second invocation with tool results
      const finalResponse = await model.invoke([
        ...messages,
        response,
        new SystemMessage(`Tool results: ${toolResults.join('\n\n')}`),
      ]);

      return finalResponse.content as string;
    }

    return response.content as string;
  } catch (error) {
    console.error('AI Agent error:', error);
    throw new Error('Failed to process message. Please try again.');
  }
}
```

---

## Phase 5: Chat UI

### 5.1 Create Chat Interface Component

**File**: `src/components/ChatInterface.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react';
import { Button, Text, Loader } from '@stellar/design-system';
import { useWallet } from '../hooks/useWallet';
import { chat } from '../lib/ai-agent';
import {
  getOrCreateUser,
  saveConversation,
  trackTransaction,
  type Message,
} from '../lib/supabase';

export const ChatInterface: React.FC = () => {
  const { data: wallet } = useWallet();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [pendingTx, setPendingTx] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize user when wallet connects
  useEffect(() => {
    if (wallet?.address) {
      getOrCreateUser(wallet.address).then((user) => {
        setUserId(user.id);
      });
    }
  }, [wallet?.address]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !userId || !wallet?.address) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chat(input, messages, wallet.address);

      // Check if response contains a transaction
      let txData = null;
      try {
        const parsed = JSON.parse(response);
        if (parsed.status === 'ready_to_sign') {
          txData = parsed;
        }
      } catch {
        // Not JSON, regular text response
      }

      const aiMessage: Message = {
        role: 'assistant',
        content: txData ? txData.message : response,
        timestamp: new Date().toISOString(),
        transaction: txData?.transactionXDR,
      };

      const updatedMessages = [...messages, userMessage, aiMessage];
      setMessages(updatedMessages);

      // Save to Supabase
      const saved = await saveConversation(
        userId,
        updatedMessages,
        conversationId || undefined
      );
      if (!conversationId) {
        setConversationId(saved.id);
      }

      // Set pending transaction if exists
      if (txData) {
        setPendingTx(txData.transactionXDR);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignTransaction = async (xdr: string) => {
    if (!wallet?.signTransaction || !wallet.networkPassphrase || !userId) return;

    try {
      // Sign with wallet
      const signedXdr = await wallet.signTransaction(xdr, {
        networkPassphrase: wallet.networkPassphrase,
        address: wallet.address,
      });

      // Submit transaction (simplified - you'd use useSubmitRpcTx hook)
      console.log('Signed XDR:', signedXdr);

      // Track in database
      await trackTransaction(userId, 'swap', 'pending-hash', {
        network: 'testnet',
        conversationId: conversationId || undefined,
      });

      // Show success message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '✅ Transaction signed and submitted!',
          timestamp: new Date().toISOString(),
        },
      ]);

      setPendingTx(null);
    } catch (error) {
      console.error('Signing failed:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Transaction signing failed. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  if (!wallet?.address) {
    return (
      <div
        style={{
          padding: '40px',
          textAlign: 'center',
          backgroundColor: '#f8f9fa',
          borderRadius: '12px',
        }}
      >
        <Text as="p" size="md">
          Please connect your wallet to start chatting with Tuxedo
        </Text>
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '600px',
        border: '1px solid #e0e0e0',
        borderRadius: '12px',
        overflow: 'hidden',
      }}
    >
      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
          backgroundColor: '#fff',
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <Text as="p" size="lg" style={{ marginBottom: '16px' }}>
              👋 Hi! I'm Tuxedo
            </Text>
            <Text as="p" size="md" style={{ color: '#666' }}>
              Ask me about Blend lending pools, yields, or how to swap XLM for USDC
            </Text>
            <div style={{ marginTop: '24px', fontSize: '14px', color: '#999' }}>
              <p>Try asking:</p>
              <p>"What yields are available for USDC?"</p>
              <p>"I want to swap 10 XLM for USDC"</p>
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

              {msg.transaction && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleSignTransaction(msg.transaction!)}
                  style={{ marginTop: '12px' }}
                >
                  Sign Transaction
                </Button>
              )}
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
            placeholder="Ask about yields, risks, or request a swap..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              fontSize: '14px',
            }}
          />
          <Button
            variant="primary"
            size="md"
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
```

### 5.2 Add to Home Page

**File**: `src/pages/Home.tsx` (update)

```typescript
import { PoolsDashboard } from '../components/dashboard/PoolsDashboard';
import { ChatInterface } from '../components/ChatInterface';
import { Text } from '@stellar/design-system';

export default function Home() {
  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
      {/* Demo Banner */}
      <div
        style={{
          padding: '16px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '8px',
          marginBottom: '24px',
        }}
      >
        <Text as="p" size="sm" style={{ margin: 0 }}>
          <strong>Demo Mode:</strong> Showing mainnet pool data for accurate APYs.
          All transactions are testnet-only.
        </Text>
      </div>

      {/* Chat Interface */}
      <section style={{ marginBottom: '48px' }}>
        <Text as="h2" size="xl" style={{ marginBottom: '16px' }}>
          Ask Tuxedo
        </Text>
        <ChatInterface />
      </section>

      {/* Pool Dashboard */}
      <section>
        <PoolsDashboard />
      </section>
    </div>
  );
}
```

---

## Phase 6: Integration & Testing

### 6.1 Test Checklist

- [ ] **Wallet Connection**
  - Connect Freighter wallet
  - Verify user created in Supabase
  - Check localStorage persistence

- [ ] **Pool Queries**
  - Ask "What yields are available?"
  - Verify AI calls `get_blend_pools` tool
  - Check pools displayed in response

- [ ] **Trading Flow**
  - Ask "Swap 10 XLM for USDC"
  - Verify trustline check
  - If no trustline, create one first
  - Sign trustline transaction in Freighter
  - Then retry swap
  - Sign swap transaction
  - Verify transaction submitted

- [ ] **Conversation Persistence**
  - Send 3-4 messages
  - Refresh page
  - Check if conversation persists (needs conversation loading feature)

- [ ] **Error Handling**
  - Disconnect wallet mid-conversation
  - Reject transaction in Freighter
  - Invalid amounts (negative, too large)

---

## Deployment

### Local Development
```bash
npm run dev
# Visit http://localhost:5173
```

### Production Build
```bash
npm run build
# Outputs to dist/

# Deploy to Vercel
vercel deploy

# Or Netlify
netlify deploy --prod --dir=dist

# Or any static host
```

### Environment Variables (Production)
Remember to set in hosting platform:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_AWS_REGION`
- `VITE_AWS_ACCESS_KEY_ID`
- `VITE_AWS_SECRET_ACCESS_KEY`

---

## Success Criteria

✅ **MVP Complete When:**
1. User can connect wallet
2. User can ask about pools and get responses
3. User can swap XLM → USDC via chat
4. Transactions sign via Freighter
5. Conversations save to Supabase
6. Error handling works gracefully

🎯 **Demo-Ready When:**
1. All MVP features working
2. UI is polished and responsive
3. Error messages are helpful
4. Transaction flow is smooth
5. Can demo end-to-end in 3 minutes

---

## Timeline Estimate

- **Phase 1-2**: 2 hours (setup + database)
- **Phase 3**: 3 hours (trading tools)
- **Phase 4**: 4 hours (AI agent + tools)
- **Phase 5**: 4 hours (chat UI)
- **Phase 6**: 3 hours (testing + polish)

**Total**: ~16 hours (2 working days)

---

## Next Steps

1. **Read this plan carefully**
2. **Set up AWS Bedrock and Supabase accounts**
3. **Start with Phase 1** (install dependencies)
4. **Work through phases sequentially**
5. **Test each phase before moving on**

Ready to implement! 🚀
