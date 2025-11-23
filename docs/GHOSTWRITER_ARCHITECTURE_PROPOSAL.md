# Ghostwriter Architecture Proposal

**Date**: 2025-11-23
**Status**: Design Phase
**Purpose**: Decouple DeFi-specific research from general report writing capabilities

---

## Executive Summary

The current `claude_sdk_wrapper.py` is tightly coupled to DeFi research use cases. This proposal outlines a refactoring to create a **general-purpose deep research ghostwriter** that:

1. **Consumes style guides** (like STYLEGUIDE.md - carbon fiber kintsugi)
2. **Performs deep research** with citation validation
3. **Generates reports** following style guidelines
4. **Separates domain logic** (DeFi) from general research capabilities

The architecture is based on the proven LangGraph workflow from `open_deep_research` with Tuxedo-specific enhancements.

---

## Current State Analysis

### Problems with Current Implementation

**File**: `backend/agent/claude_sdk_wrapper.py`

**Issues**:
1. ❌ **Tight coupling**: Methods like `analyze_strategy()`, `research_yield_opportunities()`, `generate_strategy_report()` are DeFi-specific
2. ❌ **No citation management**: Simple query-response pattern without source validation
3. ❌ **No style guide integration**: Cannot consume and apply formatting guidelines
4. ❌ **Limited research depth**: Single-turn queries instead of multi-phase research
5. ❌ **No structured workflow**: Lacks planning, critique, revision phases

**Current structure**:
```
ClaudeSDKAgent
├── query_simple()              # Generic ✅
├── analyze_strategy()          # DeFi-specific ❌
├── research_yield_opportunities() # DeFi-specific ❌
└── generate_strategy_report()  # DeFi-specific ❌
```

---

## Proposed Architecture

### Overview: Layered Separation of Concerns

```
┌─────────────────────────────────────────────────────┐
│           Application Layer (FastAPI)               │
│  - DeFi research endpoints                          │
│  - General ghostwriter endpoints                    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│          Domain Logic Layer                         │
│  ┌──────────────────┐  ┌────────────────────────┐  │
│  │  DeFi Research   │  │  Future Domains        │  │
│  │  Module          │  │  (Security, etc.)      │  │
│  └──────────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│     Core Ghostwriter Engine (LangGraph)             │
│  - Planning → Research → Citation → Draft           │
│  - Critique → Revision → Style Control              │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│       Foundation Layer (Claude SDK)                 │
│  - Model configuration (4 LLM roles)                │
│  - Tool integration (WebSearch, Read, Write)        │
│  - AWS Bedrock / Anthropic API auth                 │
└─────────────────────────────────────────────────────┘
```

---

## New File Structure

### Core Ghostwriter Engine

**New files**:

```
backend/agent/ghostwriter/
├── __init__.py
├── config.py                   # Configuration (4 LLM roles, search API)
├── state.py                    # LangGraph state definitions
├── graph.py                    # Main workflow graph
├── nodes/
│   ├── planning.py             # Research brief generation
│   ├── research_supervisor.py  # Research orchestration
│   ├── citation_check.py       # Citation validation
│   ├── draft.py                # Initial report generation
│   ├── critique.py             # Quality assessment
│   ├── revision.py             # Iterative improvement
│   └── style_control.py        # Style guide application
├── utils/
│   ├── citation_validator.py  # URL validation, claim checking
│   ├── style_loader.py         # Style guide parsing
│   └── prompts.py              # Reusable prompt templates
└── tests/
    ├── test_workflow.py
    └── test_citation.py
```

### Domain-Specific Modules

**Refactored structure**:

```
backend/agent/domains/
├── __init__.py
├── defi/
│   ├── __init__.py
│   ├── research.py             # DeFi research orchestration
│   ├── prompts.py              # DeFi-specific prompts
│   └── tools.py                # DeFi-specific research tools
└── security/                   # Future: security research
    └── ...
```

### Updated Claude SDK Wrapper

**Simplified**: `backend/agent/claude_sdk_wrapper.py`

```python
class ClaudeSDKAgent:
    """
    Foundation layer for Claude Agent SDK integration.
    Provides model configuration and tool access.
    Domain-specific logic moved to domain modules.
    """

    def __init__(self, ...):
        # Auth, tools, options (unchanged)

    async def query_simple(self, prompt: str) -> str:
        """Basic query interface - kept for simple use cases"""

    # ❌ REMOVED: analyze_strategy, research_yield_opportunities, generate_strategy_report
    # ✅ MOVED TO: backend/agent/domains/defi/research.py
```

---

## Ghostwriter Workflow (LangGraph)

### Phase-by-Phase Design

Based on `open_deep_research/ghostwriter.py`, adapted for Tuxedo:

#### **Phase 1: Planning**
```python
def planning_node(state: GhostwriterState) -> Command:
    """
    Convert user request into structured research brief.

    Input: User messages
    Output: Research brief (outline, questions, scope)
    LLM: research_model (from config)
    """
```

#### **Phase 2: Research Supervisor**
```python
def research_supervisor_node(state: GhostwriterState) -> Command:
    """
    Orchestrate deep research using sub-researchers.

    Input: Research brief
    Output: Research notes with citations
    LLM: research_model
    Tools: WebSearch, Read (for existing docs)
    Parallelization: max_concurrent_research_units
    """
```

#### **Phase 3: Citation Check**
```python
def citation_check_node(state: GhostwriterState) -> Command:
    """
    Validate all citations from research notes.

    Process:
    1. Extract URLs (markdown links, bare URLs, arXiv, DOI)
    2. Fetch each source
    3. Verify claim support via LLM judgment
    4. Fallback search if original link fails

    Output: Validated citations list
    LLM: research_model (for claim verification)
    """
```

#### **Phase 4: Draft**
```python
def draft_node(state: GhostwriterState) -> Command:
    """
    Generate initial report from research notes.

    Input: Research notes + validated citations
    Output: First draft
    LLM: final_report_model (higher quality)
    Rules: Only use validated citations, structured format
    """
```

#### **Phase 5: Critique**
```python
def critique_node(state: GhostwriterState) -> Command:
    """
    Assess draft quality and generate revision instructions.

    Input: Draft
    Output: List of actionable improvements
    LLM: research_model (analytical focus)
    Focus: Clarity, citation accuracy, argument strength
    """
```

#### **Phase 6: Revision**
```python
def revision_node(state: GhostwriterState) -> Command:
    """
    Apply critique improvements to draft.

    Input: Draft + critique
    Output: Revised draft
    LLM: final_report_model
    Constraint: Preserve validated citations
    """
```

#### **Phase 7: Style Control**
```python
def style_control_node(state: GhostwriterState) -> Command:
    """
    Apply style guide formatting (STYLEGUIDE.md).

    Input: Revised draft + style guide path
    Output: Final formatted report
    LLM: final_report_model

    Style Guide Integration:
    - Load STYLEGUIDE.md
    - Apply carbon fiber kintsugi aesthetic principles
    - Convert inline citations to footnotes
    - Ensure markdown formatting consistency
    - Preserve technical accuracy while enhancing presentation

    If no style guide: pass through unchanged
    """
```

### State Schema

```python
from typing import Annotated, TypedDict

class GhostwriterInputState(TypedDict):
    """User-facing input schema"""
    messages: list[dict]              # User request
    style_guide_path: str | None      # Path to STYLEGUIDE.md
    citations_file: str | None        # Optional pre-loaded citations
    output_file: str | None           # Where to save final report

class GhostwriterState(TypedDict):
    """Internal workflow state"""
    messages: list[dict]

    # Research phase
    research_brief: str
    supervisor_messages: Annotated[list, override_reducer]
    research_notes: Annotated[list, override_reducer]

    # Citation phase
    validated_citations: list[dict]   # [{"title": "...", "url": "..."}]

    # Draft phase
    drafts: Annotated[list, override_reducer]

    # Critique/revision phase
    critiques: Annotated[list, override_reducer]
    revision_instructions: Annotated[list, override_reducer]

    # Style control phase
    style_guide: str | None
    final_report: str
```

---

## Four LLM Roles Configuration

Based on `open_deep_research/configuration.py`:

```python
from pydantic import BaseModel, Field

class GhostwriterConfig(BaseModel):
    """Configuration for ghostwriter LLM roles"""

    # Research & supervision
    research_model: str = Field(
        default="claude-sonnet-4.5",
        description="Model for research and supervision tasks"
    )
    research_max_tokens: int = 8000

    # Summarization (compress research findings)
    summarization_model: str = Field(
        default="claude-haiku-4",
        description="Model for compressing research notes"
    )
    summarization_max_tokens: int = 4000

    # Compression (consolidate findings)
    compression_model: str = Field(
        default="claude-sonnet-4.5",
        description="Model for consolidating findings"
    )
    compression_max_tokens: int = 6000

    # Final report generation
    final_report_model: str = Field(
        default="claude-sonnet-4.5",
        description="Model for final report and style application"
    )
    final_report_max_tokens: int = 16000

    # Workflow control
    max_concurrent_research_units: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Max parallel research tasks"
    )
    max_researcher_iterations: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Max research iterations per task"
    )
```

**Why four roles?**:
- **Research model**: High-quality analysis and supervision (Sonnet 4.5)
- **Summarization model**: Fast compression (Haiku - cost effective)
- **Compression model**: Mid-tier consolidation (Sonnet 4.5)
- **Final report model**: Premium output (Sonnet 4.5 with high token limit)

---

## Style Guide Integration

### Loading STYLEGUIDE.md

```python
# backend/agent/ghostwriter/utils/style_loader.py

class StyleGuideLoader:
    """Load and parse style guide documents"""

    @staticmethod
    async def load_style_guide(path: str) -> str:
        """
        Load style guide from file.

        Args:
            path: Path to style guide (e.g., "/home/user/tuxedo/STYLEGUIDE.md")

        Returns:
            Style guide content as string
        """
        async with aiofiles.open(path, 'r') as f:
            return await f.read()

    @staticmethod
    def extract_style_rules(content: str) -> dict:
        """
        Parse style guide into structured rules.

        Returns:
            {
                "philosophy": "...",
                "color_system": {...},
                "typography": {...},
                "components": {...}
            }
        """
        # Optional: parse markdown sections for structured access
        pass
```

### Applying Style Guide

```python
# backend/agent/ghostwriter/nodes/style_control.py

async def style_control_node(state: GhostwriterState) -> Command:
    """Apply style guide to final report"""

    if not state.get("style_guide_path"):
        # No style guide - pass through
        return Command(
            update={"final_report": state["drafts"][-1]},
            goto=END
        )

    # Load style guide
    style_guide = await StyleGuideLoader.load_style_guide(
        state["style_guide_path"]
    )

    # Apply style with LLM
    prompt = f"""
Apply the following style guide to the report below.

# Style Guide
{style_guide}

# Report to Format
{state["drafts"][-1]}

# Validated Citations (use these for footnotes)
{json.dumps(state["validated_citations"], indent=2)}

# Instructions
1. Apply the carbon fiber kintsugi aesthetic principles
2. Use appropriate heading styles (metallic gradients in markdown)
3. Convert inline citations to markdown footnotes
4. Maintain technical accuracy while enhancing presentation
5. Follow typography hierarchy (sans for body, mono for technical)
6. Use appropriate emphasis (gold gradients for high-value content)
7. Structure content with proper spacing and borders

Output only the formatted report in markdown.
"""

    response = await llm.ainvoke(prompt)

    # Optionally write to file
    if state.get("output_file"):
        async with aiofiles.open(state["output_file"], 'w') as f:
            await f.write(response.content)

    return Command(
        update={"final_report": response.content},
        goto=END
    )
```

---

## DeFi Research Module (Refactored)

### Separation of Domain Logic

**File**: `backend/agent/domains/defi/research.py`

```python
from backend.agent.ghostwriter.graph import create_ghostwriter_graph
from backend.agent.ghostwriter.config import GhostwriterConfig

class DeFiResearcher:
    """
    DeFi-specific research orchestration.
    Uses general ghostwriter engine with DeFi prompts.
    """

    def __init__(self, config: GhostwriterConfig):
        self.ghostwriter = create_ghostwriter_graph(config)

    async def research_yield_opportunities(
        self,
        asset: str = "USDC",
        min_apy: float = 0.0
    ) -> dict:
        """
        Research yield opportunities using ghostwriter.

        This wraps the general ghostwriter with DeFi-specific prompts.
        """
        from .prompts import create_yield_research_prompt

        prompt = create_yield_research_prompt(asset, min_apy)

        result = await self.ghostwriter.ainvoke({
            "messages": [{"role": "user", "content": prompt}],
            "style_guide_path": "/home/user/tuxedo/STYLEGUIDE.md",
            "output_file": f"/tmp/yield_research_{asset}.md"
        })

        return {
            "success": True,
            "asset": asset,
            "min_apy": min_apy,
            "report": result["final_report"],
            "citations": result["validated_citations"]
        }

    async def analyze_strategy(
        self,
        strategy_description: str,
        market_context: dict | None = None
    ) -> dict:
        """Strategy analysis using ghostwriter"""
        from .prompts import create_strategy_analysis_prompt

        prompt = create_strategy_analysis_prompt(
            strategy_description,
            market_context
        )

        result = await self.ghostwriter.ainvoke({
            "messages": [{"role": "user", "content": prompt}],
            "style_guide_path": "/home/user/tuxedo/STYLEGUIDE.md"
        })

        return {
            "success": True,
            "strategy": strategy_description,
            "analysis": result["final_report"],
            "citations": result["validated_citations"],
            "market_context": market_context
        }
```

**File**: `backend/agent/domains/defi/prompts.py`

```python
def create_yield_research_prompt(asset: str, min_apy: float) -> str:
    """Generate DeFi yield research prompt"""
    return f"""
Research current yield farming opportunities for {asset} on Stellar blockchain.

# Requirements
- Minimum APY: {min_apy}%
- Focus on: Blend Capital, Soroswap, other major Stellar DeFi protocols
- Consider: Safety, liquidity, historical performance

# Deliverables
1. Top 3-5 opportunities ranked by risk-adjusted returns
2. Analysis of each opportunity (risks, benefits, mechanics)
3. Risk factors and mitigation strategies
4. Recommended allocation strategy for vault deployment

# Research Approach
- Use web search for current APY rates and market conditions
- Verify all claims with on-chain data when possible
- Cite all sources using markdown links
- Focus on mainnet protocols only

# Output Format
- Executive summary
- Detailed opportunity analysis
- Comparative table of yields
- Recommendations with rationale
- Appendix with all sources
"""

def create_strategy_analysis_prompt(
    strategy_description: str,
    market_context: dict | None
) -> str:
    """Generate strategy analysis prompt"""
    context_str = ""
    if market_context:
        context_str = f"\n\n# Market Context\n"
        for key, value in market_context.items():
            context_str += f"- {key}: {value}\n"

    return f"""
Analyze the following DeFi strategy for the Stellar ecosystem.

# Strategy Description
{strategy_description}
{context_str}

# Analysis Requirements
1. **Risk Assessment**
   - Smart contract risks
   - Market risks (impermanent loss, price volatility)
   - Liquidity risks
   - Counterparty risks

2. **Expected Returns**
   - Base yield calculations
   - Reward token value considerations
   - Compounding effects
   - Time-weighted analysis

3. **Potential Issues**
   - Edge cases
   - Market condition dependencies
   - Protocol-specific considerations

4. **Optimization Recommendations**
   - Position sizing
   - Rebalancing triggers
   - Risk mitigation techniques

5. **Alternative Strategies**
   - Comparable approaches
   - Risk/reward comparison
   - When to use each alternative

# Focus Areas
- Stellar-specific considerations (Soroban contracts, Blend Capital)
- Mainnet deployment readiness
- Non-custodial vault compatibility
- Gas/fee optimization

# Output Format
Structured analysis with clear sections, data-driven recommendations,
and cited sources for all claims.
"""
```

---

## API Integration

### FastAPI Endpoints

**File**: `backend/main.py` (additions)

```python
from backend.agent.ghostwriter.graph import create_ghostwriter_graph
from backend.agent.ghostwriter.config import GhostwriterConfig
from backend.agent.domains.defi.research import DeFiResearcher

# Initialize ghostwriter
ghostwriter_config = GhostwriterConfig()
ghostwriter_graph = create_ghostwriter_graph(ghostwriter_config)
defi_researcher = DeFiResearcher(ghostwriter_config)

@app.post("/api/ghostwriter/generate")
async def generate_report(request: GhostwriterRequest):
    """
    General-purpose report generation endpoint.

    Request:
    {
        "messages": [{"role": "user", "content": "Research X..."}],
        "style_guide_path": "/path/to/STYLEGUIDE.md",  // optional
        "output_file": "/path/to/output.md"  // optional
    }
    """
    try:
        result = await ghostwriter_graph.ainvoke({
            "messages": request.messages,
            "style_guide_path": request.style_guide_path,
            "citations_file": request.citations_file,
            "output_file": request.output_file
        })

        return {
            "success": True,
            "report": result["final_report"],
            "citations": result["validated_citations"],
            "output_file": result.get("output_file")
        }
    except Exception as e:
        logger.error(f"Ghostwriter error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/defi/research-yield")
async def research_yield_opportunities(request: YieldResearchRequest):
    """
    DeFi-specific yield research endpoint.
    Uses ghostwriter under the hood.
    """
    try:
        result = await defi_researcher.research_yield_opportunities(
            asset=request.asset,
            min_apy=request.min_apy
        )
        return result
    except Exception as e:
        logger.error(f"DeFi research error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/defi/analyze-strategy")
async def analyze_defi_strategy(request: StrategyAnalysisRequest):
    """
    DeFi strategy analysis endpoint.
    """
    try:
        result = await defi_researcher.analyze_strategy(
            strategy_description=request.strategy_description,
            market_context=request.market_context
        )
        return result
    except Exception as e:
        logger.error(f"Strategy analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

## Migration Plan

### Phase 1: Foundation (Week 1)
- [ ] Create `backend/agent/ghostwriter/` directory structure
- [ ] Implement `config.py` with four LLM roles
- [ ] Implement `state.py` with LangGraph state definitions
- [ ] Create basic `graph.py` with node placeholders
- [ ] Set up testing infrastructure

### Phase 2: Core Workflow (Week 2)
- [ ] Implement planning node
- [ ] Implement research supervisor node
- [ ] Implement citation validation node
- [ ] Implement draft generation node
- [ ] Test end-to-end basic research flow

### Phase 3: Quality Enhancement (Week 3)
- [ ] Implement critique node
- [ ] Implement revision node
- [ ] Implement style control node
- [ ] Integrate STYLEGUIDE.md loading
- [ ] Test style application

### Phase 4: DeFi Migration (Week 4)
- [ ] Create `backend/agent/domains/defi/` structure
- [ ] Migrate DeFi prompts to `domains/defi/prompts.py`
- [ ] Implement `DeFiResearcher` wrapper
- [ ] Update API endpoints
- [ ] Deprecate old `claude_sdk_wrapper.py` DeFi methods

### Phase 5: Integration & Testing (Week 5)
- [ ] Integration testing with real DeFi queries
- [ ] Performance optimization (caching, parallel execution)
- [ ] Documentation updates
- [ ] Frontend integration (if needed)

---

## Benefits of This Architecture

### ✅ Separation of Concerns
- **General research** (ghostwriter) separated from **domain logic** (DeFi)
- Easy to add new domains (security research, market analysis, etc.)

### ✅ Citation Management
- Validates all sources
- Prevents hallucinated URLs
- Builds trust through verified claims

### ✅ Style Guide Integration
- Consistent branding (carbon fiber kintsugi)
- Professional presentation
- Reusable across all reports

### ✅ Multi-Phase Quality
- Planning → Research → Draft → Critique → Revision → Style
- Iterative improvement built into workflow
- Higher quality output than single-pass generation

### ✅ Configurable LLM Roles
- Cost optimization (Haiku for summarization)
- Quality optimization (Sonnet 4.5 for final reports)
- Parallel execution for speed

### ✅ Extensibility
- Add new research domains easily
- Swap LLM models per role
- Integrate new tools (MCP servers, etc.)

---

## Testing Strategy

### Unit Tests
```python
# backend/agent/ghostwriter/tests/test_citation.py

async def test_citation_validation():
    """Test citation validator extracts and validates URLs"""
    research_notes = [
        "According to [Study](https://example.com/paper), ...",
        "See also https://arxiv.org/abs/1234.5678"
    ]

    validated = await citation_validator.validate_citations(research_notes)

    assert len(validated) == 2
    assert validated[0]["url"] == "https://example.com/paper"
    assert "arxiv.org" in validated[1]["url"]

# backend/agent/ghostwriter/tests/test_workflow.py

async def test_full_workflow():
    """Test complete ghostwriter workflow"""
    graph = create_ghostwriter_graph(GhostwriterConfig())

    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": "Research DeFi yields"}],
        "style_guide_path": "/home/user/tuxedo/STYLEGUIDE.md"
    })

    assert result["final_report"]
    assert result["validated_citations"]
    assert "carbon fiber" not in result["final_report"].lower()  # Style applied, not content
```

### Integration Tests
```python
# backend/agent/domains/defi/tests/test_defi_research.py

async def test_yield_research():
    """Test DeFi yield research integration"""
    researcher = DeFiResearcher(GhostwriterConfig())

    result = await researcher.research_yield_opportunities(
        asset="USDC",
        min_apy=5.0
    )

    assert result["success"]
    assert "USDC" in result["report"]
    assert len(result["citations"]) > 0
```

---

## Open Questions

1. **Citation validation strictness**: How strict should we be? Fail entire report if one citation invalid?
2. **Style guide versioning**: Should we support multiple style guides?
3. **Caching**: Should we cache research findings for similar queries?
4. **User feedback loop**: Should we allow users to provide feedback for revision?
5. **Cost management**: Token limits per research task? Budget caps?

---

## References

- **Open Deep Research**: https://github.com/yusefmosiah/open_deep_research
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **Tuxedo Style Guide**: `/home/user/tuxedo/STYLEGUIDE.md`
- **Current SDK Wrapper**: `/home/user/tuxedo/backend/agent/claude_sdk_wrapper.py`

---

**Next Steps**: Review this proposal, address open questions, and proceed with Phase 1 implementation.
