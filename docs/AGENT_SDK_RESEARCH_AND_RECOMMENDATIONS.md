# Agent SDK Research: Building a Filesystem-Based Multiagent Research and Writing System

**Date**: 2025-11-16
**Context**: Building a multiagent research and writing system for Choir using multiple Anthropic-compatible model endpoints

---

## Executive Summary

After deep research into Claude Agent SDK and OpenHands Agent SDK, **I recommend using the Claude Agent SDK** for building Choir's filesystem-based multiagent research and writing system. This recommendation is based on:

1. **Native filesystem-based architecture** designed for agent orchestration
2. **Built-in subagent support** for parallel research workflows
3. **Simpler integration** with Anthropic-compatible endpoints
4. **Better alignment** with Choir's multi-model orchestration needs (Claude for drafting, Kimi K2 for critique)
5. **Production-ready** context management and security controls

However, **OpenHands has superior multi-model routing** through RouterLLM if you need sophisticated conditional model selection at the SDK level.

---

## Comparison: Claude Agent SDK vs OpenHands Agent SDK

### 1. Architecture Philosophy

#### Claude Agent SDK
- **Core concept**: "Give Claude a computer" - filesystem as primary context
- **Design pattern**: Subagent orchestration with context isolation
- **State management**: Filesystem-based with `.claude/` directories
- **Agent loop**: Gather context → Take action → Verify → Repeat

#### OpenHands Agent SDK
- **Core concept**: "Event-sourced stateless agents" - immutable specifications
- **Design pattern**: Four-package modular architecture (sdk, tools, workspace, server)
- **State management**: ConversationState object with append-only event log
- **Agent loop**: Action → Execution → Observation pattern

### 2. Filesystem Integration

#### Claude Agent SDK ✅ **WINNER FOR FILESYSTEM-BASED SYSTEMS**
```
.claude/
├── agents/          # Subagent definitions (Markdown)
├── skills/          # Agent Skills with bundled resources
├── settings.json    # Hooks and configuration
├── commands/        # Slash commands (Markdown)
└── CLAUDE.md        # Project memory/context
```

**Key advantages**:
- Agents use bash commands (`grep`, `tail`) to selectively retrieve info
- Context engineering through filesystem organization
- Subagents maintain isolated contexts
- Memory files for durable facts and decisions

**Perfect for**: Research systems where agents need to sift through large knowledge bases

#### OpenHands Agent SDK
- Workspace abstraction (LocalWorkspace / RemoteWorkspace)
- Filesystem access through Tool system
- Primary focus on remote execution and sandboxing
- Less emphasis on filesystem as context engineering

**Better for**: Sandboxed execution environments, containerized deployments

### 3. Multi-Agent Orchestration

#### Claude Agent SDK ✅ **WINNER FOR CHOIR'S USE CASE**
```typescript
// Subagent pattern
const researchAgent = await agent.createSubagent({
  name: "Research Agent",
  instructions: "Search web and knowledge base for sources"
});

const critiqueAgent = await agent.createSubagent({
  name: "Critique Agent",
  instructions: "Provide critical feedback on drafts"
});
```

**Advantages**:
- **Parallelization**: Multiple subagents work simultaneously
- **Context isolation**: Each subagent has own context window
- **Selective reporting**: Subagents return only relevant info to orchestrator
- **Natural fit** for Choir's workflow: research → draft → critique → revise

#### OpenHands Agent SDK
```python
# Supervisor pattern with RouterLLM
class ResearchSupervisor(Agent):
    def select_agent(self, task):
        # Route to specialized agents
        pass
```

**Advantages**:
- Conditional agent selection based on task
- Registry-based tool resolver for distributed execution
- Better for complex task routing

### 4. Multi-Model Support

#### Claude Agent SDK ⚠️ **LIMITED BUT WORKABLE**
- **Native support**: Anthropic API, AWS Bedrock, Google Vertex AI
- **Custom endpoints**: Via `ANTHROPIC_BASE_URL` environment variable
- **Multi-model pattern**: Use different API keys per subagent

**Configuration**:
```bash
# Main orchestrator uses AWS Bedrock Claude
export ANTHROPIC_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com

# Research subagent uses Claude via Bedrock
# Draft subagent uses Claude via direct API
# Critique subagent uses Kimi K2
export ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic
export ANTHROPIC_AUTH_TOKEN=kimi_api_key
```

**Limitation**: No built-in model routing - requires separate agent instances

#### OpenHands Agent SDK ✅ **WINNER FOR SOPHISTICATED ROUTING**
```python
from openhands.sdk.llm import RouterLLM

class ChoirModelRouter(RouterLLM):
    def select_llm(self, messages):
        # Route research queries to efficient models
        if is_research_query(messages):
            return kimi_k2_llm
        # Route drafting to Claude
        elif is_drafting_task(messages):
            return claude_sonnet_llm
        # Route critique to Kimi K2
        elif is_critique_task(messages):
            return kimi_k2_llm
        # Route cheap queries to minimax
        else:
            return minimax_llm
```

**Advantages**:
- **Native multi-model routing** through RouterLLM
- **100+ provider support** via LiteLLM
- **Conditional selection** based on message content
- **Cost optimization** by routing to appropriate models

### 5. Security and Permissions

#### Claude Agent SDK
- Fine-grained tool control: `allowedTools`, `disallowedTools`
- Permission modes for capability restrictions
- Human-in-the-loop via hooks system
- **Best for**: User-facing applications requiring permissions

#### OpenHands Agent SDK ✅ **WINNER FOR PRODUCTION**
- LLMSecurityAnalyzer: LOW/MEDIUM/HIGH/UNKNOWN risk rating
- ConfirmationPolicy for adaptive trust
- Agents pause in WAITING_FOR_CONFIRMATION state
- **Best for**: Production deployments with varying trust levels

### 6. Ease of Integration

#### Claude Agent SDK ✅ **WINNER FOR QUICK START**
```typescript
import { Agent } from 'claude-agent-sdk';

const agent = new Agent({
  apiKey: process.env.ANTHROPIC_API_KEY,
  allowedTools: ['filesystem', 'bash', 'web_search']
});

const result = await agent.run({
  prompt: "Research DeFi yield strategies and write a report"
});
```

**Advantages**:
- Simpler API surface
- Less boilerplate
- Opinionated defaults that work well
- Faster time to prototype

#### OpenHands Agent SDK
```python
from openhands.sdk import Agent, LocalConversation
from openhands.tools import FileSystemTool, BashTool

agent = Agent(
    llm=llm_config,
    tools=[FileSystemTool(), BashTool()],
    security_analyzer=analyzer,
    confirmation_policy=policy
)

conversation = LocalConversation.create(agent_spec=agent)
```

**Advantages**:
- More explicit control
- Better for complex configurations
- Easier to test (mocked LLMs)

---

## Anthropic-Compatible Model Endpoints

All of these can work with both SDKs:

### 1. AWS Bedrock (Native Anthropic)
```bash
# Claude Agent SDK
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# Use with Bedrock provider
```

### 2. Kimi K2 (Moonshot AI)
```bash
export ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic
export ANTHROPIC_AUTH_TOKEN=your_kimi_api_key
```

**Models**: `kimi-k2`, `kimi-k2-thinking`
**Best for**: Critical feedback (as noted in Choir whitepaper)
**Supports**: Text, tool use, streaming, reasoning content
**Limitations**: No image/document input yet

### 3. Z.ai (GLM-4.5/4.6)
```bash
export ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
export ANTHROPIC_AUTH_TOKEN=your_zai_api_key
```

**Models**: `glm-4.5`, `glm-4.6`
**Best for**: Agent-oriented applications
**Supports**: Full Anthropic API compatibility
**Note**: No free credits, paid service

### 4. MiniMax (M2 Series)
```bash
# International
export ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic

# China
export ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic

export ANTHROPIC_API_KEY=your_minimax_api_key
```

**Models**: `minimax-m2`, `minimax-m2-stable`
**Best for**: High concurrency, commercial deployments
**Limitations**:
- No image/document input
- Ignores: `top_k`, `stop_sequences`, `service_tier`, `mcp_servers`
- Temperature must be in (0.0, 1.0]

---

## Recommended Architecture for Choir

Based on your Choir whitepaper context, here's the recommended architecture:

### Architecture: Claude Agent SDK with Multi-Model Subagents

```
┌─────────────────────────────────────────────────────────┐
│              Ghostwriter Orchestrator                    │
│                (Claude via Bedrock)                      │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│Research Agent │   │Draft Agent   │   │Critique Agent│
│(Kimi K2 or    │   │(Claude Sonnet│   │(Kimi K2)     │
│ Z.ai GLM-4.6) │   │ via Bedrock) │   │              │
└───────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              Filesystem Knowledge Base                   │
│  research/      drafts/       critiques/    published/  │
│  sources/       styles/       citations/    memory/     │
└─────────────────────────────────────────────────────────┘
```

### Implementation Pattern

```typescript
// Main orchestrator
const orchestrator = new Agent({
  apiKey: process.env.AWS_BEDROCK_KEY,
  baseURL: 'https://bedrock-runtime.us-east-1.amazonaws.com',
  systemPrompt: 'You orchestrate research and writing agents'
});

// Research subagent (Kimi K2 for web search and knowledge retrieval)
const researchAgent = await orchestrator.createSubagent({
  name: 'ResearchAgent',
  apiKey: process.env.KIMI_API_KEY,
  baseURL: 'https://api.moonshot.ai/anthropic',
  instructions: `
    Search web and Choir knowledge base for relevant sources.
    Query vector database for semantic similarity.
    Aggregate context into structured foundation.
  `,
  filesystem: {
    workspace: './research/',
    memory: './memory/research_memory.md'
  }
});

// Draft subagent (Claude for style-aware writing)
const draftAgent = await orchestrator.createSubagent({
  name: 'DraftAgent',
  apiKey: process.env.ANTHROPIC_API_KEY,
  instructions: `
    Generate drafts following user style guides.
    Use Claude's unique steering capability.
    Reference provided research sources.
  `,
  filesystem: {
    workspace: './drafts/',
    styleGuides: './styles/',
    memory: './memory/draft_memory.md'
  }
});

// Critique subagent (Kimi K2 for critical feedback)
const critiqueAgent = await orchestrator.createSubagent({
  name: 'CritiqueAgent',
  apiKey: process.env.KIMI_API_KEY,
  baseURL: 'https://api.moonshot.ai/anthropic',
  instructions: `
    Provide critical feedback on drafts.
    Identify weak arguments and unsupported claims.
    Suggest substantial improvements.
  `,
  filesystem: {
    workspace: './critiques/',
    memory: './memory/critique_memory.md'
  }
});

// Revision subagent (Claude for maintaining voice)
const revisionAgent = await orchestrator.createSubagent({
  name: 'RevisionAgent',
  apiKey: process.env.ANTHROPIC_API_KEY,
  instructions: `
    Incorporate critique while maintaining user voice.
    Strengthen arguments and evidence.
    Maintain style guide adherence.
  `,
  filesystem: {
    workspace: './revisions/',
    memory: './memory/revision_memory.md'
  }
});

// Orchestration workflow
async function ghostwriterWorkflow(topic: string, styleGuide: string) {
  // Phase 1: Research
  const research = await researchAgent.run({
    prompt: `Research: ${topic}`,
    context: { styleGuide }
  });

  // Phase 2: Draft
  const draft = await draftAgent.run({
    prompt: `Draft article on ${topic}`,
    context: { research, styleGuide }
  });

  // Phase 3: Critique
  const critique = await critiqueAgent.run({
    prompt: `Critically review this draft`,
    context: { draft }
  });

  // Phase 4: Revise
  const final = await revisionAgent.run({
    prompt: `Revise draft based on critique`,
    context: { draft, critique, styleGuide }
  });

  // Phase 5: Citation verification
  await verifyCitations(final);

  return final;
}
```

### Filesystem Structure

```
choir-agents/
├── .claude/
│   ├── agents/
│   │   ├── research.md          # Research agent config
│   │   ├── draft.md             # Draft agent config
│   │   ├── critique.md          # Critique agent config
│   │   └── revision.md          # Revision agent config
│   ├── skills/
│   │   ├── web-search/          # Web search skill
│   │   ├── vector-query/        # Vector DB query skill
│   │   ├── citation-verify/     # Citation verification skill
│   │   └── style-match/         # Style guide matching skill
│   ├── settings.json            # Multi-model configurations
│   └── CLAUDE.md                # Project context and memory
├── knowledge-base/
│   ├── research/                # Research outputs from agents
│   ├── sources/                 # Retrieved source documents
│   └── citations/               # Citation graph data
├── drafts/                      # Draft articles
├── critiques/                   # Critique outputs
├── revisions/                   # Revised versions
├── styles/                      # User style guides
├── published/                   # Final published articles
└── memory/
    ├── research_memory.md       # Persistent research context
    ├── draft_memory.md          # Drafting patterns and learnings
    ├── critique_memory.md       # Critique patterns
    └── revision_memory.md       # Revision strategies
```

---

## Alternative: OpenHands for Sophisticated Routing

If you need **sophisticated conditional model routing** based on query characteristics:

```python
from openhands.sdk import Agent, RouterLLM, LLMConfig

# Define model configurations
claude_bedrock = LLMConfig(
    provider='anthropic',
    model='claude-sonnet-4.5',
    api_key=os.getenv('AWS_ACCESS_KEY'),
    base_url='bedrock-runtime.us-east-1.amazonaws.com'
)

kimi_k2 = LLMConfig(
    provider='anthropic',
    model='kimi-k2-thinking',
    api_key=os.getenv('KIMI_API_KEY'),
    base_url='https://api.moonshot.ai/anthropic'
)

minimax_m2 = LLMConfig(
    provider='anthropic',
    model='minimax-m2-stable',
    api_key=os.getenv('MINIMAX_API_KEY'),
    base_url='https://api.minimax.io/anthropic'
)

zai_glm = LLMConfig(
    provider='anthropic',
    model='glm-4.6',
    api_key=os.getenv('ZAI_API_KEY'),
    base_url='https://api.z.ai/api/anthropic'
)

# Custom router for Choir use cases
class ChoirRouter(RouterLLM):
    def select_llm(self, messages):
        last_message = messages[-1].content.lower()

        # Research phase: use cost-effective models
        if 'research' in last_message or 'search' in last_message:
            return zai_glm  # Good for research

        # Drafting phase: use Claude (best style adherence)
        elif 'draft' in last_message or 'write' in last_message:
            return claude_bedrock

        # Critique phase: use Kimi K2 (best critical feedback)
        elif 'critique' in last_message or 'review' in last_message:
            return kimi_k2

        # High-volume queries: use stable endpoints
        elif 'quick' in last_message or 'fast' in last_message:
            return minimax_m2

        # Default: Claude
        else:
            return claude_bedrock

# Use the router in agents
agent = Agent(
    llm=ChoirRouter(models=[claude_bedrock, kimi_k2, minimax_m2, zai_glm]),
    tools=[FileSystemTool(), WebSearchTool(), VectorQueryTool()]
)
```

**When to use OpenHands instead**:
- Need dynamic model selection based on message content
- Want to optimize costs by routing cheap queries to cheaper models
- Require sophisticated task-based routing
- Need sandboxed execution environments

---

## Implementation Recommendations

### Phase 1: MVP with Claude Agent SDK
1. **Start simple**: Single agent using Claude via AWS Bedrock
2. **Add filesystem**: Implement `.claude/` directory structure
3. **Add subagents**: Research → Draft → Critique → Revise
4. **Test with one model**: Validate workflow with just Claude

### Phase 2: Multi-Model Integration
1. **Add Kimi K2**: Configure critique agent with Moonshot endpoint
2. **Add style guides**: Implement style guide loading and matching
3. **Add citation verification**: Build citation checking system
4. **Test multi-model**: Validate different models per phase

### Phase 3: Advanced Features
1. **Add Z.ai GLM**: Research agent alternative
2. **Add MiniMax**: High-concurrency fallback
3. **Implement routing logic**: Conditional model selection
4. **Add Agent Skills**: Package expertise as reusable skills

### Phase 4: Production Hardening
1. **Add security analyzer**: Implement risk assessment
2. **Add confirmation policies**: Human-in-loop for sensitive operations
3. **Add monitoring**: Track model performance and costs
4. **Add failover**: Graceful degradation when endpoints fail

---

## Cost Optimization Strategy

### Model Selection by Task

| Phase | Best Model | Why | Cost |
|-------|-----------|-----|------|
| Research | Z.ai GLM-4.6 or Kimi K2 | Agent-oriented, good reasoning | $ |
| Draft | Claude Sonnet 4.5 | Best style adherence | $$$ |
| Critique | Kimi K2 Thinking | Critical feedback capability | $ |
| Revision | Claude Sonnet 4.5 | Maintains voice consistency | $$$ |
| High-volume | MiniMax M2 Stable | High concurrency, commercial | $ |

### Cost Saving Patterns
1. **Use cheaper models for research**: Z.ai or MiniMax
2. **Reserve Claude for quality work**: Drafting and revision only
3. **Batch research queries**: Amortize API overhead
4. **Cache research results**: Store in filesystem, reuse across drafts
5. **Smart context management**: Use bash tools to minimize context size

---

## Security Considerations

### API Key Management
```bash
# Store in environment, never commit
.env
ANTHROPIC_API_KEY=sk-ant-xxx
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
KIMI_API_KEY=xxx
ZAI_API_KEY=xxx
MINIMAX_API_KEY=xxx
```

### Filesystem Isolation
```typescript
const agent = new Agent({
  filesystem: {
    allowedPaths: ['./knowledge-base/', './drafts/', './memory/'],
    deniedPaths: ['../', '/etc/', '/home/'],
    readOnly: ['./published/']
  }
});
```

### Rate Limiting
```typescript
const rateLimiter = {
  'kimi-k2': { requests: 100, per: 'minute' },
  'claude-sonnet': { requests: 50, per: 'minute' },
  'minimax-m2': { requests: 1000, per: 'minute' },
  'glm-4.6': { requests: 200, per: 'minute' }
};
```

---

## Testing Strategy

### Unit Tests (Fast)
```typescript
// Mock LLM responses
const mockResearch = {
  sources: [...],
  summary: '...'
};

test('research agent returns sources', async () => {
  const agent = createMockAgent(mockResearch);
  const result = await agent.run({ prompt: 'research topic' });
  expect(result.sources).toBeDefined();
});
```

### Integration Tests (Real APIs, $$$)
```typescript
// Real API calls for end-to-end validation
test('full ghostwriter workflow', async () => {
  const result = await ghostwriterWorkflow(
    'DeFi yield strategies',
    styleGuide
  );
  expect(result.citations).toHaveLength(greaterThan(0));
  expect(result.content).toContain('yield');
}, { timeout: 300000 }); // 5 min timeout
```

### Benchmark Tests
- Compare model performance on same task
- Track cost per workflow
- Measure quality (citation accuracy, style adherence)

---

## Migration Path from Current Tuxedo System

Your current system (FastAPI + LangChain) can integrate with Claude Agent SDK:

```python
# Current: LangChain tools
from langchain.tools import Tool

# New: Claude Agent SDK subagents
from claude_agent_sdk import Agent

class TuxedoOrchestrator:
    def __init__(self):
        # Existing Blend tools
        self.blend_tools = load_blend_tools()

        # New: Research agent
        self.research_agent = Agent(
            api_key=os.getenv('KIMI_API_KEY'),
            base_url='https://api.moonshot.ai/anthropic'
        )

    async def generate_strategy_report(self, strategy):
        # Research phase: Use Kimi K2 agent
        research = await self.research_agent.run({
            'prompt': f'Research DeFi strategy: {strategy}',
            'tools': ['web_search', 'vector_query']
        })

        # Draft phase: Use existing LangChain + Claude
        draft = await self.llm_chain.run({
            'research': research,
            'strategy': strategy
        })

        return draft
```

---

## Final Recommendation

**Use Claude Agent SDK** for Choir's filesystem-based multiagent research and writing system:

### Why Claude Agent SDK Wins:
1. ✅ **Native filesystem architecture** - Perfect for knowledge base systems
2. ✅ **Subagent parallelization** - Research, draft, critique simultaneously
3. ✅ **Context isolation** - Each agent maintains focused context
4. ✅ **Simpler API** - Faster development, less boilerplate
5. ✅ **Production-ready** - Powers Claude Code, proven at scale
6. ✅ **Works with all your models** - AWS Bedrock, Kimi, Z.ai, MiniMax

### When to Consider OpenHands:
- ❓ Need sophisticated RouterLLM for dynamic model selection
- ❓ Want event-sourced state for replay/debugging
- ❓ Require sandboxed remote execution
- ❓ Building multi-tenant production service

### Implementation Timeline:
- **Week 1-2**: Basic Claude Agent SDK setup, single model
- **Week 3-4**: Add subagents for research/draft/critique
- **Week 5-6**: Integrate Kimi K2 and other models
- **Week 7-8**: Production hardening, monitoring, testing

### Expected Costs:
- **Development**: $500-1000 in API calls during build
- **Production**: ~$0.50-2.00 per full ghostwriter workflow
- **Optimization potential**: 40-60% cost reduction with smart routing

---

## Additional Resources

### Claude Agent SDK
- **Docs**: https://docs.claude.com/en/docs/agent-sdk/overview
- **Python**: https://github.com/anthropics/claude-agent-sdk-python
- **TypeScript**: https://github.com/anthropics/claude-agent-sdk-typescript
- **Blog**: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

### OpenHands Agent SDK
- **Docs**: https://docs.all-hands.dev/
- **Paper**: https://arxiv.org/abs/2511.03690
- **GitHub**: https://github.com/OpenHands/agent-sdk
- **Blog**: https://openhands.dev/blog/introducing-the-openhands-software-agent-sdk

### Model Documentation
- **Kimi K2**: https://kimi-k2.ai/api-docs
- **Z.ai**: https://docs.z.ai/
- **MiniMax**: https://platform.minimax.io/docs
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/

---

**Last Updated**: 2025-11-16
**Next Review**: After MVP implementation
