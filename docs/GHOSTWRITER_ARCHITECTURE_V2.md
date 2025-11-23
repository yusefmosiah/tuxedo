# Ghostwriter Architecture V2: Filesystem-Based Research Agent

**Date**: 2025-11-23
**Status**: Architectural Research
**Purpose**: General-purpose deep research ghostwriter with filesystem orchestration

---

## Executive Summary

This proposal outlines a **filesystem-based research ghostwriter** that:

1. **Prevents citation hallucinations** (THE MOST CRITICAL REQUIREMENT)
2. **Uses filesystem for orchestration** (not LangGraph)
3. **Manages intermediate artifacts** (research notes, drafts, citations)
4. **Applies writing styleguides** (tone, voice, structure - NOT visual design)
5. **Separates domain logic** (DeFi research as pluggable module)

Based on [Anthropic's multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) and [Claude Agent SDK demos](https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent).

---

## Core Philosophy: Artifacts Over State

**Traditional approach (wrong)**:
```
Agent → generates response → passes to next agent → information loss
```

**Filesystem approach (correct)**:
```
Agent → writes artifact to disk → lightweight reference → next agent reads artifact
```

**Benefits**:
- No "game of telephone" information loss
- Persistent intermediate results for debugging
- Reduces token overhead (references instead of full content)
- Enables asynchronous parallel execution
- Audit trail for citation verification

From Anthropic: *"Specialized agents create outputs that persist independently"* - [source](https://www.anthropic.com/engineering/multi-agent-research-system)

---

## Critical Requirement: Citation Checking

### Why This is THE MOST Important Part

LLMs hallucinate citations in two ways:
1. **Fabrication**: Completely invented URLs, papers, or sources
2. **Twisting**: Real sources cited but misrepresenting their content

From research: *"Even well-curated RAG pipelines can fabricate citations, and the most promising systems add span-level verification where each claim is matched against retrieved evidence and flagged if unsupported"* - [REFIND SemEval 2025 benchmark](https://www.getmaxim.ai/articles/llm-hallucination-detection-and-mitigation-best-techniques/)

### Citation Verification Strategy

**Multi-layered approach** (Stanford 2024: 96% hallucination reduction):

1. **Span-level verification**: Match each claim to specific evidence
2. **SelfCheckGPT**: Generate multiple responses, check consistency
3. **External validation**: Cross-reference with trusted sources
4. **Must-cite rules**: Block outputs without supporting evidence
5. **Source content verification**: Fetch and verify claim support

Sources:
- [LLM Hallucination Detection Best Practices](https://www.voiceflow.com/blog/prevent-llm-hallucinations)
- [Survey on Hallucination in LLMs](https://arxiv.org/abs/2311.05232)
- [Maxim AI: LLM Hallucination Mitigation](https://www.getmaxim.ai/articles/llm-hallucination-detection-and-mitigation-best-techniques/)

---

## Directory Structure

### Artifact Organization

Based on [Anthropic's research agent demo](https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent):

```
workspace/
├── session_20251123_143022/          # Timestamped session
│   ├── research_notes/               # Raw research findings
│   │   ├── researcher_1_defi_yields.md
│   │   ├── researcher_2_blend_analysis.md
│   │   └── researcher_3_risk_assessment.md
│   ├── citations/                    # Citation verification
│   │   ├── raw_citations.json        # Extracted citations
│   │   ├── verified_citations.json   # After verification
│   │   └── failed_citations.json     # Failed verification
│   ├── drafts/                       # Writing iterations
│   │   ├── draft_v1.md
│   │   ├── critique_v1.md
│   │   ├── draft_v2.md
│   │   └── critique_v2.md
│   ├── final/                        # Output
│   │   └── report.md
│   └── logs/                         # Audit trail
│       ├── transcript.txt            # Human-readable
│       └── structured.jsonl          # Machine-readable
└── style_guides/                     # Writing style guides
    ├── academic.md                   # Academic tone/structure
    ├── technical.md                  # Technical documentation
    └── conversational.md             # Blog/informal style
```

**Pattern**: Orchestrator spawns subagents → each writes artifacts → orchestrator reads artifacts → synthesizes

---

## Architecture: Orchestrator-Worker Pattern

### Orchestrator (Lead Agent)

**Responsibilities**:
1. Decompose user request into research subtopics
2. Spawn parallel researcher subagents
3. Monitor progress (read artifacts)
4. Coordinate citation checking
5. Orchestrate draft → critique → rewrite cycle
6. Apply writing styleguide

**Tools**: `Task` (spawn subagents), `Read`, `Glob`, `Write`

### Workers (Subagents)

#### 1. Researcher Agents (Parallel)

**Input**: Research subtopic
**Tools**: `WebSearch`, `Write`
**Output**: `research_notes/researcher_N_topic.md`

**Artifact format**:
```markdown
# Research Topic: DeFi Yields on Stellar

## Key Findings
- Blend Capital offers 8.5% APY on USDC [1]
- YieldBlox provides 6.2% APY with lower risk [2]

## Sources
[1] https://blend.capital/stats (accessed 2025-11-23)
[2] https://yieldblox.io/pools (accessed 2025-11-23)

## Raw Notes
[Detailed research notes...]
```

#### 2. Citation Checker Agent (CRITICAL)

**Input**: All research notes + draft
**Tools**: `WebFetch`, `Read`, `Write`
**Output**: `citations/verified_citations.json`, `citations/failed_citations.json`

**Process**:

**Step 1: Extract citations**
```python
# Parse markdown for:
# - [Title](URL)
# - Bare URLs
# - DOI: 10.xxxx/xxxxx
# - arXiv: 2401.xxxxx
```

**Step 2: Fetch source content**
```python
for citation in raw_citations:
    try:
        content = await fetch_url(citation.url)
        citation.content = content
        citation.fetch_status = "success"
    except:
        citation.fetch_status = "failed"
        citation.fallback_search = await search_for_source(citation.title)
```

**Step 3: Verify claim support (MOST CRITICAL)**
```python
# Use LLM to verify each claim against source content
prompt = f"""
Does the following source support the claim?

CLAIM: {claim.text}

SOURCE CONTENT:
{citation.content}

Respond with JSON:
{{
  "supported": true/false,
  "confidence": "high"/"medium"/"low",
  "relevant_excerpt": "exact quote from source",
  "assessment": "explanation"
}}
"""
```

**Step 4: SelfCheckGPT consistency**
```python
# Generate claim 3-5 times, check for consistency
responses = []
for _ in range(5):
    response = await llm.query(f"What does {source_url} say about {topic}?")
    responses.append(response)

# High variance = likely hallucination
consistency_score = calculate_consistency(responses)
if consistency_score < 0.7:
    citation.warning = "Low consistency - possible hallucination"
```

**Output artifact**:
```json
{
  "verified_citations": [
    {
      "id": "cite_001",
      "url": "https://blend.capital/stats",
      "title": "Blend Capital - Pool Statistics",
      "claim": "Blend Capital offers 8.5% APY on USDC",
      "verification": {
        "supported": true,
        "confidence": "high",
        "relevant_excerpt": "USDC Supply APY: 8.52%",
        "fetch_status": "success",
        "consistency_score": 0.95,
        "verified_at": "2025-11-23T14:30:22Z"
      }
    }
  ],
  "failed_citations": [
    {
      "id": "cite_002",
      "url": "https://example.com/fake",
      "claim": "Some protocol offers 50% APY",
      "verification": {
        "supported": false,
        "confidence": "high",
        "fetch_status": "404_not_found",
        "fallback_search": "No credible sources found",
        "action": "REMOVE_FROM_DRAFT"
      }
    }
  ]
}
```

**Best practice from research**: *"Enforce 'must-cite' rules for knowledge-intensive claims and block outputs without supporting evidence for high-stakes queries"* - [Lakera AI](https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models)

#### 3. Drafter Agent

**Input**: Verified research notes + verified citations only
**Tools**: `Read`, `Write`
**Output**: `drafts/draft_v1.md`

**Key constraint**: ONLY use citations from `citations/verified_citations.json`

**Prompt includes**:
```
You MUST only cite sources from this verified list:
{json.dumps(verified_citations)}

If you need to make a claim not supported by these sources, you MUST:
1. Flag the claim as [NEEDS CITATION]
2. Do NOT invent a source
3. The citation checker will research it in the next iteration
```

#### 4. Critic Agent

**Input**: Draft + writing styleguide
**Tools**: `Read`, `Write`
**Output**: `drafts/critique_v1.md`

**Checks**:
1. **Citation accuracy**: All claims have verified citations?
2. **Style adherence**: Matches writing styleguide (tone, voice, structure)?
3. **Logical flow**: Coherent argument structure?
4. **Completeness**: Addresses all research subtopics?
5. **Clarity**: Clear, concise language?

**Artifact format**:
```markdown
# Critique of Draft V1

## Citation Issues
- [ ] Line 42: Claim needs citation [HIGH PRIORITY]
- [x] All other citations verified

## Style Issues
- [ ] Tone too informal for academic style guide
- [ ] Use more third-person voice (currently too much first-person)

## Content Issues
- [ ] Missing risk assessment section
- [ ] Yield comparison table incomplete

## Recommended Revisions
1. Add citation for claim on line 42
2. Rewrite introduction in third-person
3. Expand risk assessment section
...
```

#### 5. Rewriter Agent

**Input**: Draft + critique + verified citations
**Tools**: `Read`, `Write`
**Output**: `drafts/draft_v2.md`

**Constraints**:
- Address all critique points
- Maintain all verified citations
- Flag new claims needing citation as `[NEEDS CITATION]`

**Iteration**: draft → critique → rewrite (repeat 2-3 times until quality threshold)

#### 6. Style Agent (Final Polish)

**Input**: Final draft + writing styleguide
**Tools**: `Read`, `Write`
**Output**: `final/report.md`

**Writing styleguide integration**:

From research on [writing style guides](https://www.stylemanual.gov.au/writing-and-designing-content/clear-language-and-writing-style/voice-and-tone):
- **Tone**: formal/standard/conversational
- **Voice**: third-person/first-person, active/passive
- **Structure**: cohesion, logical flow, section organization
- **Word choice**: specialized terminology, precision

**Example styleguide** (`style_guides/academic.md`):
```markdown
# Academic Writing Style Guide

## Tone
- **Formal**: Polished, error-free, objective
- Avoid contractions, colloquialisms, emotional language
- Maintain authoritative but accessible tone

## Voice
- **Third-person predominant**: "The research demonstrates..." not "We demonstrate..."
- **Active voice preferred**: "The agent verified citations" not "Citations were verified"

## Structure
- Clear thesis statement
- Logical progression of ideas
- Topic sentences for each paragraph
- Transitions between sections
- Conclusion ties back to thesis

## Citations
- APA 7th edition format
- In-text citations with author-date
- Full reference list at end
- Every claim requires citation
```

Sources:
- [Academic Tone and Language](https://uq.pressbooks.pub/academicwritingskills/chapter/academic-tone-and-language/)
- [USC Academic Writing Style](https://libguides.usc.edu/writingguide/academicwriting)
- [Fundamentals of Engineering Technical Communications](https://ohiostate.pressbooks.pub/feptechcomm/chapter/3-1-voice-tone/)

---

## Orchestration Flow

### Phase 1: Research (Parallel)

```python
# Orchestrator decomposes request
user_request = "Research DeFi yields on Stellar for vault deployment"

research_topics = orchestrator.decompose(user_request)
# Returns: [
#   "Blend Capital yield opportunities",
#   "YieldBlox risk assessment",
#   "Soroswap liquidity analysis"
# ]

# Spawn parallel researchers
tasks = []
for i, topic in enumerate(research_topics):
    task = spawn_researcher(
        topic=topic,
        output_file=f"research_notes/researcher_{i}_{slug(topic)}.md"
    )
    tasks.append(task)

# Wait for all researchers to complete
await asyncio.gather(*tasks)

# Orchestrator reads artifacts (not passed in memory)
research_notes = []
for note_file in glob("research_notes/*.md"):
    research_notes.append(read_file(note_file))
```

### Phase 2: Citation Verification (CRITICAL)

```python
# Extract all citations from research notes
raw_citations = citation_extractor.extract_from_notes(research_notes)

# Spawn citation checker
await spawn_citation_checker(
    input_file="citations/raw_citations.json",
    output_file="citations/verified_citations.json"
)

# Read verification results
verified = read_json("citations/verified_citations.json")
failed = read_json("citations/failed_citations.json")

# For failed citations, optionally spawn additional researchers
for failed_cite in failed:
    if failed_cite.verification.fallback_search == "no_sources":
        # Claim cannot be verified - must be removed
        orchestrator.flag_for_removal(failed_cite.claim)
```

### Phase 3: Drafting

```python
# Spawn drafter with ONLY verified citations
await spawn_drafter(
    research_notes="research_notes/*.md",
    verified_citations="citations/verified_citations.json",
    output_file="drafts/draft_v1.md"
)
```

### Phase 4: Critique-Rewrite Loop

```python
iteration = 1
max_iterations = 3

while iteration <= max_iterations:
    # Spawn critic
    await spawn_critic(
        draft=f"drafts/draft_v{iteration}.md",
        style_guide="style_guides/academic.md",
        output_file=f"drafts/critique_v{iteration}.md"
    )

    # Read critique
    critique = read_file(f"drafts/critique_v{iteration}.md")

    # Check if quality threshold met
    if critique.issues_count == 0:
        break

    # Spawn rewriter
    await spawn_rewriter(
        draft=f"drafts/draft_v{iteration}.md",
        critique=f"drafts/critique_v{iteration}.md",
        verified_citations="citations/verified_citations.json",
        output_file=f"drafts/draft_v{iteration+1}.md"
    )

    iteration += 1
```

### Phase 5: Style Application

```python
# Final polish with writing styleguide
await spawn_style_agent(
    draft=f"drafts/draft_v{iteration}.md",
    style_guide="style_guides/academic.md",
    output_file="final/report.md"
)

# Final report ready
final_report = read_file("final/report.md")
```

---

## Implementation Structure

### Core Ghostwriter Engine

```
backend/agent/ghostwriter/
├── __init__.py
├── orchestrator.py              # Main orchestration logic
├── subagents/
│   ├── researcher.py            # Parallel research agent
│   ├── citation_checker.py      # Citation verification (CRITICAL)
│   ├── drafter.py               # Initial draft generation
│   ├── critic.py                # Quality assessment
│   ├── rewriter.py              # Iterative improvement
│   └── style_agent.py           # Writing styleguide application
├── utils/
│   ├── citation_extractor.py    # Parse citations from markdown
│   ├── citation_verifier.py     # Multi-layer verification
│   ├── style_loader.py          # Load writing styleguides
│   └── artifact_manager.py      # Filesystem operations
└── tests/
    ├── test_citation_verification.py  # MOST IMPORTANT
    ├── test_orchestration.py
    └── fixtures/
        ├── sample_research_notes.md
        └── sample_citations.json
```

### Domain Modules (DeFi Example)

```
backend/agent/domains/defi/
├── __init__.py
├── orchestrator.py              # DeFi-specific orchestration
├── prompts.py                   # DeFi research prompts
└── tests/
    └── test_defi_research.py
```

### Simplified Foundation

```
backend/agent/claude_sdk_wrapper.py  # SIMPLIFIED
  - Authentication only
  - Tool configuration
  - Basic query interface
  - NO domain-specific methods
```

---

## Citation Verification Implementation

### Multi-Layer Verification Process

```python
# backend/agent/ghostwriter/utils/citation_verifier.py

from typing import List, Dict
import aiohttp
from anthropic import Anthropic

class CitationVerifier:
    """
    Multi-layer citation verification to prevent hallucinations.

    Implements best practices from:
    - SelfCheckGPT (consistency checking)
    - REFIND benchmark (span-level verification)
    - Stanford 2024 study (multi-layered approach)
    """

    def __init__(self, client: Anthropic):
        self.client = client
        self.session = aiohttp.ClientSession()

    async def verify_citations(
        self,
        citations: List[Dict],
        claims: List[Dict]
    ) -> Dict:
        """
        Verify all citations using multi-layer approach.

        Returns:
            {
                "verified": [...],
                "failed": [...],
                "warnings": [...]
            }
        """
        results = {
            "verified": [],
            "failed": [],
            "warnings": []
        }

        for citation in citations:
            verification = await self._verify_single_citation(
                citation,
                claims
            )

            if verification["status"] == "verified":
                results["verified"].append(citation | verification)
            elif verification["status"] == "failed":
                results["failed"].append(citation | verification)
            else:
                results["warnings"].append(citation | verification)

        return results

    async def _verify_single_citation(
        self,
        citation: Dict,
        claims: List[Dict]
    ) -> Dict:
        """Verify a single citation through multiple checks"""

        # Layer 1: Fetch source content
        fetch_result = await self._fetch_source(citation["url"])
        if not fetch_result["success"]:
            # Try fallback search
            fallback = await self._fallback_search(citation)
            if not fallback["found"]:
                return {
                    "status": "failed",
                    "reason": "source_not_found",
                    "fetch_error": fetch_result["error"],
                    "fallback_attempted": True
                }
            # Use fallback source
            citation = fallback["citation"]
            fetch_result = fallback["fetch_result"]

        # Layer 2: Span-level verification
        # Match specific claims to source content
        relevant_claims = [
            c for c in claims
            if c["citation_id"] == citation["id"]
        ]

        for claim in relevant_claims:
            span_verification = await self._verify_claim_span(
                claim["text"],
                fetch_result["content"]
            )

            if not span_verification["supported"]:
                return {
                    "status": "failed",
                    "reason": "claim_not_supported",
                    "claim": claim["text"],
                    "assessment": span_verification["assessment"]
                }

        # Layer 3: SelfCheckGPT consistency
        consistency = await self._check_consistency(
            citation["url"],
            relevant_claims
        )

        if consistency["score"] < 0.7:
            return {
                "status": "warning",
                "reason": "low_consistency",
                "consistency_score": consistency["score"],
                "details": consistency["details"]
            }

        # All checks passed
        return {
            "status": "verified",
            "confidence": "high" if consistency["score"] > 0.9 else "medium",
            "verified_at": datetime.utcnow().isoformat(),
            "content_excerpt": fetch_result["excerpt"]
        }

    async def _fetch_source(self, url: str) -> Dict:
        """Fetch source content"""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    return {
                        "success": True,
                        "content": content,
                        "excerpt": content[:500]  # First 500 chars
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _verify_claim_span(
        self,
        claim: str,
        source_content: str
    ) -> Dict:
        """
        Verify if source content supports the claim.

        Uses LLM to check if claim is supported by source.
        """
        prompt = f"""Does the following source support the claim?

CLAIM: {claim}

SOURCE CONTENT:
{source_content[:2000]}  # Limit to 2000 chars

Respond with JSON only:
{{
  "supported": true or false,
  "confidence": "high" or "medium" or "low",
  "relevant_excerpt": "exact quote from source that supports/contradicts",
  "assessment": "brief explanation"
}}"""

        response = await self.client.messages.create(
            model="claude-sonnet-4.5",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON response
        import json
        result = json.loads(response.content[0].text)
        return result

    async def _check_consistency(
        self,
        url: str,
        claims: List[Dict]
    ) -> Dict:
        """
        SelfCheckGPT: Generate multiple responses, check consistency.

        If responses vary widely, likely hallucination.
        """
        responses = []

        for claim in claims:
            # Generate 3 independent responses
            claim_responses = []
            for _ in range(3):
                prompt = f"What does {url} say about: {claim['text']}"
                response = await self.client.messages.create(
                    model="claude-sonnet-4.5",
                    max_tokens=200,
                    temperature=0.7,  # Some randomness
                    messages=[{"role": "user", "content": prompt}]
                )
                claim_responses.append(response.content[0].text)

            # Calculate consistency (simplified - production would use embeddings)
            # For now, check if responses are similar
            consistency = self._calculate_similarity(claim_responses)
            responses.append({
                "claim": claim["text"],
                "responses": claim_responses,
                "consistency": consistency
            })

        # Overall consistency score
        avg_consistency = sum(r["consistency"] for r in responses) / len(responses)

        return {
            "score": avg_consistency,
            "details": responses
        }

    def _calculate_similarity(self, texts: List[str]) -> float:
        """
        Calculate similarity between texts.

        Simplified version - production would use embeddings.
        """
        # Simple heuristic: count common words
        from collections import Counter

        word_sets = [
            Counter(text.lower().split())
            for text in texts
        ]

        # Jaccard similarity between first and others
        base = word_sets[0]
        similarities = []

        for ws in word_sets[1:]:
            intersection = sum((base & ws).values())
            union = sum((base | ws).values())
            similarity = intersection / union if union > 0 else 0
            similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 1.0

    async def _fallback_search(self, citation: Dict) -> Dict:
        """
        If URL fails, try to find alternative source.

        Uses web search to find credible alternative.
        """
        # Search for title or claim
        search_query = citation.get("title") or citation.get("claim")

        # Use WebSearch tool (implementation depends on available tools)
        # This is a placeholder - actual implementation would use available search

        return {
            "found": False,
            "reason": "fallback_search_not_implemented"
        }

    async def close(self):
        """Close HTTP session"""
        await self.session.close()
```

### Testing Citation Verification

```python
# backend/agent/ghostwriter/tests/test_citation_verification.py

import pytest
from ghostwriter.utils.citation_verifier import CitationVerifier

@pytest.mark.asyncio
async def test_verify_valid_citation():
    """Test verification of valid citation with supporting content"""

    verifier = CitationVerifier(anthropic_client)

    citations = [{
        "id": "cite_001",
        "url": "https://blend.capital/stats",
        "title": "Blend Capital Statistics"
    }]

    claims = [{
        "text": "Blend Capital offers competitive yields on USDC",
        "citation_id": "cite_001"
    }]

    result = await verifier.verify_citations(citations, claims)

    assert len(result["verified"]) == 1
    assert result["verified"][0]["status"] == "verified"
    assert result["verified"][0]["confidence"] in ["high", "medium"]

    await verifier.close()

@pytest.mark.asyncio
async def test_reject_invalid_citation():
    """Test rejection of citation with unsupported claim"""

    verifier = CitationVerifier(anthropic_client)

    citations = [{
        "id": "cite_002",
        "url": "https://example.com/article",
        "title": "Some Article"
    }]

    claims = [{
        "text": "The moon is made of cheese",
        "citation_id": "cite_002"
    }]

    result = await verifier.verify_citations(citations, claims)

    assert len(result["failed"]) == 1
    assert result["failed"][0]["reason"] == "claim_not_supported"

    await verifier.close()

@pytest.mark.asyncio
async def test_detect_low_consistency():
    """Test SelfCheckGPT detection of inconsistent responses"""

    verifier = CitationVerifier(anthropic_client)

    # This citation should trigger low consistency
    # (if source is ambiguous or LLM hallucinates)

    citations = [{
        "id": "cite_003",
        "url": "https://ambiguous-source.com/data",
        "title": "Ambiguous Data"
    }]

    claims = [{
        "text": "Specific numerical claim that might vary",
        "citation_id": "cite_003"
    }]

    result = await verifier.verify_citations(citations, claims)

    # Should be in warnings if consistency is low
    if result["warnings"]:
        assert result["warnings"][0]["reason"] == "low_consistency"
        assert result["warnings"][0]["consistency_score"] < 0.7

    await verifier.close()
```

---

## Writing Styleguide Integration

### Example Styleguides

**Academic Style** (`style_guides/academic.md`):
```markdown
# Academic Writing Style Guide

## Tone
- Formal and objective
- Authoritative but accessible
- Avoid contractions, colloquialisms
- Maintain professional distance

## Voice
- Third-person predominant: "The research demonstrates"
- Active voice preferred
- Avoid first-person unless reflecting on methodology

## Structure
- Clear thesis statement in introduction
- Topic sentences for each paragraph
- Logical progression with transitions
- Evidence-based arguments
- Conclusion synthesizes findings

## Citations
- APA 7th edition
- In-text: (Author, Year)
- Every claim requires citation
- Reference list alphabetized

## Language
- Precise terminology
- Concise sentences
- Technical terms defined on first use
- Avoid jargon where possible

Source: [USC Academic Writing Style](https://libguides.usc.edu/writingguide/academicwriting)
```

**Technical Documentation** (`style_guides/technical.md`):
```markdown
# Technical Writing Style Guide

## Tone
- Clear and direct
- Instructional
- User-focused

## Voice
- Second-person: "You can configure..."
- Active voice: "Click the button" not "The button should be clicked"
- Imperative mood for instructions

## Structure
- Task-oriented organization
- Step-by-step procedures
- Prerequisites listed upfront
- Examples after explanations

## Language
- Simple present tense
- Short sentences (15-20 words)
- Bullet lists for sequences
- Code blocks for technical details

## Formatting
- Headings: Clear hierarchy
- Code: Inline `code` or blocks
- Notes/warnings in callouts

Source: [Fundamentals of Technical Communications](https://ohiostate.pressbooks.pub/feptechcomm/chapter/3-1-voice-tone/)
```

**Conversational Blog** (`style_guides/conversational.md`):
```markdown
# Conversational Writing Style Guide

## Tone
- Friendly and approachable
- Conversational but professional
- Enthusiastic about topic

## Voice
- First-person plural: "We discovered..."
- Second-person to engage: "You might wonder..."
- Contractions acceptable: "You'll find..."

## Structure
- Hook in introduction
- Short paragraphs (2-4 sentences)
- Subheadings for skimmability
- Examples and anecdotes

## Language
- Clear and accessible
- Metaphors and analogies welcome
- Technical terms explained simply
- Rhetorical questions for engagement

## Formatting
- Bold for emphasis
- Short sentences for impact
- Bullet lists for quick reading

Source: [UMGC: Style, Voice, and Tone](https://www.umgc.edu/current-students/learning-resources/writing-center/online-guide-to-writing/tutorial/chapter3/ch3-21)
```

### Style Agent Implementation

```python
# backend/agent/ghostwriter/subagents/style_agent.py

from pathlib import Path

class StyleAgent:
    """Apply writing styleguide to final draft"""

    def __init__(self, client):
        self.client = client

    async def apply_style(
        self,
        draft_path: Path,
        style_guide_path: Path,
        output_path: Path
    ):
        """Apply writing styleguide to draft"""

        # Read draft
        draft = draft_path.read_text()

        # Read style guide
        style_guide = style_guide_path.read_text()

        # Apply style
        prompt = f"""Apply the following writing style guide to this draft.

# Writing Style Guide
{style_guide}

# Draft to Style
{draft}

# Instructions
- Maintain all citations EXACTLY as written
- Adjust tone, voice, and structure per style guide
- Preserve all factual content
- Improve clarity and readability
- Ensure consistent formatting

Output the styled report in markdown.
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4.5",
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Write output
        styled_report = response.content[0].text
        output_path.write_text(styled_report)

        return {
            "success": True,
            "output_file": str(output_path)
        }
```

---

## DeFi Domain Module (Refactored)

### DeFi-Specific Orchestration

```python
# backend/agent/domains/defi/orchestrator.py

from ghostwriter.orchestrator import GhostwriterOrchestrator
from .prompts import create_yield_research_prompt

class DeFiResearchOrchestrator:
    """
    DeFi research using general ghostwriter engine.

    Uses filesystem-based orchestration with DeFi-specific prompts.
    """

    def __init__(self, workspace_dir: Path):
        self.ghostwriter = GhostwriterOrchestrator(workspace_dir)

    async def research_yield_opportunities(
        self,
        asset: str = "USDC",
        min_apy: float = 0.0
    ) -> Dict:
        """
        Research DeFi yield opportunities.

        Returns:
            {
                "success": True,
                "report_file": "workspace/session_XXX/final/report.md",
                "verified_citations": [...],
                "session_id": "session_20251123_143022"
            }
        """

        # Create DeFi-specific research prompt
        prompt = create_yield_research_prompt(asset, min_apy)

        # Use ghostwriter engine
        result = await self.ghostwriter.run(
            user_request=prompt,
            style_guide="style_guides/technical.md",
            max_iterations=3
        )

        return {
            "success": result["success"],
            "asset": asset,
            "min_apy": min_apy,
            "report_file": result["report_file"],
            "verified_citations": result["verified_citations"],
            "session_id": result["session_id"]
        }
```

### DeFi-Specific Prompts

```python
# backend/agent/domains/defi/prompts.py

def create_yield_research_prompt(asset: str, min_apy: float) -> str:
    """Generate DeFi yield research prompt"""
    return f"""Research current yield farming opportunities for {asset} on Stellar blockchain.

# Research Requirements

## Scope
- Asset: {asset}
- Minimum APY: {min_apy}%
- Ecosystem: Stellar (Soroban contracts)
- Network: Mainnet only

## Protocols to Research
1. Blend Capital
   - Supply APY for {asset}
   - Collateral requirements
   - BLND token rewards
   - Historical stability

2. YieldBlox
   - Lending/borrowing rates
   - Risk parameters
   - Pool liquidity

3. Soroswap
   - Liquidity pool APY
   - Impermanent loss risk
   - Trading volume

## Key Metrics for Each Opportunity
- Current APY (verified on-chain or official stats)
- Total Value Locked (TVL)
- Liquidity depth
- Historical performance (30d, 90d if available)
- Risk factors (smart contract audits, exploits, etc.)

## Analysis Required
1. Risk-adjusted return comparison
2. Vault deployment suitability
3. Recommended allocation strategy
4. Risk mitigation approaches

## Citation Requirements
- ALL APY claims MUST have citations
- Use official protocol stats pages
- Cross-verify with on-chain data sources
- If data unavailable, state explicitly

## Output Format
Technical documentation style:
- Executive summary
- Detailed opportunity analysis (one section per protocol)
- Comparative table
- Recommendations with rationale
- Full reference list

Target audience: Technical DeFi developers deploying non-custodial vaults.
"""
```

---

## API Integration

### Ghostwriter Endpoint

```python
# backend/main.py

from ghostwriter.orchestrator import GhostwriterOrchestrator
from pathlib import Path

# Initialize workspace
WORKSPACE_DIR = Path("/home/user/tuxedo/workspace")
ghostwriter = GhostwriterOrchestrator(WORKSPACE_DIR)

@app.post("/api/ghostwriter/research")
async def research_and_write(request: ResearchRequest):
    """
    General-purpose research and report generation.

    Request:
    {
        "user_request": "Research DeFi yields...",
        "style_guide": "academic" | "technical" | "conversational",
        "max_iterations": 3
    }

    Response:
    {
        "success": true,
        "session_id": "session_20251123_143022",
        "report_file": "workspace/.../final/report.md",
        "report_content": "...",
        "verified_citations": [...],
        "failed_citations": [...],
        "artifacts": {
            "research_notes": ["..."],
            "drafts": ["..."],
            "critiques": ["..."]
        }
    }
    """
    try:
        # Map style guide name to file
        style_guide_map = {
            "academic": "style_guides/academic.md",
            "technical": "style_guides/technical.md",
            "conversational": "style_guides/conversational.md"
        }

        style_guide = style_guide_map.get(
            request.style_guide,
            "style_guides/technical.md"  # default
        )

        # Run ghostwriter
        result = await ghostwriter.run(
            user_request=request.user_request,
            style_guide=style_guide,
            max_iterations=request.max_iterations or 3
        )

        # Read final report
        report_content = Path(result["report_file"]).read_text()

        return {
            "success": True,
            "session_id": result["session_id"],
            "report_file": result["report_file"],
            "report_content": report_content,
            "verified_citations": result["verified_citations"],
            "failed_citations": result["failed_citations"],
            "artifacts": {
                "research_notes": result["research_notes"],
                "drafts": result["drafts"],
                "critiques": result["critiques"]
            }
        }

    except Exception as e:
        logger.error(f"Ghostwriter error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### DeFi Research Endpoint

```python
from domains.defi.orchestrator import DeFiResearchOrchestrator

defi_researcher = DeFiResearchOrchestrator(WORKSPACE_DIR)

@app.post("/api/defi/research-yield")
async def research_defi_yields(request: YieldResearchRequest):
    """
    DeFi-specific yield research.

    Uses general ghostwriter with DeFi prompts.
    """
    try:
        result = await defi_researcher.research_yield_opportunities(
            asset=request.asset,
            min_apy=request.min_apy
        )

        # Read report
        report_content = Path(result["report_file"]).read_text()

        return {
            "success": True,
            "asset": result["asset"],
            "min_apy": result["min_apy"],
            "report": report_content,
            "citations": result["verified_citations"],
            "session_id": result["session_id"]
        }

    except Exception as e:
        logger.error(f"DeFi research error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

## Key Differences from V1 Proposal

| Aspect | V1 (Wrong) | V2 (Correct) |
|--------|------------|--------------|
| **Orchestration** | LangGraph | Filesystem-based artifacts |
| **State Management** | Graph state | Persistent files |
| **Citation Emphasis** | One node among many | MOST CRITICAL subprocess |
| **Citation Approach** | Basic URL checking | Multi-layer verification (span-level, SelfCheckGPT, external validation) |
| **Styleguide** | Visual design (carbon fiber kintsugi) | Writing style (tone, voice, structure) |
| **Subprocesses** | Missing critique/rewrite | Complete: research → cite → draft → critique → rewrite → style |
| **Information Flow** | Passed in memory | Artifacts on disk |
| **Pattern Source** | LangGraph docs | Anthropic research agent demo |

---

## Next Steps

### Immediate: Research & Validation

1. **Study citation checking literature**:
   - [LLM Hallucination Survey](https://arxiv.org/abs/2311.05232)
   - [REFIND SemEval 2025 benchmark](https://www.getmaxim.ai/articles/llm-hallucination-detection-and-mitigation-best-techniques/)
   - [SelfCheckGPT paper](https://www.voiceflow.com/blog/prevent-llm-hallucinations)

2. **Review Anthropic demo code**:
   - [Research agent demo](https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent)
   - [Multi-agent blog post](https://www.anthropic.com/engineering/multi-agent-research-system)

3. **Test citation verification patterns**:
   - Prototype multi-layer verification
   - Benchmark SelfCheckGPT effectiveness
   - Measure false positive/negative rates

### Phase 1: Core Implementation

- [ ] Implement `artifact_manager.py` (filesystem operations)
- [ ] Implement `citation_verifier.py` (multi-layer verification) **CRITICAL**
- [ ] Implement `orchestrator.py` (coordinate subagents)
- [ ] Test citation verification thoroughly

### Phase 2: Subagents

- [ ] Implement researcher subagent
- [ ] Implement citation checker subagent **CRITICAL**
- [ ] Implement drafter subagent
- [ ] Implement critic subagent
- [ ] Implement rewriter subagent
- [ ] Implement style agent

### Phase 3: Domain Migration

- [ ] Create DeFi domain module
- [ ] Migrate DeFi prompts
- [ ] Test DeFi research end-to-end
- [ ] Deprecate old wrapper methods

---

## Open Questions

1. **Citation verification strictness**: Fail entire report if one citation fails, or just flag warnings?
2. **SelfCheckGPT parameters**: How many samples? What consistency threshold?
3. **Fallback search**: Which search API for fallback (Tavily, native, other)?
4. **Cost management**: Citation verification is expensive (multiple LLM calls per citation) - budget limits?
5. **Workspace cleanup**: Auto-delete old sessions? Retention policy?
6. **Writing styleguides**: Start with 3 (academic, technical, conversational) or more?

---

## References

**Filesystem-Based Orchestration**:
- [Anthropic: Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Claude Agent SDK: Subagents](https://docs.claude.com/en/docs/agent-sdk/subagents)
- [Research agent demo](https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent)

**Citation Verification**:
- [LLM Hallucination Detection Best Practices](https://www.voiceflow.com/blog/prevent-llm-hallucinations)
- [Survey on Hallucination in LLMs](https://arxiv.org/abs/2311.05232)
- [Lakera AI: Guide to Hallucinations](https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models)
- [Maxim AI: Hallucination Mitigation Techniques](https://www.getmaxim.ai/articles/llm-hallucination-detection-and-mitigation-best-techniques/)

**Writing Styleguides**:
- [Academic Tone and Language](https://uq.pressbooks.pub/academicwritingskills/chapter/academic-tone-and-language/)
- [USC: Academic Writing Style](https://libguides.usc.edu/writingguide/academicwriting)
- [Technical Communications: Voice and Tone](https://ohiostate.pressbooks.pub/feptechcomm/chapter/3-1-voice-tone/)
- [Style Manual: Voice and Tone](https://www.stylemanual.gov.au/writing-and-designing-content/clear-language-and-writing-style/voice-and-tone)

---

**This is architectural research - not final implementation. Patterns need validation through prototyping.**
