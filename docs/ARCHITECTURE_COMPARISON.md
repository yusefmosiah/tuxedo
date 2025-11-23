# Architecture Comparison: Current vs. Proposed

## Current Architecture (Tightly Coupled)

```
┌───────────────────────────────────────────────┐
│         claude_sdk_wrapper.py                 │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │ ClaudeSDKAgent                          │ │
│  │                                         │ │
│  │  • query_simple()              ✅      │ │
│  │  • analyze_strategy()          ❌ DeFi│ │
│  │  • research_yield_opportunities() ❌  │ │
│  │  • generate_strategy_report()   ❌    │ │
│  │                                         │ │
│  │  Problems:                              │ │
│  │  - No citation management               │ │
│  │  - No style guide support               │ │
│  │  - Single-turn queries                  │ │
│  │  - Domain logic mixed with infra        │ │
│  └─────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

## Proposed Architecture (Layered & Extensible)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application Layer                    │
│  /api/ghostwriter/generate  |  /api/defi/research-yield         │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
┌──────────────────────┐              ┌──────────────────────┐
│  domains/defi/       │              │  domains/security/   │
│  research.py         │              │  (future)            │
│                      │              │                      │
│  DeFiResearcher      │              │  SecurityResearcher  │
│  • Uses ghostwriter  │              │  • Uses ghostwriter  │
│  • DeFi prompts      │              │  • Security prompts  │
│  • Stellar focus     │              │  • CVE focus         │
└──────────────────────┘              └──────────────────────┘
          │                                       │
          └───────────────────┬───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              agent/ghostwriter/ (LangGraph)                     │
│                                                                 │
│   graph.py: StateGraph orchestration                            │
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐ │
│   │ Planning │ -> │ Research │ -> │ Citation │ -> │  Draft  │ │
│   │          │    │ Supervisor│   │  Check   │    │         │ │
│   └──────────┘    └──────────┘    └──────────┘    └─────────┘ │
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│   │ Critique │ -> │ Revision │ -> │  Style   │ -> Final Report│
│   │          │    │          │    │ Control  │                │
│   └──────────┘    └──────────┘    └──────────┘                │
│                                                                 │
│   Features:                                                     │
│   ✅ Citation validation (URL checking, claim verification)    │
│   ✅ Style guide integration (STYLEGUIDE.md)                   │
│   ✅ Multi-phase quality (critique -> revision)                │
│   ✅ Parallel research (max_concurrent_research_units)         │
│   ✅ Four LLM roles (research, summary, compress, report)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           claude_sdk_wrapper.py (Simplified Foundation)         │
│                                                                 │
│   ClaudeSDKAgent (infrastructure only)                          │
│   • Authentication (Anthropic API / AWS Bedrock)                │
│   • Tool configuration (WebSearch, Read, Write)                 │
│   • Model options                                               │
│   • query_simple() for basic use cases                          │
│                                                                 │
│   ❌ REMOVED: All domain-specific methods                      │
│   ✅ FOCUSED: Pure infrastructure layer                        │
└─────────────────────────────────────────────────────────────────┘
```

## Key Improvements

### 1. **Separation of Concerns**

| Layer | Responsibility | Examples |
|-------|---------------|----------|
| **Application** | API endpoints, request handling | FastAPI routes |
| **Domain** | Business logic, domain prompts | DeFi research, Security analysis |
| **Core Engine** | General research workflow | Ghostwriter graph |
| **Foundation** | Infrastructure, auth, tools | Claude SDK wrapper |

### 2. **Research Workflow Enhancement**

**Current**: Single-turn query
```
User Question -> LLM -> Response
```

**Proposed**: Multi-phase with quality gates
```
User Question
  -> Planning (research brief)
  -> Research Supervisor (parallel sub-researchers)
  -> Citation Check (validate all URLs)
  -> Draft (initial report)
  -> Critique (quality assessment)
  -> Revision (apply improvements)
  -> Style Control (apply STYLEGUIDE.md)
  -> Final Report
```

### 3. **Citation Management**

**Current**: ❌ None (risk of hallucinated sources)

**Proposed**: ✅ Full validation pipeline
- Extract all URLs (markdown links, bare URLs, arXiv, DOI)
- Fetch each source
- Verify claims using LLM judgment
- Fallback search if original link fails
- Only use validated citations in final report

### 4. **Style Guide Integration**

**Current**: ❌ No style application

**Proposed**: ✅ Carbon fiber kintsugi aesthetic
- Load `STYLEGUIDE.md`
- Apply typography hierarchy (sans, serif, mono)
- Use metallic gradients for high-value content
- Convert inline citations to footnotes
- Maintain technical accuracy while enhancing presentation

### 5. **LLM Configuration**

**Current**: Single model for all tasks

**Proposed**: Four specialized roles
```python
research_model: "claude-sonnet-4.5"        # Deep analysis
summarization_model: "claude-haiku-4"      # Fast compression (cost-effective)
compression_model: "claude-sonnet-4.5"     # Consolidation
final_report_model: "claude-sonnet-4.5"    # Premium output
```

**Benefits**:
- Cost optimization (Haiku for summarization)
- Quality optimization (Sonnet 4.5 for final report)
- Configurable per use case

### 6. **Extensibility**

**Current**: Add DeFi methods to wrapper (tight coupling)

**Proposed**: Add new domain modules
```
backend/agent/domains/
├── defi/           # Yield research, strategy analysis
├── security/       # CVE research, threat analysis
├── market/         # Market research, trend analysis
└── technical/      # Technical documentation, API research
```

Each domain:
- Uses same ghostwriter engine
- Provides domain-specific prompts
- Can override configuration (different LLM roles)
- Isolated testing

## Migration Path

### Step 1: Build ghostwriter core (no breaking changes)
```
backend/agent/ghostwriter/  <- new
backend/agent/claude_sdk_wrapper.py  <- unchanged
```

### Step 2: Create DeFi domain module
```
backend/agent/domains/defi/  <- new
backend/agent/claude_sdk_wrapper.py  <- unchanged (deprecated methods)
```

### Step 3: Update API endpoints
```python
# New endpoint
@app.post("/api/ghostwriter/generate")
async def generate_report(...):
    return await ghostwriter_graph.ainvoke(...)

# DeFi endpoint (uses ghostwriter)
@app.post("/api/defi/research-yield")
async def research_yield(...):
    return await defi_researcher.research_yield_opportunities(...)

# Old endpoint (deprecated but working)
@app.post("/api/chat")  # Still works, uses old wrapper for now
```

### Step 4: Deprecate old methods
```python
# claude_sdk_wrapper.py

class ClaudeSDKAgent:
    async def query_simple(self, prompt: str) -> str:
        """✅ Keep - general utility"""

    async def analyze_strategy(self, ...):
        """❌ Deprecated - use domains.defi.DeFiResearcher"""
        warnings.warn("Use DeFiResearcher.analyze_strategy instead")
        # Redirect to new implementation
```

### Step 5: Remove old code (after migration complete)
```python
# claude_sdk_wrapper.py (final state)

class ClaudeSDKAgent:
    """Pure infrastructure layer - no domain logic"""

    def __init__(self, ...):
        # Auth, tools, options

    async def query_simple(self, prompt: str) -> str:
        """Basic query for simple use cases"""

    # All domain methods removed
```

## Code Volume Comparison

### Current (Single File)
```
claude_sdk_wrapper.py: ~460 lines
  - Infrastructure: ~120 lines
  - DeFi methods: ~200 lines
  - Helpers: ~140 lines
```

### Proposed (Modular)
```
Foundation Layer:
  claude_sdk_wrapper.py: ~150 lines (infrastructure only)

Core Engine:
  ghostwriter/config.py: ~80 lines
  ghostwriter/state.py: ~60 lines
  ghostwriter/graph.py: ~150 lines
  ghostwriter/nodes/: ~700 lines (7 nodes × 100 lines)
  ghostwriter/utils/: ~200 lines

Domain Layer (DeFi):
  domains/defi/research.py: ~150 lines
  domains/defi/prompts.py: ~100 lines

Total: ~1,590 lines
```

**More code, but**:
- Better separation of concerns
- Easier to test (unit test each node)
- Easier to extend (add new domains)
- Higher quality output (multi-phase workflow)
- Reusable across domains

## Performance Comparison

### Current
```
Single LLM call: 2-5 seconds
No citation validation
No style application
Total: 2-5 seconds (but lower quality)
```

### Proposed
```
Planning: 2-3 seconds
Research (5 parallel): 10-15 seconds
Citation check: 5-10 seconds (validates URLs)
Draft: 5-8 seconds
Critique: 3-5 seconds
Revision: 5-8 seconds
Style control: 3-5 seconds
Total: 33-54 seconds (but significantly higher quality)
```

**Trade-off**: 10x slower, but 10x better quality with validated citations and style.

**Optimization opportunities**:
- Cache research findings
- Parallel citation validation
- Skip critique/revision for simple queries
- Use Haiku for faster summarization

## Cost Comparison (Per Report)

### Current (Single Sonnet 4.5 call)
```
Input: 2,000 tokens × $3/M = $0.006
Output: 1,000 tokens × $15/M = $0.015
Total: $0.021 per report
```

### Proposed (Multi-phase with role optimization)
```
Research (Sonnet 4.5): 5 calls × $0.021 = $0.105
Summarization (Haiku): 5 calls × $0.002 = $0.010
Compression (Sonnet 4.5): 1 call × $0.021 = $0.021
Draft (Sonnet 4.5): 1 call × $0.030 = $0.030
Critique (Sonnet 4.5): 1 call × $0.015 = $0.015
Revision (Sonnet 4.5): 1 call × $0.030 = $0.030
Style (Sonnet 4.5): 1 call × $0.030 = $0.030
Total: $0.241 per report
```

**Trade-off**: ~11x cost, but validated citations, multi-phase quality, and professional styling.

**Cost optimizations**:
- Use Haiku for research (not just summarization): -60% research cost
- Cache research findings for similar queries: -50% repeat query cost
- Skip critique/revision for simple queries: -30% total cost
- Batch citation validation: -20% citation cost

## Conclusion

The proposed architecture trades **speed and cost** for **quality and maintainability**:

✅ **Quality**: Multi-phase workflow, citation validation, style guide
✅ **Maintainability**: Separated concerns, testable nodes, clear responsibilities
✅ **Extensibility**: Easy to add new domains without touching core
✅ **Professionalism**: Consistent branding via style guide

❌ **Speed**: 10x slower (33-54s vs 2-5s)
❌ **Cost**: 11x more expensive ($0.24 vs $0.02)

**Recommendation**: Implement proposed architecture for:
- Research reports (DeFi, security, market analysis)
- User-facing documentation
- Strategy analysis with citations

Keep current simple wrapper for:
- Quick chat responses
- Simple queries
- Real-time interactions
