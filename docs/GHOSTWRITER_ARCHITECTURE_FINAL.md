# Ghostwriter Architecture: Final Design

**Status**: Architecture Committed - Ready for Implementation
**Created**: 2025-11-23
**Purpose**: General-purpose research agent with rigorous citation verification

---

## Executive Summary

This document describes Tuxedo's **general-purpose ghostwriter system** - a research agent that produces deeply researched, properly cited documents with multi-layer citation verification. The system uses **filesystem-based orchestration** and places **citation verification as the central, most critical subprocess**.

### Core Principles

1. **Filesystem as State Store** - Intermediate results persisted to disk, not in-memory
2. **Citation Verification First** - Multi-layer verification prevents LLM hallucination
3. **8-Stage Pipeline** - Clear separation of concerns with numbered stages
4. **Atomic Fact Decomposition** - Verify individual claims, not entire documents
5. **NLI Entailment** - Logical verification, not just semantic similarity
6. **Styleguide Parameterization** - User-selected or auto-selected writing style as final step

---

## The Critical Problem: Citation Hallucination

LLMs fabricate citations in **three distinct ways**:

1. **Complete Fabrication** - Non-existent papers, journals, URLs
2. **Partial Corruption** - Incorrect titles, dates, authors
3. **Source Distortion** - Twisting citations against their essence (MOST INSIDIOUS)

**Research Findings**:
- **47% of student-submitted LLM citations** have factual errors (University of Mississippi, 2024)
- LLMs prefer **confident guessing over admitting ignorance** (systemic training issue)
- **Semantic similarity ≠ logical entailment** (high similarity can be misleading)

**Legal Consequences**: Mata v. Avianca (2023) - lawyer sanctioned for fabricated citations

**Our Solution**: Multi-layer verification with **90% threshold** before accepting output

---

## Architecture Overview

### 8-Stage Pipeline

```
1. Research    → Web search, source gathering
2. Draft       → Initial document from research
3. Extract     → Atomic claims + citations
4. Verify      → Multi-layer citation verification (CRITICAL)
5. Critique    → Quality assessment
6. Revise      → Fix unsupported claims
7. Re-verify   → Validate fixes
8. Style       → Apply user/auto-selected styleguide
```

**Key Difference from Traditional Approaches**: Stages 3-7 create a **verification-critique-revision loop** that catches and fixes citation issues before final output.

### Filesystem Structure

```
workspace/
├── sessions/
│   └── session_20251123_143022/
│       ├── 00_research/
│       │   ├── search_results.json
│       │   ├── source_1.md
│       │   ├── source_2.md
│       │   └── source_3.md
│       ├── 01_draft/
│       │   └── initial_draft.md
│       ├── 02_extraction/
│       │   ├── atomic_claims.json      # Individual verifiable facts
│       │   └── citations.json          # All citations extracted
│       ├── 03_verification/
│       │   ├── url_checks.json         # Layer 1: URL accessibility
│       │   ├── content_fetched/        # Layer 2: Source content
│       │   │   ├── source_1.txt
│       │   │   ├── source_2.txt
│       │   │   └── source_3.txt
│       │   ├── nli_results.json        # Layer 3: NLI entailment
│       │   ├── consistency_checks.json # Layer 4: SelfCheckGPT
│       │   └── verification_report.json # Summary
│       ├── 04_critique/
│       │   └── critique.md
│       ├── 05_revision/
│       │   └── revised_draft.md
│       ├── 06_re_verification/
│       │   └── verification_report.json
│       ├── 07_style/
│       │   └── final_report.md
│       └── transcript.txt              # Human-readable log
├── prompts/
│   ├── researcher.txt
│   ├── drafter.txt
│   ├── extractor.txt
│   ├── citation_verifier.txt           # MOST CRITICAL
│   ├── critic.txt
│   ├── reviser.txt
│   └── style_applicator.txt
├── style_guides/
│   ├── academic.md                     # Formal, third-person, APA
│   ├── technical.md                    # Clear, instructional, second-person
│   ├── conversational.md               # Friendly, engaging, first-person
│   └── defi_report.md                  # DeFi-specific (financial, risk-aware)
└── logs/
    └── session_20251123_143022.log     # Machine-readable log
```

**Key Patterns**:
- **Numbered directories** (00_, 01_, etc.) - clear execution order
- **Separate files per stage** - easy to inspect, debug, resume
- **Prompt files** (not inline code) - easy to iterate without code changes
- **Styleguides as config** - parameterized, user-selectable

---

## Stage-by-Stage Details

### Stage 1: Research

**Purpose**: Gather high-quality sources via web search

**Input**: User request
**Tools**: `WebSearch`, `Write`
**Output**: `00_research/*.md` files with source material

**Process**:
1. Execute 5-10 web searches covering different aspects of topic
2. Identify authoritative sources (academic, official docs, major publications)
3. For each source: verify URL, extract key information, note access date
4. Save each source as separate markdown file

**Prompt Pattern** (`prompts/researcher.txt`):
```
You are a research specialist gathering sources for a report.

CRITICAL CONSTRAINTS:
- You MUST use WebSearch for ALL research (no internal knowledge)
- You MUST save each source to {output_dir} as separate .md file
- Focus on authoritative sources (academic papers, official documentation, reputable publications)

PROCESS:
1. Analyze user request to identify 5-10 search queries
2. Execute WebSearch for each query
3. For each source found:
   - Verify URL is accessible
   - Extract: title, URL, publication date, key excerpts
   - Save as: {output_dir}/source_{n}.md

OUTPUT FORMAT (per file):
---
url: https://example.com/article
title: Article Title
date_accessed: 2025-11-23
source_type: [academic|documentation|news|blog]
---

# Key Excerpts
[Relevant quotes and information]

# Summary
[Brief summary of source content]
```

**Quality Criteria**:
- Minimum 5 sources
- Mix of source types (prefer academic/official over blogs)
- Recent sources when available (prefer 2023-2025)
- URLs must be accessible (checked via WebSearch)

---

### Stage 2: Draft

**Purpose**: Create initial document from research sources

**Input**: All files from `00_research/`
**Tools**: `Read`, `Write`
**Output**: `01_draft/initial_draft.md`

**Process**:
1. Read all research files from `00_research/`
2. Synthesize into coherent narrative
3. Include inline citations `[1]`, `[2]` for all claims
4. Add reference list at bottom
5. Save draft to `01_draft/initial_draft.md`

**Key Requirement**: **ALL claims must have citations** at this stage (even if not yet verified)

**Prompt Pattern** (`prompts/drafter.txt`):
```
You are a document drafter creating an initial report from research sources.

CRITICAL CONSTRAINTS:
- You MUST cite sources for EVERY factual claim
- Use inline citations: [1], [2], etc.
- ONLY use sources from {research_dir}
- Include full reference list at bottom

PROCESS:
1. Read all sources from {research_dir}
2. Synthesize information into coherent narrative
3. For every claim, add inline citation
4. Create reference list matching citations

CITATION FORMAT:
Inline: "Blend Capital offers 8.5% APY for USDC [1]."
References:
[1] Blend Capital Documentation. https://blend.capital/docs (accessed 2025-11-23)

OUTPUT: Save draft to {output_file}
```

**Quality Criteria**:
- Every paragraph has at least one citation
- No unsourced claims
- Citations match sources in `00_research/`
- Coherent narrative structure

---

### Stage 3: Extract (Atomic Fact Decomposition)

**Purpose**: Decompose document into atomic claims and citations for verification

**Input**: `01_draft/initial_draft.md`
**Tools**: `Write`
**Output**:
- `02_extraction/atomic_claims.json`
- `02_extraction/citations.json`

**Process**:
1. Read draft from `01_draft/`
2. Extract **atomic facts** (single, independent, verifiable claims)
3. Extract all citations (URLs, titles, etc.)
4. Map each claim to its supporting citation(s)
5. Save structured JSON

**Why Atomic Decomposition?**

Complex sentence:
> "Blend Capital, launched in 2024 with $45M TVL, offers 8.5% APY for USDC suppliers and has never been hacked."

Contains **4 atomic facts**:
1. "Blend Capital was launched in 2024"
2. "Blend Capital has $45M TVL"
3. "Blend Capital offers 8.5% APY for USDC suppliers"
4. "Blend Capital has never been hacked"

**Benefit**: Can verify each independently. Fact 4 might be unsupported even if 1-3 are verified.

**Output Format**:

`atomic_claims.json`:
```json
[
  {
    "id": "claim_1",
    "text": "Blend Capital offers 8.5% APY for USDC suppliers",
    "citation_ids": ["cite_1"],
    "location": "paragraph 2, sentence 1"
  },
  {
    "id": "claim_2",
    "text": "Blend Capital has $45M in TVL",
    "citation_ids": ["cite_1", "cite_2"],
    "location": "paragraph 2, sentence 1"
  },
  {
    "id": "claim_3",
    "text": "Blend Capital has never been hacked",
    "citation_ids": ["cite_3"],
    "location": "paragraph 3, sentence 2"
  }
]
```

`citations.json`:
```json
[
  {
    "id": "cite_1",
    "url": "https://blend.capital/docs",
    "title": "Blend Capital Documentation",
    "type": "documentation",
    "reference_number": 1
  },
  {
    "id": "cite_2",
    "url": "https://defillama.com/protocol/blend",
    "title": "DeFiLlama - Blend Capital",
    "type": "analytics",
    "reference_number": 2
  },
  {
    "id": "cite_3",
    "url": "https://example.com/security-report",
    "title": "Blend Security Audit",
    "type": "report",
    "reference_number": 3
  }
]
```

**Prompt Pattern** (`prompts/extractor.txt`):
```
You are a fact extractor creating atomic claims for verification.

CRITICAL CONSTRAINTS:
- Extract ONLY atomic facts (single, independent, verifiable claims)
- Map each claim to its citation(s)
- Do NOT combine multiple facts into one claim

ATOMIC FACT RULES:
1. One fact per claim (not compound sentences)
2. Self-contained (understandable without context)
3. Verifiable (can check against source)
4. Specific (not vague generalizations)

PROCESS:
1. Read draft from {draft_file}
2. Extract all atomic facts
3. Extract all citations
4. Map claims to citations
5. Save JSON to {output_dir}

OUTPUT: Two files:
- atomic_claims.json (list of claims with citation_ids)
- citations.json (list of citations with metadata)
```

---

### Stage 4: Verify (CRITICAL - Multi-Layer Verification)

**Purpose**: Multi-layer citation verification to prevent hallucination

**Input**:
- `02_extraction/atomic_claims.json`
- `02_extraction/citations.json`
**Tools**: `WebSearch`, `Bash`, `Write`
**Output**: `03_verification/verification_report.json`

**Process**: 4-layer defense-in-depth

#### Layer 1: URL Accessibility

```bash
# Check HTTP 200 response
curl -I <url>

# Validate content type
file <downloaded_file>
```

**Purpose**: Catch completely fabricated URLs

**Output**: `03_verification/url_checks.json`

```json
{
  "cite_1": {
    "url": "https://blend.capital/docs",
    "status": "accessible",
    "http_code": 200,
    "content_type": "text/html"
  },
  "cite_3": {
    "url": "https://example.com/fake",
    "status": "failed",
    "http_code": 404,
    "error": "Not Found"
  }
}
```

#### Layer 2: Content Fetching

**Purpose**: Download and extract text from accessible URLs

**Process**:
- Download source content
- Extract text (handle PDFs with pdftotext, HTML with trafilatura/BeautifulSoup)
- Save to `03_verification/content_fetched/cite_{n}.txt`

**Example**: `content_fetched/cite_1.txt`
```
Blend Capital Documentation

Blend Capital is a decentralized lending protocol on Stellar.

Current Rates:
- USDC Supply APY: 8.52%
- XLM Supply APY: 3.21%
...
```

#### Layer 3: NLI Entailment Verification

**Purpose**: Verify each claim is **logically supported** by source content

**Critical Distinction**: Semantic similarity ≠ entailment

**Example of Similarity Failure**:
```
Claim: "Blend Capital offers 8.5% APY for USDC"
Source: "Blend Capital is a lending protocol on Stellar"

Semantic Similarity: HIGH (0.92) - both mention Blend Capital
NLI Entailment: NEUTRAL - source doesn't address APY claim

Result: UNSUPPORTED ❌
```

**NLI Labels**:
- **Entailment**: Source logically supports claim ✅
- **Contradiction**: Source contradicts claim ❌
- **Neutral**: Source doesn't address claim ⚠️

**Models** (in order of preference):
1. **Claude Sonnet 4.5**: 87% agreement with human experts (use this)
2. **SummaC-ZS**: 77% accuracy (open-source alternative)
3. **Custom fine-tuned**: For domain-specific verification

**Verification Logic**:
```python
for claim in atomic_claims:
    for citation in claim.citations:
        # Retrieve source content
        source_content = read_file(f"content_fetched/{citation.id}.txt")

        # Extract relevant passages (semantic search)
        passages = semantic_search(claim.text, source_content, top_k=3)

        entailment_results = []
        for passage in passages:
            # NLI entailment check (using Claude Sonnet 4.5)
            result = nli_verify(
                premise=passage,
                hypothesis=claim.text
            )

            entailment_results.append(result)

        # Claim is supported if ANY passage entails it
        if any(r.label == "entailment" and r.score > 0.8 for r in entailment_results):
            claim.verification_status = "supported"
            claim.supporting_passage = max(entailment_results, key=lambda x: x.score).passage
        else:
            claim.verification_status = "unsupported"
```

**NLI Prompt for Claude**:
```
You are a fact-checking expert using Natural Language Inference (NLI).

TASK: Determine if the SOURCE logically supports the CLAIM.

SOURCE (premise):
{source_passage}

CLAIM (hypothesis):
{atomic_claim}

CRITICAL RULES:
1. "Entailment" means SOURCE logically proves CLAIM is true
2. "Contradiction" means SOURCE proves CLAIM is false
3. "Neutral" means SOURCE doesn't address CLAIM (even if similar topic)

IMPORTANT: Semantic similarity ≠ entailment
- High similarity but no logical support = NEUTRAL
- Only mark "entailment" if SOURCE directly supports CLAIM

Respond with JSON only:
{
  "label": "entailment" | "contradiction" | "neutral",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "supporting_quote": "exact quote from source if entailment"
}
```

**Output**: `03_verification/nli_results.json`

```json
{
  "claim_1": {
    "claim": "Blend Capital offers 8.5% APY for USDC suppliers",
    "citation_id": "cite_1",
    "nli_result": {
      "label": "entailment",
      "confidence": 0.95,
      "reasoning": "Source states 'USDC Supply APY: 8.52%' which supports the claim",
      "supporting_quote": "USDC Supply APY: 8.52%"
    },
    "status": "supported"
  },
  "claim_3": {
    "claim": "Blend Capital has never been hacked",
    "citation_id": "cite_3",
    "nli_result": {
      "label": "neutral",
      "confidence": 0.88,
      "reasoning": "Source doesn't mention hack history",
      "supporting_quote": null
    },
    "status": "unsupported"
  }
}
```

#### Layer 4: SelfCheckGPT Consistency Checking

**Purpose**: Detect hallucinations via response variance

**Method**: Generate same claim multiple times with temperature, check consistency

**Theory**:
- **Factual knowledge**: Consistent across samples (low variance)
- **Hallucinations**: Inconsistent across samples (high variance)

**Process**:
```python
for claim in atomic_claims:
    responses = []

    for _ in range(5):  # Generate 5 samples
        prompt = f"According to {claim.source_url}, what is the {claim.topic}?"
        response = llm.generate(prompt, temperature=0.7)
        responses.append(response)

    # Calculate consistency (simplified - production uses embeddings)
    consistency_score = calculate_similarity(responses)

    if consistency_score < 0.7:
        claim.warning = "Low consistency - possible hallucination"
```

**Output**: `03_verification/consistency_checks.json`

```json
{
  "claim_1": {
    "claim": "Blend Capital offers 8.5% APY",
    "consistency_score": 0.94,
    "samples": [
      "8.52% APY for USDC",
      "8.5% APY for USDC suppliers",
      "USDC supply rate is 8.52%",
      "8.52% annual percentage yield",
      "8.5% APY"
    ],
    "status": "consistent"
  },
  "claim_2": {
    "claim": "Protocol X has 100M TVL",
    "consistency_score": 0.43,
    "samples": [
      "100M TVL",
      "75M TVL",
      "125M TVL",
      "approximately 100M",
      "TVL around 90M"
    ],
    "status": "inconsistent",
    "warning": "High variance - verify TVL claim"
  }
}
```

#### Verification Report Generation

**Purpose**: Summarize all 4 layers into actionable report

**Output**: `03_verification/verification_report.json`

```json
{
  "summary": {
    "total_claims": 25,
    "supported": 22,
    "unsupported": 3,
    "verification_rate": 0.88,
    "threshold": 0.90,
    "status": "NEEDS_REVISION"
  },
  "unsupported_claims": [
    {
      "claim_id": "claim_3",
      "claim": "Blend Capital has never been hacked",
      "citation_id": "cite_3",
      "url": "https://example.com/security-report",
      "failure_reason": "url_not_accessible",
      "layer_1_status": "failed_404",
      "recommendation": "Find alternative source or remove claim"
    },
    {
      "claim_id": "claim_7",
      "claim": "Protocol earns 50% of all fees",
      "citation_id": "cite_2",
      "url": "https://protocol.com/docs",
      "failure_reason": "nli_neutral",
      "layer_1_status": "accessible",
      "layer_2_status": "content_fetched",
      "layer_3_status": "neutral",
      "nli_confidence": 0.12,
      "supporting_quote": null,
      "recommendation": "Source doesn't support specific fee percentage - find better source or rewrite claim"
    },
    {
      "claim_id": "claim_15",
      "claim": "TVL is exactly $100M",
      "citation_id": "cite_4",
      "url": "https://defillama.com/protocol/x",
      "failure_reason": "low_consistency",
      "layer_1_status": "accessible",
      "layer_2_status": "content_fetched",
      "layer_3_status": "entailment",
      "layer_4_status": "inconsistent",
      "consistency_score": 0.45,
      "recommendation": "High variance in repeated queries - TVL may be stale/changing - add timestamp or range"
    }
  ],
  "supported_claims": [
    {
      "claim_id": "claim_1",
      "claim": "Blend Capital offers 8.5% APY for USDC",
      "verification": "all_layers_passed",
      "confidence": "high",
      "nli_score": 0.95,
      "consistency_score": 0.94
    }
  ],
  "quality_gate": {
    "threshold_met": false,
    "required_rate": 0.90,
    "actual_rate": 0.88,
    "action": "PROCEED_TO_REVISION"
  }
}
```

**Quality Thresholds**:
- **Minimum verification rate**: 90%
- **NLI confidence threshold**: 0.8
- **Consistency threshold**: 0.7
- **If rate < 90%**: Trigger revision stage

---

### Stage 5: Critique

**Purpose**: Quality assessment incorporating verification results

**Input**:
- `01_draft/initial_draft.md`
- `03_verification/verification_report.json`
**Tools**: `Read`, `Write`
**Output**: `04_critique/critique.md`

**Process**:
1. Read draft from `01_draft/`
2. Read verification report from `03_verification/`
3. Assess quality across dimensions:
   - **Citation accuracy** (from verification report)
   - **Coherence and flow**
   - **Completeness** (vs. original request)
   - **Clarity and readability**
4. Generate structured critique with actionable recommendations

**Critique Structure**:

```markdown
# Draft Critique

## Citation Quality: ⚠️ NEEDS WORK
- Verification rate: 88% (threshold: 90%)
- 3 unsupported claims detected
- Action required: Fix or remove unsupported claims

### Unsupported Claims to Address:
1. **claim_3**: "Blend Capital has never been hacked"
   - Issue: Source URL not accessible (404)
   - Recommendation: Find alternative source or remove claim

2. **claim_7**: "Protocol earns 50% of all fees"
   - Issue: Source doesn't support specific percentage (NLI neutral)
   - Recommendation: Find source with specific fee data or rewrite as "Protocol earns a portion of fees"

3. **claim_15**: "TVL is exactly $100M"
   - Issue: Low consistency across queries (TVL volatile)
   - Recommendation: Add timestamp "as of Nov 23, 2025" or use range "$95M-$105M"

## Coherence: ✅ GOOD
- Logical flow maintained throughout
- Clear transitions between sections
- Topic sentences effective

## Completeness: ✅ GOOD
- All aspects of original request addressed
- Adequate depth on each topic

## Clarity: ⚠️ MINOR ISSUES
- Paragraph 4 could be clearer (complex sentence structure)
- Technical jargon in paragraph 7 needs definition

## Recommended Actions:
1. **PRIORITY 1**: Fix 3 unsupported claims (required to meet 90% threshold)
2. **PRIORITY 2**: Simplify paragraph 4 sentence structure
3. **PRIORITY 3**: Define "collateralization ratio" in paragraph 7
```

**Prompt Pattern** (`prompts/critic.txt`):
```
You are a quality critic assessing a draft report.

INPUT FILES:
- Draft: {draft_file}
- Verification report: {verification_report_file}

ASSESSMENT DIMENSIONS:
1. Citation Quality (from verification report)
   - What is verification rate? (target: ≥90%)
   - Which claims are unsupported?
   - Why did they fail? (URL issue, NLI neutral, low consistency)

2. Coherence
   - Logical flow?
   - Clear transitions?
   - Consistent narrative?

3. Completeness
   - All aspects of request covered?
   - Adequate depth?

4. Clarity
   - Clear language?
   - Defined jargon?
   - Readable structure?

OUTPUT: Structured critique with prioritized recommendations
Save to: {output_file}
```

---

### Stage 6: Revise

**Purpose**: Fix unsupported claims based on critique

**Input**:
- `01_draft/initial_draft.md`
- `04_critique/critique.md`
- `03_verification/verification_report.json`
**Tools**: `Read`, `WebSearch`, `Write`
**Output**: `05_revision/revised_draft.md`

**Process**:
1. Read original draft, critique, and verification report
2. For each unsupported claim, choose strategy:
   - **Option A**: Find better source (WebSearch for authoritative citation)
   - **Option B**: Rewrite claim to match existing source
   - **Option C**: Remove claim if unverifiable
3. Apply other critique recommendations (clarity, coherence)
4. Save revised draft

**Strategy Priority**:
1. **Prefer finding better sources** over weakening claims
2. **Rewrite claims** if good source exists but claim is too specific
3. **Remove claims** only if no credible source can be found

**Example Revisions**:

**Claim 3** (URL not accessible):
```
Before: "Blend Capital has never been hacked [3]."
[3] https://example.com/security-report (404 error)

Action: WebSearch for "Blend Capital security audit hack history"
Found: https://certik.com/projects/blend-capital (accessible)

After: "Blend Capital has undergone security audits by CertiK with no major vulnerabilities found [3]."
[3] CertiK - Blend Capital Audit. https://certik.com/projects/blend-capital
```

**Claim 7** (NLI neutral):
```
Before: "Protocol earns 50% of all fees [2]."
Source says: "Protocol has a fee structure for operations."
NLI: Neutral (doesn't mention specific percentage)

Action: Rewrite to match source
After: "Protocol charges fees on operations, with a portion going to the treasury [2]."
```

**Claim 15** (Low consistency):
```
Before: "TVL is exactly $100M [4]."
Consistency: 0.45 (responses varied: $100M, $95M, $105M)

Action: Add timestamp or range
After: "As of November 23, 2025, TVL is approximately $100M [4]."
```

**Prompt Pattern** (`prompts/reviser.txt`):
```
You are a revision specialist fixing unsupported claims.

INPUT FILES:
- Original draft: {draft_file}
- Critique: {critique_file}
- Verification report: {verification_report}

YOUR TASK: Fix all unsupported claims to meet 90% verification threshold.

FOR EACH UNSUPPORTED CLAIM:
1. Read failure reason (URL issue, NLI neutral, low consistency)
2. Choose strategy:
   a) Find better source (use WebSearch)
   b) Rewrite claim to match existing source
   c) Remove claim if unverifiable

STRATEGY PRIORITY:
1. Prefer (a) finding better sources
2. Use (b) if source is good but claim too specific
3. Use (c) only if no credible source exists

ALSO ADDRESS:
- Other critique recommendations (clarity, coherence)

PRESERVE:
- All supported claims (don't change what works)
- Overall document structure
- Verified citations

OUTPUT: Revised draft to {output_file}
```

---

### Stage 7: Re-verify

**Purpose**: Validate that revisions fixed citation issues

**Input**: `05_revision/revised_draft.md`
**Tools**: Same as Stage 4 (verify)
**Output**: `06_re_verification/verification_report.json`

**Process**:
1. Re-extract atomic claims from revised draft (re-run Stage 3)
2. Re-run complete 4-layer verification pipeline (re-run Stage 4)
3. Generate new verification report
4. Check if verification rate now meets 90% threshold

**Success Criteria**:
- `verification_rate >= 0.90` ✅
- If still < 0.90, can iterate revision → re-verification (max 2-3 iterations)

**Example Re-verification Report**:

```json
{
  "summary": {
    "total_claims": 25,
    "supported": 23,
    "unsupported": 2,
    "verification_rate": 0.92,
    "threshold": 0.90,
    "status": "PASSED"
  },
  "improvements": {
    "before": 0.88,
    "after": 0.92,
    "claims_fixed": 1,
    "claims_removed": 0,
    "new_sources_added": 1
  },
  "remaining_issues": [
    {
      "claim_id": "claim_22",
      "status": "unsupported",
      "note": "Low priority - non-critical background claim"
    }
  ],
  "quality_gate": {
    "threshold_met": true,
    "action": "PROCEED_TO_STYLE"
  }
}
```

**If threshold not met**: Can iterate revision → re-verification (max 2-3 times)

---

### Stage 8: Style Application (Parameterized)

**Purpose**: Apply user-selected or auto-selected writing styleguide as final step

**Input**:
- `05_revision/revised_draft.md` (or `01_draft/initial_draft.md` if no revision needed)
- User-selected styleguide OR auto-selected based on content
**Tools**: `Read`, `Write`
**Output**: `07_style/final_report.md`

**Styleguide Parameterization**:
- **User-selected**: User specifies styleguide in request (`"style": "academic"`)
- **Auto-selected**: Agent analyzes content and chooses appropriate style
- **Default**: Technical documentation style

**Available Styleguides**:
1. **Academic** (`style_guides/academic.md`) - Formal, third-person, APA citations
2. **Technical** (`style_guides/technical.md`) - Clear, instructional, second-person
3. **Conversational** (`style_guides/conversational.md`) - Friendly, engaging, first-person
4. **DeFi Report** (`style_guides/defi_report.md`) - Financial, risk-aware, data-driven

**Process**:
1. Determine styleguide:
   ```python
   if user_specified_style:
       style_guide = load_style_guide(user_specified_style)
   else:
       style_guide = auto_select_style_guide(content_type, topic)
   ```

2. Read final draft (revised or initial)

3. Apply styleguide transformation:
   - **Tone**: formal/conversational/technical
   - **Voice**: third-person/second-person/first-person
   - **Structure**: paragraph length, transitions, section organization
   - **Vocabulary**: academic/technical/accessible
   - **Citation format**: APA/IEEE/inline

4. **PRESERVE** (critical):
   - All facts and claims (no content changes)
   - All citations and sources (exact URLs)
   - Verification status (don't introduce new unsupported claims)

5. Save styled report to `07_style/final_report.md`

**Auto-Selection Logic**:
```python
def auto_select_style_guide(content_type: str, topic: str) -> str:
    """
    Auto-select appropriate styleguide based on content.

    Rules:
    - DeFi/financial topics → defi_report.md
    - Technical documentation → technical.md
    - Research papers → academic.md
    - Blog posts/articles → conversational.md
    """
    if "defi" in topic.lower() or "yield" in topic.lower():
        return "style_guides/defi_report.md"
    elif "api" in topic.lower() or "documentation" in topic.lower():
        return "style_guides/technical.md"
    elif content_type == "research":
        return "style_guides/academic.md"
    else:
        return "style_guides/conversational.md"
```

**Example Style Transformations**:

**Academic Style**:
```markdown
# Before (neutral)
We found that Blend Capital offers good yields. Users can earn 8.5% APY.

# After (academic)
The research demonstrates that Blend Capital provides competitive yields for
liquidity providers. Empirical data indicates an annual percentage yield (APY)
of 8.5% for USDC suppliers, positioning the protocol favorably within the
Stellar ecosystem (Blend Capital Documentation, 2025).
```

**Technical Style**:
```markdown
# Before (neutral)
Blend Capital offers 8.5% APY for USDC suppliers.

# After (technical)
To earn yield on USDC:
1. Navigate to blend.capital
2. Connect your Stellar wallet
3. Supply USDC to the lending pool
4. Current APY: 8.5%

**Note**: APY rates are variable and subject to market conditions.
```

**Conversational Style**:
```markdown
# Before (neutral)
Blend Capital offers 8.5% APY for USDC suppliers.

# After (conversational)
Looking to put your USDC to work? Blend Capital's got you covered with a solid
8.5% APY. That's a pretty competitive rate in the Stellar DeFi space, and you
can start earning just by supplying your stablecoins to their lending pool.
```

**Prompt Pattern** (`prompts/style_applicator.txt`):
```
You are a style specialist applying a writing styleguide to a report.

INPUT FILES:
- Draft: {draft_file}
- Style guide: {style_guide_file}

YOUR TASK: Transform the draft to match the style guide.

APPLY:
- Tone (formal/conversational/technical)
- Voice (third-person/second-person/first-person)
- Vocabulary (academic/technical/accessible)
- Structure (paragraph length, transitions)
- Citation format (per style guide)

CRITICAL - PRESERVE:
- All facts and claims (no content changes)
- All citations and sources (exact URLs, no changes)
- Verification status (don't add unsupported claims)

PROCESS:
1. Read style guide to understand requirements
2. Transform draft to match style
3. Verify no facts or citations changed
4. Save to {output_file}

OUTPUT: Styled report preserving all verified content
```

**Example Style Guide** (`style_guides/academic.md`):

```markdown
# Academic Writing Style Guide

## Tone
- **Formal and objective**: Avoid contractions, colloquialisms, emotional language
- **Authoritative but accessible**: Expert voice without condescension
- **Evidence-based**: Claims supported by citations
- **Professional distance**: Maintain scholarly tone

## Voice
- **Third-person predominant**: "The research demonstrates..." NOT "We found..."
- **Active voice preferred**: "The agent verified citations" NOT "Citations were verified"
- **Passive acceptable for methods**: "Data was collected from..."

## Structure
- **Clear thesis** in introduction
- **Topic sentences** for each paragraph
- **Logical progression** with transitions
- **Evidence before interpretation**
- **Conclusion synthesizes** findings (not just summary)

## Paragraph Structure
- **Length**: 4-6 sentences (100-150 words)
- **Unity**: One main idea per paragraph
- **Coherence**: Smooth transitions between ideas

## Citations
- **Format**: APA 7th edition
- **In-text**: (Author, Year) or Author (Year)
- **Every claim requires citation**
- **Reference list**: Alphabetized, hanging indent

## Language
- **Precise terminology**: Use exact technical terms
- **Concise**: Eliminate redundancy
- **Define on first use**: Technical terms defined when introduced
- **Avoid jargon** where simpler terms exist

## Examples

### Poor:
"We think Blend Capital is pretty good for yields. It's got like 8.5% APY which is awesome!"

### Good:
"Empirical analysis indicates that Blend Capital provides competitive yields within the
Stellar DeFi ecosystem. Current data demonstrates an annual percentage yield (APY) of
8.5% for USDC suppliers, positioning the protocol favorably relative to alternative
lending platforms (Blend Capital Documentation, 2025)."
```

---

## Implementation

### Core Pipeline Class

```python
# backend/agent/ghostwriter/pipeline.py

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import json

class GhostwriterPipeline:
    """
    Filesystem-based ghostwriter with 8-stage citation verification.

    Stages:
    1. Research - Web search and source gathering
    2. Draft - Initial document from research
    3. Extract - Atomic claims and citations
    4. Verify - Multi-layer citation verification (CRITICAL)
    5. Critique - Quality assessment
    6. Revise - Fix unsupported claims
    7. Re-verify - Validate fixes
    8. Style - Apply user/auto-selected styleguide
    """

    def __init__(
        self,
        workspace_dir: Path = Path("workspace"),
        prompts_dir: Path = Path("prompts"),
        style_guides_dir: Path = Path("style_guides")
    ):
        self.workspace_dir = workspace_dir
        self.prompts_dir = prompts_dir
        self.style_guides_dir = style_guides_dir

        # Create directories
        self.workspace_dir.mkdir(exist_ok=True)
        (workspace_dir / "sessions").mkdir(exist_ok=True)
        (workspace_dir / "logs").mkdir(exist_ok=True)

    async def execute(
        self,
        request: str,
        style: Optional[str] = None,  # "academic" | "technical" | "conversational" | None (auto)
        min_verification_rate: float = 0.90,
        max_revision_iterations: int = 3
    ) -> Dict:
        """
        Execute complete 8-stage pipeline.

        Args:
            request: User's research request
            style: Styleguide to apply (or None for auto-select)
            min_verification_rate: Minimum verification threshold (default 0.90)
            max_revision_iterations: Max revision attempts (default 3)

        Returns:
            {
                "success": True,
                "session_id": "session_20251123_143022",
                "final_report": "path/to/07_style/final_report.md",
                "verification_rate": 0.92,
                "stages_completed": 8,
                "artifacts": {...}
            }
        """
        # Create session directory
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_dir = self.workspace_dir / "sessions" / session_id
        session_dir.mkdir(parents=True)

        # Create stage directories
        for i in range(8):
            stage_names = [
                "00_research",
                "01_draft",
                "02_extraction",
                "03_verification",
                "04_critique",
                "05_revision",
                "06_re_verification",
                "07_style"
            ]
            (session_dir / stage_names[i]).mkdir()

        try:
            # Stage 1: Research
            await self._stage_1_research(session_dir, request)

            # Stage 2: Draft
            await self._stage_2_draft(session_dir)

            # Stage 3: Extract
            await self._stage_3_extract(session_dir)

            # Stage 4: Verify
            verification_result = await self._stage_4_verify(session_dir)

            # Stage 5: Critique
            await self._stage_5_critique(session_dir, verification_result)

            # Revision loop (if needed)
            iteration = 0
            while (
                verification_result["summary"]["verification_rate"] < min_verification_rate
                and iteration < max_revision_iterations
            ):
                # Stage 6: Revise
                await self._stage_6_revise(session_dir, verification_result)

                # Stage 7: Re-verify
                verification_result = await self._stage_7_reverify(session_dir)

                iteration += 1

            # Stage 8: Style
            final_style = style or self._auto_select_style(request)
            await self._stage_8_style(session_dir, final_style)

            # Read final report
            final_report_path = session_dir / "07_style" / "final_report.md"
            final_report = final_report_path.read_text()

            return {
                "success": True,
                "session_id": session_id,
                "final_report_path": str(final_report_path),
                "final_report_content": final_report,
                "verification_rate": verification_result["summary"]["verification_rate"],
                "stages_completed": 8,
                "revision_iterations": iteration,
                "style_applied": final_style,
                "artifacts": {
                    "research_sources": list((session_dir / "00_research").glob("*.md")),
                    "verification_report": str(session_dir / "06_re_verification" / "verification_report.json"),
                    "transcript": str(session_dir / "transcript.txt")
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "session_dir": str(session_dir)
            }

    async def _stage_1_research(self, session_dir: Path, request: str):
        """Execute research stage"""
        # Load prompt
        prompt = (self.prompts_dir / "researcher.txt").read_text()
        prompt = prompt.format(
            request=request,
            output_dir=session_dir / "00_research"
        )

        # Execute research agent (uses WebSearch, Write tools)
        # Implementation details...

    async def _stage_4_verify(self, session_dir: Path) -> Dict:
        """Execute 4-layer verification"""
        # Load atomic claims and citations
        claims = json.loads((session_dir / "02_extraction" / "atomic_claims.json").read_text())
        citations = json.loads((session_dir / "02_extraction" / "citations.json").read_text())

        # Layer 1: URL checks
        url_checks = await self._verify_urls(citations)

        # Layer 2: Content fetching
        await self._fetch_content(citations, session_dir / "03_verification" / "content_fetched")

        # Layer 3: NLI entailment
        nli_results = await self._verify_nli_entailment(claims, citations, session_dir)

        # Layer 4: SelfCheckGPT consistency
        consistency_results = await self._verify_consistency(claims, citations)

        # Generate verification report
        verification_report = self._generate_verification_report(
            claims, citations, url_checks, nli_results, consistency_results
        )

        # Save report
        report_path = session_dir / "03_verification" / "verification_report.json"
        report_path.write_text(json.dumps(verification_report, indent=2))

        return verification_report

    def _auto_select_style(self, request: str) -> str:
        """Auto-select appropriate styleguide"""
        request_lower = request.lower()

        if any(kw in request_lower for kw in ["defi", "yield", "tvl", "apy"]):
            return "defi_report"
        elif any(kw in request_lower for kw in ["api", "documentation", "tutorial"]):
            return "technical"
        elif any(kw in request_lower for kw in ["research", "study", "analysis"]):
            return "academic"
        else:
            return "conversational"
```

---

## Success Metrics

### Quality Metrics

| Metric | Target | Critical? |
|--------|--------|-----------|
| **Verification Rate** | ≥90% | ✅ CRITICAL |
| **Citation Accessibility** | ≥95% URLs accessible | ✅ CRITICAL |
| **NLI Entailment Confidence** | ≥0.8 for supported claims | ✅ CRITICAL |
| **Consistency Score** | ≥0.7 (SelfCheckGPT) | ⚠️ WARNING |
| **Revision Success Rate** | ≥80% unsupported claims fixed | ✅ IMPORTANT |

### Performance Metrics

| Metric | Target |
|--------|--------|
| **End-to-End Latency** | <10 minutes (1000-word report) |
| **Cost per Report** | <$2 (API costs) |
| **Concurrent Sessions** | ≥10 simultaneous |
| **Pipeline Success Rate** | ≥99% completion |

### User Experience Metrics

| Metric | Target |
|--------|--------|
| **Transparency** | 100% verification results visible |
| **Resumability** | Resume from any stage on failure |
| **Auditability** | Complete transcript + artifacts |
| **Debuggability** | Human-readable intermediate files |

---

## Migration from Current claude_sdk_wrapper.py

### Phase 1: Build Core Pipeline (Week 1-2)

**Tasks**:
- [ ] Create `backend/agent/ghostwriter/` module structure
- [ ] Implement `GhostwriterPipeline` class
- [ ] Create all 8 prompt files in `prompts/`
- [ ] Build filesystem checkpoint system
- [ ] Implement Stages 1-2 (research, draft)
- [ ] Test basic research → draft flow

**Deliverables**:
- Working research and draft stages
- Filesystem session management
- Transcript logging

### Phase 2: Citation Verification (Week 2-3)

**Tasks**:
- [ ] Implement Stage 3 (atomic fact extraction)
- [ ] Build Stage 4 Layer 1 (URL verification)
- [ ] Build Stage 4 Layer 2 (content fetching)
- [ ] Build Stage 4 Layer 3 (NLI entailment) **CRITICAL**
- [ ] Build Stage 4 Layer 4 (SelfCheckGPT consistency)
- [ ] Create verification report generation
- [ ] Test with citation-heavy documents

**Deliverables**:
- Production-grade 4-layer verification
- Verification reports with actionable insights
- Unsupported claim detection

### Phase 3: Quality Loop (Week 3-4)

**Tasks**:
- [ ] Implement Stage 5 (critique)
- [ ] Implement Stage 6 (revision)
- [ ] Implement Stage 7 (re-verification)
- [ ] Add iteration logic (max 3 revisions)
- [ ] Test full pipeline with difficult cases
- [ ] Validate 90% threshold enforcement

**Deliverables**:
- Complete critique → revise → re-verify loop
- Quality gates enforced
- Iterative improvement working

### Phase 4: Style & DeFi Integration (Week 4-5)

**Tasks**:
- [ ] Implement Stage 8 (style application)
- [ ] Create 4 styleguides (academic, technical, conversational, defi_report)
- [ ] Implement auto-style-selection logic
- [ ] Create `DeFiGhostwriter` extension class
- [ ] Migrate existing DeFi methods from `claude_sdk_wrapper.py`
- [ ] Update API endpoints

**Deliverables**:
- Parameterized styleguide system
- DeFi-specific research reports
- Backward compatibility maintained

### Phase 5: Production Hardening (Week 5-6)

**Tasks**:
- [ ] Add comprehensive error handling
- [ ] Implement retry logic for transient failures
- [ ] Add monitoring/metrics collection
- [ ] Create API endpoints with proper validation
- [ ] Write user documentation
- [ ] Create example reports

**Deliverables**:
- Production-ready system
- API integration complete
- Documentation and examples

---

## Key Architectural Decisions

### 1. ✅ Filesystem Over Graphs

**Decision**: Use filesystem for intermediate state, not in-memory graphs

**Rationale**:
- Simpler to debug (inspect files directly with `cat`, `less`, etc.)
- Durable across crashes (can resume from any stage)
- Complete audit trail (every session preserved)
- Human-in-the-loop friendly (can pause, review, manually edit, resume)

**Trade-offs**: Slightly slower than in-memory, but benefits vastly outweigh cost

### 2. ✅ Citation Verification as Central Process

**Decision**: Multi-layer verification is **non-negotiable**, not optional

**Rationale**:
- LLM citation hallucination is **critical problem** (47% error rate)
- Legal/academic/medical **consequences of bad citations**
- Multi-layer defense catches different failure modes
- 90% threshold ensures high quality before release

**Trade-offs**: Slower pipeline, but **quality is paramount**

### 3. ✅ Atomic Fact Decomposition

**Decision**: Verify atomic claims, not full paragraphs or documents

**Rationale**:
- **Precision**: Identify specific unsupported claims (not just "paragraph has issues")
- **Debugging**: Easier to fix specific issues
- **Coverage**: Don't miss claims buried in complex sentences

**Trade-offs**: More processing (extract N claims instead of 1 doc), but better quality

### 4. ✅ NLI Entailment Over Similarity

**Decision**: Use NLI for logical verification, not semantic similarity

**Rationale**:
- **Similarity can be misleading** (high similarity ≠ logical support)
- **NLI checks logical support relationship** (entailment/contradiction/neutral)
- **Better aligns with human verification** (87% agreement with experts)

**Trade-offs**: More expensive models, but correctness is critical

### 5. ✅ Prompt Files, Not Code

**Decision**: Agent behavior defined in `.txt` files, not Python code

**Rationale**:
- **Non-engineers can iterate** on prompts (no code changes needed)
- **Version control** for prompt evolution (git tracks .txt changes)
- **Clear separation** of logic (Python) and instructions (prompts)
- **Easier A/B testing** (swap prompt files without deployment)

**Trade-offs**: Need to load files at runtime, but flexibility is worth it

### 6. ✅ Styleguide Parameterization

**Decision**: Styleguide applied as **final step**, **user-selected or auto-selected**

**Rationale**:
- **Separation of concerns**: Content verification independent of style
- **User choice**: Different audiences need different styles
- **Auto-selection**: Agent can choose appropriate style if user doesn't specify
- **Preserve verified content**: Style changes tone/structure, not facts/citations

**Trade-offs**: Additional stage, but essential for professional output

---

## References

### Citation Verification Research

1. **LLM-Check** (NeurIPS 2024) - 45-450x faster hallucination detection
   - https://openreview.net/pdf?id=LYx4w3CAgy
2. **VeriScore** (2024) - Atomic fact verification framework
3. **SummaC-ZS** - 77% accuracy NLI model for citation checking
4. **REFIND** (SemEval 2025) - Span-level hallucination detection
   - https://www.getmaxim.ai/articles/llm-hallucination-detection-and-mitigation-best-techniques/
5. **Mata v. Avianca** (2023) - Legal case highlighting citation fabrication risks
6. **University of Mississippi Study** (2024) - 47% citation error rate
7. **LLM Hallucination Survey** (arXiv:2311.05232)
   - https://arxiv.org/abs/2311.05232
8. **Lakera AI: Guide to Hallucinations**
   - https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models
9. **Voiceflow: Preventing LLM Hallucinations**
   - https://www.voiceflow.com/blog/prevent-llm-hallucinations

### Filesystem Orchestration

10. **Anthropic: Multi-agent research system**
    - https://www.anthropic.com/engineering/multi-agent-research-system
11. **Claude Agent SDK: Subagents**
    - https://docs.claude.com/en/docs/agent-sdk/subagents
12. **Research agent demo** (GitHub)
    - https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent

### Writing Styleguides

13. **Academic Tone and Language**
    - https://uq.pressbooks.pub/academicwritingskills/chapter/academic-tone-and-language/
14. **USC: Academic Writing Style**
    - https://libguides.usc.edu/writingguide/academicwriting
15. **Technical Communications: Voice and Tone**
    - https://ohiostate.pressbooks.pub/feptechcomm/chapter/3-1-voice-tone/
16. **Style Manual: Voice and Tone**
    - https://www.stylemanual.gov.au/writing-and-designing-content/clear-language-and-writing-style/voice-and-tone

---

**Status**: ✅ Architecture Committed - Ready for Phase 1 Implementation

**Next Steps**: Begin Phase 1 (Core Pipeline) - Weeks 1-2
