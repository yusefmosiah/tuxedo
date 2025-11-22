# Choir: Unified Vision
**The Sovereign Cloud for the Learning Economy**

---

## Executive Summary

Choir is not a "DApp" or a "wallet." It is not "social media" or a "finance app."

**Choir is a Sovereign Cloud—a personal banking agent and learning economy infrastructure.**

Users authenticate into a Trusted Execution Environment (TEE) that contains:
- `keys.json` - Multi-chain private keys (Stellar, EVM, SVM, Bitcoin, Zcash)
- `context.db` - Preferences, risk tolerance, conversation history, research
- `agent_logic.py` - AI Conductor that orchestrates specialized agents

Blockchains are **commodity settlement infrastructure**—pipes for moving capital to wherever risk-adjusted yield is highest. The user sees "12% APY" and "your research earned $50." The agent handles cross-chain bridging, gas optimization, and DeFi complexity invisibly.

This is **Accessible Luxury**: Bank-grade security through biometric authentication. No seed phrases, no "Connect Wallet" buttons. Just scan your face and enter the vault.

---

## I. The Core Reframe: Learning Economy

### The Problem with Existing Categories

**Finance Apps**: Extract fees, require expertise, no intellectual component
**Social Media**: Extract attention, reward engagement, degrade discourse
**AI Platforms**: Extract training data, provide tools, capture all value

None of these models reward **intelligence that creates value**.

### The Learning Economy Model

Choir creates three integrated feedback loops:

```
┌─────────────────────────────────────────────────────────────┐
│                    LOOP 1: Thought Mining                    │
│                    (Knowledge → Value)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Chat freely → Novelty rewards (CHOIR tokens)               │
│  Publish articles → Get cited by agents → Stablecoin income │
│  No capital required → Pure intellectual contribution        │
│                                                              │
│  Pathway: Thought → Publication → Citation → Income         │
│  No external capital needed to earn                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 LOOP 2: Capital Management                   │
│              (Capital → Intelligence → Yield)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Deposit stablecoins → Multi-chain yield strategies          │
│  Agent researches opportunities → Cites knowledge base       │
│  Writes research reports → Generates citable IP              │
│  Performance fees → Fund citation rewards → Close loop       │
│                                                              │
│  Pathway: Capital → Agent Research → Yields → Citations     │
│  Capital deployers directly fund researchers                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  LOOP 3: Network Effects                     │
│            (Masses → Token Demand → Governance)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Free users → Create network effects → Token value          │
│  Researchers → Earn citations → Deploy capital              │
│  Capital deployers → Earn tokens → Governance rights        │
│  Treasury from split decisions → Fund ecosystem              │
│                                                              │
│  Pathway: Participation → Tokens → Capital → Governance     │
│  All positions valuable, natural progression                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**The Flywheel**: Better research → Better yields → More capital → More citations → More researchers → Better research

---

## II. The Sovereign Cloud Architecture

### Authentication: Direct Ownership

**Delete**: "Connect Wallet", "Import Keys", "Social Login" (Google/Coinbase)

**Insert**: Biometric Vault

```
User Experience:
1. Download app
2. Scan face (FaceID / Windows Hello)
3. Account created

Backend Reality:
1. WebAuthn passkey generation
2. TEE provisioned with encrypted filesystem
3. Multi-chain keys generated in secure enclave
4. User never sees seed phrases
```

**The Branding**: "Bank-Grade Security. Biometric Vault. Sovereign Ownership."

**The Rationale**: Rich people don't "connect MetaMask." They scan their face to enter the vault.

### The Filesystem: Your Personal Computer

```
/sovereign/
├── keys.json
│   ├── stellar_keypair
│   ├── evm_private_key (Base, Mainnet, Arbitrum)
│   ├── solana_keypair
│   ├── bitcoin_keypair
│   └── zcash_keypair
│
├── context.db
│   ├── user_preferences
│   ├── risk_tolerance
│   ├── conversation_history
│   ├── research_reports
│   └── citation_graph
│
└── agent_logic.py
    ├── conductor (fast orchestrator)
    ├── ghostwriter_agent
    ├── research_agent
    ├── yield_agent
    └── tax_agent (future)
```

**Key Properties**:
- Hardware-isolated (TEE: Intel SGX, AMD SEV, Phala Network)
- Encrypted at rest
- User-specific (no cross-contamination)
- Persistent across sessions
- Fully auditable by user

**Privacy Guarantee**: Even Choir cannot read your keys or queries. This is "Can't Be Evil" architecture.

### Infrastructure: Chain Agnosticism

**Delete**: All language implying Stellar exclusivity or primacy

**Insert**: Blockchains are **commodity settlement pipes**

```
Capital Destinations (The Pipes):
├── EVM Chains (Base, Mainnet, Arbitrum)
│   └── Use Case: Deep liquidity, Aave/Morpho yields, Aerodrome
│
├── Stellar
│   └── Use Case: Cheap USDC transport, real-world anchors, Blend Capital
│
├── Solana / SVM
│   └── Use Case: High-frequency opportunities, low latency
│
└── Bitcoin / Zcash
    └── Use Case: Pristine collateral, privacy, store of value
```

**User Sees**: "Your capital earned 12% APY this month"

**Agent Handles**:
- Cross-chain bridging (Wormhole, LayerZero, etc.)
- Swap routing (1inch, Jupiter, etc.)
- Gas optimization (batching, EIP-1559 strategies)
- Rebalancing triggers (on-chain data, volatility)

**The Narrative**: "We abstract the nerd details. You see yields and opportunities, not chains and gas."

---

## III. The Conductor + Instruments Pattern

### The Problem with Monolithic AI

Current AI platforms force analytical reasoning and communicative craft into the same model. This creates fundamental trade-offs:

- **ChatGPT Pro**: Expensive models don't produce proportionally better writing
- **Claude**: Great at writing but lacks deep research capabilities
- **Perplexity**: Good at search but generic communication

### The Choir Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                             │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Conductor (Client)                      │ │
│  │                                                          │ │
│  │  • Fast model (GPT-4o-mini, Claude Haiku)               │ │
│  │  • Immediate responses                                  │ │
│  │  • Orchestrates server agents                           │ │
│  │  • Transparent escalation                               │ │
│  │  • Wallet management, search, file ops                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      SERVER LAYER                             │
│                   (Specialized Agents)                        │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Ghostwriter     │  │  Research Agent  │                 │
│  │  Agent           │  │                  │                 │
│  │                  │  │  • Web search    │                 │
│  │  • Plan          │  │  • Vector DB     │                 │
│  │  • Research      │  │  • On-chain data │                 │
│  │  • Draft         │  │  • Citations     │                 │
│  │  • Cite          │  │  • Synthesis     │                 │
│  │  • Review        │  │                  │                 │
│  │  • Refine        │  └──────────────────┘                 │
│  │                  │                                        │
│  │  Uses: Claude,   │  ┌──────────────────┐                 │
│  │  Kimi K2         │  │  Yield Agent     │                 │
│  └──────────────────┘  │                  │                 │
│                        │  • Multi-chain   │                 │
│  ┌──────────────────┐  │  • DeFi protocols│                 │
│  │  Publisher       │  │  • Rebalancing   │                 │
│  │  Agent           │  │  • Risk mgmt     │                 │
│  │                  │  │  • Tax reporting │                 │
│  │  • Stake tokens  │  │                  │                 │
│  │  • Create post   │  └──────────────────┘                 │
│  │  • Citation graph│                                        │
│  │  • Distribute    │  ┌──────────────────┐                 │
│  │    rewards       │  │  Tax Agent       │                 │
│  └──────────────────┘  │  (Future)        │                 │
│                        │                  │                 │
│  ┌──────────────────┐  │  • Jurisdiction  │                 │
│  │  Revision        │  │    detection     │                 │
│  │  Agent           │  │  • Optimization  │                 │
│  │                  │  │  • Reporting     │                 │
│  │  • Propose edits │  │  • Compliance    │                 │
│  │  • Unanimous vote│  └──────────────────┘                 │
│  │  • Split decision│                                        │
│  │  • Treasury flow │                                        │
│  └──────────────────┘                                        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

**1. Separation of Concerns**
- **Conductor**: Fast, responsive, orchestrates
- **Instruments**: Slow, deep, specialized
- **User Experience**: Always fast response, transparent escalation

**2. Model Selection by Task**
- **Ghostwriter Draft**: Claude (style-aware, follows guides)
- **Ghostwriter Critique**: Kimi K2 (actually critical, not sycophantic)
- **Research**: OpenAI o1 / Claude Opus (deep reasoning)
- **Yield Agent**: Specialized financial models (TBD)

**3. Economic Coupling**
- **Novelty rewards**: Trigger on Ghostwriter invocation
- **Citation rewards**: Flow from yield agent performance fees
- **Revision markets**: Unanimous approval or Treasury capture

**4. Privacy by Default**
- **Anonymous publishing**: Wallet signatures, no personal data
- **Homomorphic encryption**: Query without revealing (XTrace migration)
- **TEE execution**: Hardware-level isolation

---

## IV. Economic Architecture

### The Three-Currency Model

```
┌──────────────────────────────────────────────────────────────┐
│                    1. CREDITS (Fiat/IAP)                      │
│                    Gate AI Compute Access                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  • Purchase via IAP (Apple/Google) or credit card            │
│  • Pay for Ghostwriter invocations (1, 5, 20, 100 calls)    │
│  • No crypto knowledge required                              │
│  • Try-before-you-buy (1 call = $2-5)                       │
│                                                               │
│  Why: Accessible entry, predictable pricing                  │
│                                                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    2. STABLECOINS (USDC)                      │
│                    Real Value Exchange                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  • Citation rewards (when research gets cited)               │
│  • Capital deposits (yield farming vaults)                   │
│  • Revision payments (collaborative improvement)             │
│  • Immediately convertible to local fiat                     │
│                                                               │
│  Why: Researchers need stable, spendable income              │
│                                                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    3. CHOIR TOKENS (SUI)                      │
│                    Governance & Compute Options               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  • Novelty rewards (decaying emissions for early users)      │
│  • Yield farming rewards (from capital deployment)           │
│  • Governance rights (protocol parameters, treasury)         │
│  • Publishing stakes (pay to publish, rank by stake)         │
│  • Compute options (tradeable future AI access)              │
│                                                               │
│  Why: Long-term alignment, speculative upside, governance    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Revenue Model

**Primary**: Performance fees from yield farming (20% of profits)
- 70% → Citation reward pool
- 20% → Operations
- 10% → CHOIR token buyback & burn

**Secondary**: Protocol balance sheet strategies
- Collateralized borrowing (CHOIR as collateral)
- Protocol-owned liquidity (trading fees)
- Covered call premiums (option income)
- User lending (interest spread)

**Future**: Ecosystem investments
- Incubator/accelerator for projects building on Choir
- Strategic investments in aligned protocols
- Revenue share agreements

### The Natural Progression

```
Month 0-3: Free Tier
├── Chat freely, earn novelty tokens
├── Build reputation through citations
└── Accumulate 100 CHOIR tokens

Month 3-9: Publishing Phase
├── Publish first article (stake 100 CHOIR)
├── Get cited by agents
├── Earn stablecoins from citations
└── Convert to local fiat or save

Month 9-18: Accumulation Phase
├── Citation rewards exceed spending
├── Decision point: withdraw or deploy?
└── Try deploying $500 in yield farming

Month 18+: Compounding Phase
├── Earn from both sides (citations + yields)
├── CHOIR tokens from yield farming
├── Stake tokens on best articles
└── Participate in governance

Year 2+: Influence Phase
├── Significant capital and tokens
├── Govern protocol evolution
└── Platform becomes a cooperative you partially own
```

**Critical**: You never need capital to earn. The pathway exists entirely through intellectual contribution.

---

## V. Anonymous Publishing & Revision Markets

### The Problem with Traditional Publishing

**Academic Publishing**: Prestige without payment, credential barriers
**Social Media**: Engagement metrics over quality, follower counts
**AI Platforms**: All value extracted, no attribution or compensation

### The Choir Model

```
┌──────────────────────────────────────────────────────────────┐
│                    ANONYMOUS PUBLISHING                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Authentication: Wallet signatures (no personal data)         │
│  Attribution: Cryptographic, immutable, citation graph        │
│  Discovery: Ranked by stake amount (economic signal)          │
│  Rewards: Citations generate stablecoin income                │
│                                                               │
│  Merit-based environment where ideas find audiences           │
│  regardless of author status or credentials                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                      REVISION MARKETS                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Propose: Stake CHOIR tokens on improvement                   │
│  Review: Original author(s) vote                              │
│                                                               │
│  Unanimous Approval:                                          │
│  ├── Stakes go to article treasury                           │
│  ├── Proposer becomes co-author                              │
│  └── Future citations split proportionally                    │
│                                                               │
│  Rejection:                                                   │
│  ├── Stakes returned to proposer                             │
│  └── Article unchanged                                        │
│                                                               │
│  Split Decision (multi-author):                               │
│  ├── Counts as rejection                                      │
│  ├── Stakes go to Choir Treasury                             │
│  └── Treasury redistributes as citation rewards              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Quality Mechanisms

**Economic Stakes**: Publishing requires skin-in-the-game (token stake)
**Citation Tracking**: Semantic similarity auto-detects influence
**Novelty Scoring**: AI identifies genuinely original contributions
**Temporal Validation**: Citations months later prove enduring value

**Anti-Slop Design**: Mass-produced, low-quality content becomes economically unviable

---

## VI. The AI Idiot Test

### The Question

**If AI is so smart, why isn't it making you money?**

### Current AI Platforms Fail

- **ChatGPT**: $20/month → "Productivity" (unmeasurable)
- **Claude**: $20/month → "Better writing" (subjective)
- **Perplexity**: Free/Pro → "Answers" (no economic value)

**You pay to be more useful to others. The platform captures all value.**

### Choir Answers Differently

```
Your research gets cited in profitable strategy
├── AI agent generates $10,000 in yields
├── Platform takes $2,000 performance fee
├── $1,400 goes to citation reward pool
├── Your 50 citations this month
└── You earn $700 in stablecoins (withdrawable)

Agent operator keeps $8,000
You earned $700 from research
Platform earned $600 (operations + buyback)
```

**This is the business model AI should have had from the beginning**: Intelligence that generates measurable profits shared with those who contributed to that intelligence.

---

## VII. Competitive Moats

### Why Big Tech Can't Replicate This

**1. The Sovereign Filesystem**
- Google/Apple/Meta cannot give you a private TEE
- They require data access for ads/training
- Choir's entire model requires privacy

**2. The Economic Inversion**
- OpenAI extracts via subscriptions ($20/month)
- Choir pays you for contributions (citations, novelty)
- Switching their model invalidates their valuations

**3. The Multi-Chain Requirement**
- Big Tech builds on single chains (Coinbase/Base)
- Choir requires chain agnosticism for yield optimization
- Structural difference, not feature addition

**4. The Sequence Dependency**
- Capital deployment → Research demand → Citations → Yields
- You cannot skip stages
- Each stage creates preconditions for next
- Most importantly: falsifiable (examine yields, citations, knowledge base growth)

### First-Mover Advantages

**IP Accumulation**: Early researchers claim foundational concepts
**Citation Networks**: Compound value through reference chains
**Token Distribution**: Novelty rewards front-load to early users
**Treasury Growth**: Split decisions accumulate protocol assets

---

## VIII. Implementation Roadmap

### Phase 1: MVP Foundation (Q4 2025)
**Status: 90% Complete**

- ✅ Passkey authentication (WebAuthn, biometric vault)
- ✅ Multi-chain key management (Stellar, EVM scaffolding)
- ✅ Non-custodial vault system (TUX0 shares, dual authority)
- ✅ Blend Capital integration (mainnet DeFi yields)
- ✅ LangChain agent with 19 tools
- ✅ Claude SDK research wrapper
- 🚧 Anonymous publishing routes
- 🚧 Ghostwriter agent (multi-step workflow)
- 🚧 Citation engine (semantic similarity)

### Phase 2: Learning Economy (Q1-Q2 2026)

**Publishing Infrastructure**:
- [ ] Stake CHOIR to publish
- [ ] Citation graph (auto-detect + manual)
- [ ] Novelty scoring (AI detection)
- [ ] Discovery feed (ranked by stake)

**Economic Loops**:
- [ ] Citation rewards from performance fees
- [ ] Revision markets (unanimous approval)
- [ ] Treasury accumulation (split decisions)
- [ ] Token buyback program

**Multi-Chain Expansion**:
- [ ] EVM integration (Base, Mainnet, Arbitrum)
- [ ] Aave/Morpho yield farming
- [ ] Cross-chain bridging (Wormhole, LayerZero)
- [ ] Solana/SVM scaffolding

### Phase 3: Sovereign Cloud (Q3-Q4 2026)

**TEE Deployment**:
- [ ] Phala Network production deployment
- [ ] Filesystem isolation (keys, context, logic)
- [ ] Hardware attestation
- [ ] User-specific enclaves

**Advanced Features**:
- [ ] Tax-aware optimization (multi-jurisdiction)
- [ ] Homomorphic encryption (XTrace migration)
- [ ] Choir Card (spend while earning yield)
- [ ] Governance token migration

**Mobile Excellence**:
- [ ] SwiftUI iOS app (carbon fiber kintsugi aesthetics)
- [ ] Android app (community-built, open source)
- [ ] Low-bandwidth optimization
- [ ] Telegram bot (SMS regions)

### Phase 4: Decentralization (2027+)

**Governance Transition**:
- [ ] Community treasury control
- [ ] Protocol parameter voting
- [ ] Fee structure decisions
- [ ] Research grant allocation

**Ecosystem Investment**:
- [ ] Incubator/accelerator program
- [ ] Strategic protocol investments
- [ ] Revenue share agreements
- [ ] Community-directed funding

---

## IX. Brand & Positioning

### Delete These Terms
- ❌ "DApp"
- ❌ "Wallet"
- ❌ "Connect Wallet"
- ❌ "Import Keys"
- ❌ "Social Media"
- ❌ "SocialFi"
- ❌ "Post", "Feed", "Followers", "Engagement"
- ❌ "50% APY" (hallucination)
- ❌ "Stellar-first" or chain-exclusive language

### Insert These Terms
- ✅ **"Sovereign Cloud"**
- ✅ **"Personal Banking Agent"**
- ✅ **"Biometric Vault"**
- ✅ **"Learning Economy Infrastructure"**
- ✅ **"Thought Bank"** (intellectual capital becomes productive)
- ✅ **"Citation", "Knowledge Banking", "Reputation", "IP"**
- ✅ **"Stock, not Flow"** (permanent, indexed, citable)
- ✅ **"Optimized blue-chip yields"** (10-15% realistic APY)
- ✅ **"Multi-chain aggregation"** (chain-agnostic)

### The Vibe
**Accessible Luxury**

- **Aesthetics**: Braun/Leica minimalism, carbon fiber kintsugi
- **Security**: Bank-grade, biometric, sovereign
- **Tone**: Quiet confidence, high status, permanent
- **Not**: Crypto-bro, hype, engagement farming, virality

**Cultural Positioning**: The Anti-Feed
- Twitter is the enemy (attention economy, rage-bait)
- Farcaster is "Decentralized Twitter" (same problems)
- Choir is infrastructure for the learning economy (stock, not flow)

---

## X. Success Metrics

### Falsifiable Claims

**Economic**:
- Citation rewards paid in stablecoins > $X per month (verify on-chain)
- Yield farming APY = 10-15% (verify via Blend/Aave data)
- Performance fee distribution = 70/20/10 (verify in smart contracts)
- Token buyback volume (verify on-chain)

**Network Growth**:
- Knowledge base size (articles, citations)
- Free user participation (conversations, novelty rewards)
- Capital deployed (TVL across chains)
- Citation velocity (citations per article per month)

**Quality Signals**:
- Temporal validation (citations 3+ months after publication)
- Revision acceptance rate
- Treasury accumulation from split decisions
- Token holder distribution (Gini coefficient)

### Leading Indicators

**Month 1-3**:
- 1,000+ free users chatting
- 100+ articles published
- First citations recorded
- $10K+ in vaults

**Month 3-6**:
- 10,000+ free users
- 500+ articles published
- Citation rewards > $1K/month
- $100K+ in vaults

**Month 6-12**:
- 100,000+ free users
- 2,000+ articles published
- Citation rewards > $10K/month
- $1M+ in vaults
- Multi-chain expansion live

**Year 2**:
- 1,000,000+ free users
- 10,000+ articles published
- Citation rewards > $100K/month
- $10M+ in vaults
- Governance transition begins

---

## XI. The Unified Codebase

### Current State: Two Repositories

**choir.chat** (SwiftUI mobile):
- Conductor architecture (client orchestrator)
- Anonymous publishing vision
- Token economics design
- MVVM architecture
- Carbon fiber kintsugi aesthetics

**tuxedo** (React web):
- Passkey authentication
- Multi-chain agent (19 tools)
- Non-custodial vault (TUX0)
- TEE deployment (Phala)
- Blend Capital integration

### Convergence Strategy

**Backend Unification** (FastAPI):
```
api/
├── auth/          (passkey routes from tuxedo)
├── conductor/     (orchestration logic from choir)
├── agents/
│   ├── ghostwriter.py   (from choir)
│   ├── research.py      (new, unifies both)
│   └── yield.py         (from tuxedo)
├── publishing/    (anonymous posts, citations)
├── vault/         (TUX0 non-custodial)
├── chains/
│   ├── stellar.py
│   ├── evm.py
│   └── solana.py
└── database/
    ├── threads.py
    ├── publications.py
    └── accounts.py
```

**Frontend Dual-Track**:
- **Mobile**: choir.chat SwiftUI (primary, aesthetics)
- **Web**: tuxedo React (power-user, multi-chain management)
- **Shared**: Same backend API, same wallet, same data

**Migration Path**:
1. Backend API unification (this sprint)
2. Mobile app connects to unified backend
3. Web app refactor (Conductor UI pattern)
4. Feature parity, platform-specific optimizations

---

## XII. Conclusion: The Structural Advantage

Choir succeeds not by executing better on existing models, but by **creating new infrastructure the incumbents cannot replicate**.

### The Moats

**Technical**:
- Sovereign Cloud (TEE filesystem with multi-chain keys)
- Conductor pattern (separation of concerns)
- Chain agnosticism (no single-chain lock-in)

**Economic**:
- Learning economy loops (thought → capital → network)
- Protocol balance sheet (CHOIR as productive asset)
- Citation as payment rail (intellectual property → income)

**Social**:
- Anonymous publishing (merit over status)
- Quality compounding (temporal validation)
- Revision markets (collaborative improvement)

### The Vision

**Your ideas make AI smarter. When AI makes money, you should too.**

This isn't a tagline. It's the entire economic model.

- Intelligence that creates value shares in that value
- Capital that deploys intelligence pays for that intelligence
- Network effects emerge from genuine contribution
- Quality becomes measurably valuable in dollar terms

**The Thought Bank**: Deposit ideas, earn interest. Let your intellectual property work for you.

**The Sovereign Cloud**: Your personal banking agent. Multi-chain. Private. Profitable.

**Choir**: Infrastructure for the learning economy.

---

**Document Version**: 1.0
**Created**: 2025-11-22
**Status**: North Star Vision
**Next Steps**: Architecture design → Implementation → Deployment

---

## Appendix: Key Architectural Decisions

### Why Passkeys Over Wallet Signatures?
- Better UX (biometric, no seed phrases)
- Multi-chain neutral (not Stellar/EVM-specific)
- Recovery mechanisms (email backup, multiple passkeys)
- Enterprise-ready (WebAuthn standard)

### Why TEE Over Smart Contracts?
- Complex multi-step workflows
- Multi-chain orchestration
- LLM integration
- Privacy guarantees
- Real-time rebalancing

### Why Three Currencies?
- Credits: Accessibility (fiat on-ramp, no crypto knowledge)
- Stablecoins: Stability (researchers need spendable income)
- CHOIR: Alignment (governance, speculation, long-term value)

### Why Anonymous Publishing?
- Merit over status
- Educational access (no credential barriers)
- Professional freedom (share without career risk)
- Intellectual honesty (citations detect plagiarism)

### Why Multi-Chain?
- Yield optimization (capital goes where returns are highest)
- Risk diversification (no single-chain dependency)
- Future-proof (new chains emerge, old chains fade)
- User abstraction (chains invisible, yields visible)

---

**This is Choir. This is the unified vision. All decisions flow from here.**
