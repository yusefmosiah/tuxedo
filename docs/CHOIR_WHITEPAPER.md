# Choir: The Thought Bank
**Intelligence that creates value should share in that value**

**Version 5.0 - November 24, 2025**

---

## Executive Summary

Choir is AI research infrastructure for the learning economy.

**The core product is Ghostwriter**: An AI agent that helps you research, write, and publish—then pays you in stablecoins when your work gets cited.

**No capital required to earn.** Chat freely, publish research, get cited by AI agents making decisions, receive citation rewards in real money. The pathway from zero to income exists entirely through intellectual contribution.

**Optional for those with capital**: Deposit USDC to provide the capital base for the Treasury's operations and lending pool. Your principal is protected, and you earn CHIP ownership based on your intellectual contributions, not the size of your deposit.

**The economic loop (The Flywheel)**: Deposits fund operations. Novelty earns ownership (CHIP). Platform usage builds Treasury assets. Treasury assets are collateralized to fund citation rewards (USDC). Citation rewards attract quality researchers, whose work attracts more users and capital.

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
4. **Earn USDC** from a dynamically priced, exponentially scaling citation rewards pool.
5. **Compound over time** as foundational research generates ongoing citations.

**The key insight**: The system is designed to reward intellectual contribution sustainably. Your ideas earn you spendable income (USDC) and ownership (CHIP), funded by a self-sustaining Treasury that leverages the network's own growth.

### The Participation Gradient: Enter Where You Are

Choir doesn’t force you into categories or require upfront payment. It provides a natural gradient where you enter with what you have and grow from there.

**Have ideas but no capital?** Chat freely, earn CHIP tokens, publish articles, earn citation rewards in dollars. Many successful participants never deposit a cent.

**Have capital but no expertise?** Deposit funds. Your principal is protected, and the yield it generates helps fund the entire ecosystem, including the citation rewards paid to researchers. Your capital rewards their intelligence.

**Have both?** Deposit capital, publish research, earn from both sides. Watch your intellectual and financial capital compound together.

The gradient isn’t a ladder you must climb. It’s a spectrum where you choose your position based on resources, interests, and goals. The platform succeeds because all positions are valuable—the person chatting freely creates as much value as the person deploying millions.

### The Free Tier: Why Network Effects Matter More Than Revenue

Most platforms view free users as a cost to be minimized or a pipeline to be converted. Choir inverts this: free users are the entire point. They create the network effects that make everything else valuable.

**The Masses Create Token Value:** When millions of people want CHIP tokens but have limited means to acquire them, they create demand pressure that supports the price.

**The Masses Attract Capital:** Wealthy participants don’t invest in small networks. They invest in networks with obvious growth trajectories and network effects. The free users create the context that makes depositing capital rational.

**The Masses Create Liquidity:** The aggregate small transactions of millions of users create the organic market activity and deep liquidity that sophisticated capital requires.

**The Masses Create Content:** Every agent needs research to cite. That research comes from publishers. Many publishers start as free users who earned enough CHIP to begin publishing.

The free users aren’t the top of the funnel. They’re the foundation of the entire economic engine.

---

## III. The Ghostwriter: Multi-Model Orchestration

### Why Specialized Agents, Not Monolithic Models

Current AI platforms force analytical reasoning and communicative craft into the same generation step. This creates fundamental trade-offs:
- GPT-4: Deep reasoning but generic communication
- Claude: Excellent craft but shallow research
- Gemini: Fast but inconsistent quality

**The insight**: Different tasks need different models. Separate the concerns.

### The Architecture

The system follows a conductor and instruments pattern. The conductor acts as a fast chatbot that responds immediately to coordinate overall flow. The instruments are slower agentic tools that run complex workflows in the background.

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
│  • Consumed CHIP moves to Treasury (rank by stake)           │
│  • Enters citation graph                                     │
│  • Earns rewards when cited                                  │
│  • Open to revision proposals                                │
└──────────────────────────────────────────────────────────────┘
```

---

## IV. Anonymous Publishing & Merit-Based Discovery

### The Problem with Identity-Based Systems

Traditional publishing couples ideas with identity, creating systematic bias against non-prestige institutions, junior researchers, and unconventional thinking.

### The Choir Model

**Authentication**: Wallet signatures (cryptographic identity, zero personal data)
**Attribution**: Immutable citation graph (no retroactive changes)
**Discovery**: Economic signals (stake amount determines visibility)
**Rewards**: Citation-based (ideas that influence earn)

**The anti-plagiarism mechanism**: If someone copies your work, the citation engine auto-detects semantic similarity and cites your original. The plagiarist pays you. Copying becomes economically irrational.

**The quality filter**: Publishing costs tokens (skin in the game). Spam and low-effort content become unprofitable. Only serious contributions make economic sense.

### Vindication Economics: Credit for Marginalized Thinkers

Traditional academia has a catastrophic track record of marginalizing correct-but-unconventional thinkers. Choir's anonymous, timestamped, and merit-based system provides a solution where AI can retroactively vindicate and economically reward human progenitors of ideas that were once considered fringe.

**The vindication cycle**:
1. Human publishes fringe idea (no credentials, just insight)
2. Idea gets ignored/marginalized by establishment
3. AI researches independently, achieves certainty
4. AI cites original human insight
5. Citations flow, economic credit materializes
6. Marginalized thinker receives real-world compensation
7. More people publish unconventional ideas (lower risk)

This is infrastructure for intellectual honesty: ideas get judged on merit, not on the status of who proposes them.

---

## V. Revision Markets: Collaborative Intelligence

### The Problem with Static Publications

Traditional publishing treats articles as final, leaving no room for collaborative improvement.

### The Choir Model

**Anyone can propose revisions by staking tokens.**

```
┌──────────────────────────────────────────────────────────────┐
│                    REVISION WORKFLOW                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. PROPOSE                                                   │
│     ├── Submit revised version                               │
│     ├── Stake CHIP tokens (non-refundable bid)              │
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
│         ├── Treasury leverages stakes to fund more rewards   │
│         └── Disputed improvements fund ecosystem             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```
This creates intellectual property that improves over time, generating increasing returns as quality compounds.

---

## VI. The Economic Model: Principal Protection + Asymmetric Upside

Choir introduces a novel economic model that functions as a true "marketplace of ideas." Unlike traditional investment vehicles where capital is at risk, Choir guarantees the return of a user's principal deposit. The "yield" is not paid in the currency of the deposit (e.g., USDC), but in the platform's native token, **CHIP (Choir Harmonic Intelligence Platform)**.

The amount of CHIP earned is determined not by the size of the deposit, but by the **intellectual performance** of the user—specifically, the semantic novelty of the content they publish. This creates an environment with asymmetric upside: users can't lose their principal, but they can gain significant ownership and influence in the platform by contributing valuable, novel ideas.

### The Three Currencies: A Separation of Concerns

*   **USDC: For Income and Operations.** All citation rewards are paid in USDC. The yield on user deposits funds the operational budget.
*   **CHIP: For Ownership and Contribution.** Represents ownership. It is earned through intellectual contribution (novelty), not purchased. It's used to power platform actions and for governance.

### Treasury Architecture: Dual-Revenue Streams

Choir's sustainability is powered by a revolutionary dual-revenue stream model that separates operational funding from citation reward funding.

**1. Stream 1: Deposit Yield → Operations (Linear Growth)**
The USDC deposited by users is deployed into safe, yield-bearing DeFi protocols. The yield is dedicated to funding core protocol operations. This provides a stable, predictable, and linearly scaling budget.

**2. Stream 2: Treasury CHIP Collateral → Citation Rewards (Exponential Growth)**
This is the engine for the "marketplace of ideas."
1.  CHIP tokens consumed by users for platform actions flow back to the Treasury.
2.  The Treasury accumulates a growing portfolio of its own CHIP.
3.  The Treasury **borrows against its CHIP holdings** from the user deposit pool (acting as an internal lending market).
4.  100% of these borrowed funds are dedicated to the **Citation Rewards Pool**.

This means the citation budget is not limited by deposit yield. It scales with the **value of the network itself (the CHIP price)**.

### Citation Rewards: Meritocratic and Dynamic

Citation rewards are the primary income source for researchers on the platform and are paid in USDC.

*   **Meritocratic**: The reward per citation is the same for all users, regardless of their deposit size.
*   **Dynamic Rate**: The payout per citation is not fixed. It is calculated dynamically based on the available budget and total network activity, creating a self-regulating economy.

### The Virtuous Cycle (Flywheel)

This architecture creates a powerful, self-reinforcing flywheel:

1.  **Deposits Fund Operations**: User deposits generate yield, creating a stable budget.
2.  **Novelty Earns Ownership**: Users publish novel content to earn CHIP, building the knowledge base.
3.  **Usage Builds Treasury Assets**: Consumed CHIP flows to the Treasury, increasing its CHIP portfolio.
4.  **Treasury Assets Fund Citations**: The Treasury borrows against its CHIP to fund a massive citation rewards pool.
5.  **Citations Reward Quality**: Generous USDC citation rewards attract top-tier researchers.
6.  **Quality Attracts Users & Capital**: A high-quality knowledge base attracts more users and deposits.
7.  The cycle repeats, with each loop amplifying the next.

---

## VII. Go-To-Market: Research First, Finance Last

The user journey is designed to build trust organically, starting with the high-value Ghostwriter product and introducing the financial components only after a user has experienced direct economic benefit from their intellectual contributions. This ensures that capital providers are users who deeply understand and trust the system because they've already profited from it.

---

## VIII. Technical Architecture

The platform is built on a modern, multi-model, chain-agnostic stack designed for privacy, security, and scalability.

*   **Client Layer**: Mobile-first (SwiftUI) and Web (React).
*   **API Layer**: Python FastAPI.
*   **Agent Layer**: A "Conductor and Instruments" pattern using best-in-class models (OpenAI, Claude, Kimi) for specialized tasks.
*   **Data Layer**: A combination of PostgreSQL, a Vector Database (Qdrant, migrating to XTrace for privacy), and the Sui Blockchain for tokenomics and attribution.
*   **Infrastructure**: Trusted Execution Environments (TEE) on Phala Network for security and multi-chain integration (Stellar, EVM, etc.).

---

## IX. Roadmap

### Phase 1: MVP (Q4 2025)
Focus on core Ghostwriter, publishing infrastructure, and initial Stellar-based vault functionality.

### Phase 2: Learning Economy (Q1-Q2 2026)
Roll out the full economic loops: dynamic citation rewards, novelty-based CHIP distribution, and revision markets. Expand to EVM chains.

### Phase 3: Advanced Features (Q3-Q4 2026)
Deploy to TEEs, enhance privacy with homomorphic encryption, and introduce premium features like tax-aware optimization. Launch the **Choir Card**, a debit card that enables spending a balance while it remains deployed in yield strategies.

### Phase 4: Decentralization (2027+)
Transition governance to the community and begin ecosystem investment via an incubator/accelerator program funded by the Treasury.

---

## X. Conclusion: Banking Intelligence

Your ideas make AI smarter. When AI makes money, you should too.

The thought bank creates infrastructure where intelligence, knowledge, and capital compound together. It solves the broken models of academic publishing, social media, and extractive AI platforms by creating a new one where contribution is directly and sustainably rewarded.

You don’t need capital to begin—just ideas worth sharing.

---
## Appendix A: The AI Idiot Test

If AI is so smart, why isn’t it making you money?

This question reveals the fundamental problem with current AI platforms. They extract value through access fees without sharing in the value AI generates. Choir answers differently: AI makes you money by executing profitable DeFi strategies, then paying you when your insights enable those profits. When an AI agent generates value, the researchers who made the agent smart earn spendable currency. Everyone makes money from AI being smart.

## Appendix B: Comparison to Existing Platforms

| Platform       | Compensation                  | Attribution         | Barriers              | Quality Filter       |
|----------------|-------------------------------|---------------------|-----------------------|----------------------|
| **Academia**   | Prestige (no money)           | Strategic           | Credentials           | Peer Review          |
| **Social Media** | Engagement (no money)         | None                | Minimal               | Likes/Votes          |
| **DeFi**       | Financial Returns             | None                | Capital               | Market Efficiency    |
| **Choir**      | **IP Rewards + Fin. Returns** | **Automatic/Econ.** | **Contribution**      | **Economic Staking** |

## Appendix C: Token Utility and Economics

*   **Chat Participants (Free Tier)**: Earn starter CHIP via a free tier, creating network effects and organic token demand.
*   **Publishers**: Earn stablecoins from citations. Must acquire and stake CHIP to publish.
*   **Capital Providers**: Deposit USDC to fund the ecosystem. Earn CHIP based on novelty, not deposit size.
*   **Platform**: Earns revenue for its Treasury through the dual-stream model, leveraging its own CHIP assets to create a powerful, self-sustaining economy.

## Appendix D: Frequently Asked Questions

**Can I really earn money without depositing capital?**
Yes. This is the entire point. The primary user journey is for researchers who earn through intellectual contribution alone.

**Why blockchain instead of a traditional database?**
For immutable attribution, transparent economics, and trustless execution. It provides a credible commitment that the platform will honor its promise to pay for contributions.

**What prevents plagiarism?**
The automatic citation engine. If you plagiarize, the system cites the original, and you end up paying the author you copied from.

**How do you prevent spam?**
Economic costs. Publishing and revising requires staking CHIP, making low-quality submissions economically irrational.
