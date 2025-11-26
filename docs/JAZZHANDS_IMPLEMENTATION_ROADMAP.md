# Jazzhands Implementation Roadmap

**From Stellar Scaffold to Citation Economics Infrastructure**

**Version 1.0 - November 26, 2025**

---

## Executive Summary

This document provides a phased migration plan from the current Tuxedo/Choir codebase (built on Stellar scaffold) to Jazzhands (OpenHands fork) with full citation economics integration.

**Current State**: Stellar scaffold with basic Ghostwriter, passkey auth, chat interface
**Target State**: Jazzhands-based Vibewriter with citation economics, semantic novelty, remote runtimes

**Timeline**: 12-16 weeks (3-4 months)
**Risk Level**: Medium (large architectural change, but clean separation of concerns)
**Reversibility**: High (can keep current system running in parallel during migration)

---

## I. Current State Analysis

### What We Have (As of Nov 2025)

**Backend (Python)**:
- ✅ FastAPI application (main.py, app.py)
- ✅ Passkey authentication (database_passkeys.py)
- ✅ LangChain agent with 19 tools (agent/core.py)
- ✅ Ghostwriter pipeline (agent/ghostwriter/) - 8 stages
- ✅ WebSearch integration (Tavily API)
- ✅ Multi-user account system (account_manager.py)
- ✅ SQLite database
- 🚧 Stellar blockchain tools (legacy, not core)

**Frontend (React)**:
- ✅ Vite + React + TypeScript
- ✅ Chat interface (ChatInterface.tsx)
- ✅ Passkey auth flow (AuthContext.tsx, passkeyAuth.ts)
- ✅ API client (api.ts)
- ⚠️ No economic dashboard (CHIP, USDC)
- ⚠️ No publishing workflow

**Infrastructure**:
- ✅ Local development environment
- ⚠️ Single-user runtime (agents run on same server as API)
- ⚠️ No container isolation
- ⚠️ No remote runtime support

### What We're Missing

**Critical for Choir Vision**:
1. ❌ Citation economics (no USDC rewards, no CHIP distribution)
2. ❌ Semantic novelty scoring (no vector database)
3. ❌ Publishing workflow (no stake-to-publish)
4. ❌ Multi-tenant runtime isolation (security vulnerability)
5. ❌ Remote runtime support (RunLoop, E2B)
6. ❌ Economic UI (no CHIP balance, no earnings dashboard)

**The Gap**: We have a functional research agent, but we're missing the economic layer and secure multi-tenant infrastructure.

---

## II. Migration Strategy: Parallel Development

### The Approach

**NOT**: Big-bang rewrite (too risky)
**YES**: Parallel development with gradual cutover

```
Current System (Tuxedo)          New System (Jazzhands)
      │                                 │
      │                                 │
      ├─── Week 1-4 ─────────────────► Fork & Setup
      │                                 │
      ├─── Week 5-8 ─────────────────► Build Core Components
      │    (Keep running)               │
      │                                 │
      ├─── Week 9-12 ────────────────► Integration & Testing
      │    (Gradual migration)          │
      │                                 │
      └─── Week 13-16 ───────────────► Full Cutover
           (Shut down)                  (Production)
```

**Benefits**:
- Current users unaffected during development
- Can test Jazzhands thoroughly before launch
- Can roll back if issues arise
- Reduces deployment risk

---

## III. Phase 1: Foundation (Weeks 1-4)

### Goals
- Fork OpenHands and clean it up
- Set up Choir Controller infrastructure
- Integrate passkey auth with Jazzhands
- Deploy basic remote runtime

### Tasks

#### Week 1: Fork & Clean Room Setup

```bash
# Day 1-2: Fork Repository
git clone https://github.com/All-Hands-AI/OpenHands.git jazzhands
cd jazzhands

# Delete proprietary code (legal requirement)
rm -rf enterprise/
git commit -m "Remove proprietary enterprise code (clean room)"

# Add Choir-specific directories
mkdir -p choir_controller/{auth,treasury,sessions,runtime_manager}
mkdir -p frontend_vibewriter/

# Update README and LICENSE
# - Add Choir copyright
# - Include OpenHands MIT license attribution
# - Document clean room approach

# Day 3-5: Repository Setup
# - Set up CI/CD (GitHub Actions)
# - Configure linting/formatting (Black, ESLint)
# - Set up development environment (Docker Compose)
# - Create initial project structure
```

**Deliverable**: Clean Jazzhands repository with no proprietary code

#### Week 2: Choir Controller - Authentication Layer

```python
# choir_controller/auth/passkey_middleware.py

class PasskeyAuthMiddleware:
    """
    Middleware that validates passkey signatures
    and injects user_id into request context.
    """

    def __init__(self, app: ASGIApp, database: Database):
        self.app = app
        self.db = database

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            # Extract bearer token from Authorization header
            token = extract_bearer_token(scope["headers"])

            if token:
                # Validate JWT (signed by our passkey auth service)
                user_id = await self.validate_session(token)

                if user_id:
                    # Inject user_id into request scope
                    scope["state"]["user_id"] = user_id

        await self.app(scope, receive, send)

    async def validate_session(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(
                token,
                settings.SESSION_SECRET_KEY,
                algorithms=["HS256"]
            )
            return payload["user_id"]
        except jwt.InvalidTokenError:
            return None
```

```python
# choir_controller/app.py

from fastapi import FastAPI
from choir_controller.auth.passkey_middleware import PasskeyAuthMiddleware

app = FastAPI(title="Choir Controller")

# Add passkey auth middleware
app.add_middleware(
    PasskeyAuthMiddleware,
    database=get_database()
)

# Mount OpenHands SDK routes (wrapped)
@app.post("/vibewriter/run")
async def run_vibewriter(request: Request, prompt: str):
    user_id = request.state.user_id  # Injected by middleware
    session = await get_or_create_session(user_id)
    result = await session.run(prompt)
    return result
```

**Deliverable**: Passkey auth integrated with Jazzhands backend

#### Week 3: Runtime Manager - Remote Runtime Support

```python
# choir_controller/runtime/manager.py

class RemoteRuntimeManager:
    """Manages per-user remote runtimes"""

    def __init__(self, provider: str = "runloop"):
        self.provider = provider
        self.sessions: Dict[str, RuntimeSession] = {}

    async def get_or_create(self, user_id: str) -> RuntimeSession:
        if user_id not in self.sessions:
            self.sessions[user_id] = await self._spawn(user_id)
        return self.sessions[user_id]

    async def _spawn(self, user_id: str) -> RuntimeSession:
        # Patch OpenHands RemoteRuntime to support auth headers
        runtime = RemoteRuntime(
            api_url=settings.RUNLOOP_API_URL,
            api_headers={
                "Authorization": f"Bearer {settings.RUNLOOP_API_KEY}",
                "X-User-ID": user_id  # For billing/isolation
            },
            workspace_url=f"s3://choir-workspaces/{user_id}/"
        )

        await runtime.connect()
        return RuntimeSession(runtime, user_id)
```

```python
# Patch to OpenHands RemoteRuntime (openhands/runtime/impl/remote/remote_runtime.py)

class RemoteRuntime:
    def __init__(
        self,
        api_url: str,
        api_headers: Optional[Dict[str, str]] = None,  # NEW
        workspace_url: Optional[str] = None,
    ):
        self.api_url = api_url
        self.api_headers = api_headers or {}  # NEW
        self.workspace_url = workspace_url

    async def _make_request(self, endpoint: str, data: dict) -> dict:
        headers = {
            "Content-Type": "application/json",
            **self.api_headers  # NEW: Include custom headers
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}{endpoint}",
                json=data,
                headers=headers
            )
            return response.json()
```

**Deliverable**: Remote runtime integration with RunLoop

#### Week 4: Database Schema for Economics

```sql
-- choir_controller/migrations/001_economic_tables.sql

-- Compute credits (offchain, internal accounting)
CREATE TABLE user_compute_credits (
    user_id TEXT PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CHIP balances (cached from blockchain)
CREATE TABLE user_chip_balances (
    user_id TEXT PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 0,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USDC earnings (cached from blockchain)
CREATE TABLE user_usdc_balances (
    user_id TEXT PRIMARY KEY,
    balance DECIMAL(18, 6) NOT NULL DEFAULT 0,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Articles (for citation tracking)
CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    author_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,  -- Markdown
    novelty_score INTEGER NOT NULL,  -- 0-100
    chip_staked INTEGER NOT NULL,  -- Amount staked to publish
    chip_rewarded INTEGER NOT NULL,  -- Amount earned for novelty
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(1536),  -- For semantic search (pgvector)
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- Citations (for reward tracking)
CREATE TABLE citations (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL,
    citing_user_id TEXT NOT NULL,
    citing_context TEXT,  -- Where/how it was cited
    reward_usdc DECIMAL(18, 6) NOT NULL,  -- Amount paid to author
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- Novelty rewards (CHIP distribution log)
CREATE TABLE novelty_rewards (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    novelty_score INTEGER NOT NULL,
    chip_amount INTEGER NOT NULL,
    reason TEXT,
    tx_hash TEXT,  -- Blockchain transaction
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Deliverable**: Database schema for citation economics

---

## IV. Phase 2: Core Components (Weeks 5-8)

### Goals
- Build semantic novelty engine
- Implement citation reward system
- Create publishing workflow backend
- Build economic UI components

### Tasks

#### Week 5: Semantic Novelty Engine

```python
# choir_controller/treasury/novelty.py

import openai
from qdrant_client import QdrantClient

class SemanticNoveltyEngine:
    def __init__(self):
        self.qdrant = QdrantClient(url=settings.QDRANT_URL)
        self.collection = "choir_articles"

    async def calculate_novelty(
        self,
        article_text: str
    ) -> NoveltyScore:
        # 1. Generate embedding
        embedding = await self.embed(article_text)

        # 2. Search for similar articles
        results = self.qdrant.search(
            collection_name=self.collection,
            query_vector=embedding,
            limit=100
        )

        if not results:
            # First article on this topic
            return NoveltyScore(score=100, reason="First in semantic region")

        # 3. Calculate semantic distance
        similarities = [r.score for r in results]
        max_similarity = max(similarities)
        min_distance = 1 - max_similarity

        # 4. Score based on distance
        score = self._calculate_score(min_distance)

        return NoveltyScore(
            score=score,
            reason=self._explain_score(score, results[0])
        )

    async def embed(self, text: str) -> List[float]:
        response = await openai.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding

    def _calculate_score(self, distance: float) -> int:
        if distance < 0.1:
            return 0
        elif distance < 0.3:
            return int(distance * 100)
        elif distance < 0.5:
            return int(30 + (distance - 0.3) * 200)
        else:
            return int(70 + (distance - 0.5) * 600)
```

**Deliverable**: Semantic novelty scoring system

#### Week 6: Citation Reward System

```python
# choir_controller/treasury/citations.py

class CitationRewardEngine:
    def __init__(self, sui_client: SuiClient, db: Database):
        self.sui = sui_client
        self.db = db

    async def record_citation(
        self,
        article_id: str,
        citing_user_id: str,
        context: str
    ):
        # 1. Get author of cited article
        article = await self.db.get_article(article_id)
        author_id = article.author_id

        # 2. Calculate current citation rate
        rate = await self.calculate_citation_rate()

        # 3. Pay author via smart contract
        tx = await self.sui.move_call(
            package="0x...::choir",
            module="treasury",
            function="pay_citation",
            args=[article.author_sui_address, int(rate * 1_000_000)],
            gas_budget=10_000_000
        )

        # 4. Record in database
        await self.db.create_citation(
            article_id=article_id,
            citing_user_id=citing_user_id,
            context=context,
            reward_usdc=rate,
            tx_hash=tx.digest
        )

        return rate

    async def calculate_citation_rate(self) -> Decimal:
        # Dynamic pricing based on Treasury's CHIP collateral
        treasury_chip = await self.get_treasury_chip_balance()
        chip_price = await self.get_chip_price()
        collateral_value = treasury_chip * chip_price

        # 30% LTV, 1% monthly budget
        borrowing_capacity = collateral_value * Decimal("0.30")
        monthly_budget = borrowing_capacity * Decimal("0.01")

        # Average citations per month (trailing 90 days)
        avg_citations = await self.db.get_avg_monthly_citations(days=90)

        if avg_citations == 0:
            return Decimal("5.00")  # Bootstrap rate

        return monthly_budget / avg_citations
```

**Deliverable**: Citation reward system with dynamic pricing

#### Week 7: Publishing Workflow Backend

```python
# choir_controller/publishing/workflow.py

class PublishingWorkflow:
    def __init__(
        self,
        novelty_engine: SemanticNoveltyEngine,
        treasury: TreasuryClient,
        db: Database
    ):
        self.novelty = novelty_engine
        self.treasury = treasury
        self.db = db

    async def publish_article(
        self,
        user_id: str,
        title: str,
        content: str
    ) -> PublishResult:
        # 1. Check user has enough CHIP to stake
        user_chip = await self.treasury.get_chip_balance(user_id)
        if user_chip < 100:
            raise InsufficientChipError("Need 100 CHIP to publish")

        # 2. Calculate semantic novelty
        novelty = await self.novelty.calculate_novelty(content)

        if novelty.score < 20:
            raise NoveltyTooLowError(novelty.reason)

        # 3. Calculate CHIP reward
        chip_reward = self._calculate_chip_reward(novelty.score)

        # 4. Stake CHIP (smart contract call)
        await self.treasury.stake_chip(user_id, amount=100)

        # 5. Save article to database
        article_id = await self.db.create_article(
            author_id=user_id,
            title=title,
            content=content,
            novelty_score=novelty.score,
            chip_staked=100,
            chip_rewarded=chip_reward
        )

        # 6. Add to vector database
        embedding = await self.novelty.embed(content)
        await self.novelty.qdrant.upsert(
            collection_name="choir_articles",
            points=[{
                "id": article_id,
                "vector": embedding,
                "payload": {"title": title, "author_id": user_id}
            }]
        )

        # 7. Reward novelty (smart contract call)
        await self.treasury.reward_chip(user_id, chip_reward, novelty.reason)

        return PublishResult(
            article_id=article_id,
            novelty_score=novelty.score,
            chip_staked=100,
            chip_rewarded=chip_reward,
            net_chip=chip_reward - 100
        )
```

**Deliverable**: Publishing workflow with novelty-based rewards

#### Week 8: Economic UI Components

```typescript
// frontend_vibewriter/src/components/EconomicDashboard.tsx

export function EconomicDashboard() {
  const { data: balances } = useQuery({
    queryKey: ["balances"],
    queryFn: () => api.getBalances()
  })

  return (
    <div className="economic-dashboard">
      <BalanceCard
        icon="💎"
        label="CHIP"
        value={balances.chip}
        tooltip="Governance tokens earned via novelty"
      />

      <BalanceCard
        icon="💰"
        label="Earned"
        value={`$${balances.usdc}`}
        tooltip="Citation rewards (withdrawable)"
      />

      <BalanceCard
        icon="⚡"
        label="Credits"
        value={balances.compute}
        tooltip="Compute credits for Vibewriter"
      />
    </div>
  )
}
```

```typescript
// frontend_vibewriter/src/components/PublishModal.tsx

export function PublishModal({ article }: { article: Draft }) {
  const [novelty, setNovelty] = useState<NoveltyScore | null>(null)
  const [publishing, setPublishing] = useState(false)

  useEffect(() => {
    // Calculate novelty when modal opens
    api.calculateNovelty(article.content).then(setNovelty)
  }, [article])

  async function handlePublish() {
    setPublishing(true)
    try {
      const result = await api.publishArticle({
        title: article.title,
        content: article.content
      })
      toast.success(`Published! Earned ${result.chip_rewarded} CHIP`)
      onSuccess(result)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setPublishing(false)
    }
  }

  if (!novelty) return <LoadingSpinner />

  return (
    <Modal>
      <h2>Publish Article</h2>

      <NoveltyMeter score={novelty.score} />
      <p className="explanation">{novelty.reason}</p>

      <EconomicsBreakdown
        stake={100}
        reward={novelty.chipReward}
        net={novelty.chipReward - 100}
      />

      <Button onClick={handlePublish} loading={publishing}>
        Confirm & Publish
      </Button>
    </Modal>
  )
}
```

**Deliverable**: Economic UI components (dashboard, publishing modal)

---

## V. Phase 3: Integration & Testing (Weeks 9-12)

### Goals
- Integrate Jazzhands with Choir Controller
- Build Vibewriter frontend
- End-to-end testing
- Performance optimization

### Tasks

#### Week 9: Vibewriter Agent Integration

```python
# choir_controller/agents/vibewriter.py

from openhands.agent import Agent
from openhands.runtime import RemoteRuntime

class VibewriterAgent:
    """
    Wraps OpenHands agent with Choir-specific workflow
    """

    def __init__(self, runtime: RemoteRuntime):
        self.runtime = runtime
        self.agent = Agent(
            llm="anthropic/claude-sonnet-4",
            runtime=runtime
        )

    async def research_and_write(
        self,
        topic: str,
        style_guide: str = "technical"
    ) -> ResearchResult:
        # 8-stage Ghostwriter pipeline
        stages = [
            self._stage_research,
            self._stage_draft,
            self._stage_extract,
            self._stage_verify,
            self._stage_critique,
            self._stage_revise,
            self._stage_reverify,
            self._stage_style
        ]

        context = {"topic": topic, "style_guide": style_guide}

        for stage in stages:
            yield StageStarted(stage.__name__)
            result = await stage(context)
            context.update(result)
            yield StageCompleted(stage.__name__, result)

        return ResearchResult(
            draft=context["final_draft"],
            citations=context["verified_citations"],
            metrics=context["metrics"]
        )

    async def _stage_research(self, context: dict) -> dict:
        # Run web search, gather sources
        prompt = f"""
        Research: {context["topic"]}

        1. Search for 5-7 high-quality sources
        2. Save sources to /workspace/sources/
        3. Return summary of findings
        """
        result = await self.agent.run(prompt)
        return {"sources": result.sources, "summary": result.output}

    # ... other stages
```

**Deliverable**: Vibewriter agent with 8-stage pipeline on Jazzhands

#### Week 10: Frontend Integration

```typescript
// frontend_vibewriter/src/hooks/useVibewriter.ts

export function useVibewriter() {
  const [stages, setStages] = useState<Stage[]>([])
  const [draft, setDraft] = useState<string | null>(null)

  async function startResearch(topic: string) {
    const eventStream = api.vibewriter.start({ topic })

    for await (const event of eventStream) {
      if (event.type === "stage_started") {
        setStages(prev => [...prev, {
          name: event.stage,
          status: "in_progress",
          startTime: Date.now()
        }])
      } else if (event.type === "stage_completed") {
        setStages(prev => prev.map(s =>
          s.name === event.stage
            ? { ...s, status: "complete", duration: event.duration }
            : s
        ))
      } else if (event.type === "draft_updated") {
        setDraft(event.content)
      }
    }
  }

  return { startResearch, stages, draft }
}
```

```typescript
// frontend_vibewriter/src/pages/VibewriterPage.tsx

export function VibewriterPage() {
  const { startResearch, stages, draft } = useVibewriter()
  const [topic, setTopic] = useState("")

  return (
    <div className="vibewriter-page">
      <EconomicHeader />

      <ResearchInput
        value={topic}
        onChange={setTopic}
        onSubmit={() => startResearch(topic)}
      />

      {stages.length > 0 && (
        <ResearchProgress stages={stages} />
      )}

      {draft && (
        <DraftPreview
          content={draft}
          onPublish={handlePublish}
        />
      )}

      <MyResearch />
    </div>
  )
}
```

**Deliverable**: Fully integrated Vibewriter frontend

#### Week 11: End-to-End Testing

**Test Scenarios**:

1. **New User Flow**
   ```
   User signs up with passkey
   → Receives 500 free compute credits
   → Receives 50 starter CHIP
   → Runs first Vibewriter session
   → Publishes first article
   → Receives novelty reward
   → Gets cited by another user
   → Earns first USDC
   → Withdraws to bank account
   ```

2. **Multi-User Isolation**
   ```
   User A starts research session
   User B starts research session
   → Verify separate runtimes
   → Verify workspace isolation
   → Verify no cross-contamination
   ```

3. **Citation Economics**
   ```
   User publishes high-novelty article (score 85)
   → Earns 500 CHIP
   → Article gets cited 10 times
   → Earns $50 USDC
   → Withdraws successfully
   → Verify Treasury balance updates
   ```

4. **Semantic Novelty**
   ```
   User publishes "Bitcoin basics" (score 5 - common knowledge)
   → Rejected (too low novelty)

   User publishes "Bitcoin quantum resistance analysis" (score 75)
   → Accepted, earns 200 CHIP

   User publishes duplicate article
   → Rejected (score 8 - too similar)
   ```

**Deliverable**: Comprehensive test suite passing

#### Week 12: Performance Optimization

**Optimizations**:

1. **Runtime Pooling**
   ```python
   # Pre-warm runtimes for faster session starts
   runtime_pool = RuntimePool(min_size=5, max_size=50)
   await runtime_pool.prewarm()
   ```

2. **Embedding Caching**
   ```python
   # Cache embeddings to avoid re-computing
   @cache(ttl=3600)
   async def get_embedding(text: str) -> Vector:
       return await openai.embed(text)
   ```

3. **Database Indexing**
   ```sql
   CREATE INDEX idx_articles_author ON articles(author_id);
   CREATE INDEX idx_citations_article ON citations(article_id);
   CREATE INDEX idx_articles_published ON articles(published_at DESC);
   ```

4. **Frontend Code Splitting**
   ```typescript
   // Lazy load heavy components
   const PublishModal = lazy(() => import("./PublishModal"))
   const DraftEditor = lazy(() => import("./DraftEditor"))
   ```

**Deliverable**: System performs well under load (50+ concurrent users)

---

## VI. Phase 4: Launch & Migration (Weeks 13-16)

### Goals
- Deploy Jazzhands to production
- Migrate existing users
- Deprecate Stellar scaffold
- Monitor and iterate

### Tasks

#### Week 13: Production Deployment

```yaml
# infrastructure/docker-compose.prod.yml

version: '3.8'

services:
  choir-controller:
    image: choir/controller:latest
    environment:
      - DATABASE_URL=postgresql://...
      - RUNLOOP_API_KEY=${RUNLOOP_API_KEY}
      - QDRANT_URL=http://qdrant:6333
      - SUI_RPC_URL=https://fullnode.mainnet.sui.io
    depends_on:
      - postgres
      - qdrant
      - redis

  vibewriter-frontend:
    image: choir/vibewriter:latest
    environment:
      - API_URL=https://api.choir.chat
    ports:
      - "443:443"

  postgres:
    image: pgvector/pgvector:latest
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
```

**Deploy to**:
- Primary: AWS ECS (Fargate)
- CDN: CloudFront
- Storage: S3 (encrypted workspaces)
- Database: RDS PostgreSQL with pgvector

**Deliverable**: Jazzhands running in production at https://choir.chat

#### Week 14: User Migration

**Strategy**: Dual-mode operation

```python
# choir_controller/migration/dual_mode.py

class DualModeRouter:
    """
    Route requests to old system or new system
    based on user migration status.
    """

    def __init__(self):
        self.old_api = OldChoirAPI()
        self.new_api = JazzhandsAPI()

    async def route_request(self, user_id: str, request: Request):
        # Check if user has been migrated
        migration_status = await db.get_migration_status(user_id)

        if migration_status == "migrated":
            return await self.new_api.handle(request)
        else:
            return await self.old_api.handle(request)

# Gradual rollout
# Week 14: 10% of users
# Week 15: 50% of users
# Week 16: 100% of users
```

**Migration Checklist per User**:
- [ ] Migrate passkey credentials
- [ ] Migrate chat history
- [ ] Migrate published articles
- [ ] Sync CHIP/USDC balances
- [ ] Test Vibewriter session
- [ ] Confirm economics working

**Deliverable**: All users migrated to Jazzhands

#### Week 15: Deprecate Stellar Scaffold

```bash
# Mark old system as deprecated
git tag -a v1.0.0-deprecated -m "Stellar scaffold deprecated, use Jazzhands"

# Update documentation
echo "This codebase is deprecated. See docs/JAZZHANDS_MIGRATION.md" > README.md

# Archive repository
gh repo archive yusefmosiah/tuxedo

# Redirect traffic
# AWS Route53: choir.chat → new infrastructure
```

**Deliverable**: Old system shut down, all traffic on Jazzhands

#### Week 16: Monitor & Iterate

**Metrics to Watch**:
- Runtime spawn time (target: <5s)
- Research session success rate (target: >95%)
- Citation reward accuracy (target: 100%)
- Novelty scoring consistency (manual review sample)
- User satisfaction (surveys, support tickets)

**Known Issues to Address**:
- Runtime cold start latency → Runtime pooling
- Embedding API rate limits → Batch processing
- Database connection pooling → PgBouncer
- Frontend loading times → Code splitting

**Deliverable**: Stable production system with <1% error rate

---

## VII. Parallel Tracks: What Stays in Current System

### Keep Running (Don't Migrate Yet)

Some components can stay in the current system and be migrated later:

1. **Passkey Auth Service** - Already production-ready, just integrate with Jazzhands
2. **Chat History Storage** - Migrate lazily (only when user logs in to new system)
3. **Stellar DeFi Tools** - Keep as legacy, eventually deprecate
4. **Basic Chat Agent** - Keep for users who don't need Vibewriter

**Why**: Focus migration effort on core value prop (Vibewriter + citation economics)

---

## VIII. Risk Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenHands API breaking changes | High | Medium | Pin to stable version, maintain fork |
| Runtime provider outages (RunLoop) | High | Low | Support multiple providers (E2B fallback) |
| Semantic novelty gaming | Medium | Medium | Manual review queue, anti-spam rules |
| Database scalability | Medium | Low | Use PostgreSQL with proper indexing |
| Frontend performance | Low | Medium | Code splitting, lazy loading |

### Economic Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| CHIP price crash | High | Medium | Treasury diversification, stablecoin reserves |
| Citation reward insolvency | High | Low | Dynamic pricing, conservative LTV |
| Novelty score manipulation | Medium | Medium | Manual review, reputation system |
| User confusion (3 currencies) | Medium | High | Clear UX, generous free tier |

### Legal Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MIT license violation | High | Low | Clean room development, legal review |
| Proprietary code contamination | High | Very Low | Deleted enterprise/ immediately |
| User data breach | High | Low | Encryption at rest, TEE in future |

---

## IX. Success Criteria

### Technical Metrics

- ✅ Vibewriter produces 95%+ citation-verified research
- ✅ Runtime isolation tested (1000+ concurrent users)
- ✅ Semantic novelty scoring <5% false positives
- ✅ System uptime >99.9%

### Economic Metrics

- ✅ Users earn $50-500/month from citations (active researchers)
- ✅ Treasury successfully funds citation rewards via CHIP collateral
- ✅ Dynamic pricing maintains stable $5/citation rate
- ✅ Novelty rewards accurately reflect intellectual contribution

### User Metrics

- ✅ 90%+ of users complete first research session
- ✅ 70%+ publish at least one article
- ✅ 50%+ earn first citation reward
- ✅ 20%+ become weekly active users
- ✅ Net Promoter Score >50

---

## X. Decision Points

### Week 4: Continue or Pivot?

**Evaluate**:
- Is remote runtime integration working?
- Can we secure RunLoop partnership?
- Is economic database schema correct?

**If No**: Consider alternative architectures (local runtimes with better isolation)

### Week 8: Economics Working?

**Evaluate**:
- Does semantic novelty scoring make sense?
- Is citation reward calculation sustainable?
- Do users understand the three-currency model?

**If No**: Simplify economics (maybe only USDC + compute credits, drop CHIP temporarily)

### Week 12: Ready for Production?

**Evaluate**:
- Are all test scenarios passing?
- Is performance acceptable?
- Is the UX intuitive?

**If No**: Delay launch, continue iteration (don't rush broken product)

---

## XI. Post-Launch Roadmap

### Months 4-6: Optimization

- Semantic similarity improvements (better embeddings, hybrid search)
- TEE deployment for encrypted workspaces (Phala Network)
- Mobile app (iOS, Android)
- Advanced citation detection (automatic back-citation)

### Months 7-12: Scaling

- Multi-chain support (migrate from Sui to Base for lower costs)
- Revision markets (collaborative improvement)
- Treasury investment strategies (yield optimization)
- Governance transition (CHIP holders vote on parameters)

### Year 2+: Ecosystem

- Developer API (third parties can build on Choir citation graph)
- Academic partnerships (universities adopt Vibewriter)
- Enterprise tier (teams, organizations)
- Decentralized governance (DAO transition)

---

## XII. Conclusion: The Path Forward

**Where We Are**: Stellar scaffold with basic Ghostwriter, passkey auth, chat interface

**Where We're Going**: Jazzhands-based Vibewriter with citation economics, semantic novelty, remote runtimes

**How We Get There**: 16-week phased migration with parallel development, gradual cutover, and continuous iteration

**Why This Works**:
1. **Proven Infrastructure**: OpenHands solves hard agent problems (runtime isolation, multi-model orchestration)
2. **Clean Architecture**: Choir Controller provides proprietary economic layer on top of MIT-licensed foundation
3. **Reversible**: Can roll back at any decision point if issues arise
4. **Focused**: Core value prop is research + citation economics, not rebuilding agent infrastructure

**The Risk**: This is a major architectural change (3-4 months of work)
**The Reward**: A defensible, scalable platform for the learning economy

**Next Step**: Get approval and start Week 1 (Fork & Clean Room Setup)

---

**Document Status**: Draft v1.0
**Related**: JAZZHANDS_FORK_STRATEGY.md, JAZZHANDS_ECONOMICS_INTEGRATION.md, JAZZHANDS_FRONTEND_TRANSFORMATION.md
**Decision Required**: Approve migration plan and allocate resources
