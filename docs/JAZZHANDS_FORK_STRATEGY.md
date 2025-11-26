# Jazzhands: The OpenHands Fork Strategy for Choir

**Version 1.0 - November 26, 2025**

---

## Executive Summary

**Choir is forking OpenHands to create Jazzhands** - a secure, multi-tenant research and writing infrastructure where AI agents have full computer control to produce high-quality, citation-verified research.

**The Core Insight**: All agents are coding agents. Effective research requires:
- Terminal access (bash, python, curl)
- File system control (organize research, manage drafts)
- Tool installation (pip install validators, fact-checkers)
- Multi-step reasoning with persistent state

**Agent Hierarchy**: `pipeline < graph < tool calling loop < terminal/full computer control`

OpenHands provides the highest level - agents with full computer access. We add 3 Choir-specific tools for economics and knowledge base integration.

**What Users See**: The OpenHands UI - terminal, code editor, file explorer. They watch the agent research, write code to verify citations, and produce high-quality articles.

**What We Add**: Citation economics on top. Publish costs CHIP (earned via semantic novelty), citations pay USDC to authors.

---

## I. The "All Agents Are Coding Agents" Realization

### Why We Can't Build on Simple Chat APIs

Your initial Choir implementation used LangChain with tool calling. This works for simple tasks but breaks down for serious research:

**The Problems**:
1. **No State Persistence**: Each request is stateless. Research context gets lost between turns.
2. **No File System**: Can't build up a research corpus, manage drafts, or run verification scripts.
3. **Limited Tool Orchestration**: Hard to chain complex workflows (research → draft → verify → revise).
4. **No Environment Control**: Can't install dependencies (citation validators, fact-checkers, domain-specific tools).

**Example: Citation Verification**

```
User: "Write a research report on DeFi yield farming with verified citations"

Simple Chat Agent:
├── Generate text with citations
├── Hope the citations are real
└── No way to actually verify them

Research Agent (with computer access):
├── Research phase: Web search → Save sources to /workspace/sources/
├── Draft phase: Generate text → Save to /workspace/draft.md
├── Verify phase:
│   ├── Call the `cite_article` tool to verify internal citations.
│   ├── For external sources, write a Python script to check URLs.
│   ├── The script verifies that each URL returns a 200 status.
│   ├── It then extracts the page content.
│   └── Finally, it verifies that the claim is supported by the source.
├── Revise phase: Fix unsupported claims
└── Publish: High-confidence, verified output
```

**The research agent's output is 10x more valuable.** It's also a coding agent.

### Why OpenHands Specifically

OpenHands is the most mature open-source framework for giving agents computer access:

- ✅ **Mature SDK**: V1 stable, well-documented
- ✅ **Event Stream Architecture**: Every action/observation is logged and observable
- ✅ **Remote Runtime Support**: Built-in support for isolated execution environments
- ✅ **Multi-Model**: Works with any LLM (not locked to OpenAI)
- ✅ **MIT Licensed**: Can fork and commercialize
- ✅ **Active Development**: Strong community, regular updates

The frontend is also valuable - it's a functional agentic UI that we can adapt rather than building from scratch.

---

## II. The Security Model: Remote Runtime Architecture

### The Rejected Approach: Permissioned Directories

Your initial plan suggested:
> "Use permissioned directories within a shared system for user isolation"

**This is dangerous.** Here's why:

**The Attack Vector**:
```python
# User A's agent (malicious or compromised)
import os
import subprocess

# Research agents need root for pip install, apt-get, etc.
# With root access:
subprocess.run(["sudo", "chmod", "-R", "777", "/workspace/user_b/"])
subprocess.run(["cat", "/workspace/user_b/private_research.md"])

# User A now has User B's intellectual property
```

**The Problem**: Research agents need elevated privileges to install tools. Any agent with `sudo` can bypass file permissions and read other users' data.

### The Correct Approach: Remote Runtime Per Session

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                    CHOIR CONTROLLER                          │
│                (FastAPI + Passkey Auth)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Request arrives with Session JWT                           │
│  ├── Validate passkey signature                             │
│  ├── Extract user_id from token                             │
│  └── Route to UserSessionManager(user_id)                   │
│                                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               USER SESSION MANAGER                           │
│                (One per user_id)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Manages user's research sessions                           │
│  ├── Check if active session exists                         │
│  ├── If not: Spawn new RemoteRuntime                        │
│  ├── Mount encrypted user volume                            │
│  └── Return session handle                                  │
│                                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬───────────────────┐
         │                       │                    │
         ▼                       ▼                    ▼
┌─────────────────┐    ┌─────────────────┐  ┌─────────────────┐
│ RemoteRuntime   │    │ RemoteRuntime   │  │ RemoteRuntime   │
│ (User A)        │    │ (User B)        │  │ (User C)        │
├─────────────────┤    ├─────────────────┤  ├─────────────────┤
│ Docker/MicroVM  │    │ Docker/MicroVM  │  │ Docker/MicroVM  │
│                 │    │                 │  │                 │
│ /workspace/     │    │ /workspace/     │  │ /workspace/     │
│ ├── sources/    │    │ ├── sources/    │  │ ├── sources/    │
│ ├── drafts/     │    │ ├── drafts/     │  │ ├── drafts/     │
│ ├── published/  │    │ ├── published/  │  │ ├── published/  │
│ └── tools/      │    │ └── tools/      │  │ └── tools/      │
│                 │    │                 │  │                 │
│ ISOLATED        │    │ ISOLATED        │  │ ISOLATED        │
└─────────────────┘    └─────────────────┘  └─────────────────┘
```

**Key Properties**:
1. **True Isolation**: Each user's agent runs in a separate container/VM
2. **Root Is Safe**: User A's agent can be root in its container, can't touch User B
3. **Encrypted Volumes**: User data encrypted at rest, mounted per-session
4. **Suspend/Resume**: Sessions can pause (save state) to reduce costs
5. **Cost Control**: Containers destroyed after idle timeout

**Provider: RunLoop** (recommended over E2B)
- Supports suspend/resume (E2B is ephemeral-only)
- Allows multi-hour research sessions without burning compute
- Preserves file system state between user interactions

---

## III. The Economics Integration: Citation vs. Compute

### Where the Draft Got It Wrong

The draft plan suggested:
> "Users purchase CHIPs, which represent claims on compute resources"

**This contradicts the actual Choir vision.** Let me correct it:

### The Actual Choir Economic Model

**Two Currencies**:

| Currency | Purpose | How Earned | How Used |
|----------|---------|------------|----------|
| **USDC** | Income | Citations | Withdraw to bank account |
| **CHIP** | Ownership | Semantic novelty | Publish, governance, collateral |

**The Flows**:

1. **Research & Writing** (Free Tier for MVP)
   ```
   User: "Write a research report on DeFi"
   ├── Costs: Free for MVP (metered by CHIP in the future, if necessary)
   ├── Agent: Autonomously researches, writes, verifies in remote runtime
   ├── Output: High-quality, citation-verified report
   └── User: Watches agent work, sees draft in workspace
   ```

2. **Publishing** (CHIP Token)
   ```
   User: "Publish this report"
   ├── Costs: 100 CHIP (staked to publish)
   ├── System: Calculates semantic novelty vs existing corpus
   ├── Reward: Earn 200 CHIP (novelty score: 85/100)
   └── Result: Net +100 CHIP, article now citable
   ```

3. **Citations** (USDC Income)
   ```
   Other User's Agent: Cites your article
   ├── Treasury: Pays you $5 USDC (dynamic rate)
   ├── Your Balance: $5 added
   ├── Compound: Foundational articles earn indefinitely
   └── Withdraw: Bank transfer or reinvest
   ```

### How This Integrates with Jazzhands

**The Choir Controller sits between users and OpenHands**:

```python
# Choir Controller Layer
class VibewriterSession:
    def __init__(self, user_id: str, session_jwt: str):
        self.user_id = user_id
        self.treasury = TreasuryClient()
        self.runtime = None

    async def start_research(self, prompt: str) -> AsyncIterator[Event]:
        # 1. Spawn isolated runtime for this user (future: check CHIP balance for metering)
        self.runtime = await RemoteRuntimeFactory.create(
            user_id=self.user_id,
            provider="runloop",
            encrypted_volume=f"s3://choir-workspaces/{self.user_id}/",
            api_headers={"Authorization": f"Bearer {RUNLOOP_API_KEY}"}
        )

        # 3. Run agent with Choir tools in isolated environment
        agent = ChoirAgent(
            runtime=self.runtime,
            user_id=self.user_id
        )

        # 4. Stream events to user (they see OpenHands UI)
        async for event in agent.run(prompt):
            # User sees: Terminal output, file operations, agent thinking
            # Agent: Uses bash, python, Choir tools (search_choir_kb, cite_article, publish_to_choir)
            yield event

        # 5. Debit compute credits ONLY if workflow succeeds
        await self.treasury.debit_compute(self.user_id, VIBEWRITER_COST)

        # 6. Suspend runtime (user might iterate on draft)
        await self.runtime.suspend()
```

**Key Points**:
- **Compute credits** are a separate infrastructure token (like AWS credits)
- **CHIP** is earned via novelty, used for publishing and governance
- **USDC** is citation income
- **Remote runtime** provides the secure, stateful environment agents need
- **Users see the OpenHands UI** - terminal, file explorer, agent working

---

## IV. Frontend: Keep OpenHands UI, Add Economics

### What OpenHands Gives Us

The OpenHands frontend is a React/Remix app that looks like an IDE:
- Left sidebar: File explorer, chat history
- Center: Terminal, code editor, browser preview
- Right sidebar: Agent settings, model selection

**We keep all of this.** Users see the agent work.

### What We Add

**Economic Components** layered on top of OpenHands UI:

1. **Header with Balances**
   ```typescript
   <ChoirHeader>
     <Balance icon="💎" label="CHIP" value={230} />
     <Balance icon="💰" label="Earned" value="$175" />
   </ChoirHeader>
   ```

2. **Publish Button** (appears when agent creates draft in workspace)
   ```typescript
   {draftExists && (
     <PublishPrompt
       draft="/workspace/draft.md"
       onPublish={handlePublish}
     />
   )}
   ```

3. **My Research Page** (new route showing published articles)
   ```typescript
   <ResearchPage>
     {articles.map(a => (
       <ArticleCard
         title={a.title}
         citations={a.citations}
         earnings={a.earnings}
         noveltyScore={a.noveltyScore}
       />
     ))}
   </ResearchPage>
   ```

**That's it.** No major transformation. OpenHands UI stays. We just add economic features on Day 3.

---

## V. The License Strategy: Clean Room Fork

### The MIT License: What We Can Do

OpenHands is MIT licensed. This means:
- ✅ We can fork the entire codebase
- ✅ We can modify it extensively
- ✅ We can use it in a commercial product
- ✅ We can keep our modifications proprietary
- ✅ We MUST include the original MIT license notice

### The Enterprise Directory: What We CANNOT Touch

OpenHands has an `enterprise/` directory with proprietary multi-tenancy code:
- ❌ Proprietary license from All Hands AI
- ❌ Not included in the MIT licensed parts
- ❌ Using it would create legal liability

**Our Strategy**:

1. **The Fork**
   ```bash
   git clone https://github.com/All-Hands-AI/OpenHands.git jazzhands
   cd jazzhands
   rm -rf enterprise/  # Delete proprietary code IMMEDIATELY
   ```

2. **The Clean Room**
   - No one on the Choir team looks at `enterprise/` code
   - We build our own multi-tenancy from scratch
   - Our implementation is called "Choir Controller"
   - Fully independent IP

3. **The Build**
   ```
   jazzhands/
   ├── openhands/          # MIT licensed (forked, minimal modifications)
   │   ├── sdk/
   │   ├── runtime/
   │   ├── agent/
   │   └── frontend/       # Keep as-is, just add economic components
   ├── choir/              # Our proprietary layer
   │   ├── tools/          # 3 Choir tools (search, cite, publish)
   │   ├── auth/           # Passkey integration
   │   ├── treasury/       # CHIP/USDC economics
   │   └── runtime_manager/# Remote runtime orchestration (RunLoop)
   ```

4. **The License File**
   ```
   jazzhands/LICENSE.md:

   Jazzhands
   Copyright (c) 2025 Choir Technologies Inc.

   This project is based on OpenHands (MIT License).
   See LICENSE-OPENHANDS for the original license.

   Components:
   - openhands/: MIT License (Copyright 2024 All Hands AI)
   - choir_controller/: Proprietary (Copyright 2025 Choir Technologies Inc.)
   - frontend/: Proprietary (Copyright 2025 Choir Technologies Inc.)
   ```

**Legal Safety**:
- We never look at proprietary OpenHands code
- We build our multi-tenancy layer independently
- We clearly mark what's forked (MIT) vs what's ours (proprietary)
- We comply with MIT license (attribution, include original notice)

---

## VI. Why "Jazzhands"?

**Naming Rationale**:

1. **Playful Evolution**: OpenHands → Jazzhands (makes it clear it's a fork, not the original)
2. **Musical Theme**: Aligns with "Choir" (the product name)
3. **Less Corporate**: "OpenHands Enterprise" sounds boring, "Jazzhands" is memorable
4. **Internal vs External**:
   - **Jazzhands**: Internal codename for the forked OpenHands infrastructure
   - **Choir**: Consumer-facing brand
   - **Vibewriter**: Consumer-facing feature name (not "Ghostwriter" - too spooky)

**Users never hear "Jazzhands"** - they use Choir and Vibewriter.

---

## VII. The Strategic Advantages

### What We Gain from Forking

1. **12 Months of Agent R&D**
   - OpenHands solved hard problems: runtime isolation, event streaming, multi-model orchestration
   - We get this for free, focus on our domain (research/writing)

2. **Production-Ready Infrastructure**
   - Battle-tested SDK
   - Active maintenance and security updates
   - Community support

3. **Extensible Foundation**
   - Can add domain-specific tools (citation validators, semantic similarity checkers)
   - Can integrate with our citation graph database
   - Can optimize for long-running research sessions

4. **Lower Development Risk**
   - Not building core agent infrastructure from scratch
   - Proven architecture for agentic workflows
   - Faster time to market

### What We Build On Top

1. **Passkey Authentication** (proprietary)
   - WebAuthn integration
   - Session management
   - User isolation

2. **Citation Economics** (proprietary)
   - Treasury integration
   - CHIP distribution (novelty-based)
   - USDC rewards (citation-based)
   - Compute credit metering

3. **Research-Focused UI** (proprietary)
   - Vibewriter interface
   - Citation verification dashboard
   - Earnings tracker
   - Publishing workflow

4. **Multi-Tenant Runtime Management** (proprietary)
   - Per-user session spawning
   - Encrypted volume mounting
   - Suspend/resume optimization
   - Cost control and metering

---

## VIII. The Risk Analysis

### Technical Risks

**Risk 1: Remote Runtime Costs**
- **Problem**: Spinning up containers per user is expensive
- **Mitigation**: Suspend idle sessions, cold start optimization, generous free tier limits

**Risk 2: OpenHands API Changes**
- **Problem**: Upstream changes could break our fork
- **Mitigation**: Pin to stable versions, maintain our own branch, contribute PRs upstream

**Risk 3: Runtime Provider Lock-In**
- **Problem**: Depending on RunLoop creates vendor risk
- **Mitigation**: Abstract runtime interface, support multiple providers (E2B, AWS Lambda, local Docker)

### Economic Risks

**Risk 4: CHIP and USDC Model Clarity**
- **Problem**: Users may find the two-currency system confusing.
- **Mitigation**: A generous free tier, clear UX design, and straightforward explanations.

**Risk 5: Citation Rewards Insufficient**
- **Problem**: Users might earn too little to care
- **Mitigation**: Treasury collateral model scales exponentially, early users benefit from low semantic density

### Legal Risks

**Risk 6: MIT License Compliance**
- **Problem**: Could accidentally violate license terms
- **Mitigation**: Clear LICENSE files, legal review, attribution in UI footer

**Risk 7: Proprietary Code Contamination**
- **Problem**: Could accidentally use `enterprise/` code
- **Mitigation**: Delete immediately after fork, clean room development, code audits

---

## IX. Success Criteria

**Technical Success**:
- ✅ Vibewriter produces higher quality research than ChatGPT
- ✅ Citation verification actually works (95%+ accuracy)
- ✅ Remote runtimes scale to 1000+ concurrent users
- ✅ Session suspend/resume works reliably

**Economic Success**:
- ✅ Users earn meaningful citation income ($50-500/month for active researchers)
- ✅ Semantic novelty scoring accurately rewards original thought
- ✅ Treasury successfully funds citations through CHIP collateral

**User Success**:
- ✅ Users don't realize they're using a "coding agent"
- ✅ Publishing workflow feels simple (not blockchain-complicated)
- ✅ Research output is publication-ready
- ✅ Citation income is real and withdrawable

---

## X. Conclusion: The OpenHands Fork Is Correct

**Why This Works**:

1. **Research Is Code**: Serious research requires computational tools. OpenHands provides the runtime.
2. **Users Don't See Code**: The frontend transformation hides complexity, shows research.
3. **Economics Are Separate**: Compute credits fund infrastructure, CHIP/USDC fund the learning economy.
4. **Security Is Solved**: Remote runtimes provide true isolation without the "permissioned directory" vulnerability.
5. **License Is Clean**: MIT fork + proprietary layer = legally sound.

**Next Steps**:

1. Fork OpenHands, delete `enterprise/`, rename to Jazzhands
2. Build Choir Controller (auth, treasury, runtime management)
3. Transform frontend (hide dev tools, show research UI)
4. Integrate citation economics (semantic novelty, USDC rewards)
5. Deploy with RunLoop remote runtimes
6. Launch Vibewriter as consumer-facing product

**The Vision**: Users chat with Vibewriter, produce high-quality research, earn real money from citations. Behind the scenes, an OpenHands-powered agent is running code, verifying facts, and managing complex workflows.

**They get thoughtful research. We get the learning economy.**

---

**Document Status**: Draft v1.0
**Next**: JAZZHANDS_ECONOMICS_INTEGRATION.md (detailed Treasury integration)
**Related**: CHOIR_WHITEPAPER.md, ECONOMIC_MODEL.md
