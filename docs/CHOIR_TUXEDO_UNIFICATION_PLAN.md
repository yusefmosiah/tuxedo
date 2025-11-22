# Choir + Tuxedo Unification Plan

**The Knot**: Reconciling Choir's "Thought Bank" vision with Tuxedo's yield farming infrastructure

**Created**: 2025-11-22
**Status**: Strategic Unification Roadmap

---

## The Problem Statement

We have **two codebases** that need to become **one product**:

### Choir.chat (Legacy)
**Location**: `github.com/yusefmosiah/choir.chat`

**What it has**:
- ✅ **SwiftUI iOS app** - Native mobile experience
- ✅ **Carbon fiber kintsugi aesthetics** - Distinctive visual identity
- ✅ **Ghostwriter agent** - Rewards novelty, helps write articles
- ✅ **Citation system** - Automatic semantic similarity, citation rewards
- ✅ **Revision markets** - Stake to propose edits, economic curation
- ✅ **Vector DB** (Qdrant) - Semantic search for articles
- ✅ **Sui blockchain** - CHOIR token on Move
- ✅ **Conductor architecture** - Client orchestrates server agents

**What it lacks**:
- ❌ Passkey authentication (relies on wallet-based identity)
- ❌ Yield farming infrastructure (no DeFi integrations)
- ❌ Multi-chain support (Sui-only)
- ❌ Modern web frontend (iOS-first)

### Tuxedo (Current)
**Location**: `github.com/yusefmosiah/tuxedo`

**What it has**:
- ✅ **Passkey authentication** - WebAuthn, recovery codes, email
- ✅ **React/TypeScript frontend** - Modern web app
- ✅ **AI agent with 19 tools** - LangChain + Claude SDK
- ✅ **Vault system** - Non-custodial, dual-authority security
- ✅ **Yield farming** - Blend Capital, Stellar mainnet
- ✅ **Multi-chain vision** - EVM (Base), Stellar, Solana, Bitcoin
- ✅ **FastAPI backend** - Production-ready Python

**What it lacks**:
- ❌ Thought Bank features (no articles, citations, ghostwriter)
- ❌ Carbon fiber kintsugi aesthetic
- ❌ Conductor/agent orchestration pattern
- ❌ Revision markets, quality curation mechanisms

---

## The Vision: Unified Sovereign Cloud

**Product Name**: **Choir** (retire "Tuxedo" as internal codename)

**Core Offering**:
> Your Sovereign Cloud Personal Banking Agent + Thought Bank
>
> Earn from your capital (10-15% APY) AND your ideas (citation rewards).

**Two-Sided Platform**:

```
┌──────────────────────────────────────────────────────┐
│                     CHOIR                             │
│        Sovereign Cloud Thought Bank                   │
├──────────────────────────────────────────────────────┤
│                                                       │
│  LEFT SIDE: Capital (Tuxedo Foundation)              │
│  - Deposit USDC to vaults                            │
│  - Agent optimizes yields across chains              │
│  - Earn 10-15% APY from DeFi                         │
│  - Generate research reports                         │
│                                                       │
│  RIGHT SIDE: Ideas (Choir Foundation)                │
│  - Chat with AI (earn CHOIR via novelty rewards)    │
│  - Ghostwriter helps write articles                  │
│  - Publish to choir.chat (stake CHOIR)              │
│  - Earn citation rewards (stablecoins)              │
│                                                       │
│  THE BRIDGE: Research Reports Cite Articles         │
│  - Vault agents write strategy reports               │
│  - Reports cite articles from Choir knowledge base   │
│  - Citation rewards flow from performance fees       │
│  - Intellectual property becomes financial capital   │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## Unification Strategy

### Phase 1: Backend Merge (Weeks 1-4)

**Goal**: Combine Choir's Ghostwriter/Citation engine with Tuxedo's yield farming agent

#### 1.1 Database Schema Unification

**Tuxedo tables** (keep as-is):
```sql
-- Authentication
users, passkey_credentials, passkey_sessions, recovery_codes

-- Vaults
vault_positions, defi_positions

-- Chat
threads, messages
```

**Add Choir tables**:
```sql
-- Articles (from Choir)
CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),  -- For semantic search
    choir_staked INTEGER NOT NULL,   -- Tokens staked on this article
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    permalink TEXT UNIQUE,  -- choir.chat/<permalink>
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Citations (track who cited whom)
CREATE TABLE citations (
    id TEXT PRIMARY KEY,
    citing_article_id TEXT,  -- NULL if from research report
    citing_report_id TEXT,   -- NULL if from article
    cited_article_id TEXT NOT NULL,
    similarity_score REAL,   -- Automatic citation score
    manual BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cited_article_id) REFERENCES articles (id),
    CHECK ((citing_article_id IS NOT NULL AND citing_report_id IS NULL) OR
           (citing_article_id IS NULL AND citing_report_id IS NOT NULL))
);

-- Research Reports (from vault agents)
CREATE TABLE research_reports (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    vault_strategy TEXT NOT NULL,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),
    transaction_hash TEXT,  -- On-chain proof
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Revision Proposals (from Choir)
CREATE TABLE revision_proposals (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL,
    proposer_id TEXT NOT NULL,
    revised_content TEXT NOT NULL,
    choir_staked INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, accepted, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (proposer_id) REFERENCES users (id)
);

-- Novelty Rewards (from Choir - CHOIR token emissions)
CREATE TABLE novelty_rewards (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    choir_amount INTEGER NOT NULL,
    novelty_score REAL,  -- 0.0 - 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Citation Rewards (stablecoin payouts from performance fees)
CREATE TABLE citation_rewards (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    amount_usdc REAL NOT NULL,
    reward_period TEXT NOT NULL,  -- e.g., "2026-Q1"
    citation_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

#### 1.2 AI Agent Architecture Merge

**Current** (Tuxedo):
```python
# backend/main.py
agent = LangChainAgent(tools=[stellar_tools, vault_tools, blend_tools])
```

**Target** (Unified):
```python
# backend/agent/conductor.py
class Conductor:
    """Client-side orchestrator (inspired by Choir)"""
    def __init__(self):
        # Vault Agent (Tuxedo foundation)
        self.vault_agent = VaultAgent(tools=[
            aave_tools, morpho_tools, vault_tools
        ])

        # Ghostwriter Agent (Choir foundation)
        self.ghostwriter = GhostwriterAgent(
            research_model="anthropic/claude-3.5-sonnet",
            draft_model="anthropic/claude-3.5-sonnet",
            critique_model="moonshot/kimi-k2"
        )

        # Research Agent (NEW - bridges both sides)
        self.research_agent = ResearchAgent(
            vector_db=qdrant_client,
            citation_engine=CitationEngine()
        )

    async def route_message(self, message: str, user_id: str):
        """Route to appropriate agent based on intent"""
        intent = self.classify_intent(message)

        if intent == "vault_operation":
            return await self.vault_agent.execute(message, user_id)
        elif intent == "write_article":
            return await self.ghostwriter.compose(message, user_id)
        elif intent == "research":
            return await self.research_agent.search(message, user_id)
        else:
            # Default: conversational + novelty rewards
            return await self.chat_with_novelty_rewards(message, user_id)
```

#### 1.3 Vector Database Integration

**Add Qdrant** (from Choir):
```python
# backend/services/vector_db.py
from qdrant_client import QdrantClient

class VectorDB:
    def __init__(self):
        self.client = QdrantClient(url=os.getenv("QDRANT_URL"))
        self.collection = "choir_articles"

    async def index_article(self, article_id: str, content: str):
        """Embed and index article for semantic search"""
        embedding = await self.get_embedding(content)
        self.client.upsert(
            collection_name=self.collection,
            points=[{
                "id": article_id,
                "vector": embedding,
                "payload": {"article_id": article_id}
            }]
        )

    async def find_similar(self, query: str, limit: int = 10):
        """Find semantically similar articles"""
        query_embedding = await self.get_embedding(query)
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_embedding,
            limit=limit
        )
        return results
```

#### 1.4 Citation Engine

**NEW Component** (bridges Choir + Tuxedo):
```python
# backend/services/citation_engine.py
class CitationEngine:
    """Automatic citation detection via semantic similarity"""

    def __init__(self, vector_db: VectorDB, threshold: float = 0.75):
        self.vector_db = vector_db
        self.similarity_threshold = threshold

    async def detect_citations(self, content: str) -> List[Citation]:
        """Find articles that should be cited based on semantic similarity"""
        similar_articles = await self.vector_db.find_similar(
            query=content,
            limit=20
        )

        citations = []
        for article in similar_articles:
            if article.score >= self.similarity_threshold:
                citations.append(Citation(
                    cited_article_id=article.payload["article_id"],
                    similarity_score=article.score,
                    manual=False
                ))

        return citations

    async def generate_research_report(
        self,
        user_id: str,
        strategy: str,
        decision_rationale: str
    ) -> ResearchReport:
        """
        Generate research report for vault strategy
        Automatically cite articles from knowledge base
        """
        # Detect citations in the rationale
        citations = await self.detect_citations(decision_rationale)

        # Create research report
        report = ResearchReport(
            user_id=user_id,
            vault_strategy=strategy,
            content=decision_rationale,
            citations=citations
        )

        # Save to DB
        await self.save_report(report)

        # Trigger citation reward distribution
        await self.distribute_citation_rewards(report)

        return report
```

---

### Phase 2: Frontend Unification (Weeks 5-8)

**Goal**: Build unified React frontend with Choir aesthetics + Tuxedo functionality

#### 2.1 Design System: Carbon Fiber Kintsugi

**Import Choir's aesthetic**:
```typescript
// src/theme/choir-theme.ts
export const choirTheme = {
  colors: {
    // Carbon fiber blacks
    background: {
      primary: '#0a0a0a',    // Deep black
      secondary: '#1a1a1a',  // Card backgrounds
      tertiary: '#2a2a2a',   // Hover states
    },

    // Kintsugi gold accents (cracks, highlights)
    accent: {
      gold: '#d4af37',       // Primary gold
      lightGold: '#f4d03f',  // Highlights
      darkGold: '#b8860b',   // Shadows
    },

    // Text
    text: {
      primary: '#ffffff',
      secondary: '#a0a0a0',
      muted: '#606060',
    },

    // Semantic colors
    success: '#10b981',  // Green for yields
    warning: '#f59e0b',  // Orange for alerts
    error: '#ef4444',    // Red for errors
  },

  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    // Choir uses clean, modern typography
  },

  effects: {
    // Carbon fiber texture
    carbonFiber: 'url(/textures/carbon-fiber.png)',

    // Kintsugi crack patterns (SVG overlays)
    kintsugiCracks: 'url(/patterns/kintsugi-01.svg)',

    // Glow effects for interactive elements
    goldGlow: '0 0 20px rgba(212, 175, 55, 0.3)',
  },
}
```

**Component library**:
```typescript
// src/components/choir-ui/Card.tsx
export const ChoirCard = ({ children, hasCracks = false }) => (
  <div className="
    bg-background-secondary
    rounded-lg
    p-6
    border border-gold/20
    backdrop-blur-sm
    relative
    overflow-hidden
  ">
    {hasCracks && (
      <div className="
        absolute inset-0
        opacity-30
        pointer-events-none
        bg-[url(/patterns/kintsugi-01.svg)]
        bg-cover
      " />
    )}
    {children}
  </div>
)
```

#### 2.2 Unified Layout

**New navigation structure**:
```
┌─────────────────────────────────────────────────────┐
│  CHOIR                            [Avatar] [☰ Menu] │
├─────────────────────────────────────────────────────┤
│  [💬 Chat] [📚 Library] [💰 Vaults] [📝 Write]    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Main Content Area                                   │
│  (Chat, Articles, Vaults, Ghostwriter)              │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Routes**:
```typescript
// src/App.tsx
const routes = [
  { path: '/', component: ChatInterface },           // Tuxedo chat + novelty rewards
  { path: '/library', component: ArticleLibrary },   // Choir article browsing
  { path: '/library/:permalink', component: Article }, // Individual article
  { path: '/vaults', component: VaultDashboard },    // Tuxedo vaults
  { path: '/write', component: Ghostwriter },        // Choir ghostwriter
  { path: '/profile', component: Profile },          // User profile + stats
]
```

#### 2.3 Key Components

**Chat Interface** (enhanced):
```typescript
// src/components/ChatInterface.tsx
export const ChatInterface = () => {
  // Tuxedo foundation: agent chat
  // + Choir addition: novelty rewards

  return (
    <div>
      <ConversationThread messages={messages} />

      {/* Show novelty rewards for insightful messages */}
      {noveltyReward && (
        <NoveltyRewardToast
          amount={noveltyReward.choir_amount}
          message="Earned CHOIR for novel insight!"
        />
      )}

      <ChatInput onSend={handleSend} />
    </div>
  )
}
```

**Ghostwriter** (NEW from Choir):
```typescript
// src/components/Ghostwriter.tsx
export const Ghostwriter = () => {
  const [topic, setTopic] = useState('')
  const [styleGuide, setStyleGuide] = useState('')
  const [draft, setDraft] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  const generateDraft = async () => {
    setIsGenerating(true)

    // Multi-model orchestration (from Choir)
    // 1. Research phase (web + vector DB)
    // 2. Draft phase (Claude with style guide)
    // 3. Critique phase (Kimi K2)
    // 4. Revision phase (Claude incorporating critique)

    const result = await api.ghostwriter.generate({
      topic,
      styleGuide,
    })

    setDraft(result.draft)
    setIsGenerating(false)
  }

  return (
    <div className="ghostwriter-interface">
      <h1>Ghostwriter</h1>
      <p>AI-assisted article creation</p>

      <Input
        label="Topic"
        value={topic}
        onChange={setTopic}
        placeholder="What do you want to write about?"
      />

      <TextArea
        label="Style Guide (optional)"
        value={styleGuide}
        onChange={setStyleGuide}
        placeholder="Paste your writing style guide here..."
      />

      <Button onClick={generateDraft} loading={isGenerating}>
        Generate Draft
      </Button>

      {draft && (
        <ArticleEditor
          content={draft}
          onSave={handleSave}
          onPublish={handlePublish}
        />
      )}
    </div>
  )
}
```

**Article Library** (NEW from Choir):
```typescript
// src/components/ArticleLibrary.tsx
export const ArticleLibrary = () => {
  const [articles, setArticles] = useState([])
  const [searchQuery, setSearchQuery] = useState('')

  // Semantic search via vector DB
  const searchArticles = async (query: string) => {
    const results = await api.articles.search(query)
    setArticles(results)
  }

  return (
    <div>
      <h1>Knowledge Library</h1>

      <SearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        onSearch={searchArticles}
        placeholder="Search articles semantically..."
      />

      <ArticleGrid articles={articles} />
    </div>
  )
}
```

---

### Phase 3: Token Migration (Weeks 9-12)

**Goal**: Migrate CHOIR token from Sui to Base (EVM)

#### 3.1 Why Migrate from Sui to Base?

**Sui limitations**:
- ❌ Smaller ecosystem vs EVM
- ❌ Fewer DeFi integrations
- ❌ Less tooling/wallet support
- ❌ Doesn't align with multichain vision

**Base advantages**:
- ✅ EVM-compatible (massive ecosystem)
- ✅ Low fees (~$0.01 per tx)
- ✅ Coinbase backing (easy onramps)
- ✅ DeFi integrations (Aave, Morpho, Uniswap)
- ✅ Aligns with Tuxedo's multichain roadmap

#### 3.2 Token Contract Migration

**Old** (Sui Move):
```move
// choir_coin/sources/choir_coin.move
module choir::choir_coin {
    struct CHOIR_COIN has drop {}
    // ...Sui-specific logic
}
```

**New** (Solidity ERC-20):
```solidity
// contracts/CHOIRToken.sol
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CHOIRToken is ERC20, Ownable {
    // Total supply: 100M CHOIR
    uint256 public constant MAX_SUPPLY = 100_000_000 * 10**18;

    // Emission schedule
    uint256 public noveltyRewardsPool;
    uint256 public yieldFarmingRewardsPool;

    constructor() ERC20("Choir", "CHOIR") {
        // Initial distribution
        noveltyRewardsPool = 40_000_000 * 10**18;  // 40% novelty
        yieldFarmingRewardsPool = 40_000_000 * 10**18;  // 40% yield farming

        // 20% to treasury (DAO controlled)
        _mint(address(this), 20_000_000 * 10**18);
    }

    function mintNoveltyReward(address to, uint256 amount) external onlyOwner {
        require(noveltyRewardsPool >= amount, "Insufficient novelty pool");
        noveltyRewardsPool -= amount;
        _mint(to, amount);
    }

    function mintYieldReward(address to, uint256 amount) external onlyOwner {
        require(yieldFarmingRewardsPool >= amount, "Insufficient yield pool");
        yieldFarmingRewardsPool -= amount;
        _mint(to, amount);
    }
}
```

#### 3.3 Migration Strategy

**For existing Sui CHOIR holders** (if any):
1. Snapshot Sui balances at block X
2. Deploy new ERC-20 CHOIR on Base
3. 1:1 migration portal (burn Sui CHOIR → mint Base CHOIR)
4. 90-day migration window

**New users**: Only Base CHOIR from day 1

---

### Phase 4: Revenue Model Integration (Weeks 13-16)

**Goal**: Connect yield farming performance fees to citation rewards

#### 4.1 Performance Fee Flow

```
Vault Generates Profit
    ↓
Performance Fee (20% of profit)
    ↓
Split:
├─ 70% → Citation Reward Pool (stablecoins)
├─ 20% → Operations
└─ 10% → CHOIR Buyback/Burn
```

#### 4.2 Citation Reward Distribution

```python
# backend/services/rewards.py
class RewardDistributor:
    async def distribute_citation_rewards(
        self,
        reward_period: str,  # e.g., "2026-Q1"
        total_performance_fees: Decimal  # USDC collected
    ):
        """
        Distribute citation rewards to article authors
        based on how many times their articles were cited
        """
        citation_pool = total_performance_fees * Decimal('0.70')

        # Get all citations from research reports this period
        citations = await db.citations.filter(
            created_at__gte=period_start,
            created_at__lt=period_end,
            citing_report_id__isnull=False  # Only from research reports
        )

        total_citations = len(citations)
        reward_per_citation = citation_pool / total_citations

        # Group by article and calculate rewards
        rewards_by_article = {}
        for citation in citations:
            article_id = citation.cited_article_id
            rewards_by_article[article_id] = (
                rewards_by_article.get(article_id, Decimal('0')) +
                reward_per_citation
            )

        # Distribute to authors
        for article_id, reward_amount in rewards_by_article.items():
            article = await db.articles.get(id=article_id)

            await db.citation_rewards.create(
                article_id=article_id,
                user_id=article.user_id,
                amount_usdc=float(reward_amount),
                reward_period=reward_period,
                citation_count=citations.filter(
                    cited_article_id=article_id
                ).count()
            )

            # Send notification
            await notify_user(
                article.user_id,
                f"You earned ${reward_amount:.2f} from citations this quarter!"
            )
```

---

## Implementation Timeline

### Month 1: Backend Foundation
- Week 1: Database schema merge
- Week 2: Vector DB integration (Qdrant)
- Week 3: Citation engine implementation
- Week 4: Ghostwriter agent integration

### Month 2: Frontend Rebuild
- Week 5: Choir design system (carbon fiber kintsugi)
- Week 6: Unified layout + navigation
- Week 7: Article library + ghostwriter UI
- Week 8: Integration testing

### Month 3: Token Migration
- Week 9: Deploy CHOIR ERC-20 on Base
- Week 10: Migration portal for Sui holders
- Week 11: Liquidity provisioning (CHOIR/USDC pool)
- Week 12: Token distribution testing

### Month 4: Revenue Integration
- Week 13: Performance fee → citation reward flow
- Week 14: Novelty reward system
- Week 15: End-to-end testing
- Week 16: Beta launch

---

## Success Metrics

**After 6 months**:
- [ ] 1,000 registered users (passkey auth)
- [ ] 500 published articles (ghostwriter-assisted)
- [ ] $50k TVL in vaults (yield farming)
- [ ] $5k distributed in citation rewards
- [ ] 50 research reports generated
- [ ] 200 automatic citations detected

**After 12 months**:
- [ ] 10,000 users
- [ ] 5,000 articles
- [ ] $500k TVL
- [ ] $50k citation rewards distributed
- [ ] Profitable (revenue > costs)

---

## Open Questions

### Technical

1. **Vector DB**: Qdrant (Choir's choice) vs Pinecone vs pgvector?
   - **Recommendation**: Qdrant (proven in Choir, open-source)

2. **Embedding model**: OpenAI `text-embedding-3-large` vs custom?
   - **Recommendation**: OpenAI (consistent with Choir)

3. **Citation threshold**: What similarity score = automatic citation?
   - **Recommendation**: Start at 0.75, tune based on feedback

4. **Multi-model orchestration**: Keep Choir's approach (Claude + Kimi K2)?
   - **Recommendation**: Yes, it's working well

### Product

1. **Mobile app priority**: When to improve SwiftUI Choir app?
   - **Recommendation**: After web app launch (Month 6+)

2. **Sui token holders**: How many exist? Migration incentive?
   - **Action**: Snapshot Sui chain, check if any holders

3. **Revision markets**: Implement now or later?
   - **Recommendation**: Later (Month 6+), focus on core flow first

### Economics

1. **Novelty reward decay schedule**: How fast should emissions decay?
   - **Recommendation**: 50% year 1, 30% year 2, 20% year 3, 5% ongoing

2. **Citation reward split**: 70% to authors vs other allocation?
   - **Recommendation**: Start at 70%, adjust based on data

---

## Next Immediate Steps

1. **Review this plan** with team
2. **Decide on priorities**: What to build first?
3. **Set up unified repo**: Merge or keep separate during transition?
4. **Choose design system**: Import Choir's aesthetic to Tuxedo
5. **Database planning**: Run migration scripts

---

**Document Version**: 1.0
**Created**: 2025-11-22
**Status**: Strategic plan awaiting approval

**Key Decision**: This unifies both codebases into a single product vision where **yield farming funds knowledge creation** and **knowledge creation improves yield farming**. The flywheel works because better research → better strategies → more profits → more citation rewards → more researchers.
