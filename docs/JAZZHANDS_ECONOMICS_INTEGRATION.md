# Jazzhands Economics Integration

**How OpenHands Runtime Meets Citation Economics**

**Version 1.0 - November 26, 2025**

---

## Executive Summary

This document explains how Choir's three-currency economic model integrates with the Jazzhands (forked OpenHands) infrastructure.

**The Challenge**: OpenHands is infrastructure (compute, runtimes, agents). Choir is economics (citations, novelty, rewards). How do they fit together?

**The Solution**: A layered architecture where:
1. **Compute Credits** pay for infrastructure (Jazzhands runtime costs)
2. **CHIP Tokens** represent ownership (earned via novelty, used for publishing)
3. **USDC** is income (earned via citations, withdrawn to bank accounts)

Each currency has a specific role. Together they create a sustainable learning economy.

---

## I. The Three Currencies: Role Separation

### Currency 1: Compute Credits (Infrastructure Layer)

**Purpose**: Pay for the computational resources required to run Vibewriter sessions.

**How Acquired**:
- **Free Tier**: New users get 500 compute credits (enough for ~10 research sessions)
- **Autopurchase**: $10 = 500 credits (automatic when balance is low)
- **Earned via Citations**: Every $10 in citation earnings = 100 bonus credits

**What They Buy**:
```
Vibewriter Session Costs:
├── Quick Research (2-3 sources, 500 words)
│   └── 20 credits (~2 minutes of runtime)
│
├── Standard Report (5-7 sources, 1500 words)
│   └── 50 credits (~5 minutes of runtime)
│
└── Deep Research (10+ sources, 3000+ words, verification)
    └── 150 credits (~15 minutes of runtime)
```

**Where the Money Goes**:
- Runtime provider (RunLoop, E2B, AWS Lambda)
- LLM API calls (Claude, GPT, etc.)
- Infrastructure overhead (Choir Controller hosting, databases)

**Key Point**: Compute credits are **not blockchain tokens**. They're internal accounting, like AWS credits.

---

### Currency 2: CHIP Token (Ownership Layer)

**Purpose**: Represent ownership of the Choir protocol and govern the knowledge base.

**How Acquired** (EARNED, not bought):
```python
def calculate_chip_reward(article: str, corpus: VectorDB) -> int:
    """
    CHIP is earned through semantic novelty.
    NOT through capital, NOT through usage.
    """
    # 1. Generate embedding for new article
    new_embedding = embed(article)

    # 2. Find nearest neighbors in existing corpus
    neighbors = corpus.search(new_embedding, k=100)

    # 3. Calculate semantic distance
    novelty_score = calculate_novelty(new_embedding, neighbors)
    # Returns 0-100 (0 = common knowledge, 100 = breakthrough insight)

    # 4. Apply reward curve (logarithmic decay)
    if novelty_score < 20:
        return 0  # Too similar to existing work
    elif novelty_score < 50:
        return int(50 * (novelty_score / 50))  # Linear up to 50 CHIP
    elif novelty_score < 80:
        return int(50 + 200 * ((novelty_score - 50) / 30))  # Accelerate
    else:
        return int(250 + 1000 * ((novelty_score - 80) / 20))  # Huge reward for breakthroughs

    # Examples:
    # novelty=25 → 25 CHIP (incremental improvement)
    # novelty=65 → 150 CHIP (solid new angle)
    # novelty=85 → 500 CHIP (major breakthrough)
    # novelty=95 → 1000+ CHIP (paradigm shift)
```

**What It's Used For**:
1. **Publishing**: Stake 100 CHIP to publish an article (makes it citable)
2. **Governance**: Vote on protocol parameters (citation rates, Treasury allocations)
3. **Collateral**: Borrow USDC from Treasury using CHIP as collateral
4. **Ranking**: Articles with more CHIP staked rank higher in discovery

**The Flywheel**:
```
Publish Novel Article
  ├── Cost: 100 CHIP (staked)
  ├── Reward: 200 CHIP (novelty score 75/100)
  └── Net: +100 CHIP

Article Gets Cited
  ├── Earn: $5 USDC per citation
  └── Staked CHIP remains (can withdraw after 30 days)

Use CHIP for Governance
  ├── Vote on Treasury strategies
  ├── Propose protocol upgrades
  └── Influence ecosystem direction
```

**Critical Property**: **CHIP earned is proportional to intellectual contribution, not capital deployed.**

A researcher with $0 deposited who publishes breakthrough insights earns more CHIP than a passive investor with $100k deposited.

---

### Currency 3: USDC (Income Layer)

**Purpose**: Spendable income earned from intellectual contribution.

**How Acquired**:
```
Your Article Gets Cited
  ├── Another user's Vibewriter agent references your work
  ├── OR: Another researcher manually cites you
  ├── Treasury pays you dynamically-priced USDC
  └── You can withdraw to bank account
```

**Citation Pricing** (Dynamic):
```python
def calculate_citation_rate(treasury: Treasury, month: str) -> Decimal:
    """
    Citation rewards are NOT fixed.
    They scale with Treasury's CHIP collateral value.
    """
    # 1. Treasury's CHIP Holdings
    treasury_chip_balance = treasury.chip_balance()  # e.g., 10M CHIP

    # 2. CHIP Market Price
    chip_price = oracle.get_price("CHIP/USDC")  # e.g., $2.50

    # 3. Calculate Collateral Value
    collateral_value = treasury_chip_balance * chip_price  # $25M

    # 4. Borrowing Capacity (30% LTV)
    borrowing_capacity = collateral_value * 0.30  # $7.5M

    # 5. Monthly Citation Budget (1% of capacity)
    monthly_budget = borrowing_capacity * 0.01  # $75k

    # 6. Historical Citation Volume
    avg_citations_per_month = analytics.get_avg_citations(months=3)  # e.g., 15,000

    # 7. Calculate Rate
    citation_rate = monthly_budget / avg_citations_per_month  # $75k / 15k = $5/citation

    return citation_rate
```

**Example Earnings**:
```
Your Published Articles:
├── "DeFi on Stellar vs EVM" (published 6 months ago)
│   ├── 45 citations
│   └── $225 earned
│
├── "Passkey Auth Best Practices" (published 3 months ago)
│   ├── 18 citations
│   └── $90 earned
│
└── "Learning Economy Thesis" (published 1 month ago)
    ├── 7 citations
    └── $35 earned

Total Lifetime: $350 USDC
Current Month: $45 USDC
Withdrawable: Yes (transferred to bank via Stripe)
```

**The Key Insight**: As the network grows and CHIP appreciates, the Treasury's borrowing capacity increases **exponentially**, meaning citation rewards can scale massively without requiring more capital deposits.

---

## II. How These Currencies Flow Through Jazzhands

### The User Journey: A Concrete Example

**Meet Alice**: A researcher with no capital, just ideas.

#### Week 1: Discovery

```
Alice discovers Choir via Twitter
  ├── Signs up with passkey (biometric, no seed phrases)
  ├── Receives: 500 free compute credits
  └── Receives: 50 starter CHIP tokens
```

#### Week 2: First Research Session

```python
# Alice in Vibewriter UI
alice.input("Research DeFi yield farming on Base vs Arbitrum")

# Behind the scenes (Jazzhands)
session = VibewriterSession(
    user_id="alice_123",
    compute_balance=500  # Free tier
)

# 1. Debit compute credits (pre-flight check)
await session.treasury.check_balance("compute", cost=50)
# Balance: 500 - 50 = 450 credits remaining

# 2. Spawn remote runtime (isolated container)
runtime = await RemoteRuntimeFactory.create(
    user_id="alice_123",
    provider="runloop",
    encrypted_volume="s3://choir-workspaces/alice_123/"
)

# 3. Run Vibewriter agent (8-stage pipeline)
agent = VibewriterAgent(runtime)
await agent.research(topic="DeFi yield farming Base vs Arbitrum")

# Agent actions (hidden from Alice):
# ├── Web search (5 sources)
# ├── Install citation-validator
# ├── Draft 1800-word report
# ├── Verify citations (5/5 valid)
# ├── Save to /workspace/drafts/defi_report_001.md
# └── Return to Alice

# 4. Alice sees clean UI
# "Research complete. 1,847 words. 5 verified citations."
# [Edit Draft] [Publish for 100 CHIP]
```

**Cost**: 50 compute credits (infrastructure)
**Balance**: 450 credits remaining

#### Week 3: Publishing

```python
# Alice clicks "Publish"
alice.publish(article="defi_report_001.md")

# Behind the scenes
# 1. Check CHIP balance
assert alice.chip_balance >= 100  # Alice has 50 (starter) - NOT ENOUGH

# 2. Purchase flow
alice.purchase_chip(amount=100, price_usdc=250)  # $250 for 100 CHIP
# Alice now has 150 CHIP

# 3. Stake CHIP to publish
await treasury.stake_chip(alice, amount=100)

# 4. Calculate semantic novelty
novelty_score = await semantic_engine.calculate_novelty(
    article=alice.article,
    corpus=choir_knowledge_base
)
# Result: novelty_score = 72 (solid new perspective)

# 5. Reward CHIP based on novelty
chip_reward = calculate_chip_reward(novelty_score)  # 72 → 180 CHIP

# 6. Net CHIP change
alice.chip_balance = 150 - 100 (staked) + 180 (reward) = 230 CHIP

# 7. Article is now live and citable
article_id = "article_alice_001"
choir_knowledge_base.add(article_id, alice.article)
```

**Cost**: 100 CHIP (staked, can withdraw later)
**Reward**: 180 CHIP (net +80 CHIP)
**Result**: Alice now has 230 CHIP and a citable article

#### Month 2-6: Citations Roll In

```python
# Other users' Vibewriter agents cite Alice's work
# (or human researchers cite it manually)

citations = [
    {"month": 2, "count": 3, "rate_per_citation": 4.50},
    {"month": 3, "count": 8, "rate_per_citation": 4.75},
    {"month": 4, "count": 12, "rate_per_citation": 5.00},
    {"month": 5, "count": 7, "rate_per_citation": 5.10},
    {"month": 6, "count": 5, "rate_per_citation": 5.25},
]

total_earned = sum(c["count"] * c["rate_per_citation"] for c in citations)
# = 3*4.50 + 8*4.75 + 12*5.00 + 7*5.10 + 5*5.25
# = $13.50 + $38 + $60 + $35.70 + $26.25
# = $173.45 USDC

# Alice's citation rewards dashboard
alice.usdc_balance = 173.45
alice.total_citations = 35
alice.chip_balance = 230 (unchanged, still owns it)
```

**Income**: $173.45 USDC (withdrawable)
**Citations**: 35 (ongoing passive income)
**Ownership**: 230 CHIP (governance rights)

#### Month 7: Alice Withdraws Earnings

```python
# Alice clicks "Withdraw to Bank Account"
await stripe.transfer(
    from_account=choir_treasury,
    to_account=alice_bank_account,
    amount_usdc=173.45,
    convert_to="USD"
)

# Alice receives $173.45 in her bank account
# This is REAL MONEY from intellectual contribution
# She never deposited capital, just published good research
```

**Result**: Alice earned $173 from one article, with no capital deployed. She still owns 230 CHIP for governance.

---

### The Architecture: How Jazzhands Enables This

```
┌─────────────────────────────────────────────────────────────┐
│                   ALICE (User)                               │
│                                                              │
│  "Research DeFi on Base vs Arbitrum"                        │
│                                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              CHOIR CONTROLLER (FastAPI)                      │
│                                                              │
│  1. Authenticate (Passkey JWT)                              │
│  2. Check Compute Balance (Alice has 450 credits)          │
│  3. Spawn RemoteRuntime (RunLoop, isolated container)       │
│  4. Route to VibewriterAgent                                │
│                                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          JAZZHANDS RUNTIME (OpenHands Fork)                  │
│                (Alice's Isolated Container)                  │
│                                                              │
│  /workspace/alice_123/                                       │
│  ├── sources/                                               │
│  │   ├── base_docs.pdf                                     │
│  │   ├── arbitrum_docs.pdf                                 │
│  │   └── aerodrome_data.json                               │
│  ├── drafts/                                                │
│  │   └── defi_report_001.md                                │
│  └── tools/                                                 │
│      └── citation_validator.py                              │
│                                                              │
│  Agent Actions (running as root in container):              │
│  1. pip install requests beautifulsoup4                     │
│  2. python fetch_sources.py                                 │
│  3. claude-api draft --sources /workspace/sources/          │
│  4. python citation_validator.py /workspace/drafts/defi_report_001.md│
│  5. Save final draft                                        │
│                                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              CHOIR TREASURY (PostgreSQL + Sui)               │
│                                                              │
│  Alice's Balances:                                           │
│  ├── Compute Credits: 450                                   │
│  ├── CHIP: 230                                              │
│  └── USDC: $173.45                                          │
│                                                              │
│  Choir Treasury:                                             │
│  ├── CHIP Holdings: 10M tokens                              │
│  ├── CHIP Value: $25M (at $2.50/CHIP)                      │
│  ├── Borrowed USDC: $7.5M (30% LTV)                        │
│  └── Citation Budget: $75k/month (1% of borrowing capacity)│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**The Flow**:
1. **Alice pays compute credits** → Jazzhands runtime spins up
2. **Agent produces research** → Saved in Alice's encrypted workspace
3. **Alice stakes CHIP to publish** → Treasury calculates novelty
4. **Novelty score → CHIP reward** → Alice earns ownership
5. **Article gets cited** → Treasury pays USDC from collateral-backed pool
6. **Alice withdraws USDC** → Real money in bank account

---

## III. The Treasury Economics: How Citation Rewards Scale

### The Dual-Revenue Model

**Stream 1: Deposit Yield → Operations** (NOT implemented in initial version)
```
Future: Users can optionally deposit USDC
  ├── Principal protected (withdrawable after lockup)
  ├── Yield goes to Treasury operations budget
  └── Users earn CHIP based on novelty, not deposit size
```

**Stream 2: Treasury CHIP Collateral → Citation Rewards** (Core model)
```
How Citation Rewards Are Funded:

1. Users consume CHIP for platform actions
   ├── Publish: 100 CHIP
   ├── Propose revision: 50 CHIP
   └── Boost article visibility: 25 CHIP

2. Consumed CHIP flows to Treasury
   ├── NOT burned (supply doesn't decrease)
   └── Treasury accumulates portfolio

3. Treasury's CHIP appreciates as network grows
   ├── More users → More demand for CHIP → Price increases
   └── $1/CHIP → $2.50/CHIP → $10/CHIP (long-term)

4. Treasury borrows against CHIP holdings
   ├── Collateral: 10M CHIP * $2.50 = $25M
   ├── LTV: 30% (conservative)
   └── Borrowing Capacity: $7.5M

5. Borrowed funds → Citation Rewards Pool
   ├── Monthly budget: 1% of borrowing capacity = $75k
   ├── If 15,000 citations/month → $5/citation
   └── If CHIP doubles to $5 → Budget doubles to $150k
```

**The Exponential Scaling**:
```
Scenario 1: Launch (Month 1)
├── Treasury CHIP: 5M tokens
├── CHIP Price: $0.50
├── Collateral Value: $2.5M
├── Borrowing Capacity: $750k (30% LTV)
├── Monthly Citation Budget: $7.5k (1%)
├── Citations/Month: 1,500
└── Rate: $5/citation

Scenario 2: Growth (Month 12)
├── Treasury CHIP: 10M tokens (more consumption)
├── CHIP Price: $2.50 (5x appreciation)
├── Collateral Value: $25M
├── Borrowing Capacity: $7.5M (30% LTV)
├── Monthly Citation Budget: $75k (1%)
├── Citations/Month: 15,000
└── Rate: $5/citation (stable despite 10x more citations)

Scenario 3: Maturity (Month 36)
├── Treasury CHIP: 25M tokens
├── CHIP Price: $10 (20x from launch)
├── Collateral Value: $250M
├── Borrowing Capacity: $75M (30% LTV)
├── Monthly Citation Budget: $750k (1%)
├── Citations/Month: 150,000
└── Rate: $5/citation (STILL STABLE)
```

**The Magic**: Citation rewards per citation remain stable (or even increase) while the total pool grows exponentially with network value.

---

## IV. Semantic Novelty: The CHIP Distribution Mechanism

### Why Novelty Matters

**The Problem**: If CHIP is distributed based on quantity (number of articles) or capital (deposit size), the system degrades:
- Spam attacks become profitable
- Wealthy users capture all ownership
- Knowledge base fills with redundant content

**The Solution**: Semantic novelty scoring ensures CHIP goes to genuine intellectual contribution.

### How It Works

```python
class SemanticNoveltyEngine:
    def __init__(self, vector_db: VectorDB):
        self.corpus = vector_db
        self.embedding_model = "text-embedding-3-large"  # OpenAI

    async def calculate_novelty(self, article: str) -> NoveltyScore:
        """
        Calculate how semantically novel an article is
        compared to the existing knowledge base.
        """
        # 1. Generate embedding for new article
        new_embedding = await self.embed(article)

        # 2. Search for similar articles in corpus
        neighbors = await self.corpus.search(
            vector=new_embedding,
            k=100,  # Check against top 100 most similar
            threshold=0.7  # Cosine similarity cutoff
        )

        # 3. Calculate semantic distance metrics
        if not neighbors:
            # First article on this topic
            return NoveltyScore(
                score=100,
                reason="First article in this semantic region"
            )

        # Average similarity to nearest neighbors
        avg_similarity = sum(n.similarity for n in neighbors) / len(neighbors)

        # Minimum similarity (closest existing article)
        min_distance = 1 - max(n.similarity for n in neighbors)

        # 4. Scoring algorithm
        if min_distance < 0.1:
            # Too similar to existing work (>90% overlap)
            score = 0
            reason = f"Too similar to article {neighbors[0].id}"

        elif min_distance < 0.3:
            # Incremental addition (70-90% overlap)
            score = int(min_distance * 100)  # 10-30
            reason = "Incremental improvement on existing work"

        elif min_distance < 0.5:
            # New angle on existing topic (50-70% overlap)
            score = int(30 + (min_distance - 0.3) * 200)  # 30-70
            reason = "Novel perspective on covered topic"

        else:
            # Breakthrough territory (>50% novel)
            score = int(70 + (min_distance - 0.5) * 600)  # 70-100
            reason = "Significant new contribution"

        return NoveltyScore(score=score, reason=reason)

    async def embed(self, text: str) -> Vector:
        """Generate embedding using OpenAI's latest model"""
        response = await openai.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
```

### Examples

**Example 1: Common Knowledge** (No Reward)
```
Article: "Bitcoin is a decentralized cryptocurrency"
Novelty Score: 0
Reason: "Covered extensively in articles #123, #456, #789"
CHIP Reward: 0
Result: Article rejected (below minimum threshold)
```

**Example 2: Incremental Improvement** (Small Reward)
```
Article: "Bitcoin's Lightning Network reduces transaction costs by 95%"
Novelty Score: 35
Reason: "Incremental data on well-covered topic (Lightning)"
CHIP Reward: 35 CHIP
Result: Published, but low visibility (small stake)
```

**Example 3: New Perspective** (Good Reward)
```
Article: "Lightning Network enables Choir-style micropayments for citations"
Novelty Score: 68
Reason: "Novel application of Lightning to citation economics"
CHIP Reward: 180 CHIP
Result: Published, good visibility, author nets +80 CHIP after staking
```

**Example 4: Breakthrough** (Huge Reward)
```
Article: "Proof that P=NP using quantum annealing on citation graphs"
Novelty Score: 98
Reason: "Paradigm-shifting mathematical proof"
CHIP Reward: 2,500 CHIP
Result: Published, top of discovery feed, author becomes whale
```

### The Emergent Logarithmic Decay

**Early Stage** (sparse semantic space):
```
Month 1: Average novelty score = 75
├── Corpus is empty
├── Every article explores new territory
└── CHIP distribution is high (bootstrap the knowledge base)
```

**Growth Stage** (filling semantic space):
```
Month 12: Average novelty score = 55
├── Major topics covered, but depth opportunities remain
├── Good research still rewarded well
└── CHIP distribution moderates
```

**Mature Stage** (dense semantic space):
```
Month 36: Average novelty score = 35
├── Most topics well-explored
├── Only breakthroughs earn significant CHIP
└── CHIP distribution low (mimics Bitcoin halving, but based on knowledge density)
```

**The Effect**: Early contributors capture more CHIP, similar to Bitcoin early miners. But instead of computational difficulty, it's **semantic difficulty** that increases over time.

---

## V. The Complete Economic Loop

### The Flywheel (Revisited with Jazzhands Integration)

```
1. User signs up (free tier)
   ├── 500 compute credits (infrastructure)
   ├── 50 CHIP tokens (publishing starter capital)
   └── $0 deposit required

2. User runs Vibewriter (Jazzhands backend)
   ├── Costs 50 compute credits
   ├── Agent uses remote runtime (OpenHands)
   └── Produces high-quality, citation-verified research

3. User publishes article
   ├── Stakes 100 CHIP
   ├── Semantic novelty scored (e.g., 72/100)
   └── Earns 180 CHIP (net +80)

4. Article enters citation graph
   ├── Vibewriter agents cite it (automatic)
   ├── Human researchers cite it (manual)
   └── Treasury pays USDC per citation

5. User earns citation income
   ├── 35 citations * $5/citation = $175 USDC
   ├── Withdrawable to bank account
   └── Real economic value from intellectual contribution

6. User reinvests (optional)
   ├── Use citation earnings to buy more compute credits
   ├── Publish more articles
   ├── Earn more CHIP (ownership compounds)
   └── Citation income scales

7. Network effects amplify
   ├── More users → More citations → Higher CHIP demand
   ├── CHIP price appreciates
   ├── Treasury's collateral value increases exponentially
   ├── Citation rewards pool scales with network value
   └── More researchers attracted by generous rewards

8. Go to step 2 (compounding loop)
```

---

## VI. Technical Implementation: The Choir Controller

### The Middleware Layer

```python
# choir_controller/treasury/balance_manager.py

class BalanceManager:
    """
    Manages the three-currency system:
    - Compute Credits (PostgreSQL, internal accounting)
    - CHIP (Sui blockchain, ownership token)
    - USDC (Sui blockchain, stablecoin)
    """

    def __init__(self, db: Database, sui_client: SuiClient):
        self.db = db
        self.sui = sui_client

    async def get_compute_balance(self, user_id: str) -> int:
        """Get user's compute credit balance (offchain)"""
        result = await self.db.query(
            "SELECT compute_credits FROM users WHERE id = $1",
            user_id
        )
        return result[0]["compute_credits"]

    async def get_chip_balance(self, user_id: str) -> int:
        """Get user's CHIP balance (onchain, cached)"""
        user_address = await self.get_sui_address(user_id)
        balance = await self.sui.get_balance(
            owner=user_address,
            coin_type="0x...::chip::CHIP"
        )
        # Cache in PostgreSQL for fast lookups
        await self.db.execute(
            "UPDATE users SET chip_balance = $1 WHERE id = $2",
            balance, user_id
        )
        return balance

    async def get_usdc_balance(self, user_id: str) -> Decimal:
        """Get user's USDC balance (onchain, cached)"""
        user_address = await self.get_sui_address(user_id)
        balance = await self.sui.get_balance(
            owner=user_address,
            coin_type="0x...::usdc::USDC"
        )
        return Decimal(balance) / Decimal(1_000_000)  # 6 decimals

    async def debit_compute(self, user_id: str, amount: int) -> bool:
        """
        Debit compute credits for a Vibewriter session.
        Returns False if insufficient balance (trigger autopurchase).
        """
        current = await self.get_compute_balance(user_id)
        if current < amount:
            # Trigger autopurchase flow (Stripe integration)
            await self.autopurchase_compute(user_id, amount)
            return False

        await self.db.execute(
            "UPDATE users SET compute_credits = compute_credits - $1 WHERE id = $2",
            amount, user_id
        )
        return True

    async def reward_chip(self, user_id: str, amount: int, reason: str):
        """
        Reward CHIP tokens for semantic novelty.
        This is an onchain transaction (Sui Move call).
        """
        user_address = await self.get_sui_address(user_id)

        # Call Sui smart contract
        tx = await self.sui.move_call(
            package="0x...::choir",
            module="treasury",
            function="reward_novelty",
            args=[user_address, amount, reason],
            gas_budget=10_000_000
        )

        await self.db.execute(
            "INSERT INTO chip_rewards (user_id, amount, reason, tx_hash) VALUES ($1, $2, $3, $4)",
            user_id, amount, reason, tx.digest
        )

    async def pay_citation(self, author_id: str, article_id: str, citation_rate: Decimal):
        """
        Pay USDC for a citation.
        Treasury borrows against CHIP collateral to fund this.
        """
        author_address = await self.get_sui_address(author_id)

        # Treasury smart contract handles the borrowing and payment
        tx = await self.sui.move_call(
            package="0x...::choir",
            module="treasury",
            function="pay_citation",
            args=[author_address, article_id, int(citation_rate * 1_000_000)],
            gas_budget=10_000_000
        )

        await self.db.execute(
            "INSERT INTO citations (article_id, author_id, amount, tx_hash) VALUES ($1, $2, $3, $4)",
            article_id, author_id, citation_rate, tx.digest
        )
```

### The Runtime Manager (Integrating with Jazzhands)

```python
# choir_controller/runtime/manager.py

class RemoteRuntimeManager:
    """
    Manages per-user Jazzhands (OpenHands) runtimes.
    Handles spawning, mounting encrypted volumes, suspending, and cleanup.
    """

    def __init__(self, balance_mgr: BalanceManager, provider: str = "runloop"):
        self.balance_mgr = balance_mgr
        self.provider = provider
        self.active_runtimes: Dict[str, RemoteRuntime] = {}

    async def get_or_create_runtime(self, user_id: str) -> RemoteRuntime:
        """
        Get existing runtime for user, or spawn a new one.
        """
        # Check if user has active runtime
        if user_id in self.active_runtimes:
            runtime = self.active_runtimes[user_id]
            if await runtime.is_alive():
                return runtime
            else:
                # Runtime died, clean up and respawn
                await self.cleanup_runtime(user_id)

        # Spawn new runtime
        runtime = await self._spawn_runtime(user_id)
        self.active_runtimes[user_id] = runtime
        return runtime

    async def _spawn_runtime(self, user_id: str) -> RemoteRuntime:
        """
        Spawn an isolated container for this user's research session.
        """
        # 1. Generate encrypted volume mount point
        volume_url = f"s3://choir-workspaces-encrypted/{user_id}/"

        # 2. Get user's encryption key (from TEE or KMS)
        encryption_key = await self.get_user_encryption_key(user_id)

        # 3. Create runtime via provider API
        if self.provider == "runloop":
            runtime = await RunLoopRuntime.create(
                user_id=user_id,
                workspace_url=volume_url,
                encryption_key=encryption_key,
                image="choir/vibewriter:latest",  # Custom image with our tools
                timeout=3600,  # 1 hour max per session
            )
        elif self.provider == "e2b":
            # E2B doesn't support suspend/resume, so use for quick tasks only
            runtime = await E2BRuntime.create(
                user_id=user_id,
                template="choir-vibewriter"
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        # 4. Wait for runtime to be ready
        await runtime.wait_until_ready(timeout=60)

        return runtime

    async def suspend_runtime(self, user_id: str):
        """
        Suspend runtime to save costs (only supported by some providers).
        State is preserved, can resume later.
        """
        runtime = self.active_runtimes.get(user_id)
        if runtime and hasattr(runtime, "suspend"):
            await runtime.suspend()
            # User can resume later without losing research context

    async def cleanup_runtime(self, user_id: str):
        """
        Destroy runtime and clean up resources.
        Called after session ends or timeout.
        """
        runtime = self.active_runtimes.pop(user_id, None)
        if runtime:
            await runtime.destroy()
```

---

## VII. The User Experience: What Users Actually See

### The Vibewriter UI (What Alice Sees)

```
┌─────────────────────────────────────────────────────────────┐
│  Choir                                    [CHIP: 230] [$175]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  New Research                                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ "Compare DeFi yield farming on Base vs Arbitrum"      │ │
│  │                                           [Research →] │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ⏳ Researching... (50 credits will be charged)             │
│                                                              │
│  Progress:                                                   │
│  ✓ Searched 7 sources (12 seconds)                          │
│  ✓ Verified citations (7/7 valid)                           │
│  ⏳ Drafting synthesis (est. 30 seconds)                    │
│  ⏸ Pending: Critique, Revision, Final Polish                │
│                                                              │
│  ── Draft Preview ──────────────────────────────────────────│
│                                                              │
│  # DeFi Yield Farming: Base vs Arbitrum                     │
│                                                              │
│  Base's Aerodrome protocol offers competitive yields...     │
│  [Citation: Aerodrome Docs, verified ✓]                     │
│                                                              │
│  Arbitrum's Aave V3 provides...                             │
│  [Citation: Aave Governance, verified ✓]                    │
│                                                              │
│  [Continue Research] [Edit] [Publish for 100 CHIP]         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Alice never sees**:
- ❌ Terminal output
- ❌ Python scripts
- ❌ Docker containers
- ❌ LLM API calls
- ❌ File system operations

**Alice only sees**:
- ✅ Research progress
- ✅ Draft preview
- ✅ Credit costs
- ✅ Citation verification status
- ✅ Publishing workflow

---

## VIII. Conclusion: Three Currencies, One Economy

**Compute Credits**: Infrastructure (pays for Jazzhands runtimes)
- Acquired: Purchase or free tier
- Used: Run Vibewriter sessions
- Benefit: Access to high-quality research agent

**CHIP Tokens**: Ownership (earned via novelty)
- Acquired: Semantic novelty scoring
- Used: Publishing, governance, collateral
- Benefit: Economic ownership of the protocol

**USDC**: Income (earned via citations)
- Acquired: Citations from other users/agents
- Used: Withdraw to bank account, reinvest
- Benefit: Real monetary compensation for intellectual contribution

**Together**: They create a sustainable learning economy where:
1. Infrastructure costs are covered (compute credits)
2. Ownership is earned through contribution (CHIP)
3. Income scales with impact (USDC citations)
4. The Treasury's collateral grows exponentially with network value
5. Users without capital can earn real income through research alone

**Jazzhands makes this possible** by providing the secure, isolated, stateful runtime environment that serious research agents need - without users having to think about code, containers, or infrastructure.

---

**Document Status**: Draft v1.0
**Related**: JAZZHANDS_FORK_STRATEGY.md, CHOIR_WHITEPAPER.md, ECONOMIC_MODEL.md
