# Ghostwriter Pipeline Redesign: Hypothesis-Driven Research

**Date**: 2025-11-23
**Status**: Design Document
**Priority**: Critical - Citation Veracity #1, #2, #3

---

## Executive Summary

This document proposes a complete redesign of the Ghostwriter pipeline from a **bottom-up source-gathering approach** to a **top-down hypothesis-driven research methodology**. The new approach treats AI research as a scientific process: form hypotheses, grade by certitude, then search the web to falsify or buttress each thesis.

**Core Philosophy**: Web searches are experiments to test hypotheses, not blind data gathering.

---

## Current Pipeline Issues

### 1. Temporary File Storage ❌
**Location**: `test_ghostwriter_pipeline.py:43`
```python
workspace_root = "/tmp/ghostwriter_test"
```
**Problem**: All research outputs saved to `/tmp` are lost on reboot.
**Impact**: Valuable research data is ephemeral.
**Fix**: Change to persistent location: `/home/user/tuxedo/ghostwriter_sessions`

---

### 2. Sequential Source Gathering (Very Slow) ❌
**Location**: `prompts/researcher.txt:6`, `pipeline.py:267-305`

**Current Flow**:
```
3 researchers (parallel)
  └─> Each executes 3-5 searches (sequential)
      └─> Each search: max_results=5
      └─> Total: 9-15 sequential API calls
      └─> Result: ~45-75 sources gathered slowly
```

**Problems**:
- Researchers execute searches sequentially via bash CLI
- Only 5 results per search (Tavily supports 20)
- No batch fetching or parallelization within researchers
- Target of 20-60 sources requires many slow sequential calls

**Math**:
- **Current**: 3 researchers × 5 searches × 5 results = 75 results (slow)
- **Optimized**: 3 researchers × 2 searches × 20 results = 120 results (fast)

---

### 3. Stuck in Research Loop ❌
**Location**: `pipeline.py:211-265` (researcher logic)

**Root Cause**: Vague completion criteria in researcher prompt:
```
YOUR TASK:
1. Execute 3-5 WebSearch queries to find authoritative sources
2. For each source: extract key information, verify URL
3. Save each source to source_N.md in the current directory
```

**Problems**:
- No explicit stop condition
- Agents may endlessly verify/review sources
- `conv.run()` blocks until agent decides it's "done" (may never happen)
- No timeout or iteration limit

---

### 4. Logs Extremely Verbose ❌
**Location**: `test_ghostwriter_pipeline.py:23`

**Current Logging**:
```python
logging.basicConfig(
    level=logging.INFO,  # Logs EVERYTHING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**What Gets Logged** (with 3 researchers × 8 stages):
- Every OpenHands SDK tool call
- Every LLM request/response (full prompts!)
- All Tavily API calls and responses
- File operations, terminal commands
- **Result**: Hundreds of log lines, impossible to read or pass to LLM

**Fix**:
```python
logging.basicConfig(level=logging.WARNING)  # Only warnings/errors
# Add structured progress indicators instead
```

---

### 5. Architecture is Backwards ❌
**Current Flow** (Bottom-Up: Sources First):
```
1. Research    → Gather 45-75 sources blindly
2. Draft       → Try to synthesize everything
3. Extract     → Pull out claims
4. Verify      → Check if sources support claims
5. Critique    → Realize half the sources are irrelevant
6. Revise      → Try to fix it
```

**Problems**:
- Wastes time gathering irrelevant sources
- No coherent thesis before research
- Hard to know what sources are needed
- "Source salad" instead of thesis-driven writing
- **Citation risk**: Writing claims, then finding sources is backwards

---

### 6. Tavily Results Too Low ❌
**Locations**:
- `openhands_websearch.py:28` → `max_results: int = 5`
- `websearch_tool.py:47` → `max_results: int = 5`
- `websearch_cli.py:45` → `default=5`
- `researcher.txt:42` → `--max-results 5`

**Tavily API Capability**: Max 20 results per call
**Current Usage**: 5 results (only 25% of capacity)
**Fix**: Change all defaults to `20`

---

## New Architecture: Hypothesis-Driven Research

### Philosophical Framework

**Research as Scientific Method**:
1. **Form Multiple Hypotheses** - Generate competing explanations/positions
2. **Grade by Certitude** - Assign confidence scores (0.0-1.0) based on prior knowledge
3. **Design Experiments** - Craft web searches to test each hypothesis
4. **Falsify or Buttress** - Update certitude based on evidence
5. **Iterate** - Refine hypotheses, discard falsified ones, strengthen supported ones
6. **Synthesize** - Write from strongest supported hypotheses

**Key Principle**: Web searches are experiments to test hypotheses, not data mining.

---

### Stage-by-Stage Redesign

#### **Stage 1: Hypothesis Formation** (Sonnet)
**Input**: Research topic
**Output**: Multiple competing hypotheses with initial certitude scores

**Process**:
```
Given topic: "DeFi yield farming on Stellar blockchain"

Generate 3-5 hypotheses:
1. [Certitude: 0.7] Stellar offers lower transaction costs than Ethereum
2. [Certitude: 0.5] Blend Capital provides competitive APYs vs other chains
3. [Certitude: 0.3] Stellar DeFi ecosystem is less mature than competitors
4. [Certitude: 0.6] Non-custodial vaults reduce user risk in yield farming
5. [Certitude: 0.4] Stellar's consensus mechanism enables faster settlements
```

**Prompt Instructions**:
- Generate diverse hypotheses (some supporting, some critical)
- Assign certitude based on general knowledge (no web search yet)
- Include specific, testable claims
- Flag hypotheses as [NEEDS_EVIDENCE], [LIKELY_TRUE], [UNCERTAIN]

**Tools**: None (pure reasoning)
**Output File**: `00_hypotheses/initial_hypotheses.json`

---

#### **Stage 2: Experimental Design** (Sonnet)
**Input**: Hypotheses with certitude scores
**Output**: Targeted search queries to test each hypothesis

**Process**:
```
Hypothesis: [Certitude: 0.7] Stellar offers lower transaction costs than Ethereum

Experimental Searches:
1. "Stellar transaction fees 2025 comparison Ethereum"
2. "Stellar average transaction cost data"
3. "Ethereum gas fees vs Stellar fees benchmarks"

Expected Evidence:
- Falsify: If Ethereum fees are actually lower
- Buttress: If Stellar fees are 10x-100x lower
- Neutral: If costs are comparable
```

**Prompt Instructions**:
- For each hypothesis, design 1-3 targeted searches
- Use max_results=20 to gather comprehensive evidence
- Prioritize recent sources (2024-2025)
- Focus on authoritative sources (academic, official docs, benchmarks)

**Tools**: None (planning only)
**Output File**: `01_experimental_design/search_plan.json`

---

#### **Stage 3: Parallel Experimentation** (Parallel Haiku)
**Input**: Search plan from Stage 2
**Output**: Evidence bundles for each hypothesis

**Process**:
```
Spawn 5-10 parallel Haiku researchers
Each researcher:
1. Gets assigned 1-2 hypotheses
2. Executes targeted searches (max_results=20)
3. Saves evidence to: evidence_hypothesis_N.md

Format per evidence file:
---
hypothesis_id: 1
hypothesis: "Stellar offers lower transaction costs than Ethereum"
initial_certitude: 0.7
---

# Search 1: "Stellar transaction fees 2025"
## Results:
[Source 1] URL | Title | Date | Key Evidence | Verdict: BUTTRESS/FALSIFY/NEUTRAL
[Source 2] ...

# Summary:
Evidence quality: HIGH/MEDIUM/LOW
Suggested certitude update: 0.7 → 0.85
Reasoning: Found 5 authoritative sources confirming 100x lower fees
```

**Prompt Instructions** (researcher.txt):
```
You are testing this hypothesis: {hypothesis}

Execute {num_searches} targeted searches with --max-results 20
For EACH source, determine:
1. Does it BUTTRESS (support) the hypothesis?
2. Does it FALSIFY (contradict) the hypothesis?
3. Is it NEUTRAL (irrelevant or inconclusive)?

Save evidence to: evidence_hypothesis_{id}.md
STOP after executing all searches and saving the evidence file.
```

**Tools**: TerminalTool (websearch), FileEditorTool
**Output Files**: `02_evidence/evidence_hypothesis_*.md`

---

#### **Stage 4: Update Certitudes** (Haiku)
**Input**: All evidence files from Stage 3
**Output**: Updated hypothesis certitudes

**Process**:
```
Hypothesis 1: "Stellar offers lower transaction costs than Ethereum"
Initial Certitude: 0.7

Evidence Summary:
- 8 sources BUTTRESS (authoritative, recent)
- 1 source NEUTRAL (outdated)
- 0 sources FALSIFY

Updated Certitude: 0.95
Status: WELL-SUPPORTED → Include in draft
```

**Certitude Update Rules**:
- **0.0-0.3**: FALSIFIED → Discard or invert hypothesis
- **0.3-0.6**: UNCERTAIN → Flag as [NEEDS_MORE_RESEARCH] or omit
- **0.6-0.8**: LIKELY → Include with hedging language ("likely", "suggests")
- **0.8-1.0**: WELL-SUPPORTED → Include as confident claim

**Tools**: FileEditorTool
**Output File**: `03_updated_hypotheses/certitude_updates.json`

---

#### **Stage 5: Thesis-Driven Draft** (Sonnet)
**Input**: Updated hypotheses + evidence files
**Output**: Coherent draft with inline citations

**Process**:
```
Write from strongest hypotheses first (certitude ≥ 0.6)

Structure:
1. Introduction - State thesis based on highest-certitude hypotheses
2. Supporting Arguments - Use certitude 0.8+ hypotheses
3. Nuanced Discussion - Include certitude 0.6-0.8 with hedging
4. Counterarguments - Address falsified hypotheses (certitude < 0.3)
5. Conclusion - Synthesize strongest findings

Citation Style:
"Stellar's transaction costs are significantly lower than Ethereum's,
with average fees under $0.01 compared to Ethereum's $5-50 range [1][2][3]."

[1] https://stellar.org/blog/transaction-costs-2025
[2] https://example.com/defi-fee-comparison
[3] https://academic-source.edu/blockchain-costs
```

**Key Principle**: Only write claims with certitude ≥ 0.6. Never write unsourced claims.

**Tools**: FileEditorTool
**Output Files**:
- `04_draft/thesis_driven_draft.md`
- `04_draft/citations.json`

---

#### **Stage 6: Citation Verification** (Parallel Haiku)
**Input**: Draft + citations.json
**Output**: Verification report

**3-Layer Verification** (same as current):
1. **Layer 1**: URL Check - curl -I to verify URLs exist
2. **Layer 2**: Content Fetch - Download source content
3. **Layer 3**: Claim Verification - Check if content supports claim

**Verification Rules**:
- **VERIFIED**: URL exists, content fetched, claim supported
- **PARTIAL**: URL exists, content fetched, claim partially supported
- **FAILED**: URL broken, content unavailable, or claim not supported

**Threshold**: 90% verification rate (configurable)

**Tools**: TerminalTool, FileEditorTool
**Output File**: `05_verification/verification_report.json`

---

#### **Stage 7: Revision (Only If Needed)** (Sonnet)
**Input**: Draft + verification report
**Output**: Revised draft with only verified claims

**Process**:
- If verification rate ≥ 90%: **Skip this stage**
- If verification rate < 90%:
  1. Remove claims with FAILED citations
  2. Hedge claims with PARTIAL verification
  3. Re-search for better sources if needed
  4. Re-verify updated claims

**Max Iterations**: 1 (not 3!)

**Tools**: FileEditorTool, TerminalTool (websearch)
**Output File**: `06_revision/revised_draft.md` (only if needed)

---

#### **Stage 8: Style & Polish** (Sonnet)
**Input**: Final verified draft
**Output**: Styled report

**Process**:
- Apply style guide (technical, academic, conversational, defi_report)
- Preserve all citations and factual claims
- Format for readability
- Add metadata (word count, source count, verification rate)

**Tools**: FileEditorTool
**Output File**: `07_final/final_report.md`

---

## Citation Veracity Safeguards

**Priority 1, 2, 3**: Citation accuracy

### Risk Mitigation

**Risk 1: Hallucinated Sources**
- **Current Mitigation**: 3-layer URL verification ✅
- **New Mitigation**: Only write claims from evidence files ✅
- **Gap Addressed**: Hypotheses formed before searching prevents post-hoc rationalization

**Risk 2: Real URL, Wrong Content**
- **Current Mitigation**: Layer 3 fetches content and verifies claims ✅
- **New Mitigation**: Claim must match evidence file quote ✅
- **Gap Addressed**: Evidence collected during experimentation, not after drafting

**Risk 3: Outdated Information**
- **Current Mitigation**: None ❌
- **New Mitigation**: Prioritize 2024-2025 sources ✅
- **New Mitigation**: Include publication dates in citations ✅

**Risk 4: Cherry-Picked Sources**
- **Current Mitigation**: None ❌
- **New Mitigation**: Hypothesis-driven search tests both support and falsification ✅
- **New Mitigation**: Include falsified hypotheses in "Counterarguments" section ✅

**Risk 5: Misleading Context**
- **Current Mitigation**: None ❌
- **New Mitigation**: Evidence files include full context, not just quotes ✅
- **New Mitigation**: Certitude grading prevents overconfident claims ✅

---

## Implementation Roadmap

### Phase 1: Quick Wins (Immediate)

**1.1 Fix File Storage**
```python
# test_ghostwriter_pipeline.py:43
workspace_root = "/home/user/tuxedo/ghostwriter_sessions"
```

**1.2 Increase Tavily Results**
```python
# openhands_websearch.py:28
max_results: int = 20  # was 5

# websearch_cli.py:45
default=20  # was 5

# researcher.txt:42
--max-results 20  # was 5
```

**1.3 Reduce Logging Verbosity**
```python
# test_ghostwriter_pipeline.py:23
logging.basicConfig(
    level=logging.WARNING,  # was INFO
    format='%(levelname)s - %(message)s'  # simpler format
)

# Add structured progress:
print(f"[Stage 1/8] Hypothesis Formation... ", end="", flush=True)
# ... run stage ...
print("✓ Complete (3 hypotheses generated)")
```

**1.4 Fix Researcher Completion Criteria**
```python
# prompts/researcher.txt
YOUR TASK:
1. Execute 2-3 WebSearch queries (--max-results 20)
2. Save results to evidence_hypothesis_{id}.md
3. STOP immediately after saving the evidence file
4. DO NOT re-verify, re-search, or loop

SUCCESS CRITERIA: File evidence_hypothesis_{id}.md exists
```

**Estimated Time**: 1-2 hours
**Impact**: Immediate speed improvement, readable logs, reliable completion

---

### Phase 2: Architectural Shift (Medium-Term)

**2.1 Implement New Stages**
- Create: `prompts/hypothesis_former.txt` (Stage 1)
- Create: `prompts/experimental_designer.txt` (Stage 2)
- Update: `prompts/researcher.txt` → hypothesis-testing format (Stage 3)
- Create: `prompts/certitude_updater.txt` (Stage 4)
- Update: `prompts/drafter.txt` → thesis-driven format (Stage 5)

**2.2 Update Pipeline Code**
```python
# pipeline.py
async def run_stage_1_hypotheses(self, topic: str) -> Dict[str, Any]:
    """Stage 1: Form multiple hypotheses with certitude scores."""

async def run_stage_2_experimental_design(self) -> Dict[str, Any]:
    """Stage 2: Design targeted searches for each hypothesis."""

async def run_stage_3_experimentation(self) -> Dict[str, Any]:
    """Stage 3: Execute searches, gather evidence."""

async def run_stage_4_update_certitudes(self) -> Dict[str, Any]:
    """Stage 4: Update hypothesis certitudes based on evidence."""

async def run_stage_5_thesis_draft(self) -> Dict[str, Any]:
    """Stage 5: Write from highest-certitude hypotheses."""

# Stages 6-8 remain similar (verify, revise if needed, style)
```

**2.3 Update Directory Structure**
```
session_YYYYMMDD_HHMMSS/
├── 00_hypotheses/
│   └── initial_hypotheses.json
├── 01_experimental_design/
│   └── search_plan.json
├── 02_evidence/
│   ├── evidence_hypothesis_1.md
│   ├── evidence_hypothesis_2.md
│   └── ...
├── 03_updated_hypotheses/
│   └── certitude_updates.json
├── 04_draft/
│   ├── thesis_driven_draft.md
│   └── citations.json
├── 05_verification/
│   └── verification_report.json
├── 06_revision/ (optional)
│   └── revised_draft.md
└── 07_final/
    └── final_report.md
```

**Estimated Time**: 1-2 days
**Impact**: Complete architectural transformation, citation veracity guaranteed

---

### Phase 3: Advanced Optimizations (Future)

**3.1 Parallel Tavily Batching**
- Batch multiple searches into single async calls
- Use `asyncio.gather()` for true parallelization

**3.2 Certitude-Based Iteration**
- Automatically re-search for low-certitude hypotheses (0.4-0.6)
- Stop when all included hypotheses ≥ 0.8

**3.3 Interactive Mode**
- Allow user to review hypotheses before searching
- Flag interesting hypotheses for deeper investigation

**3.4 Source Quality Scoring**
- Academic papers: 1.0
- Official documentation: 0.9
- Major publications: 0.8
- Blogs: 0.5
- Weight certitude updates by source quality

**Estimated Time**: 1 week
**Impact**: Production-ready research pipeline

---

## Success Metrics

### Speed
- **Current**: ~15-30 minutes for 3 researchers × 5 searches
- **Target**: ~5-10 minutes for hypothesis formation + targeted research

### Source Quality
- **Current**: ~75 random sources, many irrelevant
- **Target**: 20-60 targeted sources, all relevant to specific hypotheses

### Citation Veracity
- **Current**: ~80% verification rate (post-hoc checking)
- **Target**: ≥95% verification rate (hypothesis-driven prevents hallucination)

### Readability
- **Current**: Hundreds of log lines, impossible to debug
- **Target**: Clean progress indicators, warnings/errors only

### Coherence
- **Current**: "Source salad" - synthesis of random findings
- **Target**: Thesis-driven narrative from tested hypotheses

---

## Example: Before vs After

### Before (Current Pipeline)

```
[INFO] Creating researcher 1...
[INFO] Researcher 1 executing search: "DeFi yield farming"
[INFO] Tavily API call: max_results=5
[INFO] Got 5 results
[INFO] Researcher 1 saving source_1.md
[INFO] Researcher 1 executing search: "Stellar blockchain"
[INFO] Tavily API call: max_results=5
... (300+ log lines) ...

Output: 75 sources, some relevant, some not
Draft: Tries to synthesize everything
Verification: 80% of citations valid
```

### After (Hypothesis-Driven)

```
[Stage 1/8] Hypothesis Formation... ✓ Complete (5 hypotheses)
[Stage 2/8] Experimental Design... ✓ Complete (12 searches planned)
[Stage 3/8] Parallel Experimentation... ✓ Complete (240 sources, 12 evidence files)
[Stage 4/8] Update Certitudes... ✓ Complete (3 well-supported, 1 falsified, 1 uncertain)
[Stage 5/8] Thesis-Driven Draft... ✓ Complete (2,500 words, 35 citations)
[Stage 6/8] Citation Verification... ✓ Complete (97% verified)
[Stage 7/8] Revision... ⊘ Skipped (verification ≥90%)
[Stage 8/8] Style & Polish... ✓ Complete

Output: 35 carefully selected sources
Draft: Coherent thesis from tested hypotheses
Verification: 97% of citations valid
```

---

## Conclusion

The hypothesis-driven approach transforms Ghostwriter from a **source aggregator** into a **scientific research tool**. By treating web searches as experiments to test hypotheses, we:

1. **Eliminate wasted effort** - Only gather sources relevant to specific claims
2. **Improve citation veracity** - Claims are tested before writing, not after
3. **Increase coherence** - Draft follows from tested hypotheses, not random synthesis
4. **Reduce time** - Targeted searches (max_results=20) gather more data faster
5. **Enable falsification** - Actively seek counterevidence, not just confirmation

**Next Step**: Implement Phase 1 quick wins, then proceed to Phase 2 architectural shift.

---

**Document Version**: 1.0
**Author**: Claude Code
**Review Status**: Awaiting approval to implement
