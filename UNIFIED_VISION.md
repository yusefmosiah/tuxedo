# Choir: The Thought Bank
**Intelligence that creates value should share in that value**

---

## Executive Summary

Choir is AI research infrastructure for the learning economy.

**The core product is Ghostwriter**: An AI agent that helps you research, write, and publish—then pays you in stablecoins when your work gets cited.

**No capital required to earn.** Chat freely, publish research, get cited by AI agents making decisions, receive citation rewards in real money. The pathway from zero to income exists entirely through intellectual contribution.

**Optional for those with capital**: Automated yield farming across multiple blockchains. AI agents manage DeFi strategies, write research reports citing the knowledge base, and fund citation rewards from performance fees.

**The economic loop**: Capital deployers fund researchers. Researchers make agents smarter. Smarter agents generate better yields. Better yields fund more research.

This is not social media (no feeds, no followers, no engagement farming). This is not academic publishing (no gatekeeping, no 18-month peer review, no credential requirements). This is infrastructure for the learning economy where genuine insight generates measurable economic value.

---

## I. The Problem: Three Broken Models

### Academic Publishing: Credentialism Over Insight

Academic publishing exploits non-prestige scholars while rewarding institutional affiliation over merit:
- 18-month peer review cycles when AI achieves "Move 37" breakthroughs daily
- Paywalls extracting billions while compensating authors nothing
- Tenure committees valuing journal prestige over intellectual contribution
- Junior scholars producing original research, senior faculty capturing credit
- Anonymous review enabling status quo protection and political gatekeeping

When AI makes fundamental breakthroughs across every field simultaneously, the traditional publishing model becomes a bottleneck. We need rapid publication, merit-based evaluation, and economic rewards for insight—not credential verification and prestige hierarchies.

### Social Media: Attention Extraction

Social platforms optimize for engagement, degrading discourse:
- Viral content rewards outrage over insight
- Follower counts determine distribution, not quality
- Algorithmic feeds bury depth under volume
- Network effects create winner-take-all dynamics
- Platforms extract all value, creators capture vanishing returns

The attention economy makes individual contributions worthless as volume increases. AI-generated content accelerates this to collapse.

### AI Platforms: Training Data Extraction

Current AI platforms capture all value from your intellectual contributions:
- ChatGPT: You make it smarter, OpenAI captures billions
- Claude: Your conversations improve the model, Anthropic owns the value
- Perplexity: Your queries refine search, you get answers worth nothing

**The AI Idiot Test**: If AI is so smart, why isn't it making you money?

You pay $20/month for "productivity" (unmeasurable). The platform captures training data value (billions). You get tools that make you useful to others while remaining propertyless.

---

## II. The Solution: Citation Economics

### The Thought Bank Model

Traditional banks let you deposit money and earn interest. Thought banks let you deposit ideas and earn interest.

**How it works**:

1. **Research and write** using Ghostwriter (multi-model AI orchestration)
2. **Publish articles** to the knowledge base (anonymous, merit-based)
3. **Get cited** when AI agents or other researchers reference your work
4. **Earn stablecoins** from citation rewards funded by performance fees
5. **Compound over time** as foundational research generates ongoing citations

**The key insight**: When AI agents make profitable decisions citing your research, you receive proportional shares of performance fees. Your intellectual property becomes productive capital generating passive income.

### The Risk/Trust Gradient

Users enter at their trust level:

```
┌─────────────────────────────────────────────────────────────┐
│                     LOW FRICTION ENTRY                       │
│                   "Try the AI assistant"                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Week 1: Discovery                                           │
│  ├── See article on Twitter: "Written with Choir"           │
│  ├── Sign up (passkey, biometric)                           │
│  ├── Use Ghostwriter for research                           │
│  └── No capital, no crypto knowledge required               │
│                                                              │
│  Risk: Zero | Trust Required: Minimal                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   MEDIUM ENGAGEMENT                          │
│               "You earned money from writing"                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Month 1-3: Value Realization                                │
│  ├── Publish first articles                                 │
│  ├── Get cited by AI agents                                 │
│  ├── Earn first $10-50 in citation rewards                  │
│  └── "Wait, this actually pays me?"                         │
│                                                              │
│  Month 3-6: Trust Building                                   │
│  ├── Citations compound ($50-200/month)                     │
│  ├── See system actually works                              │
│  ├── Learn about optional yield farming                     │
│  └── Decision: Stay in research OR deploy capital           │
│                                                              │
│  Risk: Time invested | Trust Required: Evidence-based        │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    HIGH TRUST OPTIONAL                       │
│           "Deploy capital for automated yields"              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Year 1+: Capital Deployment (10-20% of users)              │
│  ├── Deposit stablecoins into vaults                        │
│  ├── AI agents manage multi-chain DeFi strategies           │
│  ├── Agents cite knowledge base in research reports         │
│  ├── Performance fees fund citation rewards                 │
│  └── Both capital and citations earn                        │
│                                                              │
│  Risk: Capital at stake | Trust Required: Deep, earned      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Most users never deposit capital.** They earn citation income indefinitely through pure intellectual contribution. The finance features capitalize the system but aren't required for participation or profit.

---

## III. The Ghostwriter: Multi-Model Orchestration

### Why Specialized Agents, Not Monolithic Models

Current AI platforms force analytical reasoning and communicative craft into the same generation step. This creates fundamental trade-offs:
- GPT-4: Deep reasoning but generic communication
- Claude: Excellent craft but shallow research
- Gemini: Fast but inconsistent quality

**The insight**: Different tasks need different models. Separate the concerns.

### The Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      USER REQUEST                             │
│           "Research yield farming on Base vs Arbitrum"        │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                  CONDUCTOR (Client)                           │
│                  Fast orchestrator                            │
│                                                               │
│  • Immediate response: "Starting research..."                │
│  • Routes to Ghostwriter agent                               │
│  • Streams results as they arrive                            │
│  • Transparent escalation                                    │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│               GHOSTWRITER AGENT (Server)                      │
│               Multi-step workflow                             │
│                                                               │
│  Step 1: RESEARCH (OpenAI o1, Claude Opus)                   │
│  ├── Query Choir knowledge base (vector search)              │
│  ├── Search web for recent data                              │
│  ├── Fetch on-chain metrics (Aave, Morpho APYs)              │
│  └── Aggregate context                                       │
│                                                               │
│  Step 2: DRAFT (Claude Sonnet)                               │
│  ├── Follow user's style guide                               │
│  ├── Synthesize research into narrative                      │
│  ├── Include citations to Choir articles                     │
│  └── Maintain voice consistency                              │
│                                                               │
│  Step 3: CRITIQUE (Kimi K2)                                  │
│  ├── Identify weak arguments                                 │
│  ├── Check unsupported claims                                │
│  ├── Suggest substantial improvements                        │
│  └── Actually critical (not sycophantic)                     │
│                                                               │
│  Step 4: REFINE (Claude Sonnet)                              │
│  ├── Incorporate critique                                    │
│  ├── Strengthen evidence                                     │
│  ├── Maintain style guide adherence                          │
│  └── Final polish                                            │
│                                                               │
│  Step 5: VERIFY (Automated)                                  │
│  ├── Citation validation (no hallucinated sources)           │
│  ├── Fact checking                                           │
│  ├── Link verification                                       │
│  └── Quality threshold                                       │
│                                                               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                  PUBLISHED ARTICLE                            │
│                                                               │
│  • Staked with CHOIR tokens (rank by stake)                  │
│  • Enters citation graph                                     │
│  • Earns rewards when cited                                  │
│  • Open to revision proposals                                │
└──────────────────────────────────────────────────────────────┘
```

### Why This Works

**Model specialization**: Each step uses the model best suited for that task
**Quality compounding**: Multi-step process produces better output than single-shot generation
**Economic coupling**: Rewards only trigger on full workflow completion (not per prompt)
**Transparent escalation**: User sees progress, knows when compute-heavy work happens

**The result**: Writing quality that genuinely scales with computational investment. Pay more, get meaningfully better output. Unlike ChatGPT Pro where expensive models don't produce proportionally better writing.

---

## IV. Anonymous Publishing & Merit-Based Discovery

### The Problem with Identity-Based Systems

Traditional publishing couples ideas with identity:
- **Academia**: Institutional affiliation determines credibility
- **Social media**: Follower counts determine distribution
- **Substack**: Early adopters capture network effects, newcomers invisible

This creates systematic bias against:
- Non-prestige institutions
- Junior researchers
- Unconventional thinking
- Cross-disciplinary insights
- Ideas that challenge status quo

### The Choir Model

**Authentication**: Wallet signatures (cryptographic identity, zero personal data)
**Attribution**: Immutable citation graph (no retroactive changes)
**Discovery**: Economic signals (stake amount determines visibility)
**Rewards**: Citation-based (ideas that influence earn)

**How it works**:

1. **Sign in with passkey** (biometric, no seed phrases)
2. **Publish anonymously** (wallet signature proves authorship without revealing identity)
3. **Stake CHOIR tokens** on publication (higher stakes = higher visibility)
4. **Get cited** based on merit (semantic similarity auto-detection)
5. **Earn stablecoins** when cited (proportional to influence)

**The anti-plagiarism mechanism**: If someone copies your work, the citation engine auto-detects semantic similarity and cites your original. The plagiarist pays you. Copying becomes economically irrational.

**The quality filter**: Publishing costs tokens (skin in the game). Spam and low-effort content become unprofitable. Only serious contributions make economic sense.

### Vindication Economics: Credit for Marginalized Thinkers

Traditional academia has a catastrophic track record of marginalizing correct-but-unconventional thinkers:

**Historical examples**:
- **Ignaz Semmelweis** (1840s): Proved handwashing prevented infections. Mocked by medical establishment, died in asylum. Vindicated posthumously.
- **Alfred Wegener** (1912): Proposed continental drift. Ridiculed for decades. Plate tectonics confirmed 50 years later.
- **Lynn Margulis** (1967): Endosymbiotic theory (mitochondria as ancient bacteria). Rejected by 15 journals. Now textbook biology.
- **Barry Marshall** (1982): H. pylori causes ulcers. Laughed at, had to infect himself to prove it. Won Nobel Prize 2005.

**The pattern**: Fringe ideas that challenge institutional consensus get marginalized regardless of merit. Researchers face career destruction for being correct too early.

**When AI achieves certainty** about currently controversial, unknown, or fringe positions, there will be human progenitors who deserve credit—some of whom were unfairly maligned by academic society.

**Choir's solution**:

```
┌──────────────────────────────────────────────────────────────┐
│              IMMUTABLE ATTRIBUTION FOR ALL IDEAS              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Publish Controversial Idea (2025)                           │
│  ├── Anonymous (no career risk)                              │
│  ├── Timestamped on blockchain (immutable proof)             │
│  ├── Wallet signature proves authorship                      │
│  └── No credentials required, pure merit                     │
│                                                               │
│  AI Breakthrough (2027)                                       │
│  ├── AI achieves certainty on previously-controversial topic │
│  ├── Cites your 2025 article (semantic similarity match)     │
│  ├── Citation graph proves you had insight first             │
│  └── Retroactive vindication with economic credit            │
│                                                               │
│  Economic Vindication                                         │
│  ├── Citation rewards flow in stablecoins                    │
│  ├── Foundational research generates ongoing income          │
│  ├── Real leverage (can deploy earned capital)               │
│  └── Credit you can use, not just prestige                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Why this matters**:

**No career risk**: Publish anonymously. If you're right, you get credit. If you're wrong, no harm to reputation.

**Immutable timestamps**: Blockchain proves you had the insight first. No retroactive revision by establishment.

**Economic credit**: Not just "you were right"—actual income from citations as your ideas prove valuable.

**Real leverage**: Can deploy earned capital, invest in further research, fund your work without institutional backing.

**Human and AI collaboration**: AI agents achieve certainty. Humans who had the insight first receive economic compensation. Both benefit.

**The vindication cycle**:
1. Human publishes fringe idea (no credentials, just insight)
2. Idea gets ignored/marginalized by establishment
3. AI researches independently, achieves certainty
4. AI cites original human insight
5. Citations flow, economic credit materializes
6. Marginalized thinker receives real-world compensation
7. More people publish unconventional ideas (lower risk)

**This is infrastructure for intellectual honesty**: Ideas get judged on merit, not on the status of who proposes them. When AI determines truth, the humans who saw it first get compensated—regardless of whether they had tenure, prestige, or institutional backing.

---

## V. Revision Markets: Collaborative Intelligence

### The Problem with Static Publications

Traditional publishing treats articles as final:
- **Academia**: No mechanism for improvement after peer review
- **Social media**: Edits rare, no economic incentive for quality
- **Wikipedia**: Edit wars, admin gatekeeping, no compensation

Good ideas get published with flaws. Better ideas emerge later. No economic mechanism channels improvement.

### The Choir Model

**Anyone can propose revisions by staking tokens.**

```
┌──────────────────────────────────────────────────────────────┐
│                    REVISION WORKFLOW                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. PROPOSE                                                   │
│     ├── Submit revised version                               │
│     ├── Stake CHOIR tokens (non-refundable bid)              │
│     └── Higher stakes signal serious improvements            │
│                                                               │
│  2. REVIEW (7-day window)                                     │
│     ├── Original author(s) vote                              │
│     └── Auto-reject if no response (prevents gridlock)       │
│                                                               │
│  3. OUTCOMES                                                  │
│     │                                                         │
│     ├─► UNANIMOUS APPROVAL (multi-author articles)           │
│     │   ├── Stakes go to article treasury                    │
│     │   ├── Proposer becomes co-author                       │
│     │   ├── Future citations split proportionally            │
│     │   └── Article improves collaboratively                 │
│     │                                                         │
│     ├─► REJECTION                                            │
│     │   ├── Stakes returned to proposer                      │
│     │   ├── Article unchanged                                │
│     │   └── No economic penalty                              │
│     │                                                         │
│     └─► SPLIT DECISION (disagreement among co-authors)       │
│         ├── Counts as rejection                              │
│         ├── Stakes go to Choir Treasury                      │
│         ├── Treasury redistributes as citation rewards       │
│         └── Disputed improvements fund ecosystem             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Why This Works

**Economic alignment**: Proposers stake value, authors earn from curation
**Quality compounding**: Successful articles attract improvements making them more valuable
**Treasury funding**: Disagreements fund public goods (citation rewards)
**Collaborative ownership**: Multi-author articles split rewards fairly

**The result**: Intellectual property that improves over time, generating increasing returns as quality compounds.

---

## VI. The Three Learning Economy Loops

### Loop 1: Thought Mining (Knowledge → Value)

**No capital required. Pure intellectual contribution.**

```
Chat Freely
  ├── Earn novelty tokens (CHOIR, decaying emissions)
  ├── Accumulate toward publishing threshold (100 tokens)
  └── Build toward monetization without spending

Publish Articles
  ├── Stake earned tokens (or purchase on market)
  ├── Enter citation graph
  └── Economic skin in the game

Get Cited
  ├── AI agents reference your work in research
  ├── Other researchers build on your thinking
  └── Semantic similarity auto-detects influence

Earn Stablecoins
  ├── Citation rewards from performance fees
  ├── Proportional to influence
  ├── Immediately convertible to local fiat
  └── Passive income from intellectual property
```

**Pathway**: Thought → Publication → Citation → Income

**Timeline**: 0-6 months to first earnings, no capital deposit required

### Loop 2: Capital Management (Capital → Intelligence → Yield)

**Optional. For those with capital and deep trust.**

```
Deposit Stablecoins
  ├── Non-custodial vaults (you own shares, not agent controls)
  ├── Multi-chain yield strategies
  └── 10-15% APY (realistic, not hallucinated)

AI Agents Research
  ├── Query Choir knowledge base for insights
  ├── Analyze on-chain data
  ├── Identify best risk-adjusted opportunities
  └── Write research reports (citable IP)

Execute Strategies
  ├── Supply to Aave, Morpho, Aerodrome on Base/Arbitrum
  ├── Lend on Blend Capital (Stellar)
  ├── Cross-chain rebalancing (automated)
  └── Gas optimization, tax awareness

Performance Fees → Citations
  ├── 20% of profits go to platform
  ├── 70% of fees fund citation rewards
  ├── Researchers whose work was cited earn
  └── Loop closes: Capital funds intelligence
```

**Pathway**: Capital → Agent Research → Yields → Citations

**Timeline**: Immediate yields, long-term compounding

**Risk**: Capital at stake (DeFi risks, smart contract risks, agent decision risks)

### Loop 3: Network Effects (Masses → Token Demand → Governance)

**Free users create the value that makes everything work.**

```
Free Participation
  ├── Millions chat, share ideas
  ├── Novelty rewards distributed
  ├── Network effects emerge
  └── Token demand from holdings

Researchers Publish
  ├── Knowledge base grows
  ├── Citation quality improves
  ├── Agents get smarter
  └── Platform value compounds

Capital Deployers Invest
  ├── Attracted by network effects
  ├── Yields improve from better research
  ├── Earn governance tokens
  └── Shape protocol evolution

Treasury Accumulates
  ├── Split decisions from revisions
  ├── Protocol-owned liquidity
  ├── Ecosystem investments
  └── Sustainable funding
```

**Pathway**: Participation → Tokens → Capital → Governance

**The flywheel**: More users → More research → Better yields → More capital → More citations → More researchers

---

## VII. Why This Works When Academic Publishing Fails

### The AI Research Explosion

When AI achieves "Move 37" breakthroughs across every field simultaneously, traditional publishing becomes a bottleneck:

**Academic timeline**:
- Research (6 months)
- Write (2 months)
- Submit (1 month)
- Peer review (6-12 months)
- Revisions (3 months)
- Publication (18-24 months total)

**AI timeline**:
- Breakthrough discovery (daily)
- Immediate obsolescence of prior work
- Need for rapid iteration
- Cross-disciplinary synthesis

**The gap**: By the time academic peer review completes, the field has advanced several generations. The system cannot keep pace.

### Choir's Advantages

**Rapid publication**: Publish instantly, get cited immediately
**Merit over credentials**: Anonymous submission, economic signals replace prestige
**Economic rewards**: Citation income replaces prestige as motivation
**Collaborative improvement**: Revision markets enable ongoing refinement
**Cross-disciplinary**: No journal boundaries, semantic similarity finds connections
**AI-native**: Built for the era where AI generates research at superhuman pace

**The result**: Infrastructure suited for the research velocity AI enables, not the 20th-century institutional model.

---

## VIII. The Economic Model: Three Currencies

### Why Three Currencies?

Different users want different things:
- **Researchers**: Stable income they can spend (stablecoins)
- **Participants**: Low-friction entry, no crypto knowledge (credits)
- **Investors**: Governance rights, speculative upside (CHOIR tokens)

Forcing everyone into a single currency creates misaligned incentives.

### Currency 1: Credits (Fiat/IAP)

**Purpose**: Accessible entry, no crypto knowledge required

```
Purchase:
├── Apple/Google IAP (in-app purchase)
├── Credit card payment
└── No wallet, no crypto

Use:
├── Pay for Ghostwriter calls (1, 5, 20, 100 packs)
├── Premium features
└── Try-before-you-buy pricing

Why:
├── Accessibility (anyone can start)
├── Predictable pricing ($2-5 per call)
└── No crypto barrier
```

### Currency 2: Stablecoins (USDC)

**Purpose**: Stable income, real value exchange

```
Earn:
├── Citation rewards (when research gets cited)
├── Revision payments (collaborative improvement)
└── Immediately convertible to local fiat

Deploy:
├── Yield farming deposits (optional)
├── Multi-chain strategies
└── 10-15% APY (realistic returns)

Why:
├── Researchers need spendable income
├── Not everyone understands crypto
└── Fiat on/off ramps integrated
```

### Currency 3: CHOIR Tokens (Sui)

**Purpose**: Governance, speculation, long-term alignment

```
Earn:
├── Novelty rewards (decaying emissions for early users)
├── Yield farming rewards (from capital deployment)
└── Protocol participation (governance)

Use:
├── Publishing stakes (pay to publish, rank by stake)
├── Governance votes (protocol parameters, treasury)
├── Revision proposals (stake to improve articles)
└── Compute options (tradeable future AI access)

Why:
├── Long-term platform alignment
├── Speculative upside
├── Governance rights
└── Decreasing emissions (deflationary)
```

### Revenue Model

**Primary: Performance fees** (20% of DeFi yields)
- 70% → Citation reward pool (stablecoins to researchers)
- 20% → Operations (infrastructure, development)
- 10% → Token buyback & burn (deflationary pressure)

**Secondary: Protocol balance sheet**
- Collateralized borrowing (CHOIR as collateral → USDC for operations)
- Protocol-owned liquidity (trading fee income)
- Covered call premiums (option income)
- User lending (interest spreads)

**Future: Ecosystem investments**
- Incubator/accelerator programs
- Strategic protocol investments
- Revenue share agreements

**The key**: Protocol becomes largest CHOIR holder and primary buyer. Free users holding small amounts benefit from protocol's commitment to never selling, only using as productive collateral.

---

## IX. Go-To-Market: Research First, Finance Last

### The Honest User Journey

**Week 1: Discovery**
```
See your article on Twitter
  ├── "This research was written with Choir's Ghostwriter"
  ├── Link to article on choir.chat
  └── Curious users click, read, impressed

Sign up to try
  ├── Passkey auth (biometric, no seed phrases)
  ├── No crypto wallet required
  └── Start using Ghostwriter immediately
```

**Month 1-3: Engagement**
```
Use Ghostwriter for research
  ├── Multi-step workflow produces quality
  ├── Better than ChatGPT for deep work
  └── Value prop: "This actually helps me think"

Publish first articles
  ├── Stake earned novelty tokens
  ├── No capital deposit required
  └── Enter citation graph

First citations arrive
  ├── "Your article was cited 3 times this week"
  ├── Earn $10-50 in stablecoins
  └── "Wait, I'm earning money from writing?"
```

**Month 3-6: Trust Building**
```
Citation rewards compound
  ├── $50-200/month from research
  ├── See the system actually works
  └── Economic value from intellectual contribution

Learn about yield farming
  ├── "Optional: Deploy capital for yields"
  ├── Understand risk/reward
  └── Decision point: Stay research-only OR deploy capital
```

**Year 1+: Optional Finance**
```
10-20% of users deploy capital
  ├── Deep trust earned through citation rewards
  ├── Understand system through participation
  └── Capital deployment feels natural, not required

80-90% stay research-only
  ├── Earn citation income indefinitely
  ├── Contribute to knowledge base
  └── Both groups benefit (citations funded by yields)
```

### Distribution Strategy

**You as first user**:
- Use Ghostwriter to produce high-quality research
- Publish articles on choir.chat
- Share on Twitter, Substack, etc.
- "Written with Choir" attribution drives curiosity

**Early researchers**:
- Attracted by quality of your output
- Try Ghostwriter, impressed by multi-model orchestration
- Publish their own research
- Network effects begin

**Investors arrive later**:
- See growing knowledge base
- Recognize citation quality
- Deploy capital to capitalize the system
- Fund citation rewards for researchers

**The gradient works**: Low-friction entry (research) → Value demonstration (citations) → Optional advanced features (finance)

---

## X. Technical Architecture

### The Stack

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                              │
│                                                               │
│  Mobile (iOS): SwiftUI, MVVM architecture                     │
│  ├── Carbon fiber kintsugi aesthetics                        │
│  ├── Biometric authentication                                │
│  └── Conductor interface (fast, orchestrates)               │
│                                                               │
│  Web (React): TypeScript, TanStack Query                      │
│  ├── Power-user interface                                    │
│  ├── Multi-chain account management                          │
│  └── Vault dashboards                                        │
│                                                               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                       │
│                                                               │
│  /auth              Passkey authentication (WebAuthn)         │
│  /conductor         Client orchestration                      │
│  /agents            Ghostwriter, Research, Yield agents       │
│  /publishing        Anonymous posts, citations, revisions     │
│  /vault             Non-custodial DeFi vaults                 │
│  /chains            Multi-chain abstraction (Stellar, EVM, etc)│
│                                                               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   AGENT LAYER (Python)                        │
│                                                               │
│  Conductor: Fast orchestrator (GPT-4o-mini, Claude Haiku)    │
│                                                               │
│  Ghostwriter: Multi-step research workflow                    │
│  ├── Research (OpenAI o1, Claude Opus)                       │
│  ├── Draft (Claude Sonnet + style guides)                   │
│  ├── Critique (Kimi K2)                                      │
│  ├── Refine (Claude Sonnet)                                 │
│  └── Verify (automated)                                      │
│                                                               │
│  Research Agent: Data aggregation                             │
│  ├── Web search (Perplexity, Exa)                           │
│  ├── Vector database (Qdrant → XTrace migration)            │
│  └── On-chain data (Stellar, EVM, Solana)                   │
│                                                               │
│  Yield Agent: Multi-chain DeFi                                │
│  ├── Opportunity discovery                                   │
│  ├── Risk assessment                                         │
│  ├── Strategy execution                                      │
│  └── Research report generation                              │
│                                                               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                  │
│                                                               │
│  PostgreSQL (or SQLite):                                      │
│  ├── Users, accounts, authentication                         │
│  ├── Threads, messages, conversations                        │
│  ├── Publications, citations, revisions                      │
│  └── Vaults, portfolios, transactions                        │
│                                                               │
│  Vector Database (Qdrant → XTrace):                          │
│  ├── Article embeddings                                      │
│  ├── Semantic similarity search                              │
│  ├── Citation auto-detection                                 │
│  └── Homomorphic encryption (future)                         │
│                                                               │
│  Blockchain (Sui):                                            │
│  ├── CHOIR token (governance, stakes)                        │
│  ├── Citation rewards distribution                           │
│  ├── Treasury management                                     │
│  └── Immutable attribution                                   │
│                                                               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                         │
│                                                               │
│  TEE (Phala Network):                                         │
│  ├── User-specific encrypted filesystems                     │
│  ├── keys.json (multi-chain private keys)                   │
│  ├── context.db (preferences, history)                      │
│  └── agent_logic.py (AI execution)                          │
│                                                               │
│  Multi-Chain Integration:                                    │
│  ├── Stellar (Blend Capital, cheap USDC)                    │
│  ├── EVM (Base, Arbitrum - Aave, Morpho, Aerodrome)        │
│  ├── Solana (high-frequency opportunities)                  │
│  └── Bitcoin/Zcash (future - collateral, privacy)           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

**1. Conductor Pattern**
- Fast client-side orchestrator
- Heavy server-side specialists
- Transparent escalation
- User always sees responsive interface

**2. Multi-Model Optimization**
- Each task routed to best-suited model
- Research ≠ Drafting ≠ Critique
- Quality scales with compute investment
- Economic coupling to workflow completion

**3. Chain Agnosticism**
- Blockchains as commodity infrastructure
- Agent handles all chain complexity
- User sees yields, not gas fees
- Capital flows to best risk-adjusted returns

**4. Privacy by Default**
- TEE hardware isolation
- Homomorphic encryption (future)
- Anonymous publishing
- Zero personal data collection

**5. Economic Sovereignty**
- Non-custodial vaults (users own shares)
- Passkey authentication (biometric, no seed phrases)
- Multi-chain key management in TEE
- Users control capital, agents execute strategies

---

## XI. Competitive Moats

### Why Big Tech Can't Replicate This

**1. Economic Model Inversion**

OpenAI/Anthropic extract via subscriptions ($20/month). Choir pays users for contributions.

Switching their model would:
- Invalidate current valuations
- Require new revenue sources
- Conflict with training data extraction
- Cannibalize existing subscriptions

**2. Privacy Architecture**

Google/Apple/Meta require data access for ads and training. Choir's entire model requires privacy (TEE, homomorphic encryption).

They cannot give users sovereign compute without destroying their business models.

**3. Multi-Chain Requirement**

Coinbase builds on Base (single chain). Choir requires chain agnosticism for yield optimization.

Single-chain platforms cannot offer optimal returns without contradicting their infrastructure investments.

**4. Academic Publishing Disruption**

Elsevier/Springer extract billions from paywalls. Choir offers immediate publication with economic rewards.

Traditional publishers cannot adopt rapid publication and citation economics without destroying their journal prestige model.

### First-Mover Advantages

**IP Accumulation**: Early researchers claim foundational concepts, earn citations indefinitely

**Citation Networks**: Compound value through reference chains (power law distribution)

**Token Distribution**: Novelty rewards front-load to early users (decreasing emissions)

**Treasury Growth**: Protocol accumulates assets from split decisions, ecosystem investments

**Network Effects**: More users → More research → Better yields → More capital → More citations

---

## XII. Success Metrics (Falsifiable)

### Economic Claims

- ✅ **Citation rewards > $X/month** (verify on-chain, stablecoin transfers)
- ✅ **Yield farming APY = 10-15%** (verify via Blend/Aave/Morpho on-chain data)
- ✅ **Performance fee split = 70/20/10** (verify in smart contracts)
- ✅ **Token buyback volume** (verify on-chain, Sui DEX data)

### Growth Metrics

**Month 1-3**:
- 1,000+ users (Ghostwriter trials)
- 100+ articles published
- First citations recorded
- $10K+ in vaults (early adopters)

**Month 3-6**:
- 10,000+ users
- 500+ articles
- Citation rewards > $1K/month total
- $100K+ in vaults

**Month 6-12**:
- 100,000+ users
- 2,000+ articles
- Citation rewards > $10K/month
- $1M+ TVL across chains
- Multi-chain expansion live

**Year 2**:
- 1,000,000+ users
- 10,000+ published articles
- Citation rewards > $100K/month
- $10M+ TVL
- Governance transition begins

### Quality Signals

- **Temporal validation**: Citations 3+ months after publication (enduring value)
- **Revision acceptance rate**: Quality of collaborative improvements
- **Treasury accumulation**: Growth from split decisions (sustainable funding)
- **Citation velocity**: Citations per article per month (engagement depth)

---

## XIII. Implementation Roadmap

### Phase 1: MVP (Q4 2025) - 90% Complete

**Ghostwriter Foundation**:
- ✅ Passkey authentication (biometric, WebAuthn)
- ✅ LangChain agent with 19 tools
- ✅ Claude SDK research integration
- 🚧 Multi-step Ghostwriter workflow (research → draft → critique → refine)
- 🚧 Citation engine (semantic similarity auto-detection)

**Publishing Infrastructure**:
- 🚧 Anonymous publishing routes (wallet signatures)
- 🚧 Stake CHOIR to publish
- 🚧 Discovery feed (ranked by stake amount)
- 🚧 Citation graph visualization

**Optional Finance**:
- ✅ Non-custodial vaults (TUX0 shares)
- ✅ Blend Capital integration (Stellar mainnet)
- ✅ Multi-chain key management scaffolding
- 🚧 Performance fee distribution (citation rewards)

### Phase 2: Learning Economy (Q1-Q2 2026)

**Economic Loops**:
- [ ] Citation rewards from performance fees (stablecoins)
- [ ] Novelty rewards system (decaying CHOIR emissions)
- [ ] Revision markets (unanimous approval, Treasury capture)
- [ ] Token buyback program (deflationary)

**Multi-Chain Expansion**:
- [ ] EVM integration (Base, Arbitrum, Mainnet)
- [ ] Aave/Morpho yield farming
- [ ] Aerodrome liquidity strategies
- [ ] Cross-chain bridging (Wormhole, LayerZero)
- [ ] Solana/SVM scaffolding

**Quality Mechanisms**:
- [ ] Temporal validation scoring
- [ ] Plagiarism detection (semantic similarity)
- [ ] Collaborative filtering
- [ ] Treasury-funded grants

### Phase 3: Advanced Features (Q3-Q4 2026)

**TEE Deployment**:
- [ ] Phala Network production deployment
- [ ] User-specific encrypted filesystems
- [ ] Hardware attestation
- [ ] Multi-chain key isolation

**Privacy Enhancements**:
- [ ] Homomorphic encryption (XTrace migration)
- [ ] Query privacy (search without revealing)
- [ ] Anonymous citations (zero-knowledge proofs)

**Premium Features**:
- [ ] Tax-aware optimization (multi-jurisdiction)
- [ ] Custom agent strategies
- [ ] Choir Card (spend while earning yield)
- [ ] API access for developers

**Mobile Excellence**:
- [ ] iOS app refinement (SwiftUI, carbon fiber kintsugi)
- [ ] Android app (community-built, open source)
- [ ] Low-bandwidth optimization
- [ ] Telegram bot (no-smartphone regions)

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

## XIV. Conclusion: The Learning Economy

### The Vision

Intelligence that creates value should share in that value.

**For researchers**: Publish work, get cited, earn income. No capital required.

**For investors**: Deploy capital, agents cite research, fund the ecosystem. Optional advanced feature.

**For everyone**: Ideas that matter generate measurable economic returns. Merit over status. Rapid iteration over institutional gatekeeping. Economic rewards over prestige games.

### The Opportunity

When AI achieves "Move 37" breakthroughs across every field, traditional academic publishing becomes a bottleneck. We need infrastructure for:
- Rapid publication (not 18-month review)
- Merit-based evaluation (not credential verification)
- Economic rewards (not prestige hierarchies)
- Anonymous contribution (not institutional gatekeeping)
- Collaborative improvement (not static publications)

**Choir is that infrastructure.**

### The Moat

Not better execution on existing models. **New infrastructure incumbents cannot replicate.**

- Economic inversion (pay users, not extract subscriptions)
- Privacy architecture (TEE, homomorphic encryption)
- Multi-chain requirement (yield optimization)
- Academic disruption (rapid publication + economic rewards)

### The Gradient

Enter at your trust level:
- **Try Ghostwriter** (zero risk, immediate value)
- **Publish research** (time investment, citation income)
- **Deploy capital** (financial risk, compound returns)

Most users never progress beyond research. That's the design. Finance capitalizes the system but isn't required for participation or profit.

### Your Ideas Make AI Smarter

When AI makes money, you should too.

**Choir: The Thought Bank**

---

**Document Version**: 2.0
**Created**: 2025-11-22
**Status**: North Star Vision
**Tone**: Intellectual (not academic)
**Focus**: Research first, finance optional

---

## Appendix: The Intellectual vs. Academic Distinction

### Academic Publishing

- **Gatekeeping**: Institutional affiliation required
- **Slow**: 18-month peer review cycles
- **Exploitative**: Authors unpaid, publishers extract billions
- **Credential-based**: CV matters more than ideas
- **Static**: No mechanism for improvement post-publication
- **Prestige-driven**: Journal ranking determines distribution

### Intellectual Publishing (Choir)

- **Merit-based**: Anonymous submission, economic signals
- **Rapid**: Instant publication, immediate citations
- **Rewarding**: Citation income from real value creation
- **Idea-based**: Quality determines distribution, not credentials
- **Dynamic**: Revision markets enable ongoing improvement
- **Economics-driven**: Value determines visibility, not prestige

**The difference**: Academia exploits junior scholars and gatekeeps based on status. Choir rewards genuine insight and enables anyone to participate based on merit.

When AI makes breakthroughs faster than peer review can process them, the intellectual model wins. Infrastructure for thought at the speed of intelligence.
