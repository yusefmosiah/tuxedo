# Jazzhands 3-Day Sprint

**Fork OpenHands. Add Vibewriter. Ship Citation Economics.**

**Version 1.0 - November 26, 2025**

---

## Philosophy

- **Keep OpenHands UI as-is** - Terminal, code editor, file explorer stay. Users see the coding agent work.
- **Add Vibewriter tools** - 8-stage research pipeline as OpenHands tools
- **Layer on economics** - CHIP, USDC, citations on top of existing architecture
- **Polish later** - Day 3 UX improvements, not a rewrite

**Timeline**: 3 days (you + coding agents)

---

## Day 1: Fork + Remote Runtime + Vibewriter Tools

### Hour 1-2: Fork and Clean

```bash
# Fork OpenHands
git clone https://github.com/All-Hands-AI/OpenHands.git jazzhands
cd jazzhands

# Delete proprietary code
rm -rf enterprise/
git commit -m "Remove proprietary enterprise code"

# Add Choir directories
mkdir -p choir/{tools,economics,auth}

# Update branding
sed -i 's/OpenHands/Jazzhands/g' frontend/src/**/*.tsx
sed -i 's/OpenHands/Jazzhands/g' README.md

git remote add origin git@github.com:yusefmosiah/jazzhands.git
git push -u origin main
```

### Hour 3-4: Remote Runtime Integration

```python
# choir/runtime/runloop.py

from openhands.runtime.impl.remote import RemoteRuntime

class ChoirRuntime(RemoteRuntime):
    """
    Extended RemoteRuntime with:
    - User-specific workspace mounting
    - Cost tracking
    - Suspend/resume support
    """

    def __init__(self, user_id: str):
        super().__init__(
            api_url=settings.RUNLOOP_API_URL,
            api_headers={
                "Authorization": f"Bearer {settings.RUNLOOP_API_KEY}",
                "X-User-ID": user_id
            },
            workspace_url=f"s3://choir-workspaces/{user_id}/"
        )
        self.user_id = user_id
        self.start_time = None

    async def connect(self):
        self.start_time = time.time()
        await super().connect()

    async def get_cost(self) -> float:
        """Return compute cost so far (in credits)"""
        if not self.start_time:
            return 0
        duration_minutes = (time.time() - self.start_time) / 60
        return duration_minutes * CREDITS_PER_MINUTE
```

**Test**: Spawn a runtime, run a command, verify isolation

```python
# test_runtime.py
runtime = ChoirRuntime(user_id="test_user")
await runtime.connect()
result = await runtime.run("echo 'Hello from Jazzhands'")
assert "Hello from Jazzhands" in result
print(f"Cost: {await runtime.get_cost()} credits")
```

### Hour 5-8: Vibewriter Pipeline as Tools

```python
# choir/tools/vibewriter.py

from openhands.core.tool import Tool

class ResearchTool(Tool):
    """Stage 1: Web research and source gathering"""

    name = "research_topic"
    description = "Research a topic using web search and Choir knowledge base"

    async def run(self, topic: str, num_sources: int = 5) -> dict:
        # 1. Search Choir knowledge base (vector search)
        choir_articles = await search_choir_kb(topic, limit=3)

        # 2. Web search via Tavily
        web_sources = await tavily.search(topic, num_results=num_sources)

        # 3. Save to workspace
        await self.runtime.run(f"mkdir -p /workspace/sources/")
        for i, source in enumerate(web_sources):
            await self.runtime.run(
                f"curl -o /workspace/sources/source_{i}.html {source.url}"
            )

        return {
            "choir_articles": choir_articles,
            "web_sources": web_sources,
            "workspace": "/workspace/sources/"
        }


class DraftTool(Tool):
    """Stage 2: Draft article from research"""

    name = "draft_article"
    description = "Draft an article from research sources"

    async def run(self, sources_dir: str, style: str = "technical") -> dict:
        # Load style guide
        style_guide = await load_style_guide(style)

        # Read sources
        sources_content = await self.runtime.run(
            f"cat {sources_dir}/*.html | html2text"
        )

        # Draft with Claude
        draft = await claude.complete(
            model="claude-sonnet-4",
            prompt=f"""
            Style Guide: {style_guide}

            Sources: {sources_content}

            Write a comprehensive article synthesizing these sources.
            Include citations as [1], [2], etc.
            """
        )

        # Save draft
        await self.runtime.run(
            f"cat > /workspace/draft.md <<'EOF'\n{draft}\nEOF"
        )

        return {
            "draft": draft,
            "word_count": len(draft.split()),
            "path": "/workspace/draft.md"
        }


class VerifyTool(Tool):
    """Stage 3: Verify citations"""

    name = "verify_citations"
    description = "Verify all citations in draft are accurate"

    async def run(self, draft_path: str) -> dict:
        # Extract citations
        citations = await extract_citations(draft_path)

        # Verify each
        results = []
        for citation in citations:
            # Check URL is valid
            valid_url = await check_url(citation.url)

            # Fetch content and verify claim
            if valid_url:
                content = await fetch_url(citation.url)
                claim_supported = await claude.complete(
                    model="claude-sonnet-4",
                    prompt=f"""
                    Claim: {citation.claim}
                    Source Content: {content}

                    Is the claim supported by the source? Yes/No and explain.
                    """
                )
                results.append({
                    "citation": citation,
                    "url_valid": True,
                    "claim_supported": "Yes" in claim_supported
                })
            else:
                results.append({
                    "citation": citation,
                    "url_valid": False,
                    "claim_supported": False
                })

        verified_count = sum(1 for r in results if r["url_valid"] and r["claim_supported"])

        return {
            "total_citations": len(citations),
            "verified": verified_count,
            "results": results
        }

# Register tools with OpenHands
VIBEWRITER_TOOLS = [
    ResearchTool(),
    DraftTool(),
    VerifyTool(),
    # ... Add other 5 stages
]
```

**Integration with OpenHands**:

```python
# choir/agent.py

from openhands.agent import Agent
from choir.tools.vibewriter import VIBEWRITER_TOOLS

class ChoirAgent(Agent):
    """OpenHands agent with Vibewriter tools"""

    def __init__(self, runtime, user_id: str):
        super().__init__(
            llm="anthropic/claude-sonnet-4",
            runtime=runtime
        )
        self.user_id = user_id

        # Add Vibewriter tools
        for tool in VIBEWRITER_TOOLS:
            self.register_tool(tool)
```

**Test**: Run full Vibewriter pipeline

```python
# test_vibewriter.py
agent = ChoirAgent(runtime, user_id="test")
result = await agent.run("""
Research DeFi yield farming on Base vs Arbitrum.
Use the research_topic tool, then draft_article, then verify_citations.
""")
# Should produce verified draft in /workspace/draft.md
```

**End of Day 1 Deliverable**: Fork works, remote runtime spawns, Vibewriter tools produce verified drafts

---

## Day 2: Crypto Economic Integrations

### Hour 1-3: Database Schema + CHIP/USDC Tracking

```sql
-- choir/migrations/001_economics.sql

CREATE TABLE users (
    id TEXT PRIMARY KEY,
    sui_address TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE balances (
    user_id TEXT PRIMARY KEY REFERENCES users(id),
    compute_credits INTEGER DEFAULT 500,  -- Free tier
    chip_balance INTEGER DEFAULT 50,      -- Starter CHIP
    usdc_balance DECIMAL(18,6) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    author_id TEXT REFERENCES users(id),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    novelty_score INTEGER,
    chip_staked INTEGER,
    chip_rewarded INTEGER,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(1536)  -- OpenAI embedding
);

CREATE TABLE citations (
    id TEXT PRIMARY KEY,
    article_id TEXT REFERENCES articles(id),
    citing_user_id TEXT REFERENCES users(id),
    reward_usdc DECIMAL(18,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```python
# choir/economics/balance_manager.py

class BalanceManager:
    def __init__(self, db: Database):
        self.db = db

    async def get_balances(self, user_id: str) -> dict:
        result = await self.db.fetchrow(
            "SELECT * FROM balances WHERE user_id = $1",
            user_id
        )
        return {
            "compute": result["compute_credits"],
            "chip": result["chip_balance"],
            "usdc": float(result["usdc_balance"])
        }

    async def debit_compute(self, user_id: str, amount: int):
        await self.db.execute(
            "UPDATE balances SET compute_credits = compute_credits - $1 WHERE user_id = $2",
            amount, user_id
        )

    async def credit_chip(self, user_id: str, amount: int, reason: str):
        await self.db.execute(
            "UPDATE balances SET chip_balance = chip_balance + $1 WHERE user_id = $2",
            amount, user_id
        )
        # Also record on blockchain (async task)
        await self.sui_mint_chip(user_id, amount)
```

### Hour 4-6: Semantic Novelty Scoring

```python
# choir/economics/novelty.py

import openai
from qdrant_client import QdrantClient

class NoveltyEngine:
    def __init__(self):
        self.qdrant = QdrantClient(url=settings.QDRANT_URL)
        self.collection = "choir_articles"

    async def score(self, article: str) -> int:
        # 1. Embed
        embedding = await self.embed(article)

        # 2. Search
        results = self.qdrant.search(
            collection_name=self.collection,
            query_vector=embedding,
            limit=10
        )

        if not results:
            return 100  # First article

        # 3. Calculate distance
        max_similarity = max(r.score for r in results)
        distance = 1 - max_similarity

        # 4. Score
        if distance < 0.1:
            return 0  # Too similar
        elif distance < 0.3:
            return int(distance * 100)  # 0-30
        elif distance < 0.5:
            return int(30 + (distance - 0.3) * 200)  # 30-70
        else:
            return int(70 + (distance - 0.5) * 600)  # 70-100

    async def embed(self, text: str) -> list:
        response = await openai.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding
```

### Hour 7-8: Publishing + Citation System

```python
# choir/economics/publishing.py

class PublishingService:
    def __init__(self, db, novelty, balance_mgr):
        self.db = db
        self.novelty = novelty
        self.balance = balance_mgr

    async def publish(self, user_id: str, title: str, content: str) -> dict:
        # 1. Check CHIP balance
        balances = await self.balance.get_balances(user_id)
        if balances["chip"] < 100:
            raise InsufficientChipError()

        # 2. Calculate novelty
        score = await self.novelty.score(content)
        if score < 20:
            raise NoveltyTooLowError(f"Score: {score}")

        # 3. Calculate reward
        reward = self.calculate_reward(score)

        # 4. Debit stake, credit reward
        await self.balance.debit_chip(user_id, 100, "stake")
        await self.balance.credit_chip(user_id, reward, "novelty")

        # 5. Save article
        article_id = await self.db.execute("""
            INSERT INTO articles (id, author_id, title, content, novelty_score, chip_staked, chip_rewarded)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, uuid4(), user_id, title, content, score, 100, reward)

        # 6. Add to vector DB
        embedding = await self.novelty.embed(content)
        self.novelty.qdrant.upsert(
            collection_name="choir_articles",
            points=[{"id": article_id, "vector": embedding}]
        )

        return {
            "article_id": article_id,
            "novelty_score": score,
            "chip_staked": 100,
            "chip_rewarded": reward,
            "net_chip": reward - 100
        }

    def calculate_reward(self, score: int) -> int:
        if score < 50:
            return int(score)
        elif score < 80:
            return int(50 + (score - 50) * 5)
        else:
            return int(200 + (score - 80) * 20)


class CitationService:
    def __init__(self, db, balance_mgr):
        self.db = db
        self.balance = balance_mgr

    async def record_citation(self, article_id: str, citing_user_id: str):
        # 1. Get article author
        article = await self.db.fetchrow(
            "SELECT author_id FROM articles WHERE id = $1",
            article_id
        )

        # 2. Calculate rate (fixed $5 for MVP)
        rate = 5.0

        # 3. Credit author
        await self.balance.credit_usdc(article["author_id"], rate)

        # 4. Record citation
        await self.db.execute("""
            INSERT INTO citations (id, article_id, citing_user_id, reward_usdc)
            VALUES ($1, $2, $3, $4)
        """, uuid4(), article_id, citing_user_id, rate)

        return rate
```

**Integration with Vibewriter**:

```python
# choir/tools/vibewriter.py (add this)

class CiteTool(Tool):
    """Tool for agents to cite Choir articles"""

    name = "cite_choir_article"
    description = "Cite an article from Choir knowledge base"

    async def run(self, article_id: str, context: str) -> dict:
        # Record citation (pays author)
        reward = await citation_service.record_citation(
            article_id=article_id,
            citing_user_id=self.user_id
        )

        # Get article details
        article = await db.get_article(article_id)

        return {
            "article_title": article.title,
            "author_rewarded": reward,
            "citation_text": f"[{article.title}]({article_id})"
        }
```

**End of Day 2 Deliverable**: Economics work - publishing earns CHIP, citations pay USDC

---

## Day 3: UX Improvements

### Hour 1-2: Economic Header

```typescript
// frontend/src/components/ChoirHeader.tsx

import { useQuery } from '@tanstack/react-query'

export function ChoirHeader() {
  const { data: balances } = useQuery({
    queryKey: ['balances'],
    queryFn: () => api.getBalances(),
    refetchInterval: 5000  // Poll every 5s
  })

  if (!balances) return null

  return (
    <div className="choir-header">
      <div className="balances">
        <Balance icon="💎" label="CHIP" value={balances.chip} />
        <Balance icon="💰" label="Earned" value={`$${balances.usdc}`} />
        <Balance icon="⚡" label="Credits" value={balances.compute} />
      </div>
    </div>
  )
}

function Balance({ icon, label, value }) {
  return (
    <div className="balance">
      <span className="icon">{icon}</span>
      <div>
        <div className="label">{label}</div>
        <div className="value">{value}</div>
      </div>
    </div>
  )
}
```

```typescript
// frontend/src/App.tsx (add header)

export function App() {
  return (
    <div>
      <ChoirHeader />  {/* NEW */}
      {/* Keep existing OpenHands UI */}
      <OpenHandsLayout />
    </div>
  )
}
```

### Hour 3-4: Publish Button in Chat

```typescript
// frontend/src/components/ChatInterface.tsx

export function ChatInterface() {
  const [draft, setDraft] = useState<string | null>(null)

  // Watch for draft in workspace
  useEffect(() => {
    const checkForDraft = async () => {
      const content = await api.readFile('/workspace/draft.md')
      if (content) setDraft(content)
    }
    const interval = setInterval(checkForDraft, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      {/* Existing OpenHands chat */}
      <Chat />

      {/* NEW: Publish button when draft exists */}
      {draft && (
        <PublishPrompt
          draft={draft}
          onPublish={handlePublish}
        />
      )}
    </div>
  )
}

function PublishPrompt({ draft, onPublish }) {
  const [loading, setLoading] = useState(false)

  async function publish() {
    setLoading(true)
    try {
      const result = await api.publish({
        title: extractTitle(draft),
        content: draft
      })
      toast.success(`Published! Earned ${result.net_chip} CHIP (novelty: ${result.novelty_score})`)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="publish-prompt">
      <p>✅ Draft ready: <code>/workspace/draft.md</code></p>
      <Button onClick={publish} loading={loading}>
        Publish for 100 CHIP →
      </Button>
    </div>
  )
}
```

### Hour 5-6: My Research Page

```typescript
// frontend/src/pages/ResearchPage.tsx

export function ResearchPage() {
  const { data: articles } = useQuery({
    queryKey: ['my-articles'],
    queryFn: () => api.getMyArticles()
  })

  return (
    <div className="research-page">
      <h1>My Research</h1>

      <div className="stats">
        <Stat label="Articles" value={articles?.length || 0} />
        <Stat label="Total Citations" value={sum(articles, a => a.citations)} />
        <Stat label="Total Earned" value={`$${sum(articles, a => a.earnings)}`} />
      </div>

      <div className="articles">
        {articles?.map(article => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  )
}

function ArticleCard({ article }) {
  return (
    <div className="article-card">
      <h3>{article.title}</h3>
      <div className="meta">
        <span>{article.citations} citations</span>
        <span>${article.earnings} earned</span>
        <span>Novelty: {article.novelty_score}/100</span>
      </div>
      <time>{formatDistanceToNow(article.published_at)} ago</time>
    </div>
  )
}
```

### Hour 7-8: Polish + Testing

- Add loading states
- Error handling for low CHIP balance
- Tooltips explaining CHIP, USDC, compute credits
- Mobile responsiveness (basic)
- End-to-end test: Research → Draft → Publish → Cite → Earn

**End of Day 3 Deliverable**: Usable Choir/Jazzhands with economic UI

---

## API Routes to Add

```python
# choir/api.py

from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/balances")
async def get_balances(user_id: str = Depends(get_user)):
    return await balance_manager.get_balances(user_id)

@app.post("/publish")
async def publish_article(
    title: str,
    content: str,
    user_id: str = Depends(get_user)
):
    return await publishing_service.publish(user_id, title, content)

@app.get("/articles")
async def get_my_articles(user_id: str = Depends(get_user)):
    return await db.fetch("""
        SELECT
            id, title, novelty_score, chip_rewarded,
            (SELECT COUNT(*) FROM citations WHERE article_id = articles.id) as citations,
            (SELECT SUM(reward_usdc) FROM citations WHERE article_id = articles.id) as earnings
        FROM articles
        WHERE author_id = $1
        ORDER BY published_at DESC
    """, user_id)

@app.post("/cite")
async def cite_article(
    article_id: str,
    user_id: str = Depends(get_user)
):
    return await citation_service.record_citation(article_id, user_id)
```

---

## Testing Checklist

### Day 1 Tests
- [ ] Fork builds and runs
- [ ] Remote runtime spawns
- [ ] Vibewriter research tool fetches sources
- [ ] Draft tool generates article
- [ ] Verify tool checks citations

### Day 2 Tests
- [ ] User gets 500 free compute credits
- [ ] Publishing costs 100 CHIP
- [ ] Novelty scoring returns 0-100
- [ ] High novelty (70+) earns >100 CHIP
- [ ] Citation records and pays author

### Day 3 Tests
- [ ] Economic header shows real balances
- [ ] Publish button appears after draft
- [ ] Publishing succeeds and shows reward
- [ ] My Research page shows articles
- [ ] Full flow: Research → Publish → Cite → Earn

---

## Deployment (End of Day 3)

```bash
# Build Docker images
docker build -t choir/jazzhands:latest .

# Deploy to fly.io (or similar)
flyctl launch
flyctl deploy

# Set secrets
flyctl secrets set RUNLOOP_API_KEY=xxx
flyctl secrets set QDRANT_URL=xxx
flyctl secrets set DATABASE_URL=xxx
flyctl secrets set SUI_RPC_URL=xxx
```

---

## What We're NOT Doing (Yet)

- ❌ Removing OpenHands components
- ❌ Hiding terminal/code editor
- ❌ Mobile app
- ❌ Multi-chain (just Sui for CHIP/USDC)
- ❌ TEE deployment
- ❌ Advanced UX polish
- ❌ Marketing site

**Ship fast. Improve later.**

---

## Success Criteria

**Day 1**: Vibewriter produces a verified draft
**Day 2**: Publishing earns CHIP, citing pays USDC
**Day 3**: Users see balances and can publish from UI

**If all three succeed**: We have a working Choir/Jazzhands with citation economics. Polish from there.

---

## Risk Mitigation

**If Day 1 fails** (remote runtime issues):
- Fall back to local Docker runtime
- Security risk, but works for MVP

**If Day 2 fails** (novelty scoring broken):
- Use fixed CHIP rewards (e.g., 150 CHIP per article)
- Add semantic scoring later

**If Day 3 fails** (UX too rough):
- Ship without polish
- Users can use terminal/file explorer to see drafts
- Iterate based on feedback

---

## Post-Sprint Roadmap

**Week 2**: Polish UX, add onboarding, invite first users
**Week 3**: Optimize novelty scoring, tune CHIP rewards
**Week 4**: Add revision markets, improve citation detection
**Month 2+**: Mobile app, TEE, advanced features

---

**This is the plan. 3 days. Let's execute.**

---

**Document Status**: Tactical Sprint Plan v1.0
**Related**: JAZZHANDS_FORK_STRATEGY.md (strategic overview)
**Execute**: Tomorrow, Day 1, Hour 1
