# Jazzhands Frontend: Minimal Changes

**Keep OpenHands UI, Add Economics**

**Version 2.0 - November 26, 2025**

---

## Executive Summary

**The Realization**: We're NOT transforming the OpenHands frontend. We're keeping it as-is and adding economic components on top.

**Why**: Users should see the agent work. The terminal, code editor, and file explorer are features, not bugs. Watching the agent research, write verification scripts, and produce high-quality work is valuable UX.

**What We Add**: Economic header (CHIP/USDC balances), publish button, research dashboard. That's it.

---

## Philosophy Change

**Old Thinking** (WRONG):
- "OpenHands looks like VS Code, too developer-focused"
- "Hide terminal, code editor, file explorer"
- "Surgically remove dev tools, add research UI"
- "Users shouldn't see code"

**New Thinking** (CORRECT):
- "All agents are coding agents - embrace it"
- "Users see the agent work - that's valuable"
- "OpenHands UI is already good - keep it"
- "Just add economics on top"

**Agent Hierarchy**: `pipeline < graph < tool calling loop < terminal/full computer control`

OpenHands provides the highest level. Don't fight it, use it.

---

## What We Keep (Everything)

✅ Terminal - Users watch agent run bash, python, curl
✅ Code Editor - Agent writes verification scripts, users can edit
✅ File Explorer - Shows workspace structure (/workspace/sources/, /workspace/draft.md)
✅ Browser Preview - Agent can display research sources
✅ Chat Interface - User prompts agent
✅ Settings - Model selection, runtime configuration

**All of this stays.** Zero removals.

---

## What We Add (Minimal)

### 1. Economic Header (Day 3, Hour 1-2)

```typescript
// frontend/src/components/ChoirHeader.tsx

export function ChoirHeader() {
  const { data: balances } = useQuery({
    queryKey: ['balances'],
    queryFn: () => api.getBalances()
  })

  return (
    <div className="choir-header">
      <div className="logo">🎵 Choir</div>
      <div className="balances">
        <Balance icon="💎" label="CHIP" value={balances.chip} />
        <Balance icon="💰" label="Earned" value={`$${balances.usdc}`} />
        <Balance icon="⚡" label="Credits" value={balances.compute} />
      </div>
      <ProfileMenu />
    </div>
  )
}
```

Add to OpenHands App.tsx:
```typescript
<ChoirHeader />  {/* New */}
<OpenHandsLayout />  {/* Existing */}
```

### 2. Publish Button (Day 3, Hour 3-4)

Appears in chat when agent creates a draft file.

```typescript
// frontend/src/components/ChatInterface.tsx

export function ChatInterface() {
  const [draftPath, setDraftPath] = useState<string | null>(null)

  // Poll for draft file
  useEffect(() => {
    const checkDraft = async () => {
      const exists = await api.fileExists('/workspace/draft.md')
      if (exists) setDraftPath('/workspace/draft.md')
    }
    const interval = setInterval(checkDraft, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <Chat />  {/* Existing OpenHands chat */}

      {draftPath && (
        <PublishPrompt
          path={draftPath}
          onPublish={handlePublish}
        />
      )}
    </div>
  )
}

function PublishPrompt({ path, onPublish }) {
  return (
    <div className="publish-prompt">
      <p>✅ Draft ready: <code>{path}</code></p>
      <Button onClick={onPublish}>
        Publish for 100 CHIP →
      </Button>
    </div>
  )
}
```

### 3. My Research Page (Day 3, Hour 5-6)

New route: `/research`

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
        <Stat label="Citations" value={sum(articles, a => a.citations)} />
        <Stat label="Earned" value={`$${sum(articles, a => a.earnings)}`} />
      </div>

      <div className="articles">
        {articles?.map(article => (
          <ArticleCard
            key={article.id}
            title={article.title}
            citations={article.citations}
            earnings={article.earnings}
            noveltyScore={article.noveltyScore}
          />
        ))}
      </div>
    </div>
  )
}
```

---

## Implementation Checklist

### Day 3, Hour 1-2: Economic Header
- [ ] Create `ChoirHeader.tsx` component
- [ ] Add to App.tsx above OpenHands layout
- [ ] Connect to `/balances` API endpoint
- [ ] Style to match OpenHands theme

### Day 3, Hour 3-4: Publish Button
- [ ] Add draft detection to ChatInterface
- [ ] Create PublishPrompt component
- [ ] Connect to `/publish` API endpoint
- [ ] Show success message with CHIP reward

### Day 3, Hour 5-6: Research Dashboard
- [ ] Create ResearchPage component
- [ ] Add `/research` route
- [ ] Connect to `/articles` API endpoint
- [ ] Display articles with stats

### Day 3, Hour 7-8: Polish
- [ ] Add loading states
- [ ] Error handling (insufficient CHIP, etc.)
- [ ] Tooltips for CHIP/USDC/Credits
- [ ] Mobile responsiveness (basic)

---

## What We DON'T Do

❌ Remove terminal component
❌ Remove code editor
❌ Remove file explorer
❌ Hide agent logs
❌ Sanitize event streams
❌ Create "clean" research UI
❌ Build markdown editor
❌ Custom navigation
❌ Mobile-first redesign
❌ Branding overhaul

**All of that is unnecessary.** Ship fast, improve later.

---

## Why This Approach Works

1. **Faster**: 8 hours of work vs 4 weeks
2. **Simpler**: 3 new components vs complete redesign
3. **Lower Risk**: Minimal changes to OpenHands codebase
4. **Better UX**: Users see agent work (transparency builds trust)
5. **Easier to Maintain**: Fewer divergences from upstream OpenHands

---

## Success Criteria

**Day 3 Complete When**:
- [ ] Users see CHIP/USDC balances in header
- [ ] Publish button appears when draft exists
- [ ] Publishing works (stake CHIP, earn based on novelty)
- [ ] Research page shows published articles
- [ ] Citation earnings visible

**That's it.** Everything else is future work.

---

**Document Status**: v2.0 (Corrected)
**Related**: JAZZHANDS_3DAY_SPRINT.md, JAZZHANDS_FORK_STRATEGY.md
**Replaces**: v1.0 (outdated "hide dev tools" approach)
