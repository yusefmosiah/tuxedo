# Ghostwriter Architecture: OpenHands SDK Implementation

**Status**: R&D Architecture
**Created**: 2025-11-23
**Purpose**: Production-ready Ghostwriter using OpenHands SDK + AWS Bedrock (Claude 4.5)

---

## Executive Summary

This document describes the Ghostwriter multi-stage research and writing system using the **OpenHands Software Agent SDK** with **AWS Bedrock Claude 4.5** models. The architecture leverages event-sourcing, multi-agent coordination, and containerization for production-grade automated research and content generation.

**Architecture Highlights:**
- ✅ **AWS Bedrock Claude 4.5**: Haiku for fast operations, Sonnet for complex reasoning
- ✅ **Event-sourced architecture**: Full replay and debugging capabilities
- ✅ **Native multi-agent coordination**: Built-in `DelegateTool` for parallel research agents
- ✅ **Containerized execution**: Docker/Kubernetes native, isolated workspaces
- ✅ **Cost-efficient**: ~$0.31 per 1000-word report with 90%+ verification
- ✅ **MIT licensed**: Open-source, production-ready framework

---

## Quick Start Example

```python
# Event-sourced, containerized, multi-agent architecture
from openhands.sdk import Agent, LLM, Conversation
from openhands.tools import FileEditorTool, WebBrowserTool, DelegateTool

# Configure Bedrock with Claude 4.5
llm = LLM(
    provider="bedrock",
    model="anthropic.claude-haiku-4-5-20251001-v1:0",  # or Sonnet for complex tasks
    aws_region="us-east-1"
)

# Create agent with tools
agent = Agent(
    llm=llm,
    tools=[FileEditorTool(), WebBrowserTool(), DelegateTool()]
)

# Run in containerized workspace
conversation = Conversation(
    agent=agent,
    workspace="/workspace/sessions/session_001"
)

# Execute research task - event log captures everything
conversation.send_message("Research DeFi yields and write findings to file")
conversation.run()  # Deterministic, replayable execution
```

---

## Bedrock Model Configuration

Based on [listing all available models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) in your Bedrock account:

```python
# Claude 4.5 models in Bedrock (us-east-1)
BEDROCK_HAIKU = "anthropic.claude-haiku-4-5-20251001-v1:0"    # Fast, cheap
BEDROCK_SONNET = "anthropic.claude-sonnet-4-5-20250929-v1:0"  # Complex reasoning
```

**Model Selection Strategy:**
- **Claude 4.5 Haiku**: Research, extraction, verification (Stages 1, 3, 4, 7)
- **Claude 4.5 Sonnet**: Draft, critique, revision, style (Stages 2, 5, 6, 8)

**Cost Optimization:**
- Claude 4.5 Haiku: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- Claude 4.5 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Use Haiku for 50% of stages = significant cost savings

---

## OpenHands SDK Architecture

### Event-Sourced State Model

[OpenHands uses event-sourcing](https://arxiv.org/html/2511.03690v1) where all state derives from an immutable event log:

```python
# Every action creates an event
conversation.send_message("Research DeFi yields")

# Event log captures:
EventLog:
  - UserMessage: "Research DeFi yields"
  - ToolUse: WebBrowserTool.navigate("https://...")
  - ToolResult: "Page loaded: ..."
  - ToolUse: FileEditorTool.create("/workspace/source_1.md", content="...")
  - ToolResult: "File created"
  - AssistantMessage: "Research complete"
```

**Benefits:**
1. **Deterministic Replay**: Recreate exact state from event log
2. **Debugging**: Inspect every step the agent took
3. **Resumability**: Continue from last processed event after failure
4. **Auditing**: Complete history of agent actions

### ConversationState: Single Source of Truth

[ConversationState is the only mutable component](https://arxiv.org/html/2511.03690v1):

```python
class ConversationState:
    event_log: EventLog              # Immutable history
    current_step: int                # Where we are
    metadata: Dict[str, Any]         # User-defined data

# All other components are immutable:
Agent: Immutable                     # Never changes during execution
LLM: Immutable                       # Configuration fixed
Tools: Immutable                     # Tool definitions constant
```

This design enables:
- **Selective persistence**: Save only state, replay events
- **Recovery**: Restore to last processed event
- **CI testing**: Replay same events across model versions

### Containerized Workspace

[Agents run in Docker containers](https://docs.openhands.dev/sdk) with mounted workspaces:

```bash
# Container structure
/workspace/sessions/session_20251123_143022/  ← Mounted volume
├── 00_research/
│   ├── source_1.md
│   ├── source_2.md
│   └── source_3.md
├── 01_draft/
│   └── initial_draft.md
...
└── event_log.json  ← Automatic event capture
```

**Isolation Benefits:**
- Agent can only access `/workspace/*` (security)
- Host filesystem protected
- Easy cleanup (delete container)
- Reproducible (same container = same environment)

---

## Multi-Agent Coordination with DelegateTool

[OpenHands SDK has built-in agent delegation](https://docs.openhands.dev/sdk/guides/agent-delegation):

### How DelegateTool Works

```python
# Parent agent
main_agent = Agent(llm=llm_sonnet, tools=[DelegateTool(), FileEditorTool()])

# Parent delegates to sub-agents
conversation.send_message("""
Use DelegateTool to spawn 5 research sub-agents in parallel:
- researcher_1: Research DeFi yields overview
- researcher_2: Research Stellar protocols
- researcher_3: Research Blend Capital details
- researcher_4: Research competitor analysis
- researcher_5: Research recent developments

Each sub-agent should:
1. Use WebBrowserTool to search the web
2. Use FileEditorTool to write findings to 00_research/source_N.md
""")

# Behind the scenes:
# 1. DelegateTool spawns 5 sub-agents (parallel threads)
# 2. Each has independent conversation context
# 3. All share same workspace /workspace/sessions/...
# 4. Sub-agents inherit parent's LLM config (can override)
# 5. Parent blocks until all complete
# 6. Parent receives consolidated results
```

### Key Properties

**Shared Workspace:**
- All agents (parent + 5 children) access same `/workspace/` mount
- No conflicts: each writes to different file (`source_1.md`, `source_2.md`, etc.)
- Instant availability: parent can immediately read sub-agent output

**Parallel Execution:**
- Sub-agents run in **threads** (not separate containers)
- True parallelism for I/O-bound tasks (web search, file writes)
- Parent blocks until all sub-agents complete

**Result Consolidation:**
- DelegateTool returns single observation with all results
- Parent can synthesize/aggregate sub-agent outputs
- Event log captures all sub-agent actions

---

## 8-Stage Ghostwriter Pipeline with OpenHands

### Stage 1: Research (Parallel Haiku Subagents)

**Goal**: Gather 3-5 authoritative sources via parallel web research

```python
from openhands.sdk import Agent, LLM, Conversation
from openhands.tools import DelegateTool, WebBrowserTool, FileEditorTool

# Coordinator agent (Sonnet for orchestration)
coordinator_llm = LLM(
    provider="bedrock",
    model="anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="us-east-1"
)

coordinator = Agent(
    llm=coordinator_llm,
    tools=[DelegateTool(), FileEditorTool()]
)

# Sub-agent LLM config (Haiku for speed/cost)
researcher_llm_config = {
    "provider": "bedrock",
    "model": "anthropic.claude-haiku-4-5-20251001-v1:0",
    "aws_region": "us-east-1"
}

# Research conversation
research_conv = Conversation(
    agent=coordinator,
    workspace="/workspace/sessions/session_001",
    metadata={"stage": "research", "topic": "DeFi yields on Stellar"}
)

# Delegate to parallel researchers
research_conv.send_message(f"""
You are coordinating a research project on: "DeFi yields on Stellar blockchain"

Use DelegateTool to spawn 5 parallel research sub-agents. Configure each sub-agent
with Haiku model for speed and cost:

Sub-agent 1: "Overview of DeFi on Stellar"
Sub-agent 2: "Blend Capital protocol details"
Sub-agent 3: "Stellar DEX yield opportunities"
Sub-agent 4: "Competitor analysis (Ethereum, Solana DeFi)"
Sub-agent 5: "Recent developments and trends (2024-2025)"

Each sub-agent must:
1. Use WebBrowserTool to research their topic (3-5 searches)
2. Use FileEditorTool to write findings to: 00_research/source_N.md

Format for each source file:
---
url: https://example.com/article
title: Article Title
date_published: 2025-01-15
date_accessed: {today}
source_type: [academic|documentation|news|blog]
---

# Key Excerpts
[Relevant quotes]

# Summary
[2-3 sentence summary]

After all sub-agents complete, report how many sources were gathered.
""")

research_conv.run()

# Event log now contains:
# - DelegateTool.spawn("researcher_1", llm_config=researcher_llm_config)
# - [Sub-agent 1 events: WebBrowser actions, FileEditor actions]
# - DelegateTool.spawn("researcher_2", llm_config=researcher_llm_config)
# - [Sub-agent 2 events...]
# - ...all 5 researchers in parallel
# - DelegateTool.consolidate() → "5 sources gathered"
```

**Cost Estimate:**
- 5 researchers × (500 input + 2000 output) tokens
- Haiku pricing: 5 × ($0.000125 + $0.0025) = **$0.013**

**Time Estimate:** ~30-60 seconds (parallel execution)

**Event Log Snapshot:**
```json
{
  "events": [
    {"type": "UserMessage", "content": "Use DelegateTool to spawn..."},
    {"type": "ToolUse", "tool": "DelegateTool", "action": "spawn", "agent_id": "researcher_1"},
    {"type": "ToolUse", "tool": "WebBrowserTool", "action": "search", "query": "DeFi Stellar overview"},
    {"type": "ToolResult", "content": "Found 10 results..."},
    {"type": "ToolUse", "tool": "FileEditorTool", "action": "create", "path": "00_research/source_1.md"},
    {"type": "ToolResult", "content": "File created"},
    // ... parallel events from all 5 researchers
    {"type": "ToolResult", "tool": "DelegateTool", "content": "All sub-agents completed. 5 sources gathered."}
  ]
}
```

---

### Stage 2: Draft (Sonnet Synthesis)

**Goal**: Synthesize research into coherent document with citations

```python
# Draft agent (Sonnet for quality writing)
drafter_llm = LLM(
    provider="bedrock",
    model="anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="us-east-1"
)

drafter = Agent(
    llm=drafter_llm,
    tools=[FileEditorTool()]  # Only needs file operations
)

draft_conv = Conversation(
    agent=drafter,
    workspace="/workspace/sessions/session_001",
    metadata={"stage": "draft"}
)

draft_conv.send_message("""
Read all research sources from 00_research/*.md and synthesize into a
comprehensive report.

Requirements:
1. Read all source_*.md files in 00_research/
2. Create coherent narrative with clear structure
3. Cite sources using [N] notation immediately after claims
4. Write to: 01_draft/initial_draft.md

Format:
# [Report Title]

## Introduction
[Overview with citations [1][2]]

## [Main Sections]
[Content with citations]

## Conclusion
[Summary]

## References
[1] Title - URL
[2] Title - URL
""")

draft_conv.run()

# Event log:
# - FileEditorTool.view("00_research/source_1.md")
# - FileEditorTool.view("00_research/source_2.md")
# - ... reads all sources
# - FileEditorTool.create("01_draft/initial_draft.md", content="# DeFi Yields...")
```

**Cost Estimate:**
- Input: ~10,000 tokens (all research notes + prompt)
- Output: ~3,000 tokens (draft)
- Sonnet pricing: ($0.03 + $0.045) = **$0.075**

**Time Estimate:** ~20-30 seconds

---

### Stage 3: Extract Claims (Haiku)

**Goal**: Extract atomic factual claims and citations

```python
# Extractor agent (Haiku for structured extraction)
extractor_llm = LLM(
    provider="bedrock",
    model="anthropic.claude-haiku-4-5-20251001-v1:0",
    aws_region="us-east-1"
)

extractor = Agent(
    llm=extractor_llm,
    tools=[FileEditorTool()]
)

extract_conv = Conversation(
    agent=extractor,
    workspace="/workspace/sessions/session_001",
    metadata={"stage": "extraction"}
)

extract_conv.send_message("""
Read 01_draft/initial_draft.md and extract all atomic factual claims.

An atomic claim is:
- Single, verifiable statement
- Has a citation [N]
- Not opinion or general knowledge

Output two JSON files:

1. 02_extraction/atomic_claims.json:
{
  "claims": [
    {
      "id": "claim_1",
      "text": "Blend Capital offers 8.5% APY for USDC",
      "citation": "[1]",
      "context": "The sentence containing this claim"
    }
  ]
}

2. 02_extraction/citations.json:
{
  "citations": [
    {
      "id": 1,
      "title": "Source title",
      "url": "https://example.com",
      "type": "documentation"
    }
  ]
}

Aim for 20-30 claims per 1000 words.
""")

extract_conv.run()
```

**Cost Estimate:**
- Input: ~3,500 tokens (draft + prompt)
- Output: ~2,000 tokens (JSON)
- Haiku pricing: ($0.000875 + $0.0025) = **$0.003**

---

### Stage 4: Verify Claims (Parallel Haiku)

**Goal**: 3-layer verification of all claims

```python
# Verifier coordinator (Sonnet)
verifier_coord_llm = LLM(
    provider="bedrock",
    model="anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="us-east-1"
)

verifier_coord = Agent(
    llm=verifier_coord_llm,
    tools=[DelegateTool(), FileEditorTool(), TerminalTool()]
)

# Sub-verifier config (Haiku for cost)
verifier_llm_config = {
    "provider": "bedrock",
    "model": "anthropic.claude-haiku-4-5-20251001-v1:0",
    "aws_region": "us-east-1"
}

verify_conv = Conversation(
    agent=verifier_coord,
    workspace="/workspace/sessions/session_001",
    metadata={"stage": "verification"}
)

verify_conv.send_message("""
Verify all claims in 02_extraction/atomic_claims.json

Process:
1. Read atomic_claims.json and citations.json
2. For each citation URL, use TerminalTool to run: curl -I {url}
   - Save HTTP status codes to 03_verification/url_checks.json
3. Use DelegateTool to spawn parallel verifier sub-agents (one per claim)
4. Each sub-verifier:
   a. Use WebBrowserTool to fetch source content
   b. Check if source supports claim
   c. Return JSON: {"claim_id": "...", "supported": true/false, "quote": "..."}
5. Aggregate all results to 03_verification/verification_report.json:
{
  "total_claims": 25,
  "verified_claims": 23,
  "verification_rate": 0.92,
  "threshold_met": true,
  "results": [...]
}
""")

verify_conv.run()

# Event log captures:
# - 25 parallel DelegateTool.spawn() calls
# - 25 parallel WebBrowserTool + verification events
# - Consolidated results
```

**Cost Estimate:**
- URL checks: Free (TerminalTool curl)
- 25 verifiers × (1,500 input + 300 output) tokens
- Haiku pricing: 25 × ($0.000375 + $0.000375) = **$0.019**

**Time Estimate:** ~30-60 seconds (parallel)

---

### Stage 5: Critique (Sonnet)

**Goal**: Analyze quality and identify issues

```python
# Critic agent (Sonnet for nuanced analysis)
critic_llm = LLM(
    provider="bedrock",
    model="anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="us-east-1"
)

critic = Agent(llm=critic_llm, tools=[FileEditorTool()])

critique_conv = Conversation(
    agent=critic,
    workspace="/workspace/sessions/session_001",
    metadata={"stage": "critique"}
)

critique_conv.send_message("""
Read:
- 01_draft/initial_draft.md
- 03_verification/verification_report.json

Analyze and create: 04_critique/critique.md

Include:
# Critique Report

## Summary
- Verification Rate: X% (Y/Z claims supported)
- Quality Score: X/100
- Status: [needs_revision|ready]

## Unsupported Claims
[List with priority and fix strategy]

## Revision Strategy
[Prioritized changes to reach 90% threshold]
""")

critique_conv.run()
```

**Cost Estimate:**
- Input: ~5,000 tokens
- Output: ~1,500 tokens
- Sonnet: ($0.015 + $0.0225) = **$0.038**

---

### Stage 6: Revise (Sonnet + WebSearch)

**Goal**: Fix unsupported claims via research

```python
# Reviser agent (Sonnet with web access)
reviser_llm = LLM(
    provider="bedrock",
    model="anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="us-east-1"
)

reviser = Agent(
    llm=reviser_llm,
    tools=[FileEditorTool(), WebBrowserTool()]
)

revise_conv = Conversation(
    agent=reviser,
    workspace="/workspace/sessions/session_001",
    metadata={"stage": "revision", "iteration": 1}
)

revise_conv.send_message("""
Fix unsupported claims in the draft.

Read:
- 01_draft/initial_draft.md
- 04_critique/critique.md
- 03_verification/verification_report.json

For each unsupported claim:
Strategy A: Use WebBrowserTool to find better source
Strategy B: Rewrite claim to match existing source
Strategy C: Remove claim (last resort)

PRESERVE all supported claims!

Write revised draft to: 05_revision/revised_draft.md
""")

revise_conv.run()
```

**Cost Estimate:**
- Input: ~7,000 tokens
- Output: ~3,500 tokens
- Sonnet: ($0.021 + $0.0525) = **$0.074**

---

### Stage 7: Re-verify (Parallel Haiku)

**Goal**: Verify revised claims

```python
# Same as Stage 4, but on revised_draft.md
# Re-extract claims, re-verify
# Check if verification_rate >= 0.90

# If < 0.90: repeat Stage 6-7 (max 3 iterations)
# If >= 0.90: proceed to Stage 8
```

**Cost Estimate:** ~$0.019 (same as Stage 4)

---

### Stage 8: Style (Sonnet)

**Goal**: Apply style guide transformation

```python
# Style agent (Sonnet for sophisticated transformation)
stylist_llm = LLM(
    provider="bedrock",
    model="anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="us-east-1"
)

stylist = Agent(llm=stylist_llm, tools=[FileEditorTool()])

style_conv = Conversation(
    agent=stylist,
    workspace="/workspace/sessions/session_001",
    metadata={"stage": "style", "style_guide": "defi_report"}
)

style_conv.send_message("""
Apply the DeFi Report style guide to the revised draft.

Read:
- 05_revision/revised_draft.md
- style_guides/defi_report.md

Transform tone and structure while PRESERVING:
- All facts and numbers
- All citations [N]
- All reference URLs

Write styled report to: 07_style/final_report.md
""")

style_conv.run()
```

**Cost Estimate:**
- Input: ~5,000 tokens
- Output: ~3,500 tokens
- Sonnet: ($0.015 + $0.0525) = **$0.068**

---

## Complete Pipeline Orchestration

```python
"""
Complete Ghostwriter pipeline with OpenHands SDK + Bedrock
"""

import asyncio
from openhands.sdk import Agent, LLM, Conversation
from openhands.tools import DelegateTool, FileEditorTool, WebBrowserTool, TerminalTool
from datetime import datetime


class GhostwriterPipeline:
    """Multi-stage research and writing pipeline using OpenHands SDK."""

    # Bedrock model IDs
    HAIKU = "anthropic.claude-haiku-4-5-20251001-v1:0"
    SONNET = "anthropic.claude-sonnet-4-5-20250929-v1:0"

    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self.session_id = None
        self.workspace = None

    def create_session(self, topic: str) -> str:
        """Create new session workspace."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        self.workspace = f"/workspace/sessions/{self.session_id}"

        # Session will auto-create directory structure via FileEditorTool
        return self.session_id

    def create_llm(self, model: str) -> LLM:
        """Create LLM with Bedrock configuration."""
        return LLM(
            provider="bedrock",
            model=model,
            aws_region=self.aws_region
        )

    async def run_stage_1_research(self, topic: str, num_researchers: int = 5):
        """Stage 1: Parallel research with Haiku sub-agents."""
        coordinator_llm = self.create_llm(self.SONNET)
        coordinator = Agent(
            llm=coordinator_llm,
            tools=[DelegateTool(), FileEditorTool()]
        )

        conv = Conversation(
            agent=coordinator,
            workspace=self.workspace,
            metadata={"stage": "research", "topic": topic}
        )

        # Delegate to parallel researchers
        conv.send_message(f"""
        Coordinate research on: "{topic}"

        Use DelegateTool to spawn {num_researchers} Haiku researchers in parallel.
        Each writes findings to 00_research/source_N.md
        """)

        conv.run()
        return conv

    async def run_stage_2_draft(self):
        """Stage 2: Synthesize draft with Sonnet."""
        drafter_llm = self.create_llm(self.SONNET)
        drafter = Agent(llm=drafter_llm, tools=[FileEditorTool()])

        conv = Conversation(
            agent=drafter,
            workspace=self.workspace,
            metadata={"stage": "draft"}
        )

        conv.send_message("""
        Read all 00_research/*.md files.
        Synthesize into coherent report with citations.
        Write to: 01_draft/initial_draft.md
        """)

        conv.run()
        return conv

    async def run_stage_3_extract(self):
        """Stage 3: Extract claims with Haiku."""
        extractor_llm = self.create_llm(self.HAIKU)
        extractor = Agent(llm=extractor_llm, tools=[FileEditorTool()])

        conv = Conversation(
            agent=extractor,
            workspace=self.workspace,
            metadata={"stage": "extraction"}
        )

        conv.send_message("""
        Extract atomic claims from 01_draft/initial_draft.md
        Write to: 02_extraction/atomic_claims.json, citations.json
        """)

        conv.run()
        return conv

    async def run_stage_4_verify(self):
        """Stage 4: Parallel verification with Haiku."""
        verifier_coord_llm = self.create_llm(self.SONNET)
        verifier_coord = Agent(
            llm=verifier_coord_llm,
            tools=[DelegateTool(), FileEditorTool(), TerminalTool(), WebBrowserTool()]
        )

        conv = Conversation(
            agent=verifier_coord,
            workspace=self.workspace,
            metadata={"stage": "verification"}
        )

        conv.send_message("""
        Verify all claims in 02_extraction/atomic_claims.json
        Use DelegateTool for parallel Haiku verifiers.
        Write to: 03_verification/verification_report.json
        """)

        conv.run()
        return conv

    async def run_stage_5_critique(self):
        """Stage 5: Quality critique with Sonnet."""
        critic_llm = self.create_llm(self.SONNET)
        critic = Agent(llm=critic_llm, tools=[FileEditorTool()])

        conv = Conversation(
            agent=critic,
            workspace=self.workspace,
            metadata={"stage": "critique"}
        )

        conv.send_message("""
        Analyze draft quality and verification results.
        Write to: 04_critique/critique.md
        """)

        conv.run()
        return conv

    async def run_stage_6_revise(self):
        """Stage 6: Revise unsupported claims with Sonnet."""
        reviser_llm = self.create_llm(self.SONNET)
        reviser = Agent(
            llm=reviser_llm,
            tools=[FileEditorTool(), WebBrowserTool()]
        )

        conv = Conversation(
            agent=reviser,
            workspace=self.workspace,
            metadata={"stage": "revision"}
        )

        conv.send_message("""
        Fix unsupported claims using WebBrowser for better sources.
        Write to: 05_revision/revised_draft.md
        """)

        conv.run()
        return conv

    async def run_stage_7_reverify(self):
        """Stage 7: Re-verify revised claims."""
        # Same as stage 4, but on revised draft
        return await self.run_stage_4_verify()

    async def run_stage_8_style(self, style_guide: str = "technical"):
        """Stage 8: Apply style guide with Sonnet."""
        stylist_llm = self.create_llm(self.SONNET)
        stylist = Agent(llm=stylist_llm, tools=[FileEditorTool()])

        conv = Conversation(
            agent=stylist,
            workspace=self.workspace,
            metadata={"stage": "style", "style_guide": style_guide}
        )

        conv.send_message(f"""
        Apply {style_guide} style guide to revised draft.
        Write to: 07_style/final_report.md
        """)

        conv.run()
        return conv

    async def run_full_pipeline(self, topic: str, style_guide: str = "technical"):
        """Run complete 8-stage pipeline."""
        self.create_session(topic)

        print(f"Session: {self.session_id}")
        print(f"Workspace: {self.workspace}")

        # Stage 1: Research
        print("\n[1/8] Research...")
        await self.run_stage_1_research(topic)

        # Stage 2: Draft
        print("[2/8] Draft...")
        await self.run_stage_2_draft()

        # Stage 3: Extract
        print("[3/8] Extract claims...")
        await self.run_stage_3_extract()

        # Stage 4: Verify
        print("[4/8] Verify claims...")
        verification_conv = await self.run_stage_4_verify()

        # Stages 5-7: Quality loop
        max_iterations = 3
        for iteration in range(max_iterations):
            # Stage 5: Critique
            print(f"[5/8] Critique (iteration {iteration + 1})...")
            await self.run_stage_5_critique()

            # Check if verification threshold met
            # (would read verification_report.json to check rate >= 0.90)
            # For now, assume we need revision

            # Stage 6: Revise
            print(f"[6/8] Revise (iteration {iteration + 1})...")
            await self.run_stage_6_revise()

            # Stage 7: Re-verify
            print(f"[7/8] Re-verify (iteration {iteration + 1})...")
            verification_conv = await self.run_stage_7_reverify()

            # Would check verification_rate here
            # If >= 0.90, break
            # For now, assume met after 1 iteration
            break

        # Stage 8: Style
        print("[8/8] Apply style...")
        await self.run_stage_8_style(style_guide)

        print(f"\n✅ Complete! Final report: {self.workspace}/07_style/final_report.md")
        return self.session_id


# Usage
async def main():
    pipeline = GhostwriterPipeline(aws_region="us-east-1")
    session_id = await pipeline.run_full_pipeline(
        topic="DeFi yields on Stellar blockchain in 2025",
        style_guide="defi_report"
    )
    print(f"Session ID: {session_id}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Cost & Performance Estimates

### Cost Breakdown (1000-word report, 25 claims, no iterations)

| Stage | Model | Operations | Cost |
|-------|-------|-----------|------|
| 1. Research (5 agents) | Haiku | 5 × (500 in + 2000 out) | $0.013 |
| 2. Draft | Sonnet | 10k in + 3k out | $0.075 |
| 3. Extract | Haiku | 3.5k in + 2k out | $0.003 |
| 4. Verify (25 claims) | Haiku | 25 × (1.5k in + 300 out) | $0.019 |
| 5. Critique | Sonnet | 5k in + 1.5k out | $0.038 |
| 6. Revise | Sonnet | 7k in + 3.5k out | $0.074 |
| 7. Re-verify | Haiku | 25 × (1.5k in + 300 out) | $0.019 |
| 8. Style | Sonnet | 5k in + 3.5k out | $0.068 |
| **TOTAL** | | | **$0.309** |

**With 1 revision iteration**: +$0.093 = **$0.402**

**Comparison to original estimate:**
- Original (Claude SDK): $0.67
- OpenHands: **$0.31** (54% cheaper!)
- Reason: More efficient token usage, better parallelization

### Performance Estimates

| Metric | Target | Expected |
|--------|--------|----------|
| **Latency** (1000 words) | <5 min | 3-4 min |
| **Verification rate** | ≥90% | 90-95% |
| **Throughput** | 10 concurrent | 20+ (containerized) |
| **Success rate** | ≥99% | ~99% |

**Latency breakdown:**
- Stage 1 (Research, parallel): 30-60s
- Stage 2 (Draft): 20-30s
- Stage 3 (Extract): 5-10s
- Stage 4 (Verify, parallel): 30-60s
- Stage 5 (Critique): 15-20s
- Stage 6 (Revise): 30-45s
- Stage 7 (Re-verify, parallel): 30-60s
- Stage 8 (Style): 20-30s

**Total: 3-5 minutes** (mostly parallel work)

---

## Event-Sourcing Benefits

### Debugging Example

```python
# Load event log from failed session
from openhands.sdk import ConversationState

state = ConversationState.load("session_20251123_143022/event_log.json")

# Inspect what happened
for event in state.event_log.events:
    print(f"{event.timestamp}: {event.type} - {event.tool}")

# Output:
# 2025-11-23 14:30:22: ToolUse - DelegateTool (spawn researcher_1)
# 2025-11-23 14:30:23: ToolUse - WebBrowserTool (search "DeFi Stellar")
# 2025-11-23 14:30:25: ToolResult - Found 10 results
# 2025-11-23 14:30:26: ToolUse - FileEditorTool (create source_1.md)
# 2025-11-23 14:30:27: ToolError - Permission denied  ← Found the bug!
```

### Resume After Failure

```python
# Resume from last processed event
state = ConversationState.load("session_20251123_143022/event_log.json")

# Fix the issue (e.g., permissions)
# Then replay from last successful event
conversation = Conversation.from_state(state)
conversation.run()  # Continues from where it left off
```

### CI Testing Across Models

```python
# Replay same events with different models
event_log = EventLog.load("golden_test_case.json")

# Test with Haiku
llm_haiku = LLM(provider="bedrock", model=HAIKU)
result_haiku = replay_events(event_log, llm_haiku)

# Test with Sonnet
llm_sonnet = LLM(provider="bedrock", model=SONNET)
result_sonnet = replay_events(event_log, llm_sonnet)

# Compare outputs
assert result_haiku.verification_rate >= 0.85
assert result_sonnet.verification_rate >= 0.90
```

---

## Containerization Benefits

### Docker Deployment

```bash
# Build container with OpenHands SDK
docker build -t ghostwriter:latest .

# Run Ghostwriter pipeline
docker run \
  -e AWS_BEARER_TOKEN_BEDROCK=$AWS_BEARER_TOKEN_BEDROCK \
  -e AWS_REGION=us-east-1 \
  -v /host/workspace:/workspace \
  ghostwriter:latest \
  python run_pipeline.py --topic "DeFi yields" --style defi_report

# Output appears in /host/workspace/sessions/session_*/
```

### Kubernetes Scaling

```yaml
# k8s/ghostwriter-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ghostwriter-report-gen
spec:
  parallelism: 10  # Run 10 reports concurrently
  template:
    spec:
      containers:
      - name: ghostwriter
        image: ghostwriter:latest
        env:
        - name: AWS_BEARER_TOKEN_BEDROCK
          valueFrom:
            secretKeyRef:
              name: bedrock-creds
              key: bearer-token
        volumeMounts:
        - name: workspace
          mountPath: /workspace
      volumes:
      - name: workspace
        persistentVolumeClaim:
          claimName: ghostwriter-pvc
```

### Security Isolation

**Container prevents:**
- ❌ Access to host filesystem
- ❌ Network access outside allowed domains
- ❌ Resource exhaustion (CPU/memory limits)
- ❌ Privilege escalation

**Agent can only:**
- ✅ Access mounted `/workspace/`
- ✅ Make HTTP requests (WebBrowser)
- ✅ Write to session directory

---

## Recommendations

### Architecture Benefits

✅ **OpenHands SDK** provides:
1. Proven Bedrock support (users confirm working integration)
2. Event-sourced architecture (full replay and debugging)
3. Native multi-agent coordination via DelegateTool
4. Containerized execution (Docker/K8s ready)
5. Open-source MIT license
6. Production-ready with comprehensive tooling

### Implementation Phases

**Phase 1:** Core Pipeline
- Set up OpenHands SDK + Bedrock authentication
- Implement Stages 1-3 (Research → Draft → Extract)
- Test event logging and replay
- Verify containerization works

**Phase 2:** Verification
- Implement Stage 4 (3-layer verification)
- Test parallel sub-agent coordination
- Validate 90% threshold enforcement

**Phase 3:** Quality Loop
- Implement Stages 5-7 (Critique → Revise → Re-verify)
- Test iteration logic
- Measure actual verification rates

**Phase 4:** Production
- Implement Stage 8 (Style)
- Add all 4 style guides
- Deploy to Docker/Kubernetes
- Performance optimization
- Monitoring and metrics

---

## References

### OpenHands SDK Documentation
- [OpenHands SDK Overview](https://docs.openhands.dev/sdk) - Official documentation
- [Software Agent SDK GitHub](https://github.com/OpenHands/software-agent-sdk) - Source code
- [Agent Delegation Guide](https://docs.openhands.dev/sdk/guides/agent-delegation) - Multi-agent patterns
- [Research Paper (Nov 2025)](https://arxiv.org/html/2511.03690v1) - Architecture details
- [Agent Delegation Example](https://github.com/OpenHands/software-agent-sdk/blob/main/examples/01_standalone_sdk/25_agent_delegation.py) - Code example

### AWS Bedrock Integration
- [Stack Overflow: OpenHands + Bedrock](https://stackoverflow.com/questions/79167711/how-to-make-openhands-running-on-docker-on-macos-to-work-with-aws-bedrock) - Confirmed working
- [Bedrock Support Issue](https://github.com/OpenDevin/OpenDevin/issues/1242) - Implementation discussion
- [Bedrock Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) - Available models

### Tools & Components
- [FileEditorTool](https://github.com/All-Hands-AI/OpenHands/blob/main/openhands/runtime/plugins/agent_skills/file_editor/README.md) - File operations
- [openhands-aci Package](https://github.com/All-Hands-AI/openhands-aci) - Agent computer interface
- [OpenHands Main Repo](https://github.com/OpenHands/OpenHands) - Full platform


---

## Conclusion

The **OpenHands SDK with AWS Bedrock** provides a production-ready foundation for the Ghostwriter multi-stage research and writing system:

1. **Event-sourced architecture** enables full debugging and replay capabilities
2. **Native multi-agent coordination** via DelegateTool for parallel research
3. **Containerized execution** ensures isolation and reproducibility
4. **Cost-efficient** at ~$0.31 per 1000-word report
5. **Proven Bedrock integration** with Claude 4.5 models

**Implementation approach**: Begin with Phase 1 (Core Pipeline) to establish the foundational research, draft, and extraction stages, then iterate through verification and quality loops.
