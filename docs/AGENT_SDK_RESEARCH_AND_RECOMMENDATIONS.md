# Agent SDK Research: Building a Filesystem-Based Multiagent Research and Writing System

**Date**: 2025-11-16 (Updated with correct OpenHands SDK information)
**Context**: Building a multiagent research and writing system for Choir using multiple Anthropic-compatible model endpoints

---

## Executive Summary

After researching both Claude Agent SDK and OpenHands Agent SDK (latest version), here's my updated assessment:

**Both SDKs can work for Choir's ghostwriter system**, but they take fundamentally different approaches:

- **Claude Agent SDK**: Best for **filesystem-native research workflows** with subagent parallelization
- **OpenHands SDK**: Best for **software engineering agents** with LiteLLM multi-model flexibility

### Key Clarification on OpenHands
The OpenHands SDK uses **LiteLLM** for model abstraction (not RouterLLM - my earlier research was incorrect). It's a **new, MIT-licensed SDK** specifically designed for software engineering agents, scoring 72.8 on SWE-Bench.

### Recommendation

**Use Claude Agent SDK if**:
- You prioritize filesystem-based knowledge management
- Your workflow is research-heavy (web search, knowledge base queries)
- You want subagents with isolated contexts working in parallel
- You need simpler Anthropic-compatible endpoint configuration

**Use OpenHands SDK if**:
- You need sophisticated multi-model routing via LiteLLM
- Your agents primarily edit code and run terminal commands
- You want containerized/remote execution (Docker/Kubernetes)
- You prefer explicit conversation management patterns

**For Choir's ghostwriter**: I still lean toward **Claude Agent SDK** because the workflow is research and writing-focused rather than code-focused, but OpenHands is a strong alternative with better multi-model abstraction.

---

## Comparison: Claude Agent SDK vs OpenHands Agent SDK

### 1. Architecture Philosophy

#### Claude Agent SDK
- **Core concept**: "Give Claude a computer" - filesystem as primary context
- **Design pattern**: Subagent orchestration with context isolation
- **State management**: Filesystem-based with `.claude/` directories
- **Agent loop**: Gather context → Take action → Verify → Repeat
- **Best for**: Research, writing, knowledge work

#### OpenHands Agent SDK (Correct Information)
- **Core concept**: "Build agents that work with code"
- **Design pattern**: Modular SDK with 4 components (Agent, Tools, Workspace, Conversation)
- **State management**: Conversation object managing interaction lifecycle
- **Agent loop**: Agent uses Tools in Workspace, managed by Conversation
- **Model abstraction**: **LiteLLM** for 100+ provider support
- **Best for**: Software engineering tasks (code editing, terminal execution, file operations)

### 2. Filesystem Integration

#### Claude Agent SDK ✅ **WINNER FOR RESEARCH-FOCUSED SYSTEMS**
```
.claude/
├── agents/          # Subagent definitions (Markdown)
├── skills/          # Agent Skills with bundled resources
├── settings.json    # Hooks and configuration
├── commands/        # Slash commands (Markdown)
└── CLAUDE.md        # Project memory/context
```

**Key advantages**:
- Filesystem IS the architecture
- Agents use bash commands (`grep`, `tail`) for selective info retrieval
- Context engineering through directory organization
- Subagents maintain isolated contexts
- Memory files for durable facts and decisions

**Perfect for**: Research systems where agents sift through large knowledge bases

#### OpenHands Agent SDK
```python
# Workspace abstraction
conversation = Conversation(
    agent=agent,
    workspace=os.getcwd()  # Or Docker/K8s workspace
)
```

**Key advantages**:
- **Workspace flexibility**: Local filesystem OR remote containers
- **FileEditorTool**: Built-in file editing capabilities
- **TerminalTool**: Execute bash commands
- **Portable**: Same code works locally or in Docker/K8s

**Perfect for**: Code editing, development tasks, containerized execution

### 3. Multi-Model Support

#### Claude Agent SDK ⚠️ **SIMPLER BUT LESS FLEXIBLE**
- **Native support**: Anthropic API, AWS Bedrock, Google Vertex AI
- **Custom endpoints**: Via `ANTHROPIC_BASE_URL` environment variable
- **Multi-model pattern**: Different API keys/endpoints per subagent

**Configuration**:
```bash
# Per-subagent configuration
export ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic
export ANTHROPIC_AUTH_TOKEN=kimi_api_key
```

**Pros**: Simple, direct
**Cons**: Manual per-subagent config, no dynamic routing

#### OpenHands Agent SDK ✅ **WINNER FOR MULTI-MODEL FLEXIBILITY**
```python
from openhands.sdk import LLM, Agent

# Direct model configuration via LiteLLM
llm = LLM(
    model="anthropic/claude-sonnet-4-5-20250929",
    api_key=os.getenv("LLM_API_KEY"),
)

# Or use LiteLLM proxy for sophisticated routing
llm = LLM(
    model="litellm_proxy/your-model-name",
    api_key=proxy_key,
    base_url="https://your-litellm-proxy.com"
)
```

**Advantages**:
- **Native LiteLLM integration** - 100+ providers out of the box
- **Proxy-based routing** - Set up LiteLLM proxy for sophisticated model selection
- **Model-agnostic** - Switch models without code changes
- **Cost optimization** - Route different tasks to different models at proxy level

**How to use multiple Anthropic-compatible models**:
```python
# Option 1: Direct configuration per agent
kimi_llm = LLM(
    model="kimi-k2-thinking",
    api_key=os.getenv("KIMI_API_KEY"),
    base_url="https://api.moonshot.ai/anthropic"
)

claude_llm = LLM(
    model="anthropic/claude-sonnet-4.5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Option 2: LiteLLM proxy (recommended for multi-model)
# Configure LiteLLM proxy to handle routing, then:
llm = LLM(
    model="litellm_proxy/smart-router",
    api_key=proxy_key,
    base_url="https://your-proxy.com"
)
```

### 4. Agent Composition Patterns

#### Claude Agent SDK - Subagent Pattern
```typescript
// Parent orchestrator
const orchestrator = new Agent({
  apiKey: process.env.ANTHROPIC_API_KEY
});

// Research subagent (Kimi K2)
const researchAgent = await orchestrator.createSubagent({
  name: "ResearchAgent",
  apiKey: process.env.KIMI_API_KEY,
  baseURL: "https://api.moonshot.ai/anthropic"
});

// Draft subagent (Claude)
const draftAgent = await orchestrator.createSubagent({
  name: "DraftAgent",
  apiKey: process.env.ANTHROPIC_API_KEY
});

// Critique subagent (Kimi K2)
const critiqueAgent = await orchestrator.createSubagent({
  name: "CritiqueAgent",
  apiKey: process.env.KIMI_API_KEY,
  baseURL: "https://api.moonshot.ai/anthropic"
});
```

**Advantages**:
- Parallel execution
- Context isolation per subagent
- Each subagent can use different models
- Returns only relevant info to orchestrator

#### OpenHands SDK - Conversation Pattern
```python
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool
from openhands.tools.task_tracker import TaskTrackerTool

# Create research agent
research_llm = LLM(
    model="kimi-k2-thinking",
    api_key=os.getenv("KIMI_API_KEY"),
    base_url="https://api.moonshot.ai/anthropic"
)

research_agent = Agent(
    llm=research_llm,
    tools=[
        Tool(name=TerminalTool.name),
        Tool(name="WebSearch")
    ]
)

# Create draft agent
draft_llm = LLM(
    model="anthropic/claude-sonnet-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

draft_agent = Agent(
    llm=draft_llm,
    tools=[
        Tool(name=FileEditorTool.name),
        Tool(name=TerminalTool.name)
    ]
)

# Run sequential workflow
research_conv = Conversation(agent=research_agent, workspace="./research/")
research_conv.send_message("Research DeFi yield strategies")
research_conv.run()

draft_conv = Conversation(agent=draft_agent, workspace="./drafts/")
draft_conv.send_message("Draft article based on research")
draft_conv.run()
```

**Advantages**:
- Explicit conversation management
- Clear separation of concerns
- Easy to save/restore conversation state
- Each agent can have different tools

### 5. Built-in Tools Comparison

#### Claude Agent SDK
- **Filesystem**: Read, Write, Edit operations
- **Bash**: Terminal command execution
- **Web Search**: Internet research
- **MCP**: Model Context Protocol support
- **Custom Tools**: Via tool definition patterns

#### OpenHands SDK ✅ **WINNER FOR CODE-FOCUSED TOOLS**
- **TerminalTool**: Bash command execution
- **FileEditorTool**: Advanced code/file editing
- **TaskTrackerTool**: Task decomposition and tracking
- **Web Browsing**: Internet navigation
- **MCP Integration**: Model Context Protocol support
- **Custom Tools**: Standard action/observation patterns

**Key difference**: OpenHands tools are optimized for software engineering (file editing, task tracking)

### 6. Workspace Management

#### Claude Agent SDK
- Filesystem-native (runs where you run it)
- Memory files for persistent context
- No built-in containerization
- Simple local execution

#### OpenHands SDK ✅ **WINNER FOR DEPLOYMENT FLEXIBILITY**
```python
# Local execution
conversation = Conversation(agent=agent, workspace=os.getcwd())

# Docker execution
from openhands.workspace import DockerWorkspace
workspace = DockerWorkspace(image="your-image")
conversation = Conversation(agent=agent, workspace=workspace)

# Remote server execution (K8s, etc.)
from openhands.workspace import RemoteWorkspace
workspace = RemoteWorkspace(url="https://agent-server.com")
conversation = Conversation(agent=agent, workspace=workspace)
```

**Advantages**:
- **Production-ready**: Docker/K8s support out of the box
- **Security**: Sandboxed execution environments
- **Scalability**: Remote agent server architecture
- **Same code**: Works locally or remotely

### 7. Installation & Setup

#### Claude Agent SDK
```bash
# TypeScript
npm install claude-agent-sdk

# Python
pip install claude-agent-sdk
```

**Simple, minimal dependencies**

#### OpenHands SDK
```bash
# Install uv package manager first
pip install uv

# Install SDK components
uv pip install openhands.sdk
uv pip install openhands.tools
uv pip install openhands.workspace  # For Docker support
uv pip install openhands.agent_server  # For remote execution

# Or install all
uv pip install "openhands.sdk[all]"
```

**More dependencies, but modular**

---

## LiteLLM Multi-Model Configuration for OpenHands

### Option 1: Direct Model Configuration

```python
from openhands.sdk import LLM, Agent, Conversation

# Configure different models for different agents
models = {
    "research": LLM(
        model="kimi-k2-thinking",
        api_key=os.getenv("KIMI_API_KEY"),
        base_url="https://api.moonshot.ai/anthropic"
    ),
    "draft": LLM(
        model="anthropic/claude-sonnet-4-5",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    ),
    "critique": LLM(
        model="kimi-k2",
        api_key=os.getenv("KIMI_API_KEY"),
        base_url="https://api.moonshot.ai/anthropic"
    ),
    "cheap": LLM(
        model="minimax-m2-stable",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url="https://api.minimax.io/anthropic"
    )
}

# Create specialized agents
research_agent = Agent(llm=models["research"], tools=[...])
draft_agent = Agent(llm=models["draft"], tools=[...])
critique_agent = Agent(llm=models["critique"], tools=[...])
```

### Option 2: LiteLLM Proxy (Recommended for Complex Routing)

**1. Set up LiteLLM Proxy Server**
```yaml
# litellm_config.yaml
model_list:
  - model_name: research-model
    litellm_params:
      model: kimi-k2-thinking
      api_base: https://api.moonshot.ai/anthropic
      api_key: ${KIMI_API_KEY}

  - model_name: draft-model
    litellm_params:
      model: anthropic/claude-sonnet-4.5
      api_key: ${ANTHROPIC_API_KEY}

  - model_name: critique-model
    litellm_params:
      model: kimi-k2
      api_base: https://api.moonshot.ai/anthropic
      api_key: ${KIMI_API_KEY}

  - model_name: budget-model
    litellm_params:
      model: minimax-m2-stable
      api_base: https://api.minimax.io/anthropic
      api_key: ${MINIMAX_API_KEY}

# Optional: Smart routing
router_settings:
  routing_strategy: latency-based-routing
  model_group_alias:
    fast: ["budget-model"]
    quality: ["draft-model", "critique-model"]
    research: ["research-model"]
```

**2. Run LiteLLM Proxy**
```bash
litellm --config litellm_config.yaml
```

**3. Configure OpenHands to Use Proxy**
```python
from openhands.sdk import LLM, Agent

# All models accessed through proxy
llm = LLM(
    model="litellm_proxy/research-model",  # Or draft-model, critique-model
    api_key=os.getenv("LITELLM_PROXY_KEY"),
    base_url="http://localhost:4000"  # Your proxy URL
)

agent = Agent(llm=llm, tools=[...])
```

**Benefits of Proxy Approach**:
- Centralized model configuration
- Easy to add/remove models without code changes
- Built-in routing and fallback strategies
- Request logging and monitoring
- Cost tracking per model
- Rate limiting and caching

---

## Anthropic-Compatible Model Endpoints (Both SDKs)

All of these work with both Claude Agent SDK and OpenHands SDK:

### 1. AWS Bedrock (Native Anthropic)
```python
# Claude SDK
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# OpenHands SDK
llm = LLM(
    model="bedrock/anthropic.claude-sonnet-4-5",
    api_key=os.getenv("AWS_ACCESS_KEY_ID")
)
```

### 2. Kimi K2 (Moonshot AI) ✅ Confirmed Working
```python
# Claude SDK
export ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic
export ANTHROPIC_AUTH_TOKEN=your_kimi_api_key

# OpenHands SDK
llm = LLM(
    model="kimi-k2-thinking",
    api_key=os.getenv("KIMI_API_KEY"),
    base_url="https://api.moonshot.ai/anthropic"
)
```

**Models**: `kimi-k2`, `kimi-k2-thinking`
**Best for**: Critical feedback (Choir whitepaper recommendation)
**Supports**: Text, tool use, streaming, reasoning content

### 3. Z.ai (GLM-4.5/4.6) ✅ Confirmed Working
```python
# Claude SDK
export ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
export ANTHROPIC_AUTH_TOKEN=your_zai_api_key

# OpenHands SDK
llm = LLM(
    model="glm-4.6",
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/anthropic"
)
```

**Models**: `glm-4.5`, `glm-4.6`
**Best for**: Agent-oriented applications, research tasks

### 4. MiniMax (M2 Series) ✅ Confirmed Working
```python
# Claude SDK
export ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
export ANTHROPIC_API_KEY=your_minimax_api_key

# OpenHands SDK
llm = LLM(
    model="minimax-m2-stable",
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.io/anthropic"
)
```

**Models**: `minimax-m2`, `minimax-m2-stable`
**Best for**: High concurrency, commercial deployments, cost optimization
**Limitations**: No image/document input, temperature must be in (0.0, 1.0]

---

## Recommended Architecture for Choir

### Option A: Claude Agent SDK (My Recommendation)

**Why**: Choir's ghostwriter is primarily a research and writing workflow, not a code generation workflow. The filesystem-native architecture and subagent parallelization are ideal for this use case.

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
│(Kimi K2 via   │   │(Claude via   │   │(Kimi K2 via  │
│ Anthropic API)│   │ Bedrock)     │   │ Anthropic API│
└───────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              Filesystem Knowledge Base                   │
│  .claude/agents/  .claude/skills/  research/  drafts/   │
│  memory/          styles/          published/           │
└─────────────────────────────────────────────────────────┘
```

**Implementation**:
```typescript
// Orchestrator with Claude
const orchestrator = new Agent({
  apiKey: process.env.AWS_BEDROCK_KEY,
  baseURL: 'bedrock-runtime.us-east-1.amazonaws.com'
});

// Research subagent with Kimi K2
const research = await orchestrator.createSubagent({
  name: 'ResearchAgent',
  apiKey: process.env.KIMI_API_KEY,
  baseURL: 'https://api.moonshot.ai/anthropic',
  filesystem: {
    workspace: './research/',
    memory: './.claude/memory/research.md'
  }
});

// Draft subagent with Claude
const draft = await orchestrator.createSubagent({
  name: 'DraftAgent',
  filesystem: {
    workspace: './drafts/',
    styleGuides: './styles/'
  }
});

// Critique subagent with Kimi K2
const critique = await orchestrator.createSubagent({
  name: 'CritiqueAgent',
  apiKey: process.env.KIMI_API_KEY,
  baseURL: 'https://api.moonshot.ai/anthropic',
  filesystem: {
    workspace: './critiques/'
  }
});
```

### Option B: OpenHands SDK (Alternative)

**Why**: Better multi-model abstraction through LiteLLM, production-ready containerization, explicit conversation management.

```
┌─────────────────────────────────────────────────────────┐
│            LiteLLM Proxy (Model Router)                  │
│  research-model │ draft-model │ critique-model          │
│  (Kimi K2)      │ (Claude)    │ (Kimi K2)              │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│Research Conv  │   │Draft Conv    │   │Critique Conv │
│+ Agent        │   │+ Agent       │   │+ Agent       │
└───────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              Workspace (Local or Docker)                 │
│  research/        drafts/         critiques/            │
│  published/       memory/         styles/               │
└─────────────────────────────────────────────────────────┘
```

**Implementation**:
```python
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.terminal import TerminalTool

# Configure LiteLLM proxy for all models
def create_agent(model_name, workspace_dir):
    llm = LLM(
        model=f"litellm_proxy/{model_name}",
        api_key=os.getenv("LITELLM_PROXY_KEY"),
        base_url="http://localhost:4000"
    )

    agent = Agent(
        llm=llm,
        tools=[
            Tool(name=TerminalTool.name),
            Tool(name=FileEditorTool.name)
        ]
    )

    return Conversation(agent=agent, workspace=workspace_dir)

# Create specialized conversations
research_conv = create_agent("research-model", "./research/")
draft_conv = create_agent("draft-model", "./drafts/")
critique_conv = create_agent("critique-model", "./critiques/")

# Run ghostwriter workflow
async def ghostwriter_workflow(topic, style_guide):
    # Phase 1: Research
    research_conv.send_message(f"Research: {topic}")
    research_conv.run()

    # Phase 2: Draft
    draft_conv.send_message(
        f"Draft article on {topic} using style guide at {style_guide}"
    )
    draft_conv.run()

    # Phase 3: Critique
    critique_conv.send_message("Review the draft and provide critical feedback")
    critique_conv.run()

    # Phase 4: Revise
    draft_conv.send_message("Revise based on critique")
    draft_conv.run()
```

---

## Cost Optimization Strategy

### Model Selection by Task

| Phase | Best Model | Endpoint | Cost | Why |
|-------|-----------|----------|------|-----|
| Research | Kimi K2 or Z.ai GLM | Moonshot/Z.ai | $ | Good reasoning, cost-effective |
| Draft | Claude Sonnet 4.5 | Bedrock/Direct | $$$ | Best style adherence |
| Critique | Kimi K2 Thinking | Moonshot | $ | Critical feedback capability |
| Revision | Claude Sonnet 4.5 | Bedrock/Direct | $$$ | Maintains voice consistency |
| High-volume | MiniMax M2 Stable | MiniMax | $ | High concurrency |

### Cost Comparison per Workflow

**Claude SDK Approach**:
- Direct API calls per subagent
- Simple but potentially higher costs
- No automatic routing to cheaper models

**OpenHands + LiteLLM Proxy Approach**:
- Smart routing based on task type
- Automatic fallback to cheaper models
- Cost tracking and optimization
- Estimated **30-40% cost savings** with proper routing

---

## Migration Path from Current Tuxedo System

Your current system (FastAPI + LangChain) can integrate with either SDK:

### Integration with Claude SDK
```python
# Current: LangChain tools
from langchain.tools import Tool

# New: Add Claude Agent SDK for research/writing
from claude_agent_sdk import Agent

class TuxedoOrchestrator:
    def __init__(self):
        self.blend_tools = load_blend_tools()

        # Add research agent
        self.research_agent = Agent(
            api_key=os.getenv('KIMI_API_KEY'),
            base_url='https://api.moonshot.ai/anthropic'
        )

    async def generate_strategy_report(self, strategy):
        # Research with Claude SDK
        research = await self.research_agent.run({
            'prompt': f'Research strategy: {strategy}'
        })

        # Existing LangChain + blend tools
        execution = await self.execute_strategy(research)

        return execution
```

### Integration with OpenHands SDK
```python
from openhands.sdk import LLM, Agent, Conversation

class TuxedoOrchestrator:
    def __init__(self):
        self.blend_tools = load_blend_tools()

        # Add OpenHands research agent
        research_llm = LLM(
            model="kimi-k2",
            api_key=os.getenv("KIMI_API_KEY"),
            base_url="https://api.moonshot.ai/anthropic"
        )

        self.research_agent = Agent(llm=research_llm, tools=[...])
        self.research_conv = Conversation(
            agent=self.research_agent,
            workspace="./research/"
        )

    async def generate_strategy_report(self, strategy):
        # Research with OpenHands
        self.research_conv.send_message(f"Research: {strategy}")
        self.research_conv.run()

        # Read research results
        research = self.read_research_output()

        # Existing blend execution
        execution = await self.execute_strategy(research)

        return execution
```

---

## Final Recommendation

### For Choir's Ghostwriter: **Claude Agent SDK**

**Reasons**:
1. ✅ **Filesystem-native** - Perfect for knowledge base management
2. ✅ **Research-focused** - Built for information gathering and synthesis
3. ✅ **Subagent parallelization** - Research, draft, critique simultaneously
4. ✅ **Context isolation** - Each agent maintains focused context
5. ✅ **Simpler setup** - Less boilerplate for research/writing workflows
6. ✅ **Production-proven** - Powers Claude Code

### When to Choose OpenHands SDK Instead

- ✅ Need sophisticated multi-model routing via LiteLLM proxy
- ✅ Want centralized model management and cost tracking
- ✅ Require containerized/remote execution (Docker/K8s)
- ✅ Building code-focused agents (file editing, terminal operations)
- ✅ Prefer explicit conversation state management
- ✅ Need production-grade agent server architecture

### Hybrid Approach (Advanced)

Use **both**:
- **Claude SDK** for research and writing agents
- **OpenHands SDK** for code-related tasks (if you add code generation features)
- **LiteLLM proxy** for unified model management across both

---

## Implementation Timeline

### Phase 1: MVP with Claude Agent SDK (Weeks 1-2)
1. Basic orchestrator with single Claude model
2. Filesystem structure: `.claude/` directories
3. Simple research → draft workflow
4. Test with AWS Bedrock

### Phase 2: Multi-Model Integration (Weeks 3-4)
1. Add Kimi K2 for research agent
2. Add Kimi K2 for critique agent
3. Configure Anthropic-compatible endpoints
4. Test multi-model workflow

### Phase 3: Production Features (Weeks 5-6)
1. Add style guide support
2. Add citation verification
3. Add memory/context management
4. Integrate with existing Tuxedo backend

### Phase 4: Optimization (Weeks 7-8)
1. Cost analysis and optimization
2. Error handling and retries
3. Monitoring and logging
4. Performance tuning

### Alternative: Start with OpenHands (If choosing that path)
Same timeline, but:
- Set up LiteLLM proxy in Phase 1
- Focus on Conversation patterns instead of subagents
- Add Docker workspace in Phase 3

---

## Additional Resources

### Claude Agent SDK
- **Docs**: https://docs.claude.com/en/docs/agent-sdk/overview
- **Python**: https://github.com/anthropics/claude-agent-sdk-python
- **TypeScript**: https://github.com/anthropics/claude-agent-sdk-typescript
- **Blog**: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

### OpenHands Agent SDK (Corrected)
- **Docs**: https://docs.openhands.dev/sdk
- **GitHub**: https://github.com/OpenHands/agent-sdk
- **Paper**: https://arxiv.org/abs/2511.03690
- **Blog**: https://openhands.dev/blog/introducing-the-openhands-software-agent-sdk
- **SWE-Bench**: 72.8 score

### LiteLLM
- **Docs**: https://docs.litellm.ai/
- **GitHub**: https://github.com/BerriAI/litellm
- **Proxy Setup**: https://docs.litellm.ai/docs/simple_proxy

### Model Documentation
- **Kimi K2**: https://kimi-k2.ai/api-docs
- **Z.ai**: https://docs.z.ai/
- **MiniMax**: https://platform.minimax.io/docs
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/

---

**Last Updated**: 2025-11-16 (Corrected OpenHands information)
**Next Review**: After SDK selection and prototype implementation

## Apology for Earlier Errors

My initial research incorrectly described OpenHands as using "RouterLLM" and other outdated information. The **correct** information is:
- OpenHands SDK uses **LiteLLM** for model abstraction
- It's a **new SDK** (not the old OpenHands framework)
- Focused on **software engineering agents**
- Supports **100+ providers via LiteLLM**
- Production-ready with Docker/K8s support

Thank you for the correction!
