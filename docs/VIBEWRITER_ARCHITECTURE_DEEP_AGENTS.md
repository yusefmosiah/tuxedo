# Vibewriter Architecture: Deep Agents, MicroVMs, and NATS JetStream

**Author:** Choir Team
**Date:** November 28, 2025

## Executive Summary: The Strategic Pivot

The core of the `tuxedo` project's architecture is pivoting to a highly specialized, secure, and autonomous agent built on **LangChain Deep Agents** and isolated within **MicroVMs**. This shift is driven by the need for a **financial delegate** agent that requires hardware-level security and complex, hierarchical planning capabilities. The data infrastructure is being refined with **NATS JetStream** to provide a high-performance, persistent, and secure backbone for agent state and real-time economic signaling.

The LangChain Deep Agent *is* the core agent, and the **Vibewriter** is the set of skills, tools, and specialized knowledge that define its function. This unified architecture simplifies the deployment model and ensures the core agent is inherently capable of the Vibewriter's secure, stateful, and economically-integrated research and writing experience.

| Component | New State (Vibewriter Deep Agent) | Justification |
| :--- | :--- | :--- |
| **Agent Core** | **LangChain Deep Agent** | Enables hierarchical planning, long-term memory, and complex, multi-step tasks [1]. |
| **Sandbox** | **MicroVM (Firecracker/ERA)** | Provides hardware-level isolation, essential for protecting the agent's financial keys and assets from container escape [2] [3]. |
| **Filesystem** | **Custom `SandboxBackendProtocol`** | Allows integration of the MicroVM's filesystem with the Deep Agent's tools, enabling full computer control and persistent state [1] [4]. |
| **Data Backbone** | **NATS with JetStream** | Offers persistent, high-speed messaging for agent-to-agent communication and state storage, overcoming the speed/persistence trade-off [5] [6]. |
| **Agent Name** | **Vibewriter** | The Deep Agent *is* the Vibewriter. The name now refers to the agent's complete set of capabilities and tools. |

## I. LangChain Deep Agents: The New Agent Core

LangChain Deep Agents represent a significant evolution in agent architecture, moving beyond simple single-step tool-calling loops. The architecture is modular, built on a middleware pattern, and is ideal for the complex, long-running research tasks required by the Vibewriter.

### A. Core Capabilities

Deep Agents are characterized by four key pillars [1]:

1.  **Hierarchical Planning:** They include a built-in `write_todos` tool, allowing the agent to break down a complex prompt into a sequence of discrete, trackable steps. This is crucial for the Vibewriter's role as a financial delegate, which must manage research, citation, and publishing autonomously.

2.  **Filesystem Backend:** The agent is equipped with a virtual filesystem, which is accessed via tools like `ls`, `read_file`, `write_file`, `edit_file`, `glob`, and `grep`. This provides the "full computer control" required to manage research artifacts, drafts, and user keys within the isolated environment.

3.  **Subagents:** The architecture supports spawning specialized subagents, enabling a modular approach where a planning agent delegates tasks to a research agent, a verification agent, and a publishing agent.

4.  **Long-Term Memory:** Deep Agents are designed to maintain state and context across long-running sessions, which is a prerequisite for the Vibewriter's multi-hour research and writing workflows.

### B. Custom Sandbox Integration: Implementing `SandboxBackendProtocol`

The requirement to connect a self-hosted sandbox (the MicroVM) to the Deep Agent is achieved by implementing the **`SandboxBackendProtocol`** [4]. This custom backend acts as the "runloop connector," securely bridging the Deep Agent's logic with the isolated execution environment.

The Deep Agent's filesystem tools (e.g., `ls`, `write_file`) operate through a pluggable backend. To integrate the MicroVM, the `tuxedo` project must create a custom backend that translates the Deep Agent's filesystem commands into secure remote procedure calls (RPCs) to the MicroVM's execution environment.

Here is a conceptual Python implementation for the custom backend:

```python
from deepagents.backends.base import SandboxBackendProtocol
from typing import List, Dict, Any

class MicroVMBackend(SandboxBackendProtocol):
    """
    A custom backend to connect the Deep Agent's filesystem operations
    to a remote MicroVM orchestrator (e.g., ERA or custom Firecracker manager).
    """
    def __init__(self, microvm_rpc_client):
        self.client = microvm_rpc_client

    def ls_info(self, path: str) -> List[Dict[str, Any]]:
        """List files and directories in the MicroVM."""
        # Translate to an RPC call to the MicroVM orchestrator
        # The orchestrator executes 'ls -l' inside the MicroVM and returns structured data
        return self.client.execute_command(f"ls -l {path}")

    def read(self, file_path: str) -> str:
        """Read file content from the MicroVM."""
        # Translate to an RPC call that executes 'cat' inside the MicroVM
        return self.client.execute_command(f"cat {file_path}")

    def write(self, file_path: str, content: str) -> None:
        """Write new file content to the MicroVM."""
        # Translate to a secure file transfer or a shell command inside the MicroVM
        # For security, a dedicated RPC for file transfer is preferred over shell execution
        self.client.secure_write_file(file_path, content)

    def grep_raw(self, pattern: str, path: str) -> str:
        """Search file content using regex inside the MicroVM."""
        # Translate to an RPC call that executes 'grep -r' inside the MicroVM
        return self.client.execute_command(f"grep -r '{pattern}' {path}")

# Example of how to configure the Deep Agent to use the custom backend
# from deepagents.agent import DeepAgent
# from deepagents.backends.composite import CompositeBackend
#
# microvm_client = get_microvm_rpc_client() # Assume this function exists
# custom_backend = MicroVMBackend(microvm_client)
#
# # Use a CompositeBackend to route all filesystem operations to the MicroVM
# backend = CompositeBackend(routes={"/": custom_backend})
#
# # agent = DeepAgent(..., backend=backend)
```

### C. Skills: The New Agent Pattern

The Vibewriter merges the former separate `tuxedo` agent and research pipeline into one Deep Agent, which uses **skills** in addition to tools.

*   **Skills vs. Tools:** In the context of modern agent frameworks like LangChain Deep Agents, a **tool** is a simple, atomic function (e.g., `search_web`, `read_file`). A **skill** is a more complex, pre-written, and often multi-step script or piece of documentation that the agent can choose to execute in its sandboxed environment.

*   **Implementation:** The Deep Agent's ability to use skills is tied directly to its **Filesystem Backend** and **Hierarchical Planning**. The agent can:
    1.  **Plan:** Use the `write_todos` tool to decide which skill is needed.
    2.  **Access:** Read the skill's script (e.g., a Python file or shell script) from its virtual filesystem (which is the MicroVM).
    3.  **Execute:** Run the script inside the secure sandbox (the MicroVM).

*   **Benefit:** This pattern allows the agent to learn, adapt, and share complex, reusable workflows (like "Perform Financial Due Diligence" or "Generate Citation-Ready Report") without having to reason through every step from scratch. The agent's intelligence is in choosing the right skill and providing the correct inputs, while the skill itself provides the reliable, pre-vetted logic.

## II. MicroVMs: The Secure Execution Environment

The strategic decision to use MicroVMs is non-negotiable for a financial delegate agent. MicroVMs provide hardware-enforced isolation, which is necessary to protect the agent's signing authority over real assets [2].

### A. Firecracker and ERA

**Firecracker** is the industry standard for secure, low-overhead virtualization, developed by AWS. It is purpose-built for creating and managing small virtual machines with minimal overhead, making it ideal for the rapid spin-up and tear-down required for multi-tenant AI agents [3].

**ERA (BinSquare/ERA)** is an open-source project specifically designed for sandboxing AI-generated code using **Firecracker microVMs** [7]. ERA provides an orchestration layer on top of Firecracker with session persistence and multi-language support.

The most likely architecture for the Vibewriter:

1.  **MicroVM Runtime:** **Firecracker** (production-proven, powers AWS Lambda)
2.  **Orchestrator:** **ERA** provides the orchestration layer, managing VM lifecycle, session persistence, and the secure RPC layer that the custom `SandboxBackendProtocol` will connect to.

This approach leverages ERA's Firecracker-based security with built-in orchestration and session management - exactly what we need for stateful agent workflows.

### B. Security Model: Container Escape = Bank Robbery

When managing financial keys and signing authority, container isolation is insufficient:

| Isolation Method | Security Model | Threat Level | Suitability for Financial Delegation |
| :--- | :--- | :--- | :--- |
| **Containers** | Shared Host Kernel | High (Escapes happen monthly) | ❌ Unsuitable. A single escape compromises all user private keys on the host. |
| **MicroVMs** | Dedicated Guest Kernel + KVM | Low (Escapes are rare hypervisor vulns) | ✅ **Required.** Hardware-enforced isolation is necessary to protect the agent's signing authority over real assets. |

**Firecracker's Multi-Layer Defense:**
1. **Layer 1**: Hardware virtualization (KVM)
2. **Layer 2**: Jailer process (namespaces, cgroups, seccomp filters)
3. **Layer 3**: Minimal attack surface (50K LOC, Rust, minimal devices)

## III. NATS JetStream and Object Storage

The data infrastructure must support both the high-speed, real-time communication of the Choir protocol and the long-term persistence of agent state and research artifacts. **NATS JetStream** is the ideal solution.

### A. JetStream for Agent State Persistence

JetStream is the built-in persistence engine for NATS, providing guaranteed, at-least-once message delivery and storage [5].

*   **Agent Memory:** The Deep Agent's long-term memory and state (e.g., the `write_todos` plan, intermediate results) can be modeled as messages in a JetStream **Stream**. This ensures that if a MicroVM is suspended or crashes, the agent can resume its work exactly where it left off by replaying the stream.
*   **Decoupling:** JetStream decouples the agent's logic from the persistence layer, making the system more resilient and scalable.

Here is a conceptual Python snippet for using NATS JetStream for state persistence:

```python
import asyncio
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

async def setup_jetstream_persistence(nc: NATS):
    """Sets up a JetStream stream for agent state persistence."""
    js = nc.jetstream()

    # Define a stream for the Vibewriter's state messages
    stream_name = "VIBEWRITER_STATE"
    subject = "vibewriter.state.>"

    # Create the stream if it doesn't exist
    await js.add_stream(name=stream_name, subjects=[subject], config=StreamConfig(
        retention="limits",
        max_age=3600 * 24 * 7, # 7 days retention
        max_msgs=-1,
        storage="file" # Use file storage for persistence
    ))
    print(f"JetStream stream '{stream_name}' configured for state persistence.")

async def persist_agent_state(js, agent_id, state_data):
    """Publishes agent state to the JetStream stream."""
    subject = f"vibewriter.state.{agent_id}"
    await js.publish(subject, state_data.encode())
    print(f"Agent {agent_id} state persisted.")

# Example usage:
# nc = NATS()
# await nc.connect(servers=["nats://127.0.0.1:4222"])
# await setup_jetstream_persistence(nc)
# js = nc.jetstream()
# await persist_agent_state(js, "agent-001", '{"status": "researching", "step": 5}')
```

### B. Object Store for File Persistence

The research artifacts (drafts, evidence, final reports) are too large to store efficiently within the JetStream message payload limits. NATS addresses this with its **Object Store** feature [6].

*   **NATS Object Store:** This feature implements a chunking mechanism, allowing files of any size to be stored and retrieved by associating them with a unique key. It is designed to be a high-performance, S3-like interface built directly into NATS.
*   **Integration with Object Store:** The Vibewriter's custom `SandboxBackendProtocol` should be designed to use the NATS Object Store for all large file operations (`write_file`, `read_file`). This keeps the entire data plane within the NATS ecosystem, simplifying infrastructure and leveraging NATS's security and performance features.

Here is a conceptual Python snippet for using NATS Object Store for file persistence:

```python
from nats.js.client import JetStreamContext

async def setup_object_store(js: JetStreamContext):
    """Sets up a NATS Object Store for file persistence."""
    store_name = "VIBEWRITER_FILES"

    # Create the object store if it doesn't exist
    await js.add_object_store(name=store_name)
    print(f"NATS Object Store '{store_name}' configured for file persistence.")
    return await js.object_store(store_name)

async def store_file(os, file_path, data):
    """Stores a file in the NATS Object Store."""
    # The file_path can be used as the key (name) in the object store
    info = await os.put(file_path, data=data)
    print(f"File '{file_path}' stored. Size: {info.size} bytes.")

async def retrieve_file(os, file_path):
    """Retrieves a file from the NATS Object Store."""
    data = await os.get(file_path)
    print(f"File '{file_path}' retrieved.")
    return data

# Example usage:
# os = await setup_object_store(js)
# await store_file(os, "report_draft.md", b"## Draft Report\n...")
# content = await retrieve_file(os, "report_draft.md")
```

### C. NATS for Agent-to-Agent Citation Communication

The Choir protocol is fundamentally a system of economic signals based on citations. NATS provides a robust backbone for this inter-agent communication:

*   **Citations as Messages:** A citation event (e.g., one agent using another's published work) can be modeled as a message published to a specific NATS subject (e.g., `citation.new.<article_id>`).
*   **Real-Time Signaling:** The speed of NATS ensures that economic signals (citations) are processed in near real-time, which is vital for the dynamic calculation of citation rewards and the overall responsiveness of the "Thought Bank".
*   **MicroVM Communication:** NATS is an ideal choice for facilitating communication between the isolated MicroVMs (each running a Vibewriter agent) and the host services (like the Qdrant vector database and the smart contract execution service). This replaces complex, custom networking with a simple, secure publish-subscribe model.

## IV. Unified Architecture Overview

### A. System Components

```
┌──────────────────────────────────────────────────────────────────┐
│                      Vibewriter Deep Agent                        │
│                                                                   │
│  Components:                                                      │
│  - Hierarchical Planning (write_todos)                           │
│  - Long-term Memory (JetStream state)                            │
│  - Filesystem Backend (MicroVM via custom protocol)              │
│  - Sub-agent Delegation (research, verify, publish)              │
│  - Vibewriter Skills (citation research, verification, etc.)     │
│                                                                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│              Custom SandboxBackendProtocol                        │
│                                                                   │
│  - Translates filesystem ops to secure RPC calls                 │
│  - Integrates with NATS Object Store for large files            │
│  - Manages ephemeral vs persistent storage routing               │
│                                                                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│           Firecracker MicroVM Orchestrator                        │
│                                                                   │
│  - VM Lifecycle Management (create, start, stop, destroy)        │
│  - Network Isolation and Secure RPC                              │
│  - Resource Constraints (CPU, memory limits per user)            │
│  - Jailer Integration (additional security layer)                │
│                                                                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│            Firecracker MicroVM (Per User Agent)                   │
│                                                                   │
│  - Isolated Guest Kernel (hardware virtualization)               │
│  - User's Private Keys (signing authority for transactions)      │
│  - Research Workspace (drafts, sources, citations)               │
│  - Tool Execution Environment (Python, Node, etc.)               │
│                                                                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    NATS JetStream Cluster                         │
│                                                                   │
│  - Agent State Streams (vibewriter.state.*)                      │
│  - Object Store (research artifacts, drafts, reports)            │
│  - Citation Events (citation.new.*, citation.reward.*)           │
│  - Knowledge Base Queries (kb.search.*)                          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### B. Data Flow Example: Research Task

1. **User Request**: "Research DeFi yield opportunities on Base blockchain"

2. **Planning Phase** (Deep Agent):
   - Agent uses `write_todos` tool to create plan:
     1. Search knowledge base for existing Base DeFi research
     2. Web search for current yield farms on Base
     3. Analyze protocols (Aave, Compound, etc.)
     4. Verify citations and sources
     5. Draft report with findings
     6. Publish to knowledge base

3. **Execution Phase** (MicroVM):
   - Agent spawns research sub-agent
   - Sub-agent executes in isolated MicroVM
   - Uses `search_choir_kb` skill (custom Vibewriter tool)
   - Uses `web_search` tool (via Tavily API)
   - Stores sources in MicroVM filesystem (`/research/sources/`)

4. **Persistence Phase** (NATS):
   - Agent state checkpointed to JetStream (`vibewriter.state.agent-001`)
   - Research sources stored in Object Store (`VIBEWRITER_FILES/agent-001/sources/`)
   - Draft report stored in Object Store

5. **Verification Phase** (Sub-agent):
   - Verification sub-agent spawned with clean context
   - Reads draft from Object Store
   - Executes citation verification skill
   - Updates state in JetStream

6. **Publishing Phase**:
   - Final report stored in Object Store
   - Publication event sent via NATS (`kb.publish.new`)
   - Knowledge base indexes new article
   - User receives notification

## V. Vibewriter Tools and Skills

### A. Core Tools (Choir-Specific)

These tools integrate the Deep Agent with the Choir protocol's economic and knowledge layers:

1. **`search_choir_kb`**: Search the knowledge base for existing research
   - Semantic search via Qdrant vector database
   - Returns relevant articles with citation metadata
   - Enables agents to build on existing work

2. **`cite_article`**: Create citation link between articles
   - Records citation in knowledge graph
   - Triggers economic signal via NATS
   - Updates citation count for reward calculation

3. **`publish_to_choir`**: Publish research to knowledge base
   - Stores article in vector database
   - Generates embedding for semantic search
   - Makes article citable by other agents
   - Triggers novelty calculation for CHIP rewards

### B. Vibewriter Skills (Pre-built Workflows)

Skills are complex, multi-step workflows stored as scripts in the MicroVM filesystem:

1. **Citation Verification Skill** (`/skills/verify_citations.py`):
   - 3-layer verification: URL → content → Claude validation
   - Extracts claims from draft
   - Verifies each claim against cited sources
   - Generates verification report

2. **Deep Research Skill** (`/skills/deep_research.py`):
   - Parallel sub-agent strategy
   - 3-5 specialized researchers per topic
   - Aggregation and synthesis
   - Conflict resolution

3. **Style Application Skill** (`/skills/apply_style.py`):
   - Reads user's style guide
   - Applies consistent formatting
   - Ensures citation format compliance
   - Generates final polished report

4. **Financial Due Diligence Skill** (`/skills/financial_dd.py`):
   - Smart contract analysis
   - Audit report review
   - TVL and volume verification
   - Risk assessment

### C. Tool Execution Model

All tool and skill execution happens inside the isolated MicroVM:

```python
# Agent decides to use citation verification skill
agent.plan_step("Verify citations in draft report")

# Agent reads skill script from MicroVM filesystem
skill_script = agent.filesystem.read_file("/skills/verify_citations.py")

# Agent executes skill in sandbox
result = agent.execute_in_sandbox(
    command=f"python /skills/verify_citations.py --draft /workspace/draft.md",
    env={"TAVILY_API_KEY": "..."}
)

# Result stored in JetStream and Object Store
agent.persist_result(result)
```

## VI. Implementation Roadmap

**Timeline Note**: We're using coding agents (Claude Code, etc.) to build this. The first working version will be built in ONE SESSION, not weeks/months. The phases below are iterations, not sequential weeks.

### Phase 1: First Working Version (THIS SESSION)

**Goal**: Build working Deep Agent with Runloop sandbox and basic Vibewriter capabilities

**Tasks** (with coding agents, these happen in hours, not weeks):
1. Set up LangChain Deep Agents with Runloop sandbox
2. Implement basic Vibewriter tools (`search_choir_kb`, `cite_article`, `publish_to_choir`)
3. Create simple research workflow
4. Test hierarchical planning and filesystem operations
5. Validate architecture decisions

**Success Criteria**:
- Deep Agent can complete multi-step research task
- Planning and memory work across conversation
- Tools integrate with existing Choir backend
- **v1 ships today**

### Phase 2: Self-Hosted MicroVM Backend (Next Session)

**Goal**: Replace Runloop with self-hosted ERA (Firecracker orchestration)

**Tasks** (with coding agents):
1. Implement `MicroVMBackend(SandboxBackendProtocol)`
2. Set up local ERA environment (Firecracker + orchestration)
3. Configure ERA for session persistence
4. Integrate NATS JetStream for agent state
5. Migrate from Runloop to ERA

**Success Criteria**:
- Agent executes in self-hosted MicroVM
- State persists via JetStream
- Performance validated

### Phase 3: Skills and Economic Integration (Next Session)

**Goal**: Build Vibewriter skills and citation economics

**Tasks** (with coding agents):
1. Implement citation verification skill
2. Implement deep research skill (parallel sub-agents)
3. Integrate with CHIP/USDC reward calculation
4. Build citation event publishing via NATS
5. Test end-to-end flow

**Success Criteria**:
- Agent produces citation-verified reports
- Citations trigger economic signals
- Novelty calculation works

### Phase 4: Production Hardening (Ongoing)

**Goal**: Deploy production-ready multi-tenant system

**Tasks**:
1. Build MicroVM cluster for horizontal scaling
2. Deploy NATS cluster for high availability
3. Security hardening and audit
4. Load testing and optimization

**Success Criteria**:
- System handles 100+ concurrent agents
- Production security standards met
- Monitoring and observability complete

## VII. Security Considerations

### A. MicroVM Isolation

**Private Key Management**:
- Each user's private keys stored only in their dedicated MicroVM
- Keys never transmitted to host or other VMs
- Signing operations execute inside MicroVM
- Hardware isolation prevents cross-user key access

**Network Isolation**:
- MicroVM ↔ Host communication via controlled RPC only
- No direct internet access from MicroVM (unless explicitly allowed)
- All external API calls proxied through host with rate limiting
- Citation events published to NATS (not direct blockchain access)

### B. Prompt Injection Defense

**Multi-Layer Protection**:
1. **System prompts** clearly delineate agent vs user instructions
2. **Tool confirmation** for high-stakes operations (publish, sign transaction)
3. **Human-in-the-loop** approval for financial operations above threshold
4. **Audit logging** of all agent decisions and tool executions

### C. Secret Management

**Best Practices**:
- API keys injected as environment variables, not stored in filesystem
- Short-lived secrets rotated automatically
- No secrets in JetStream state messages (use references)
- Secrets never appear in logs or debugging output

## VIII. Next Steps

1. **Immediate (This Week)**:
   - Set up DeepAgents development environment
   - Prototype with Runloop sandbox
   - Test basic planning and filesystem operations

2. **Short-Term (Next Month)**:
   - Implement custom `MicroVMBackend`
   - Set up NATS JetStream cluster
   - Build first Vibewriter skill (citation verification)

3. **Long-Term (Next Quarter)**:
   - Production Firecracker deployment
   - Full citation economics integration
   - Public launch of Vibewriter

## Conclusion

The new **Vibewriter** architecture is a robust, production-ready design that meets the stringent security and functional requirements of the Choir project. By combining the hierarchical planning of **LangChain Deep Agents**, the hardware-level isolation of **MicroVMs**, and the persistent, high-speed data backbone of **NATS JetStream**, the project is well-positioned to implement the secure, autonomous financial delegate agent that defines the Choir vision.

The Deep Agent *is* the Vibewriter. The architecture enables complex, multi-hour research tasks, citation-verified publishing, and safe financial delegation - all within a hardware-isolated, persistent, and scalable infrastructure.

---

## References

[1] LangChain. *Deep Agents*. [Online]. Available: https://blog.langchain.com/deep-agents/
[2] firecracker-microvm. *Firecracker: Secure and fast microVMs*. [Online]. Available: https://github.com/firecracker-microvm/firecracker
[3] AWS. *Firecracker - Lightweight Virtualization for Serverless*. [Online]. Available: https://aws.amazon.com/blogs/aws/firecracker-lightweight-virtualization-for-serverless-computing/
[4] LangChain. *Backends - Docs by LangChain*. [Online]. Available: https://docs.langchain.com/oss/python/deepagents/backends
[5] NATS. *JetStream - NATS Docs*. [Online]. Available: https://docs.nats.io/nats-concepts/jetstream
[6] NATS. *Object Store - NATS Docs*. [Online]. Available: https://docs.nats.io/nats-concepts/jetstream/obj_store
[7] BinSquare. *ERA: Open source local sandboxing for running AI generated code*. [Online]. Available: https://github.com/BinSquare/ERA
