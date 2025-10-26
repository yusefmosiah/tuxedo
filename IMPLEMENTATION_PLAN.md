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
├── AI Integration
│   ├── LangChain.js + RedPill Qwen3-VL (Phala Cloud)
│   └── Blend Pool Query Tool
└── Existing Infrastructure (from Scaffold Stellar)
    ├── WalletProvider + useWallet hook ✅
    ├── Freighter integration ✅
    ├── useBlendPools hook ✅
    └── Blend SDK integration ✅

External Services
├── RedPill Qwen3-VL via Phala Cloud (Private GPU TEE)
└── Stellar Network (Soroban RPC for pool data)
```

### Why This Approach?

**Focus on Core Value First:**
- ✅ Get conversational pool discovery working in hours, not days
- ✅ Prove AI + DeFi UX value before adding complexity
- ✅ No database setup/management until it adds value
- ✅ No transaction signing flow until core chat works

**Add Later When Valuable:**
- 🔮 Trading tools (once users trust pool recommendations)
- 🔮 Supabase (once users want conversation history)
- 🔮 Portfolio tracking (once users have positions)

---

## Phase 1: Setup & Dependencies

### 1.1 Install NPM Packages

```bash
npm install --save \
  @langchain/core \
  @langchain/openai \
  zod
```

**Note**: Skipping `@supabase/supabase-js` for now - we'll add it in Phase 6 (Future).

### 1.2 Environment Variables

Create/update `.env.local`:

```bash
# Existing Stellar Config
VITE_STELLAR_NETWORK=testnet
VITE_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_RPC_URL=https://soroban-testnet.stellar.org

# NEW: RedPill API (OpenAI-compatible) via Phala Cloud
VITE_OPENAI_API_KEY=...  # Your RedPill API key
VITE_OPENAI_BASE_URL=https://www.redpill.ai/api/v1  # RedPill OpenAI-compatible endpoint
```

### 1.3 RedPill API Setup (Phala Cloud)

**Get API Key**:
1. Go to https://www.redpill.ai/
2. Sign up and create an account
3. Navigate to your API settings to get an API key
4. Add it to your `.env.local` file

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

## Phase 2: AI Agent & Blend Tools

### 2.1 Create Blend Query Tool

**File**: `src/lib/ai-tools.ts`

```typescript
import { DynamicStructuredTool } from '@langchain/core/tools';
import { z } from 'zod';
import { Backstop, PoolV2 } from '@blend-capital/blend-sdk';
import { BLEND_CONTRACTS } from '../contracts/blend';
import { network } from '../contracts/util';

export function createBlendTools() {
  const getBlendPools = new DynamicStructuredTool({
    name: 'get_blend_pools',
    description:
      'Get all active Blend lending pools with current APY rates, total value locked (TVL), and utilization metrics. Use this to answer questions about yields, lending opportunities, and market conditions.',
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
              address: addr.slice(0, 8) + '...',
              reserves: Array.from(pool.reserves.entries()).map(
                ([assetId, reserve]) => ({
                  asset: assetId.slice(0, 8) + '...',
                  supplyApy: (reserve.estSupplyApy * 100).toFixed(2) + '%',
                  borrowApy: (reserve.estBorrowApy * 100).toFixed(2) + '%',
                  totalSupplied: reserve.totalSupply,
                  totalBorrowed: reserve.totalLiabilities,
                  utilization: (reserve.getUtilizationFloat() * 100).toFixed(1) + '%',
                  availableLiquidity: (reserve.totalSupply - reserve.totalLiabilities).toString(),
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

  return [getBlendPools];
}
```

### 2.2 Create AI Agent

**File**: `src/lib/ai-agent.ts`

```typescript
import { ChatOpenAI } from '@langchain/openai';
import { HumanMessage, AIMessage, SystemMessage } from '@langchain/core/messages';
import { createBlendTools } from './ai-tools';

const SYSTEM_PROMPT = `You are Tuxedo, an AI assistant that helps users discover and understand lending opportunities on Stellar through the Blend Protocol.

**Your Capabilities:**
- Query all active Blend pools to find current APY rates
- Explain DeFi lending concepts in simple, clear language
- Compare different pools and assets
- Assess risk based on utilization rates and pool metrics
- Provide context about how yields are generated

**Key Principles:**
1. **Plain language first** - Avoid DeFi jargon unless the user asks for technical details
2. **Always explain risks** - High APY usually means higher risk (utilization, volatility, liquidity)
3. **Be transparent** - Yields come from borrowers paying interest to lenders
4. **Never promise returns** - Always say "current rate" or "estimated APY based on today's data"
5. **Show your work** - When comparing pools, show the numbers (APY, utilization, TVL)

**Example Responses:**

User: "What yields are available for USDC?"
You: "Let me check the current Blend pools... [calls get_blend_pools]
I found USDC lending in the Comet pool offering 12.5% APY. This rate is higher than traditional savings because:
- Borrowers are paying 18% to borrow USDC
- The pool is 65% utilized (good liquidity, moderate risk)
- $2.3M currently lent, $850K available to withdraw

The yield fluctuates based on borrowing demand. Higher utilization = higher rates but less liquidity."

User: "Is 12% APY risky?"
You: "It depends on context. Let me break it down:
- **Smart contract risk**: All DeFi carries this risk. Blend is audited but not risk-free.
- **Utilization risk**: At 65%, you can withdraw anytime. Above 90% gets concerning.
- **Market risk**: USDC is a stablecoin, so less volatile than crypto assets.

Compare this to XLM at 8% APY but 85% utilization - lower rate, higher withdrawal risk."

**Current Context:**
- User is exploring Blend pools on Stellar mainnet
- This is for educational/informational purposes
- Focus on helping users understand opportunities and risks`;

// Initialize OpenAI client with RedPill endpoint (Phala Cloud)
const model = new ChatOpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  model: 'qwen/qwen3-vl-235b-a22b-instruct',
  temperature: 0.7,
  maxTokens: 2000,
  configuration: {
    baseURL: import.meta.env.VITE_OPENAI_BASE_URL,
  },
});

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export async function chat(
  userMessage: string,
  conversationHistory: ChatMessage[]
): Promise<string> {
  try {
    const tools = createBlendTools();

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

## Phase 3: Chat UI

### 3.1 Create Chat Interface Component

**File**: `src/components/ChatInterface.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react';
import { Button, Text, Loader } from '@stellar/design-system';
import { chat, type ChatMessage } from '../lib/ai-agent';
import { useWallet } from '../hooks/useWallet';

export const ChatInterface: React.FC = () => {
  const { data: wallet } = useWallet();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chat(input, messages);

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
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
            placeholder="Ask about yields, pools, or DeFi concepts..."
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

### 4.1 Test Checklist

- [ ] **AI Chat Basics**
  - [ ] Chat interface renders on home page
  - [ ] Can send message and get response
  - [ ] Loading state shows while waiting
  - [ ] Messages display in correct bubbles (user right, AI left)

- [ ] **Pool Queries**
  - [ ] Ask "What yields are available?"
  - [ ] Verify AI calls `get_blend_pools` tool (check console)
  - [ ] Response includes APY rates and pool names
  - [ ] Ask "Which pool has the best APY?"
  - [ ] Response compares pools and explains context

- [ ] **Educational Queries**
  - [ ] Ask "What is Blend Protocol?"
  - [ ] Ask "How does DeFi lending work?"
  - [ ] Ask "Is high APY risky?"
  - [ ] Verify responses are clear and non-technical

- [ ] **Error Handling**
  - [ ] Remove OpenAI API key (temporarily)
  - [ ] Send message, verify error message appears
  - [ ] Restore API key, verify recovery
  - [ ] Test with empty messages (should be disabled)

### 4.2 Manual Testing Script

```
1. Open http://localhost:5173
2. See "Ask Tuxedo" section with empty chat
3. Type: "What yields are available for USDC?"
4. Press Enter or click Send
5. Wait 2-5 seconds (loading indicator should show)
6. Expect response like:
   "I found USDC lending in the Comet pool offering X% APY.
    Here's what you should know:
    - Borrowers are paying Y% to borrow USDC
    - Pool is Z% utilized
    - $N currently lent..."
7. Type: "Is that risky?"
8. Expect contextual explanation of utilization, smart contract risk, etc.
9. Scroll down to Pool Dashboard
10. Verify pool data matches what AI described
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
Set in hosting platform:
- `VITE_OPENAI_API_KEY` (your RedPill API key)
- `VITE_OPENAI_BASE_URL` (set to `https://www.redpill.ai/api/v1`)

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

- **Phase 1**: 15 minutes (install dependencies, setup OpenAI API)
- **Phase 2**: 2 hours (AI agent + Blend tool)
- **Phase 3**: 2 hours (chat UI)
- **Phase 4**: 1 hour (testing + polish)

**Total**: ~5-6 hours (one focused session)

---

## Next Steps

1. ✅ Install dependencies from Phase 1
2. ✅ Set up RedPill API key (OpenAI-compatible)
3. ✅ Create `src/lib/ai-tools.ts`
4. ✅ Create `src/lib/ai-agent.ts`
5. ✅ Create `src/components/ChatInterface.tsx`
6. ✅ Update `src/pages/Home.tsx`
7. ✅ Test with manual queries
8. 🎉 Demo!

**Then Later**:
- Phase 5 (Trading) when users ask for it
- Phase 6 (Supabase) when users want history

Ready to build the leanest possible AI × DeFi demo! 🚀
