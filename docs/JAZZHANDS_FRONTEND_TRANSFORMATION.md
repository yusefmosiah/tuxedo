# Jazzhands Frontend Transformation

**From Developer IDE to Research Workbench**

**Version 1.0 - November 26, 2025**

---

## Executive Summary

This document details the frontend modifications required to transform OpenHands from a developer-focused IDE into **Vibewriter** - a consumer-friendly research and writing interface for Choir.

**The Challenge**: OpenHands looks like VS Code (terminals, file explorers, debuggers). Choir users are researchers and writers, not developers. They shouldn't see code.

**The Solution**: Surgically remove dev tools, add research-focused components, preserve the underlying agent architecture.

**Scope**: Frontend-only changes. The Jazzhands backend (OpenHands SDK, runtime, agent logic) remains largely untouched.

---

## I. Current OpenHands UI (What We're Starting With)

### The Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  OpenHands                                           [Settings ⚙] │
├───────────┬──────────────────────────────────────────────────────┤
│           │                                                       │
│  Chat     │              TERMINAL                                │
│  ───────  │  $ pip install pandas                                │
│           │  Collecting pandas                                   │
│  Agent    │  Successfully installed pandas-2.1.0                 │
│  ───────  │                                                       │
│           │  $ python research.py                                │
│  Files    │  Fetching sources...                                 │
│  ───────  │  ├── source1.pdf                                     │
│  /workspace│  └── source2.pdf                                    │
│  ├── src/ │                                                       │
│  ├── tools│  ── BROWSER ─────────────────────                   │
│  └── output│                                                       │
│           │  <iframe src="http://localhost:8000"/>               │
│  Jupyter  │                                                       │
│  ───────  │                                                       │
│           │  ── CODE EDITOR ─────────────────────                │
│  Browser  │                                                       │
│  ───────  │  1  def research():                                  │
│           │  2      sources = fetch()                            │
│           │  3      return draft()                               │
│           │                                                       │
└───────────┴──────────────────────────────────────────────────────┘
```

**Components Visible**:
- Left Sidebar: Chat, Agent logs, File explorer, Jupyter, Browser tabs
- Main Area: Terminal, Browser iframe, Code editor (tabbed)
- Top Bar: OpenHands branding, Settings gear

**User Persona**: Software engineers building/debugging code with AI assistance

---

## II. Target Vibewriter UI (What We're Building)

### The Transformed Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  🎵 Choir                       [💎 230 CHIP] [$175] [Profile ▼] │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ╔══════════════════════════════════════════════════════════════╗│
│  ║  New Research                                                 ║│
│  ║  ┌─────────────────────────────────────────────────────────┐ ║│
│  ║  │ "Compare DeFi yield opportunities on Base vs Arbitrum"  │ ║│
│  ║  │                                           [Start →]      │ ║│
│  ║  └─────────────────────────────────────────────────────────┘ ║│
│  ╚══════════════════════════════════════════════════════════════╝│
│                                                                   │
│  ⏳ Research in progress... (will cost 50 compute credits)       │
│                                                                   │
│  ┌─ Research Progress ───────────────────────────────────────┐  │
│  │                                                             │  │
│  │  Stage 1: Research  ✓ Complete (8 sources, 23s)           │  │
│  │  Stage 2: Draft     ✓ Complete (1,847 words, 45s)         │  │
│  │  Stage 3: Extract   ✓ Complete (12 claims extracted)      │  │
│  │  Stage 4: Verify    ⏳ In Progress (9/12 verified)          │  │
│  │  Stage 5: Critique  ⏸ Pending                              │  │
│  │  Stage 6: Revise    ⏸ Pending                              │  │
│  │  Stage 7: Re-verify ⏸ Pending                              │  │
│  │  Stage 8: Style     ⏸ Pending                              │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─ Draft Preview ──────────────────────────────────────────┐   │
│  │                                                            │   │
│  │  # DeFi Yield Farming: Base vs Arbitrum                   │   │
│  │                                                            │   │
│  │  ## Executive Summary                                     │   │
│  │                                                            │   │
│  │  Base's Aerodrome protocol offers competitive yields      │   │
│  │  through concentrated liquidity pools, with APYs          │   │
│  │  ranging from 15-45% depending on pair selection.         │   │
│  │  ¹                                                         │   │
│  │                                                            │   │
│  │  Arbitrum's Aave V3 deployment provides more stable       │   │
│  │  but lower returns, typically 8-12% APY on major          │   │
│  │  assets. ²                                                 │   │
│  │                                                            │   │
│  │  ── Citations ────────────────────────────                │   │
│  │  1. Aerodrome Finance Docs (verified ✓)                   │   │
│  │  2. Aave V3 Arbitrum Governance (verified ✓)              │   │
│  │                                                            │   │
│  │  [Continue Editing] [Publish for 100 CHIP →]             │   │
│  │                                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─ My Research ────────────────────────────────────────────┐   │
│  │                                                            │   │
│  │  📄 "DeFi on Stellar vs EVM" (6 months ago)               │   │
│  │     45 citations · $225 earned · 8.2/10 quality           │   │
│  │                                                            │   │
│  │  📄 "Passkey Auth Best Practices" (3 months ago)          │   │
│  │     18 citations · $90 earned · 7.5/10 quality            │   │
│  │                                                            │   │
│  │  📄 "Learning Economy Thesis" (1 month ago)               │   │
│  │     7 citations · $35 earned · 9.1/10 quality             │   │
│  │                                                            │   │
│  │  [View All Research →]                                     │   │
│  │                                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Components Visible**:
- Top Bar: Choir branding, CHIP balance, USDC earnings, Profile menu
- Main Area: Research prompt, Progress tracker, Draft preview (markdown), Earnings dashboard
- No Sidebar: Everything in single-column flow

**User Persona**: Researchers, writers, students producing citation-verified content

---

## III. Component Removal (What We Delete)

### Components to Remove from OpenHands

#### 1. Terminal Component
```typescript
// REMOVE: frontend/src/components/Terminal.tsx
// Why: Users should never see bash output, pip install logs, etc.
```

**Replacement**: Progress indicators with semantic descriptions
```typescript
// NEW: frontend/src/components/ResearchProgress.tsx
<ResearchProgress stages={[
  { name: "Research", status: "complete", duration: 23 },
  { name: "Draft", status: "in_progress", duration: 45 },
  // ...
]} />
```

#### 2. File Explorer
```typescript
// REMOVE: frontend/src/components/FileExplorer.tsx
// Why: Users don't need to see /workspace/src/research_agent.py
```

**Replacement**: Research history list with article titles
```typescript
// NEW: frontend/src/components/MyResearch.tsx
<MyResearch articles={[
  {
    title: "DeFi on Stellar vs EVM",
    citations: 45,
    earnings: 225,
    qualityScore: 8.2
  },
  // ...
]} />
```

#### 3. Code Editor
```typescript
// REMOVE: frontend/src/components/CodeEditor.tsx
// Why: No Python/TypeScript editing for end users
```

**Replacement**: Markdown editor for drafts
```typescript
// NEW: frontend/src/components/DraftEditor.tsx
// Markdown-based, citation-aware, style guide hints
<DraftEditor
  content={draft}
  citations={verifiedCitations}
  onPublish={handlePublish}
/>
```

#### 4. Jupyter Notebook Tab
```typescript
// REMOVE: frontend/src/components/JupyterTab.tsx
// Why: Notebooks are dev tools, not needed for research writing
```

#### 5. Browser Preview (Mostly)
```typescript
// REMOVE: frontend/src/components/BrowserPreview.tsx (as default tab)
// KEEP: As modal for viewing sources
```

**Replacement**: Source viewer modal
```typescript
// NEW: frontend/src/components/SourceViewer.tsx
<SourceViewer source={url} onClose={handleClose} />
```

#### 6. Agent Logs Panel
```typescript
// REMOVE: frontend/src/components/AgentLogs.tsx
// Why: Raw event stream is too technical
```

**Replacement**: Simplified progress tracker (see above)

#### 7. Raw Settings Panel
```typescript
// REMOVE: frontend/src/components/SettingsModal.tsx (LLM selection, runtime config)
// Why: Too many knobs, users shouldn't configure LLM APIs
```

**Replacement**: Simplified profile menu
```typescript
// NEW: frontend/src/components/ProfileMenu.tsx
<ProfileMenu>
  <MenuItem>My Research</MenuItem>
  <MenuItem>Earnings: $175</MenuItem>
  <MenuItem>CHIP Balance: 230</MenuItem>
  <MenuItem>Style Guide Settings</MenuItem>
  <MenuItem>Logout</MenuItem>
</ProfileMenu>
```

---

## IV. Component Addition (What We Build)

### New Components for Vibewriter

#### 1. Economic Header
```typescript
// NEW: frontend/src/components/EconomicHeader.tsx

interface EconomicHeaderProps {
  chipBalance: number
  usdcEarnings: number
  computeCredits: number
}

export function EconomicHeader({ chipBalance, usdcEarnings, computeCredits }: EconomicHeaderProps) {
  return (
    <header className="economic-header">
      <div className="logo">
        🎵 Choir
      </div>

      <div className="balances">
        <Tooltip content="CHIP tokens for publishing and governance">
          <Balance icon="💎" label="CHIP" value={chipBalance} />
        </Tooltip>

        <Tooltip content="Citation earnings (withdrawable)">
          <Balance icon="💰" label="Earned" value={`$${usdcEarnings}`} />
        </Tooltip>

        <Tooltip content="Compute credits for Vibewriter sessions">
          <Balance icon="⚡" label="Credits" value={computeCredits} />
        </Tooltip>
      </div>

      <ProfileMenu />
    </header>
  )
}
```

#### 2. Research Progress Tracker
```typescript
// NEW: frontend/src/components/ResearchProgress.tsx

interface Stage {
  name: string
  status: "pending" | "in_progress" | "complete" | "error"
  duration?: number  // seconds
  details?: string
}

export function ResearchProgress({ stages }: { stages: Stage[] }) {
  return (
    <div className="research-progress">
      <h3>Research Progress</h3>
      {stages.map((stage, i) => (
        <StageRow key={i} stage={stage} />
      ))}
    </div>
  )
}

function StageRow({ stage }: { stage: Stage }) {
  const icon = {
    pending: "⏸",
    in_progress: "⏳",
    complete: "✓",
    error: "✗"
  }[stage.status]

  return (
    <div className={`stage-row stage-${stage.status}`}>
      <span className="icon">{icon}</span>
      <span className="name">{stage.name}</span>
      {stage.duration && (
        <span className="duration">({stage.duration}s)</span>
      )}
      {stage.details && (
        <span className="details">{stage.details}</span>
      )}
    </div>
  )
}
```

#### 3. Draft Preview with Citations
```typescript
// NEW: frontend/src/components/DraftPreview.tsx

interface Citation {
  id: number
  url: string
  title: string
  verified: boolean
}

interface DraftPreviewProps {
  content: string  // Markdown
  citations: Citation[]
  onEdit: () => void
  onPublish: () => void
  publishCostChip: number
}

export function DraftPreview({
  content,
  citations,
  onEdit,
  onPublish,
  publishCostChip
}: DraftPreviewProps) {
  return (
    <div className="draft-preview">
      <div className="draft-header">
        <h3>Draft Preview</h3>
        <WordCount content={content} />
      </div>

      <MarkdownRenderer
        content={content}
        citations={citations}
        onCitationClick={(id) => showCitationDetails(id)}
      />

      <div className="citations-section">
        <h4>Citations</h4>
        {citations.map(cit => (
          <CitationRow key={cit.id} citation={cit} />
        ))}
      </div>

      <div className="actions">
        <Button variant="secondary" onClick={onEdit}>
          Continue Editing
        </Button>
        <Button variant="primary" onClick={onPublish}>
          Publish for {publishCostChip} CHIP →
        </Button>
      </div>
    </div>
  )
}

function CitationRow({ citation }: { citation: Citation }) {
  return (
    <div className="citation-row">
      <span className="citation-number">{citation.id}.</span>
      <a href={citation.url} target="_blank" rel="noopener">
        {citation.title}
      </a>
      {citation.verified ? (
        <span className="verified">✓ verified</span>
      ) : (
        <span className="unverified">⚠ unverified</span>
      )}
    </div>
  )
}
```

#### 4. My Research Dashboard
```typescript
// NEW: frontend/src/components/MyResearch.tsx

interface Article {
  id: string
  title: string
  publishedAt: Date
  citations: number
  earnings: number
  qualityScore: number
}

export function MyResearch({ articles }: { articles: Article[] }) {
  return (
    <div className="my-research">
      <h3>My Research</h3>
      {articles.map(article => (
        <ArticleCard key={article.id} article={article} />
      ))}
      <Link to="/research/all">View All Research →</Link>
    </div>
  )
}

function ArticleCard({ article }: { article: Article }) {
  return (
    <div className="article-card">
      <h4>📄 {article.title}</h4>
      <div className="article-meta">
        <span>{article.citations} citations</span>
        <span>${article.earnings} earned</span>
        <span>{article.qualityScore}/10 quality</span>
      </div>
      <span className="publish-date">
        {formatDistanceToNow(article.publishedAt)} ago
      </span>
    </div>
  )
}
```

#### 5. Publishing Workflow Modal
```typescript
// NEW: frontend/src/components/PublishModal.tsx

interface PublishModalProps {
  article: Article
  noveltyScore: number
  chipReward: number
  onConfirm: () => void
  onCancel: () => void
}

export function PublishModal({
  article,
  noveltyScore,
  chipReward,
  onConfirm,
  onCancel
}: PublishModalProps) {
  const netChip = chipReward - 100  // Stake 100, earn reward

  return (
    <Modal>
      <h2>Publish Article</h2>

      <div className="novelty-score">
        <h3>Novelty Score: {noveltyScore}/100</h3>
        <NoveltyMeter score={noveltyScore} />
        <p className="novelty-explanation">
          {getNoveltyExplanation(noveltyScore)}
        </p>
      </div>

      <div className="chip-economics">
        <h3>CHIP Economics</h3>
        <EconomicsRow label="Stake to Publish" value="-100 CHIP" />
        <EconomicsRow label="Novelty Reward" value={`+${chipReward} CHIP`} />
        <Divider />
        <EconomicsRow label="Net Change" value={`${netChip > 0 ? '+' : ''}${netChip} CHIP`} bold />
      </div>

      <div className="actions">
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button variant="primary" onClick={onConfirm}>
          Confirm & Publish
        </Button>
      </div>
    </Modal>
  )
}

function getNoveltyExplanation(score: number): string {
  if (score < 20) return "Too similar to existing articles"
  if (score < 50) return "Incremental improvement on existing work"
  if (score < 70) return "Novel perspective on covered topics"
  return "Significant new contribution to knowledge base"
}
```

#### 6. Compute Credit Autopurchase Flow
```typescript
// NEW: frontend/src/components/AutopurchaseModal.tsx

export function AutopurchaseModal({ onComplete }: { onComplete: () => void }) {
  const [loading, setLoading] = useState(false)

  async function handlePurchase() {
    setLoading(true)
    // Stripe integration
    const session = await api.createCheckoutSession({
      product: "compute_credits",
      quantity: 500,
      priceUsd: 10
    })
    window.location.href = session.url  // Redirect to Stripe
  }

  return (
    <Modal>
      <h2>⚡ Out of Compute Credits</h2>
      <p>You need 50 credits to run this research session.</p>
      <p>Current balance: 0 credits</p>

      <div className="purchase-option">
        <h3>Purchase Credits</h3>
        <div className="pricing">
          <span className="amount">500 compute credits</span>
          <span className="price">$10 USD</span>
        </div>
        <Button onClick={handlePurchase} loading={loading}>
          Purchase via Stripe →
        </Button>
      </div>

      <div className="earn-option">
        <h3>Or Earn Credits</h3>
        <p>Earn 100 free credits for every $10 in citation rewards</p>
        <Link to="/research">View My Articles →</Link>
      </div>
    </Modal>
  )
}
```

---

## V. Layout & Navigation Changes

### Before (OpenHands): Left Sidebar + Tabs

```
┌─────────┬──────────────────────────────────────┐
│ Chat    │  [Terminal] [Browser] [Code] [Planner]│
│         │                                       │
│ Agent   │  $ pip install ...                   │
│         │  Successfully installed ...          │
│ Files   │                                       │
│ ├─ src/ │                                       │
│         │                                       │
│ Jupyter │                                       │
│         │                                       │
└─────────┴──────────────────────────────────────┘
```

**Problems**:
- Sidebar is developer-focused (files, Jupyter)
- Tabs expose raw agent internals
- No economic context visible

### After (Vibewriter): Single Column + Context Header

```
┌────────────────────────────────────────────────┐
│ 🎵 Choir    [💎 CHIP] [$] [Profile]            │
├────────────────────────────────────────────────┤
│                                                │
│  [Research Input]                              │
│                                                │
│  [Progress Tracker]                            │
│                                                │
│  [Draft Preview]                               │
│                                                │
│  [My Research]                                 │
│                                                │
└────────────────────────────────────────────────┘
```

**Benefits**:
- Focused: No distracting sidebars
- Economic: Balances visible at all times
- Contextual: Everything related to current research task
- Progressive: Scroll down to see more (mobile-friendly)

### Navigation Philosophy

**OpenHands**: Tab-based (switch between Terminal, Browser, Code, etc.)
**Vibewriter**: Section-based (scroll through Research → Progress → Draft → History)

```typescript
// REMOVE: Tab-based navigation
<Tabs>
  <Tab name="terminal" />
  <Tab name="browser" />
  <Tab name="code" />
</Tabs>

// ADD: Section-based scrolling
<main className="vibewriter-layout">
  <section id="research-input">...</section>
  <section id="progress">...</section>
  <section id="draft">...</section>
  <section id="history">...</section>
</main>
```

---

## VI. Event Stream Sanitization

### The Challenge

OpenHands streams raw agent events to the frontend:
```json
{
  "type": "CmdRunAction",
  "command": "pip install pandas",
  "thought": "I need to install pandas to process the data"
}
```

Users shouldn't see this. They should see:
```
"Installing research tools..."
```

### The Solution: Event Translator

```typescript
// NEW: frontend/src/utils/eventTranslator.ts

export function translateEvent(event: AgentEvent): UserFriendlyMessage {
  switch (event.type) {
    case "CmdRunAction":
      return translateCommand(event.command)

    case "FileWriteAction":
      return {
        message: "Saving research draft...",
        icon: "💾"
      }

    case "BrowseAction":
      return {
        message: `Reading source: ${getDomain(event.url)}`,
        icon: "🔍"
      }

    case "MessageAction":
      // LLM thinking
      return {
        message: extractUserFriendlyThought(event.content),
        icon: "💭"
      }

    default:
      return null  // Hide unknown events
  }
}

function translateCommand(cmd: string): UserFriendlyMessage {
  if (cmd.includes("pip install")) {
    return { message: "Installing research tools...", icon: "📦" }
  }
  if (cmd.includes("python")) {
    const scriptName = extractScriptName(cmd)
    return { message: `Running ${scriptName}...`, icon: "🔬" }
  }
  // Don't show raw commands
  return null
}

function extractUserFriendlyThought(content: string): string {
  // Extract only high-level intent from LLM thoughts
  // "I'm going to search for sources on DeFi..."
  // → "Searching for sources..."

  const patterns = [
    { regex: /searching for (.*)/i, template: "Searching for {0}" },
    { regex: /drafting (.*)/i, template: "Drafting {0}" },
    { regex: /verifying (.*)/i, template: "Verifying {0}" },
  ]

  for (const { regex, template } of patterns) {
    const match = content.match(regex)
    if (match) {
      return template.replace("{0}", match[1])
    }
  }

  // Fallback: generic message
  return "Processing..."
}
```

**Result**: Users see semantic progress ("Researching sources", "Verifying citations") instead of technical commands.

---

## VII. Styling & Branding

### Design System

**Remove**: OpenHands dark theme, developer aesthetics
**Add**: Choir luxury minimalism

```scss
// NEW: frontend/src/styles/choir-theme.scss

:root {
  /* Choir Brand Colors */
  --choir-gold: #D4AF37;
  --choir-black: #0A0A0A;
  --choir-white: #FAFAFA;
  --choir-gray: #2A2A2A;

  /* Semantic Colors */
  --color-success: #00D4AA;  // Verified citations
  --color-warning: #FFB800;  // Pending verification
  --color-error: #FF4444;    // Failed verification
  --color-info: #4A90E2;     // Informational

  /* Typography */
  --font-primary: "Inter", -apple-system, sans-serif;
  --font-serif: "Merriweather", Georgia, serif;  // For article text
  --font-mono: "JetBrains Mono", monospace;      // For rare code snippets

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2.5rem;
  --space-xl: 4rem;
}

/* Remove: OpenHands terminal aesthetic */
/* Add: Elegant research workbench */

body {
  background: var(--choir-white);
  color: var(--choir-black);
  font-family: var(--font-primary);
}

/* Luxury card style for major components */
.card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: var(--space-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Progress indicator: clean and minimal */
.research-progress {
  .stage-row {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-xs);

    &.stage-complete {
      color: var(--color-success);
    }

    &.stage-in_progress {
      color: var(--color-info);
      animation: pulse 2s ease-in-out infinite;
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Draft preview: focus on readability */
.draft-preview {
  font-family: var(--font-serif);
  font-size: 1.125rem;
  line-height: 1.7;
  max-width: 680px;  // Optimal reading width
  margin: 0 auto;

  h1, h2, h3 {
    font-family: var(--font-primary);
    font-weight: 600;
  }

  sup {
    color: var(--choir-gold);  // Citation superscripts in gold
  }
}

/* Economic header: always visible context */
.economic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.balance {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-variant-numeric: tabular-nums;  // Monospaced numbers

  .icon {
    font-size: 1.25rem;
  }

  .value {
    font-weight: 600;
  }
}
```

---

## VIII. Mobile Considerations

### OpenHands: Desktop Only

OpenHands assumes large screens (terminal, multi-pane layout).

### Vibewriter: Mobile First

Research and writing happen on phones and tablets.

```typescript
// NEW: frontend/src/components/ResponsiveLayout.tsx

export function ResponsiveLayout({ children }: { children: ReactNode }) {
  const isMobile = useMediaQuery("(max-width: 768px)")

  return (
    <div className={`layout ${isMobile ? "mobile" : "desktop"}`}>
      {isMobile ? (
        <MobileLayout>{children}</MobileLayout>
      ) : (
        <DesktopLayout>{children}</DesktopLayout>
      )}
    </div>
  )
}

function MobileLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <MobileHeader />
      <main className="mobile-main">
        {children}
      </main>
      <MobileBottomNav />  {/* Tab bar: Research | My Work | Profile */}
    </>
  )
}

function DesktopLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <EconomicHeader />
      <main className="desktop-main">
        {children}
      </main>
    </>
  )
}
```

**Mobile Optimizations**:
- Collapsible progress tracker (tap to expand)
- Swipe gestures for navigation
- Bottom tab bar (familiar iOS/Android pattern)
- Reduced whitespace, larger touch targets
- Inline editing (no separate editor modal)

---

## IX. Implementation Plan

### Phase 1: Core Component Removal (Week 1)

```bash
# Delete unnecessary components
rm -rf frontend/src/components/Terminal.tsx
rm -rf frontend/src/components/FileExplorer.tsx
rm -rf frontend/src/components/CodeEditor.tsx
rm -rf frontend/src/components/JupyterTab.tsx
rm -rf frontend/src/components/AgentLogs.tsx

# Update main layout
# frontend/src/App.tsx
# Remove tabs, add single-column layout
```

### Phase 2: Add Research Components (Week 2)

```bash
# Create new components
frontend/src/components/vibewriter/
├── EconomicHeader.tsx
├── ResearchProgress.tsx
├── DraftPreview.tsx
├── MyResearch.tsx
├── PublishModal.tsx
└── AutopurchaseModal.tsx

# Add to layout
# frontend/src/pages/VibewriterPage.tsx
```

### Phase 3: Event Stream Translation (Week 3)

```bash
# Add event translator
frontend/src/utils/eventTranslator.ts

# Update event listener
# frontend/src/hooks/useAgentEvents.ts
# - Translate raw events before displaying
# - Filter out low-level technical events
```

### Phase 4: Styling & Branding (Week 4)

```bash
# Add Choir theme
frontend/src/styles/choir-theme.scss

# Update all components to use theme
# Remove OpenHands branding
# Add Choir logo, colors, fonts
```

### Phase 5: Mobile Optimization (Week 5)

```bash
# Add responsive layouts
frontend/src/components/ResponsiveLayout.tsx
frontend/src/components/MobileBottomNav.tsx

# Test on iOS/Android
# Adjust touch targets, gestures
```

---

## X. Migration Checklist

### Must Remove
- [ ] Terminal component and all terminal output
- [ ] File explorer (show research history instead)
- [ ] Code editor (show markdown editor instead)
- [ ] Jupyter notebook tab
- [ ] Raw agent logs
- [ ] Settings panel (LLM selection, runtime config)
- [ ] OpenHands branding and logos

### Must Add
- [ ] Economic header (CHIP, USDC, compute credits)
- [ ] Research progress tracker (8-stage pipeline)
- [ ] Draft preview with citation verification
- [ ] Markdown editor for drafts
- [ ] Publishing workflow (stake CHIP, novelty score)
- [ ] My Research dashboard (earnings, citations)
- [ ] Autopurchase flow for compute credits
- [ ] Event stream translator (hide technical details)
- [ ] Choir branding and design system
- [ ] Mobile-responsive layout

### Must Modify
- [ ] Main layout: Tabs → Single column
- [ ] Navigation: Left sidebar → Top header
- [ ] Agent event handling: Raw events → User-friendly messages
- [ ] Settings: Complex configs → Simple profile menu
- [ ] Color scheme: Dark dev theme → Light luxury theme

---

## XI. Success Criteria

**Technical Success**:
- ✅ No terminal output visible to users
- ✅ No file paths or code snippets exposed
- ✅ Event stream translated to semantic progress
- ✅ Mobile-responsive (works on iPhone, Android)

**UX Success**:
- ✅ Users understand what Vibewriter is doing at each stage
- ✅ Economic context always visible (balances, costs)
- ✅ Publishing workflow feels simple (not blockchain-complicated)
- ✅ Draft preview looks like a real article (not a code file)

**Business Success**:
- ✅ Users never realize they're using a "coding agent"
- ✅ Vibewriter feels like "smart research assistant" not "developer tool"
- ✅ Onboarding friction is low (no need to understand Git, Docker, etc.)
- ✅ Users focus on writing quality, not technical details

---

## XII. Conclusion: From IDE to Workbench

**What We're Doing**:
Transforming OpenHands from a developer IDE into a consumer research workbench.

**What We're Preserving**:
The powerful agent infrastructure (runtime isolation, event streaming, multi-model orchestration).

**What We're Hiding**:
All technical implementation details (code, terminals, file systems).

**What We're Showing**:
High-level research progress, economic context, and beautiful draft previews.

**The Result**:
Users get the computational power of a coding agent applied to research and writing, without having to think about code. They see progress bars, not Python. They see citation verification, not HTTP requests. They see earnings, not transaction hashes.

**Vibewriter feels like magic. Jazzhands makes it possible.**

---

**Document Status**: Draft v1.0
**Related**: JAZZHANDS_FORK_STRATEGY.md, JAZZHANDS_ECONOMICS_INTEGRATION.md
**Next**: JAZZHANDS_IMPLEMENTATION_ROADMAP.md (phased migration plan)
