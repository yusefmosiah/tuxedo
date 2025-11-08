# Strategic Pivot: Research-First Agent Architecture
**Tuxedo/Choir Security-First Development Strategy**

**Date:** 2025-11-08
**Status:** Strategic Planning - Actionable Recommendations

---

## Executive Summary

**Core Thesis:** DeFi agents are inevitable (2027-2030 timeline), but security is the blocking issue. Tuxedo/Choir succeeds by:

1. **Understanding security concepts** > implementing features
2. **Rewarding security research** with platform tokens
3. **Building community trust** through transparent work-in-progress
4. **Demonstrating agentic finance** on testnet before mainnet
5. **Architecting for research** as the foundation of agent intelligence

**Critical Pivot:** Move from LangChain tool calling to **Claude API with extended thinking + interleaved tool use**, enabling the research-centric architecture described in the Choir whitepaper.

---

## The Core Message

### What We're Building

**Not:** "Another DeFi optimizer with AI"
**Instead:** "The first platform where security testing earns you ownership in inevitable agentic finance infrastructure"

### Why Anyone Should Care

1. **For Security Researchers:** Earn platform tokens for finding vulnerabilities in testnet
2. **For Beta Users:** Early adopters accumulate tokens before mainnet launch
3. **For Engineers:** Build trusted brand through transparent, community-validated security
4. **For Everyone:** When agents are managing trillions by 2030, you want the one that was battle-tested by community security researchers from day one

### Honest Positioning

> "Tuxedo is built with AI coding agents, so it's as secure as AI slop. Which is to say, not secure yet. We know this. That's why we're paying security researchers in platform tokens to help us get to mainnet. DeFi is risky enough—we're doing our best with security while being transparent that it's a work in progress requiring community effort."

---

## Research-First Architecture: The Paradigm Shift

### From Tool Calling to Code Mode

**Current Problem:** LangChain's tool calling pattern has fundamental limitations:

```
User → Agent → LangChain Tool Selection → Tool Execution → Response
```

**Issues:**
- All tool definitions loaded upfront (context bloat)
- Intermediate results pass through model repeatedly (token waste)
- Sequential tool calls require model round-trips
- No native state persistence across conversations
- Inflexible chaining of operations

**New Paradigm:** Claude Code Mode Pattern

```
User → Agent writes TypeScript → Secure sandbox executes → Results filtered → Response
```

**Advantages:**
- Progressive disclosure: Load tool definitions on-demand
- Data filtering: Process 10K rows → return 5 relevant ones
- Native control flow: Loops, conditionals, error handling in code
- State persistence: Workspace files enable resumable workflows
- Privacy: Sensitive data stays in execution environment

**Example from Anthropic's analysis:**
- Traditional: 150,000 tokens for multi-step research task
- Code Mode: 2,000 tokens for same task
- **98.7% reduction in cost and latency**

### Extended Thinking + Interleaved Tool Use

**Claude 4 capabilities** (available now via OpenRouter, Bedrock, and anthropic-compatible endpoints):

1. **Extended Thinking:** Model thinks deeply before responding
2. **Interleaved Thinking:** Model thinks *between* tool calls
3. **Parallel Tool Calls:** Multiple tools execute simultaneously
4. **Thinking in Context:** Thinking blocks remain in context for better agent performance

**Critical API Requirement:**
```python
# Enable interleaved thinking with tools
headers = {
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "interleaved-thinking-2025-05-14"
}

# MUST pass thinking blocks back to API
messages = [
    {"role": "user", "content": "Research DeFi strategies"},
    {"role": "assistant", "content": [
        {"type": "thinking", "thinking": "I need to..."},  # REQUIRED
        {"type": "tool_use", "name": "research", ...},
    ]},
    {"role": "user", "content": [{"type": "tool_result", ...}]},
    # Continue conversation with thinking preserved
]
```

**Why This Matters for Tuxedo:**

Your agents need to:
- Research DeFi protocols continuously
- Write reports that go into vector database
- Make decisions informed by live data + historical research
- Chain multiple tools (market data → analysis → transaction execution)
- Maintain context across long research sessions

Extended thinking + interleaved tool use makes this possible efficiently.

### Research Agent: The Missing Piece

**From Choir Whitepaper:**

> "Agents don't just execute trades—they write research reports explaining every decision. Before moving capital from one protocol to another, an agent must document why this move makes sense given current market conditions, on-chain data, and relevant research from Choir's knowledge base."

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  Platform Agency (24/7 background operation)            │
│  ├── Live Data Feeds (Somnia Data Streams)              │
│  ├── Research Agent (constant writing)                  │
│  │   ├── Analyzes market conditions                     │
│  │   ├── Monitors on-chain data                         │
│  │   ├── Writes reports → Vector DB                     │
│  │   └── Updates every N minutes                        │
│  └── Report Repository (growing knowledge base)         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  User Agents (on-demand)                                │
│  ├── Read platform research reports                     │
│  ├── Conduct live research                              │
│  ├── Make informed decisions                            │
│  ├── Execute transactions                               │
│  └── Write their own reports (citeable by others)       │
└─────────────────────────────────────────────────────────┘
```

**Example Flow:**

1. **Platform Agency (Background):**
   - Monitors Blend lending rates every 5 minutes
   - Detects XLM/USDC rate spike
   - Writes report: "Blend XLM borrowing rates increased 2% in last hour, likely due to..."
   - Stores in vector DB with timestamp and on-chain references

2. **User Agent (On-Demand):**
   - User asks: "Should I move capital from DeFindex to Blend?"
   - Agent queries vector DB: Finds platform report from 3 minutes ago
   - Agent conducts live research: Confirms current rates
   - Agent writes decision report: "Moving 1000 USDC to Blend because [cites platform report + live data]"
   - Executes transaction
   - Stores own report (other agents can cite it later)

**This is the Choir thesis:** Research compounds. Early reports inform later decisions. Citations reward quality thinking. The platform gets smarter over time.

---

## Migration Plan Reassessment

### What the Current Plan Gets Right

✅ **Quantum Leap Approach:** No gradual migration—complete replacement
✅ **User Isolation:** `user_id` flows through every layer
✅ **AccountManager over PortfolioManager:** Flat account storage, agents construct abstractions
✅ **Chain-Agnostic Design:** Supports Stellar, Solana, EVM, Sui
✅ **Import/Export:** Respects "not-your-keys-not-your-crypto"

### Critical Gaps

❌ **No transaction execution capability** - Agents can't actually trade yet
❌ **LangChain tool calling** - Wrong paradigm for research-heavy workflows
❌ **No research agent** - Missing the core of Choir's value proposition
❌ **No live data feeds** - Can't monitor markets 24/7
❌ **No vector database integration** - Reports have nowhere to go

### Revised Priority Stack

**Phase 0: Agent Architecture Pivot** (NEW - HIGHEST PRIORITY)
- Research Claude API patterns (extended thinking, interleaved tools)
- Prototype code execution sandbox (or use managed service)
- Test OpenRouter/Bedrock Claude endpoints
- Design research agent workflow
- Integrate vector database (Qdrant or XTrace)

**Phase 1: Security Migration** (Keep as-is)
- Quantum leap to AccountManager
- User isolation at every boundary
- Encrypted key storage
- Permission-checked tool calls

**Phase 2: Transaction Execution** (NEW)
- Enable DeFindex API calls
- Enable Soroban contract interactions
- Implement transaction signing with user-isolated keys
- Add transaction approval workflows (future: multi-sig)

**Phase 3: Research Infrastructure** (NEW)
- Platform agency deployment (24/7 worker)
- Somnia Data Streams integration
- Research report generation pipeline
- Vector database population

**Phase 4: Testnet Beta Launch**
- Distribute tokens to beta users
- Security bug bounty program (paid in tokens)
- Public security audit logging
- Community validation period

---

## Somnia Data Streams Opportunity

### Hackathon Details

- **Dates:** November 4-15, 2025 (ACTIVE NOW)
- **Prize:** $300 worth of SOMI tokens per winner
- **Focus:** Real-time blockchain data applications
- **Link:** https://dorahacks.io/hackathon/somnia-datastreams

### Why This Matters

**Somnia Data Streams** is exactly what we need for the platform agency:

- **Subscription-based RPCs:** Subscribe to specific data, get instant updates
- **State change notifications:** Rather than polling, receive push notifications
- **1M+ TPS network:** Sub-second finality
- **Firebase-like dev experience:** Modern database feel with blockchain security

**Use Case for Tuxedo:**

Instead of:
```python
# Poll every 30 seconds (expensive, slow)
while True:
    rates = poll_blend_rates()
    if changed_significantly(rates):
        write_report(rates)
    await asyncio.sleep(30)
```

Do this:
```python
# Subscribe once, get instant updates
somnia.subscribe("blend.lending_rates", callback=on_rate_change)

async def on_rate_change(data):
    # Platform agency writes report immediately
    report = research_agent.analyze_rate_change(data)
    vector_db.store(report)
```

**Hackathon Strategy:**

1. **Quick Integration:** Build Somnia adapter for Tuxedo's platform agency
2. **Demonstrate Concept:** Show research agent writing reports from live data
3. **Win Recognition:** $300 + ecosystem visibility
4. **Long-term Value:** Prove concept for future multi-chain data feeds

**Time Investment:** 1-2 days if scoped to proof-of-concept
**Deadline:** November 15, 2025 (7 days from now)

---

## Tool Calling Architecture Recommendations

### Option 1: Claude API Direct (RECOMMENDED)

**Advantages:**
- Extended thinking + interleaved tool use (best-in-class)
- Parallel tool execution
- Thinking preserved in context (crucial for research)
- Multiple providers (OpenRouter, Bedrock, Anthropic direct)

**Implementation:**
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Or via OpenRouter for model flexibility
client = anthropic.Anthropic(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

tools = [
    {
        "name": "research_defi_protocol",
        "description": "Research DeFi protocol metrics and rates",
        "input_schema": {
            "type": "object",
            "properties": {
                "protocol": {"type": "string"},
                "metrics": {"type": "array", "items": {"type": "string"}}
            }
        }
    },
    # ... other tools
]

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # For extended thinking
    },
    tools=tools,
    messages=[...],
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    }
)
```

**Migration Path:**
1. Extract tool definitions from current LangChain setup
2. Convert to Anthropic tool schema
3. Build thin wrapper for OpenRouter/Bedrock compatibility
4. Test with extended thinking enabled
5. Replace agent loop in `backend/api/routes/agent.py`

### Option 2: Code Mode Pattern

**Advantages:**
- 98.7% token reduction for multi-step workflows
- Native Python/TypeScript execution
- State persistence
- Progressive tool discovery

**Challenges:**
- Requires secure sandbox (V8 isolate or Cloudflare Workers)
- More complex to set up initially
- Need to expose filesystem-style interface

**When to Use:**
- For ghostwriter agent (complex multi-step research)
- For long-running background jobs (platform agency)
- When token costs become prohibitive

**Recommendation:** Start with Option 1 (direct API), migrate to Code Mode for specific heavy workflows

### Option 3: Hybrid Approach (ULTIMATE GOAL)

```
┌─────────────────────────────────────┐
│  User Chat Agent                    │
│  - Claude API with extended thinking│
│  - Fast, conversational             │
│  - Parallel tool calls              │
└────────────┬────────────────────────┘
             │ Delegates to ↓
┌────────────────────────────────────┐
│  Research Agent (Code Mode)         │
│  - Long-running research tasks      │
│  - Multi-step analysis              │
│  - Report generation                │
│  - Runs in sandbox                  │
└────────────┬────────────────────────┘
             │ Stores in ↓
┌────────────────────────────────────┐
│  Vector Database                    │
│  - Qdrant or XTrace                 │
│  - Homomorphic encryption           │
│  - Citeable research reports        │
└────────────────────────────────────┘
```

---

## Immediate Action Plan

### Week 1: Agent Architecture Pivot (Nov 8-15)

**Day 1-2: Research & Design**
- [ ] Test Claude API with extended thinking (use AWS Bedrock credits)
- [ ] Prototype tool calling pattern (migrate 1-2 tools from LangChain)
- [ ] Design research agent workflow
- [ ] Evaluate Somnia Data Streams integration effort

**Day 3-4: Core Implementation**
- [ ] Replace LangChain agent loop with Claude API
- [ ] Implement extended thinking + interleaved tool use
- [ ] Test parallel tool execution
- [ ] Migrate all tools to new pattern

**Day 5-6: Research Agent Prototype**
- [ ] Build background worker service (platform agency)
- [ ] Integrate vector database (Qdrant)
- [ ] Implement report generation pipeline
- [ ] Test research agent writing + storage

**Day 7: Somnia Hackathon Submission**
- [ ] Build Somnia adapter (if feasible)
- [ ] Demo research agent responding to live data
- [ ] Submit to hackathon
- [ ] Document learnings

### Week 2: Security Migration (Nov 16-22)

Execute the quantum leap migration plan as documented in `AGENT_MIGRATION_QUANTUM_LEAP.md`:

**Day 1-2: Database & Encryption**
- [ ] Delete KeyManager (quantum leap)
- [ ] Implement AccountManager
- [ ] Update database schema
- [ ] Test encryption/decryption

**Day 3-4: Tool Signature Updates**
- [ ] Add `user_id` to all tool functions
- [ ] Implement permission checks
- [ ] Update agent tool registration
- [ ] Test user isolation

**Day 5-6: Transaction Execution**
- [ ] Enable DeFindex API calls with user-isolated keys
- [ ] Enable Soroban contract interactions
- [ ] Test transaction signing
- [ ] Verify security boundaries

**Day 7: Security Testing**
- [ ] Run isolation tests (user A can't access user B's accounts)
- [ ] Test cross-user attack vectors
- [ ] Document security assumptions
- [ ] Create security disclosure template

### Week 3-4: Beta Launch Preparation

**Token Distribution Strategy:**
- [ ] Define token allocation for beta users
- [ ] Implement token grants for security findings
- [ ] Create bug bounty tiers (minor/medium/critical)
- [ ] Design public security audit log

**Documentation:**
- [ ] Security assumptions document
- [ ] Known limitations disclosure
- [ ] Responsible disclosure guidelines
- [ ] Beta user agreement (testnet only, security testing encouraged)

**Community Building:**
- [ ] Launch security researcher outreach
- [ ] Create Discord/Telegram for beta users
- [ ] Publish roadmap transparency page
- [ ] Begin documenting security improvements publicly

---

## Security Concepts to Master

### 1. Threat Modeling for Agentic Finance

**Question:** What attack vectors exist when AI controls crypto?

**Study Areas:**
- Prompt injection attacks (can user trick agent into transferring funds?)
- Tool call manipulation (can malicious tool results compromise agent?)
- Key isolation failures (can one user's agent access another's keys?)
- Replay attacks (can attacker replay signed transactions?)
- Oracle manipulation (can fake price feeds trick agent?)

### 2. Trusted Execution Environments (TEEs)

**Question:** How do we give agents key custody without trusting our own servers?

**Study Areas:**
- Intel SGX, AMD SEV, ARM TrustZone
- Attestation and remote verification
- Sealed storage for secrets
- Limitations and attacks on TEE systems
- Practical deployment on cloud providers

### 3. Multi-Signature and Social Recovery

**Question:** How do we prevent total loss if agent is compromised?

**Study Areas:**
- Threshold signatures (2-of-3, 3-of-5)
- Time-locked recovery mechanisms
- Guardian-based recovery (Argent model)
- Account abstraction on EVM chains
- Stellar sponsorship and clawback

### 4. Homomorphic Encryption for Private Research

**Question:** How can agents share research without revealing user strategies?

**Study Areas:**
- XTrace vector database (homomorphic embedding search)
- Differential privacy for aggregated reports
- Zero-knowledge proofs for strategy verification
- Secure multi-party computation for collaborative research

### 5. Transaction Approval Workflows

**Question:** What should require user approval vs. autonomous execution?

**Design Considerations:**
- Spending limits (< $100 = auto, > $100 = approval?)
- Risk tiers (stablecoin lending = low, leveraged perps = high)
- Emergency stop mechanisms
- User preference profiles (conservative vs. aggressive autonomy)

---

## Messaging Framework

### For Security Researchers

**Pitch:**
> "We're building the infrastructure for agentic finance in 2027-2030. We know we're not secure yet—we're built with AI coding agents. Help us get to mainnet and earn platform tokens for every vulnerability you find. When agents are managing trillions, you'll own a piece of the platform that was battle-tested from day one."

**Call to Action:**
- Join our Discord security channel
- Review our public codebase
- Test on testnet (we'll fund your accounts)
- Submit findings via GitHub Security
- Earn tokens based on severity tiers

### For Beta Users

**Pitch:**
> "DeFi agents are inevitable. Everyone will have one managing their yield by 2030. But who do you trust with your keys? Tuxedo is building trust through transparent security development and community validation. Testnet beta users earn tokens for providing product validation and security feedback."

**Value Proposition:**
- Early token accumulation (before mainnet)
- Demonstrate agentic finance on testnet
- Vote on roadmap priorities with tokens
- Learn DeFi without risking real capital
- Build reputation as early adopter

### For Engineers

**Pitch:**
> "Join us in solving the hardest problem in DeFi: making AI agents secure enough to manage real money. We're researching TEEs, homomorphic encryption, multi-sig workflows, and transparent security development. This is greenfield infrastructure work with compounding network effects."

**Opportunities:**
- Research-first development culture
- Public security documentation
- Token grants for security improvements
- Collaboration with security researchers
- Building trusted brand through transparency

---

## Success Metrics

### Phase 1: Agent Architecture (Week 1)
- [ ] Claude API integration working with extended thinking
- [ ] Parallel tool calls executing correctly
- [ ] Research agent prototype writing reports
- [ ] Vector database storing citeable research
- [ ] (Stretch) Somnia hackathon submission

### Phase 2: Security Migration (Week 2)
- [ ] Zero cross-user account access attempts succeed
- [ ] All transactions require user-owned keys
- [ ] Permission checks enforce at every boundary
- [ ] Encryption tested and validated
- [ ] Transaction execution works on testnet

### Phase 3: Beta Launch (Week 3-4)
- [ ] 10+ security researchers engaged
- [ ] First security finding submitted and rewarded
- [ ] 50+ beta users testing on testnet
- [ ] Public security audit log established
- [ ] Roadmap to mainnet published

---

## Open Questions for Discussion

1. **TEE Strategy:** Deploy our own (complex) vs. use managed service vs. defer until post-MVP?

2. **Transaction Approval:** What default autonomy level? All transactions require approval initially? Or spending limits?

3. **Token Economics:** How to value security findings? Fixed tiers vs. percentage of total supply?

4. **Vector Database:** Qdrant (familiar) vs. XTrace (homomorphic encryption but newer)?

5. **Code Mode:** Invest now or defer until agent loops are stable?

6. **Somnia Hackathon:** Worth 1-2 day sprint given current architecture uncertainty?

---

## Related Documents

- `AGENT_MIGRATION_QUANTUM_LEAP.md` - Security migration plan
- `AGENT_ACCOUNT_SECURITY_PLAN.md` - Overall security architecture
- `CHOIR_WHITEPAPER.md` - Long-term vision and product thesis
- `CLAUDE.md` - Current codebase state

---

**Version:** 1.0
**Author:** Claude Code
**Date:** 2025-11-08
**Status:** Strategic recommendation - awaiting discussion and prioritization
