# Ghostwriter Architecture: Practical Implementation Guide

**Status**: Implementation-Ready
**Created**: 2025-11-23
**Purpose**: Simplified, buildable architecture with token/cost optimization

---

## Prerequisites ✅

**Claude Agent SDK is ALREADY configured and ready to use:**

- ✅ **Integration**: Complete (see [CLAUDE_SDK_INTEGRATION.md](./CLAUDE_SDK_INTEGRATION.md))
- ✅ **Authentication**: AWS Bedrock with API key (configured in `.env`)
- ✅ **Tools Available**: Read, Write, WebSearch, Bash, Glob, Grep, Task
- ✅ **Dependencies**: Installed via UV (`uv add claude-agent-sdk`)
- ✅ **Status**: Production ready (v1.0, 2025-11-20)

**Environment variables already set:**
```bash
CLAUDE_SDK_USE_BEDROCK=true
AWS_BEARER_TOKEN_BEDROCK=<configured>
AWS_REGION=us-east-1
ENABLE_CLAUDE_SDK=true
```

**👉 This document describes how to BUILD the ghostwriter system using our existing Claude SDK infrastructure.**

**No setup required - start implementing immediately.**

---

## Executive Summary

This document describes how to **implement** Tuxedo's ghostwriter system using our **existing Claude Agent SDK integration**. The SDK is already configured with AWS Bedrock authentication and provides all tools needed (Read, Write, WebSearch, Bash, etc.).

**Key Design Principles**:
- ❌ No vector databases (Claude handles relevance)
- ❌ No special NLI models (Claude does reasoning)
- ❌ No embeddings (simple keyword matching if needed)
- ✅ 3-layer verification (URL → content → Claude verification)
- ✅ Haiku for simple tasks (speed + cost)
- ✅ Sonnet for complex reasoning
- ✅ Prompt caching for iteration
- ✅ **Uses existing Claude SDK infrastructure** (no new setup needed)

---

## Quick Start 🚀

Since Claude Agent SDK is already configured, you can start implementing immediately:

```python
# backend/agent/ghostwriter/pipeline.py
from claude_agent_sdk import query, ClaudeAgentOptions
import asyncio

async def run_research_stage(topic: str):
    """Stage 1: Research with parallel Haiku subagents"""
    options = ClaudeAgentOptions(
        model="claude-3-5-haiku-20241022",  # Haiku for speed/cost
        allowed_tools=["WebSearch", "Write"],
        cwd="/workspace/sessions/session_001/00_research"
    )

    prompt = f"""You are a research specialist.

    TOPIC: {topic}

    Execute 3-5 WebSearch queries and save each source to source_N.md
    """

    async for message in query(prompt, options):
        print(message)

# Run it
asyncio.run(run_research_stage("DeFi yields on Stellar"))
```

**That's it!** The Claude SDK handles authentication, model selection, tool execution, and file operations.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                               │
│                  "Research DeFi yields on Stellar"                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 1: RESEARCH (Parallel Haiku Subagents)                       │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │ Researcher  │  │ Researcher  │  │ Researcher  │  (5-10 parallel)│
│  │     #1      │  │     #2      │  │     #3      │                │
│  │   Haiku     │  │   Haiku     │  │   Haiku     │                │
│  │             │  │             │  │             │                │
│  │ Input: 500t │  │ Input: 500t │  │ Input: 500t │                │
│  │ Output: 2kt │  │ Output: 2kt │  │ Output: 2kt │                │
│  │ No history  │  │ No history  │  │ No history  │                │
│  │ Cost: $0.01 │  │ Cost: $0.01 │  │ Cost: $0.01 │                │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│         │                │                │                        │
│         ▼                ▼                ▼                        │
│  00_research/     00_research/     00_research/                    │
│  source_1.md      source_2.md      source_3.md                     │
│                                                                     │
│  Total Stage Cost: ~$0.05 (5 researchers × $0.01)                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 2: DRAFT (Sonnet - Reads All Research)                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Drafter Agent (Sonnet 4.5)                                   │  │
│  │                                                              │  │
│  │ Input: ~10k tokens (all research notes + drafter prompt)    │  │
│  │ Output: ~3k tokens (initial draft with citations)           │  │
│  │ No history needed                                           │  │
│  │ Cost: $0.08                                                  │  │
│  │                                                              │  │
│  │ Tools: Read, Write (via Claude SDK)                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Output: 01_draft/initial_draft.md                                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 3: EXTRACT (Haiku - Simple Structured Output)                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Extractor Agent (Haiku 4.5)                                  │  │
│  │                                                              │  │
│  │ Input: ~3.5k tokens (draft + extractor prompt)              │  │
│  │ Output: ~2k tokens (JSON claims + citations)                │  │
│  │ No history needed                                           │  │
│  │ Cost: $0.01                                                  │  │
│  │                                                              │  │
│  │ Tools: Read, Write (via Claude SDK)                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Output: 02_extraction/atomic_claims.json                          │
│          02_extraction/citations.json                              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 4: VERIFY (CRITICAL - Parallel Haiku Per Claim)              │
│                                                                     │
│  Layer 1: URL Check (Bash tool via Claude SDK)                     │
│  ┌────────┐  ┌────────┐  ┌────────┐                                │
│  │ curl   │  │ curl   │  │ curl   │  (parallel, instant)           │
│  │ cite_1 │  │ cite_2 │  │ cite_3 │                                │
│  └────────┘  └────────┘  └────────┘                                │
│  Cost: $0.00                                                        │
│                                                                     │
│  Layer 2: Content Fetch (WebFetch tool via Claude SDK)             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │ WebFetch    │  │ WebFetch    │  │ WebFetch    │  (parallel)    │
│  │ source_1    │  │ source_2    │  │ source_3    │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│  Cost: Included in verification                                    │
│                                                                     │
│  Layer 3: Claim Verification (Haiku per claim)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │ Verify      │  │ Verify      │  │ Verify      │  (20-30 parallel)│
│  │ claim_1     │  │ claim_2     │  │ claim_3     │                │
│  │   Haiku     │  │   Haiku     │  │   Haiku     │                │
│  │             │  │             │  │             │                │
│  │ Input: 1.5kt│  │ Input: 1.5kt│  │ Input: 1.5kt│                │
│  │ Output: 300t│  │ Output: 300t│  │ Output: 300t│                │
│  │ No history  │  │ No history  │  │ No history  │                │
│  │ Cost: $0.005│  │ Cost: $0.005│  │ Cost: $0.005│                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│                                                                     │
│  Total Stage Cost: ~$0.15 (25 claims × $0.005)                    │
│                                                                     │
│  Output: 03_verification/verification_report.json                  │
│          03_verification/url_checks.json                           │
│          03_verification/content_fetched/*.txt                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 5: CRITIQUE (Sonnet - Analysis)                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Critic Agent (Sonnet 4.5 via Claude SDK)                    │  │
│  │                                                              │  │
│  │ Input: ~5k tokens (draft + verification report + prompt)    │  │
│  │ Output: ~1.5k tokens (structured critique)                  │  │
│  │ No history needed                                           │  │
│  │ Cost: $0.05                                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Output: 04_critique/critique.md                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 6: REVISE (Sonnet - Complex Reasoning + WebSearch)           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Reviser Agent (Sonnet 4.5 via Claude SDK)                   │  │
│  │                                                              │  │
│  │ Input: ~7k tokens (draft + critique + verification)         │  │
│  │ Output: ~3.5k tokens (revised draft)                        │  │
│  │ USES HISTORY for iteration (prompt caching eligible)        │  │
│  │ Cost: $0.10 (first), $0.03 (cached iterations)              │  │
│  │                                                              │  │
│  │ Tools: Read, WebSearch, Write (via Claude SDK)              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Output: 05_revision/revised_draft.md                              │
│                                                                     │
│  📌 PROMPT CACHING: Draft + critique cached for iterations        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 7: RE-VERIFY (Haiku - Same as Stage 4)                       │
│                                                                     │
│  Same process as Stage 4, but on revised draft                     │
│  Cost: ~$0.15 (25 claims × $0.005)                                │
│                                                                     │
│  Output: 06_re_verification/verification_report.json               │
│                                                                     │
│  ✅ Check: verification_rate >= 0.90?                             │
│     If NO: Repeat Stage 6-7 (max 2-3 iterations)                  │
│     If YES: Proceed to Stage 8                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 8: STYLE (Sonnet - Final Polish)                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Style Agent (Sonnet 4.5 via Claude SDK)                     │  │
│  │                                                              │  │
│  │ Input: ~5k tokens (draft + style guide + prompt)            │  │
│  │ Output: ~3.5k tokens (styled report)                        │  │
│  │ No history needed                                           │  │
│  │ Cost: $0.08                                                  │  │
│  │                                                              │  │
│  │ 📌 PROMPT CACHING: Style guide cached across requests      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Output: 07_style/final_report.md                                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                          ✅ FINAL REPORT

┌─────────────────────────────────────────────────────────────────────┐
│ TOTAL COST PER REPORT (1000 words, 25 claims, no iterations)       │
│                                                                     │
│ Stage 1 (Research):      $0.05                                     │
│ Stage 2 (Draft):         $0.08                                     │
│ Stage 3 (Extract):       $0.01                                     │
│ Stage 4 (Verify):        $0.15                                     │
│ Stage 5 (Critique):      $0.05                                     │
│ Stage 6 (Revise):        $0.10                                     │
│ Stage 7 (Re-verify):     $0.15                                     │
│ Stage 8 (Style):         $0.08                                     │
│                                                                     │
│ TOTAL:                   $0.67 per report                          │
│                                                                     │
│ With 1 revision iteration (cached): +$0.18                         │
│ With 2 revision iterations (cached): +$0.36                        │
│                                                                     │
│ TIME ESTIMATE: 3-5 minutes (parallel execution)                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Model Selection Strategy

**Note**: Model selection is handled via `ClaudeAgentOptions(model="...")` parameter when using the Claude SDK.

### Use Haiku 4.5 For:

**Model ID**: `claude-3-5-haiku-20241022`
**Characteristics**: Fast, cheap, good at structured tasks
**Cost**: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens

1. **Research** (Stage 1)
   - Simple web search + summarization
   - Independent subagents (no context needed)
   - Can spawn 10+ in parallel

2. **Extract** (Stage 3)
   - Structured JSON output
   - Pattern-based extraction
   - No complex reasoning

3. **Verify** (Stage 4, Layer 3)
   - Per-claim verification
   - Simple yes/no + quote extraction
   - 20-30 parallel calls

4. **Re-verify** (Stage 7)
   - Same as verify

### Use Sonnet 4.5 For:

**Model ID**: `claude-sonnet-4-5-20250929`
**Characteristics**: Strong reasoning, complex tasks, quality output
**Cost**: ~$3 per 1M input tokens, ~$15 per 1M output tokens

1. **Draft** (Stage 2)
   - Synthesize multiple sources
   - Coherent narrative
   - Proper citation placement

2. **Critique** (Stage 5)
   - Quality assessment
   - Nuanced analysis
   - Actionable recommendations

3. **Revise** (Stage 6)
   - Complex reasoning (fix claims)
   - WebSearch for better sources
   - Rewrite with preservation

4. **Style** (Stage 8)
   - Sophisticated style transformation
   - Preserve facts while changing tone
   - Final polish

---

## Token Breakdown by Stage

### Stage 1: Research (Haiku × 5-10)

**Per researcher**:
```
Input:
- User request: ~200 tokens
- Researcher prompt: ~300 tokens
Total input: ~500 tokens

Output:
- Source summary: ~2000 tokens

Cost per researcher: (500 × $0.25 + 2000 × $1.25) / 1M = $0.003

Total for 5 researchers: $0.015
Total for 10 researchers: $0.03
```

**History**: ❌ Not needed (independent subagents)
**Parallelization**: ✅ All researchers run simultaneously
**Caching**: ❌ Not applicable

---

### Stage 2: Draft (Sonnet × 1)

```
Input:
- Research notes (5 sources × 2k): ~10,000 tokens
- Drafter prompt: ~500 tokens
Total input: ~10,500 tokens

Output:
- Initial draft: ~3,000 tokens

Cost: (10,500 × $3 + 3,000 × $15) / 1M = $0.076
```

**History**: ❌ Not needed (reads files directly)
**Parallelization**: ❌ Single sequential task
**Caching**: ❌ Not applicable (one-time task)

---

### Stage 3: Extract (Haiku × 1)

```
Input:
- Draft: ~3,000 tokens
- Extractor prompt: ~400 tokens
Total input: ~3,400 tokens

Output:
- JSON (claims + citations): ~2,000 tokens

Cost: (3,400 × $0.25 + 2,000 × $1.25) / 1M = $0.0034
```

**History**: ❌ Not needed
**Parallelization**: ❌ Single task
**Caching**: ❌ Not applicable

---

### Stage 4: Verify (Haiku × 25 claims)

**Layer 1: URL Check (Bash)**
```bash
curl -I https://example.com/article
# Cost: $0 (no LLM)
```

**Layer 2: Content Fetch (WebFetch)**
```
# Included in Layer 3 verification cost
```

**Layer 3: Per-claim verification (Haiku)**
```
Input (per claim):
- Claim text: ~50 tokens
- Source content snippet: ~1,000 tokens
- Verification prompt: ~400 tokens
Total input: ~1,450 tokens

Output (per claim):
- JSON result: ~300 tokens

Cost per claim: (1,450 × $0.25 + 300 × $1.25) / 1M = $0.0007

Total for 25 claims: 25 × $0.0007 = $0.0175
```

**History**: ❌ Not needed (independent verifications)
**Parallelization**: ✅ All 25 claims verified simultaneously
**Caching**: ❌ Not applicable (different claims each time)

**Important**: We give Claude the **whole source content** (up to ~1k tokens), let it find relevant parts. No semantic search needed.

---

### Stage 5: Critique (Sonnet × 1)

```
Input:
- Draft: ~3,000 tokens
- Verification report: ~1,500 tokens (JSON summary)
- Critique prompt: ~500 tokens
Total input: ~5,000 tokens

Output:
- Structured critique: ~1,500 tokens

Cost: (5,000 × $3 + 1,500 × $15) / 1M = $0.0375
```

**History**: ❌ Not needed (reads files)
**Parallelization**: ❌ Single task
**Caching**: ❌ Not applicable

---

### Stage 6: Revise (Sonnet × 1, with iterations)

**First iteration**:
```
Input:
- Original draft: ~3,000 tokens
- Critique: ~1,500 tokens
- Verification report: ~1,500 tokens
- Reviser prompt: ~1,000 tokens
Total input: ~7,000 tokens

Output:
- Revised draft: ~3,500 tokens

Cost (first): (7,000 × $3 + 3,500 × $15) / 1M = $0.0735
```

**Subsequent iterations (with prompt caching)**:
```
Cached:
- Original draft: ~3,000 tokens (cached)
- Critique: ~1,500 tokens (cached)
- Reviser prompt: ~1,000 tokens (cached)
Total cached: ~5,500 tokens

Non-cached:
- New verification report: ~1,500 tokens

Cost (cached iteration): (1,500 × $3 + 3,500 × $15) / 1M = $0.057
Savings: ~22% per iteration
```

**History**: ✅ **USES HISTORY** for iterative refinement
**Parallelization**: ❌ Sequential (must see previous critique)
**Caching**: ✅ **PROMPT CACHING ELIGIBLE**
  - Cache: draft + critique + prompt
  - Update: verification report only

---

### Stage 7: Re-verify (Haiku × 25 claims)

Same as Stage 4: **$0.0175**

**History**: ❌ Not needed
**Parallelization**: ✅ All claims simultaneously
**Caching**: ❌ Different claims than first verification

---

### Stage 8: Style (Sonnet × 1)

**First request (no cache)**:
```
Input:
- Revised draft: ~3,500 tokens
- Style guide: ~1,200 tokens
- Style applicator prompt: ~300 tokens
Total input: ~5,000 tokens

Output:
- Styled report: ~3,500 tokens

Cost: (5,000 × $3 + 3,500 × $15) / 1M = $0.0675
```

**Subsequent requests (style guide cached)**:
```
Cached:
- Style guide: ~1,200 tokens (cached across sessions)
- Style applicator prompt: ~300 tokens (cached)

Non-cached:
- Draft: ~3,500 tokens

Cost (cached): (3,500 × $3 + 3,500 × $15) / 1M = $0.063
Savings: ~7% per request (accumulates across many reports)
```

**History**: ❌ Not needed (stateless transformation)
**Parallelization**: ❌ Single task
**Caching**: ✅ **PROMPT CACHING ELIGIBLE**
  - Cache: style guide (reused across all reports using same style)
  - Update: draft only

---

## Prompt Caching Strategy

### What is Prompt Caching?

Claude caches the **prefix of your prompt** and charges less for cached tokens on subsequent requests.

**Pricing**:
- Cached input: ~$0.30 per 1M tokens (10× cheaper than regular input)
- Regular input: ~$3 per 1M tokens
- Output: ~$15 per 1M tokens

### Where We Use It

#### 1. Revision Iterations (Stage 6)

**Setup**:
```python
# First revision
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"{draft}\n\n{critique}\n\n{reviser_prompt}",
                "cache_control": {"type": "ephemeral"}  # Cache this
            },
            {
                "type": "text",
                "text": f"Verification report:\n{verification_report}"  # Don't cache (changes)
            }
        ]
    }
]

# Second revision (after re-verification)
# Draft + critique + prompt are cached (5,500 tokens × $0.30 = $0.00165)
# Only new verification report is non-cached (1,500 tokens × $3 = $0.0045)
# Total input cost: $0.00615 vs $0.021 (70% savings)
```

**Benefit**: If we need 2-3 revision iterations, saves ~$0.03-$0.05 per report

#### 2. Style Guide (Stage 8)

**Setup**:
```python
# Load style guide once, cache for all reports using this style
style_guide = load_file("style_guides/academic.md")  # ~1,200 tokens

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"{style_guide}\n\n{style_applicator_prompt}",
                "cache_control": {"type": "ephemeral"}  # Cache across sessions
            },
            {
                "type": "text",
                "text": f"Draft to style:\n{draft}"  # Changes per report
            }
        ]
    }
]
```

**Benefit**: After first report, style guide is cached
- First report: 1,200 tokens × $3 = $0.0036
- Subsequent: 1,200 tokens × $0.30 = $0.00036 (90% savings on style guide)
- If we generate 100 reports with same style: saves ~$0.33 total

---

## Simplified 3-Layer Verification

### Why 3 Layers (Not 4)?

The architecture doc mentioned 4 layers, but practically we only need 3:

1. ✅ **URL Check** (Bash) - Is URL accessible?
2. ✅ **Content Fetch** (WebFetch) - Can we retrieve source?
3. ✅ **Claim Verification** (Claude) - Does source support claim?

**Removed**: "SelfCheckGPT" (Layer 4) - too expensive for most claims, optional for high-stakes

### Layer 1: URL Check (Bash)

```python
async def check_url(url: str) -> dict:
    """
    Check if URL is accessible.
    No LLM needed - pure bash.
    """
    cmd = f'curl -I -s -o /dev/null -w "%{{http_code}}" {url}'
    result = await run_bash(cmd)

    status_code = int(result.stdout.strip())

    return {
        "url": url,
        "accessible": 200 <= status_code < 400,
        "http_code": status_code
    }
```

**Cost**: $0
**Time**: ~100ms per URL
**Parallelization**: Check all URLs simultaneously

### Layer 2: Content Fetch

```python
async def fetch_content(url: str) -> str:
    """
    Fetch source content using Claude SDK's WebFetch tool.
    Claude SDK handles the HTTP request and content extraction.
    """
    from claude_agent_sdk import query, ClaudeAgentOptions

    options = ClaudeAgentOptions(
        model="claude-3-5-haiku-20241022",
        allowed_tools=["WebFetch"]
    )

    prompt = f"Fetch content from {url} and extract the main text"

    content = ""
    async for message in query(prompt, options):
        content += message

    return content[:4000]  # Limit to 4000 chars (~1000 tokens)
```

**Cost**: Minimal (included in verification)
**Time**: ~500ms per URL
**Parallelization**: Fetch all sources simultaneously
**Note**: Claude SDK's WebFetch tool handles all HTTP/HTML complexity

### Layer 3: Claim Verification (Claude Haiku)

**This is where the magic happens** - Claude does NLI entailment + semantic search in one call using the Claude SDK:

```python
async def verify_claim(
    claim: str,
    source_url: str,
    source_content: str
) -> dict:
    """
    Verify if source supports claim using Claude SDK.
    Claude handles both finding relevant parts AND checking logical support.
    """
    from claude_agent_sdk import query, ClaudeAgentOptions
    import json

    options = ClaudeAgentOptions(
        model="claude-3-5-haiku-20241022",
        allowed_tools=[]  # No tools needed for verification
    )

    prompt = f"""You are a fact-checker verifying citations.

SOURCE: {source_url}
{source_content}

CLAIM TO VERIFY:
{claim}

TASK: Determine if this source supports the claim.

RULES:
1. "supported" = source DIRECTLY proves claim is true
2. "unsupported" = source doesn't mention claim OR contradicts it
3. Provide exact quote from source if supported

Respond with JSON only:
{{
  "supported": true/false,
  "confidence": 0.0-1.0,
  "quote": "exact quote from source" or null,
  "reasoning": "brief explanation (1 sentence)"
}}
"""

    response_text = ""
    async for message in query(prompt, options):
        response_text += message

    result = json.loads(response_text)

    return {
        "claim": claim,
        "source_url": source_url,
        "supported": result["supported"],
        "confidence": result["confidence"],
        "quote": result["quote"],
        "reasoning": result["reasoning"]
    }
```

**Input**: ~1,450 tokens (claim + source snippet + prompt)
**Output**: ~300 tokens (JSON result)
**Cost**: ~$0.0007 per claim
**Time**: ~1-2 seconds per claim (parallel)
**Parallelization**: ✅ Verify 25+ claims simultaneously

**No need for**:
- ❌ Vector database (Claude finds relevant parts)
- ❌ Semantic search embeddings
- ❌ Special NLI models (Claude does reasoning)
- ❌ Keyword extraction

**Claude is smart enough** to:
1. Scan the source content
2. Find relevant passages
3. Determine if claim is logically supported
4. Extract exact quotes

---

## Optional: SelfCheckGPT for High-Stakes Claims

**When to use**: Only for critical claims where hallucination would be dangerous
- Financial numbers (APY, TVL, prices)
- Safety claims ("never been hacked")
- Legal statements
- Medical information

**How it works**: Generate claim multiple times, check variance

```python
async def consistency_check(claim: str, source_url: str) -> dict:
    """
    Optional: Check if responses are consistent across samples.
    High variance = possible hallucination.
    """
    topic = extract_topic(claim)  # e.g., "USDC APY on Blend"

    responses = []
    for _ in range(3):  # 3-5 samples
        prompt = f"According to {source_url}, what is the {topic}?"
        response = await claude_haiku.query(
            prompt,
            temperature=0.7  # Add randomness
        )
        responses.append(response)

    # Extract numbers and check variance
    numbers = [extract_number(r) for r in responses if extract_number(r)]

    if numbers:
        mean = sum(numbers) / len(numbers)
        variance = sum((n - mean) ** 2 for n in numbers) / len(numbers)

        # Low variance = consistent = trustworthy
        # If all responses are 8.5 ± 0.2, good
        # If responses are [8.5, 12, 6, 15], high variance = suspicious

        consistency_score = 1.0 - min(variance / mean, 1.0) if mean > 0 else 0.0

        return {
            "consistent": consistency_score > 0.7,
            "score": consistency_score,
            "samples": responses,
            "warning": "Low consistency - verify claim" if consistency_score < 0.7 else None
        }

    # For non-numeric claims, simple word overlap
    # ...
```

**Cost**: 3 × $0.0007 = $0.002 per claim
**When to run**: Only if claim flagged as "high-stakes" (10-20% of claims)
**Total added cost**: ~$0.01-$0.02 per report

**Decision**: Start WITHOUT SelfCheckGPT, add later if we see hallucination issues

---

## Filesystem Structure (Simplified)

```
workspace/
├── sessions/
│   └── session_20251123_143022/
│       ├── 00_research/
│       │   ├── source_1.md
│       │   ├── source_2.md
│       │   └── source_3.md
│       ├── 01_draft/
│       │   └── initial_draft.md
│       ├── 02_extraction/
│       │   ├── atomic_claims.json
│       │   └── citations.json
│       ├── 03_verification/
│       │   ├── url_checks.json
│       │   ├── content_fetched/
│       │   │   ├── cite_1.txt
│       │   │   ├── cite_2.txt
│       │   │   └── cite_3.txt
│       │   └── verification_report.json
│       ├── 04_critique/
│       │   └── critique.md
│       ├── 05_revision/
│       │   └── revised_draft.md
│       ├── 06_re_verification/
│       │   └── verification_report.json
│       ├── 07_style/
│       │   └── final_report.md
│       └── transcript.txt
├── prompts/
│   ├── researcher.txt
│   ├── drafter.txt
│   ├── extractor.txt
│   ├── verifier.txt
│   ├── critic.txt
│   ├── reviser.txt
│   └── style_applicator.txt
├── style_guides/
│   ├── academic.md
│   ├── technical.md
│   ├── conversational.md
│   └── defi_report.md
└── logs/
    └── session_20251123_143022.log
```

---

## Implementation Priorities

### Phase 1: Core Pipeline (Week 1)

**Goal**: Get basic research → draft → verify working

**Prerequisites**: ✅ Claude SDK already configured (see [Prerequisites](#prerequisites-) section)

**Tasks**:
1. Create `backend/agent/ghostwriter/` module
2. Implement `GhostwriterPipeline` class using Claude SDK
3. Create filesystem checkpoint system
4. Build Stage 1 (Research with Haiku via `ClaudeAgentOptions`)
5. Build Stage 2 (Draft with Sonnet via `ClaudeAgentOptions`)
6. Build Stage 3 (Extract with Haiku via `ClaudeAgentOptions`)
7. Build Stage 4 Layer 1-2 (URL check with Bash tool, content fetch with WebFetch tool)
8. Test basic flow (no verification yet)

**Key Implementation Detail**: All stages use `claude_agent_sdk.query()` with appropriate `ClaudeAgentOptions` for model and tool selection.

**Deliverables**:
- ✅ Research agent spawns 5 parallel Haiku subagents (using Claude SDK)
- ✅ Drafter synthesizes research into coherent document (using Claude SDK)
- ✅ Extractor produces atomic_claims.json (using Claude SDK)
- ✅ URL checking works (using Bash tool via Claude SDK)
- ✅ Content fetching works (using WebFetch tool via Claude SDK)

**Not included**: Verification, critique, revision (Phase 2)

**Example code structure**:
```python
# backend/agent/ghostwriter/pipeline.py
from claude_agent_sdk import query, ClaudeAgentOptions
import asyncio

class GhostwriterPipeline:
    async def run_stage_1_research(self, topic: str):
        options = ClaudeAgentOptions(
            model="claude-3-5-haiku-20241022",
            allowed_tools=["WebSearch", "Write"],
            cwd=self.research_dir
        )
        prompt = self._load_prompt("researcher.txt", topic=topic)
        async for msg in query(prompt, options):
            print(msg)
```

---

### Phase 2: Citation Verification (Week 2)

**Goal**: Get 3-layer verification working with 90% threshold

**Tasks**:
1. Implement Stage 4 Layer 3 (claim verification with Haiku)
2. Build verification report generation
3. Test with real DeFi content (high citation density)
4. Tune confidence thresholds
5. Add parallel verification (25+ claims simultaneously)

**Deliverables**:
- ✅ Per-claim verification with Haiku
- ✅ Verification report with supported/unsupported breakdown
- ✅ 90% threshold enforcement
- ✅ Parallel verification (fast)

**Test case**: Generate report about "Blend Capital yields" with 20+ claims, verify all citations

---

### Phase 3: Quality Loop (Week 3)

**Goal**: Critique → revise → re-verify loop working

**Tasks**:
1. Implement Stage 5 (Critique with Sonnet)
2. Implement Stage 6 (Revise with Sonnet)
3. Implement Stage 7 (Re-verify with Haiku)
4. Add iteration logic (max 3 revisions)
5. Implement prompt caching for revisions
6. Test full pipeline end-to-end

**Deliverables**:
- ✅ Critique identifies unsupported claims
- ✅ Reviser fixes claims (WebSearch for better sources)
- ✅ Re-verification confirms fixes
- ✅ Iterates until 90% threshold met
- ✅ Prompt caching reduces iteration cost

**Test case**: Intentionally include bad citations, verify system catches and fixes them

---

### Phase 4: Style & DeFi (Week 4)

**Goal**: Style application + DeFi domain integration

**Tasks**:
1. Implement Stage 8 (Style with Sonnet)
2. Create 4 style guides (academic, technical, conversational, defi_report)
3. Implement auto-style-selection logic
4. Create `DeFiGhostwriter` extension
5. Migrate existing DeFi methods from `claude_sdk_wrapper.py`
6. Add API endpoints

**Deliverables**:
- ✅ Parameterized style guide system
- ✅ Auto-selection based on content
- ✅ DeFi-specific research reports
- ✅ API endpoints for general + DeFi ghostwriter

**Test case**: Generate same report with 3 different styles, verify tone/voice changes but facts preserved

---

### Phase 5: Production Polish (Week 5)

**Goal**: Error handling, monitoring, documentation

**Tasks**:
1. Add comprehensive error handling
2. Implement retry logic (transient failures)
3. Add session resumability (crash recovery)
4. Create monitoring/metrics
5. Write user documentation
6. Create example reports

**Deliverables**:
- ✅ Production-ready error handling
- ✅ Resumable sessions (can continue from any stage)
- ✅ Metrics collection (cost, latency, quality)
- ✅ User-facing documentation

---

## Cost & Performance Targets

### Cost Targets (Per Report)

| Scenario | Target | Actual Estimate |
|----------|--------|-----------------|
| **Simple report** (1000 words, 15 claims, no revisions) | <$0.50 | $0.52 |
| **Standard report** (1500 words, 25 claims, 1 revision) | <$1.00 | $0.85 |
| **Complex report** (2500 words, 40 claims, 2 revisions) | <$2.00 | $1.45 |

**We're under target** ✅ (thanks to Haiku for simple tasks)

### Performance Targets

| Metric | Target | Expected |
|--------|--------|----------|
| **Latency** (1000-word report) | <5 min | 3-4 min |
| **Verification rate** | ≥90% | 90-95% |
| **Throughput** | 10 concurrent | 20+ (Haiku parallel) |
| **Success rate** | ≥99% | ~99% |

**Latency breakdown**:
- Stage 1 (Research): ~30-60s (parallel Haiku)
- Stage 2 (Draft): ~20-30s (Sonnet)
- Stage 3 (Extract): ~5-10s (Haiku)
- Stage 4 (Verify): ~30-60s (parallel Haiku)
- Stage 5 (Critique): ~15-20s (Sonnet)
- Stage 6 (Revise): ~30-45s (Sonnet + WebSearch)
- Stage 7 (Re-verify): ~30-60s (parallel Haiku)
- Stage 8 (Style): ~20-30s (Sonnet)

**Total**: 3-5 minutes (mostly parallel work)

---

## Key Simplifications from Academic Architecture

| Academic Version | Practical Version |
|------------------|-------------------|
| 4-layer verification (URL, content, NLI, SelfCheckGPT) | 3-layer (URL, content, Claude) |
| Special NLI models (SummaC-ZS, VeriScore) | Claude Haiku does reasoning |
| Vector database for semantic search | Claude finds relevant passages |
| Embeddings for similarity | Simple keyword overlap (if needed) |
| Complex consistency algorithms | Optional SelfCheckGPT for high-stakes |
| Multiple verification models | Single model (Haiku) for all verification |

**Philosophy**: Use Claude's intelligence instead of specialized models/databases

---

## Example Prompts

### Researcher Prompt (`prompts/researcher.txt`)

```
You are a research specialist gathering authoritative sources.

TOPIC: {topic}

YOUR TASK:
1. Execute 3-5 WebSearch queries to find authoritative sources
2. For each source: extract key information, verify URL
3. Save each source to {output_dir}/source_N.md

CRITICAL CONSTRAINTS:
- ONLY use WebSearch (no internal knowledge)
- Focus on authoritative sources (academic, official docs, major publications)
- Include: URL, title, publication date, key excerpts
- Verify URLs are accessible

SEARCH STRATEGY:
- Search 1: Overview/general information
- Search 2: Specific data/statistics
- Search 3: Recent developments/news
- Search 4-5: Alternative perspectives/sources

OUTPUT FORMAT (per source file):
---
url: https://example.com/article
title: Article Title
date_published: 2025-01-15
date_accessed: 2025-11-23
source_type: [academic|documentation|news|blog]
---

# Key Excerpts
[Relevant quotes from the source]

# Summary
[Brief 2-3 sentence summary]

TOOLS:
- WebSearch: Find sources
- Write: Save to {output_dir}
```

### Verifier Prompt (`prompts/verifier.txt`)

```
You are a fact-checker verifying citations.

SOURCE: {source_url}
{source_content}

CLAIM TO VERIFY:
{claim}

YOUR TASK: Determine if this source supports the claim.

VERIFICATION RULES:
1. "supported" = source DIRECTLY proves claim is true
2. "unsupported" = source doesn't mention claim OR contradicts it
3. High confidence (>0.8) required for "supported"
4. Provide exact quote if supported

EXAMPLES:

Example 1 (SUPPORTED):
Source: "USDC Supply APY on Blend: 8.52%"
Claim: "Blend Capital offers 8.5% APY for USDC"
Result: supported (8.52% ≈ 8.5%)
Quote: "USDC Supply APY on Blend: 8.52%"

Example 2 (UNSUPPORTED - doesn't mention):
Source: "Blend Capital is a lending protocol on Stellar"
Claim: "Blend Capital offers 8.5% APY for USDC"
Result: unsupported (source doesn't mention APY)

Example 3 (UNSUPPORTED - contradicts):
Source: "USDC Supply APY on Blend: 3.2%"
Claim: "Blend Capital offers 8.5% APY for USDC"
Result: unsupported (contradicts: 3.2% ≠ 8.5%)

Respond with JSON only:
{
  "supported": true/false,
  "confidence": 0.0-1.0,
  "quote": "exact quote from source" or null,
  "reasoning": "brief explanation (1 sentence)"
}
```

### Reviser Prompt (`prompts/reviser.txt`)

```
You are a revision specialist fixing unsupported claims.

ORIGINAL DRAFT:
{draft}

CRITIQUE:
{critique}

UNSUPPORTED CLAIMS:
{unsupported_claims_json}

YOUR TASK: Fix all unsupported claims to meet 90% verification threshold.

FOR EACH UNSUPPORTED CLAIM:

Strategy A: Find better source (PREFERRED)
- Use WebSearch to find authoritative source
- Update citation with new URL
- Preserve claim if possible

Strategy B: Rewrite claim
- If source is good but claim too specific, rewrite to match source
- Example: "8.5% APY" → "approximately 8-9% APY"

Strategy C: Remove claim
- Only if no credible source exists
- Preserve narrative flow when removing

CRITICAL CONSTRAINTS:
- PRESERVE all supported claims (don't change what works!)
- Maintain overall document structure
- Keep all verified citations intact
- Focus ONLY on fixing unsupported claims

TOOLS:
- Read: Access draft, critique, verification report
- WebSearch: Find better sources
- Write: Save revised draft to {output_file}

OUTPUT: Revised draft with all unsupported claims fixed
```

---

## Implementation Checklist

Before starting, verify:

- [x] **Claude SDK installed**: `uv list | grep claude-agent-sdk` shows v0.1.8+
- [x] **AWS Bedrock configured**: `.env` has `CLAUDE_SDK_USE_BEDROCK=true` and `AWS_BEARER_TOKEN_BEDROCK`
- [x] **Environment loaded**: `python -c "from config.settings import settings; print(settings.enable_claude_sdk)"` prints `True`
- [x] **Integration tested**: `python test_claude_sdk_integration.py` passes

If all checked, you're ready to implement!

---

## Next Steps

**Infrastructure is ready** ✅ **Architecture is designed** ✅ **Start building now** 🚀

**Recommendation**: Start with Phase 1 (Week 1)
- Build core pipeline using `claude_agent_sdk.query()`
- Use `ClaudeAgentOptions(model="claude-3-5-haiku-20241022")` for research and extraction
- Use `ClaudeAgentOptions(model="claude-sonnet-4-5-20250929")` for drafting
- Test with real DeFi content

**Key files to create**:
```
backend/agent/ghostwriter/
├── __init__.py
├── pipeline.py          # Main GhostwriterPipeline class
├── stages.py            # Individual stage implementations
├── prompts/
│   ├── researcher.txt
│   ├── drafter.txt
│   └── extractor.txt
└── utils.py             # Filesystem, checkpointing utilities
```

**First commit**: Core pipeline skeleton with Stage 1 (Research) working.

Ready to start implementation!
