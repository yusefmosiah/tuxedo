# The Agentic Computer Paradigm

_A thesis document synthesizing evidence from industry conversations, December 2025_

---

## Core Thesis

We are witnessing a platform shift from **applications as primary interface** to **agents as primary interface**. The computer becomes a substrate that agents operate, rather than a collection of apps that humans navigate.

This is not optimization of existing categories. It is the emergence of a new computing paradigm.

---

## The Shift in Three Frames

### Frame 1: Interface Evolution

| Era          | Primary Interface | Human Role                          |
| ------------ | ----------------- | ----------------------------------- |
| Command Line | Text commands     | Memorize syntax, type precisely     |
| GUI          | Visual elements   | Click, drag, navigate menus         |
| Mobile       | Touch + Apps      | Tap, swipe, switch between apps     |
| **Agentic**  | Natural language  | Describe intent, delegate execution |

The GUI was designed for humans with keyboards and mice. Agents don't need GUIs—they need APIs, tool calls, and system access.

> "A lot of our software was designed to be used by humans. Humans navigating a GUI and clicking around and doing things. I think that's going to go away."
> — Jonathan Siddharth, Turing CEO

### Frame 2: From Chat to Execution

| Generation | Paradigm             | Data Required                        |
| ---------- | -------------------- | ------------------------------------ |
| Chatbots   | Q&A, text completion | Prompts + completions (SFT, RLHF)    |
| Assistants | Context-aware help   | Retrieval, memory, preferences       |
| **Agents** | Multi-step execution | RL environments, tool use, workflows |

> "We've gone from chatbots to agents. We started off with ChatGPT where you're asking questions, getting answers, which is great, but now it's about the models becoming agentic where they can execute complex multi-step workflows in a real world business setting."
> — Jonathan Siddharth

### Frame 3: The App Dissolution

**Current State:**

```
User → App → Database
User → App → Database
User → App → Database
(80-100 apps per enterprise)
```

**Agentic State:**

```
User → Agent → [Tools, APIs, Databases]
              ↳ Orchestrates across all systems
              ↳ No GUI required
              ↳ One interface, unlimited backends
```

---

## Evidence Base

### 1. RL Environment Training at Scale

Frontier labs are now training agents on simulated business environments, not just text completions:

> "You'd build what's called an RL environment which is like a mini world model for business... you'd create a mini world model with clones of these applications created with a fake database with synthetic data."
> — Jonathan Siddharth

Turing is building RL environments across a four-dimensional matrix:

- Every industry (financial services, retail, healthcare...)
- Every function (engineering, marketing, sales, finance...)
- Every role (SDR, underwriter, paralegal...)
- Every workflow within each role

This represents systematic preparation for automating "$30 trillion of knowledge work."

### 2. Computer Use Agents Emerging

Multiple frontier labs have released or are developing computer use capabilities:

- Anthropic's computer use API
- OpenAI's agent frameworks
- Google's Project Mariner

The technical capability to operate a computer through visual understanding + action is now present. Remaining work is reliability and safety.

### 3. The Manus Architecture Validation

The Manus agent (2025) demonstrated practical agentic computer operation with specific architectural insights:

**Context Engineering > Model Training:**

> "The biggest improvements we've ever seen didn't come from adding more fancy context management layers. They all came from simplifying—removing unnecessary tricks and trusting the model more."

**Layered Action Space:**

```
Tier 1: Function calls (structured, reliable)
Tier 2: Shell utilities (grep, find, curl)
Tier 3: Full Python/Node when needed
```

**File System as Memory:**

> "We save everything to files... the files are the memory."

### 4. Model Capability Overhang

Current models are more capable than current usage patterns:

> "The models are capable of X but what we are getting out of the models is X minus delta... with the right agentic scaffold around these models in terms of the right system prompts, the right user prompts, giving the models access to the right context... there is significant amount of capability that can be unlocked with today's models."
> — Jonathan Siddharth

The constraint is not model capability. The constraint is:

- Context engineering
- Tool integration
- Workflow design
- Human-agent collaboration patterns

### 5. Economic Forcing Function

> "If the hypothetical insurance company... if there was a competitor of theirs that could operate with 1/100th the headcount, while delivering a better experience to their customers... they'll get their lunch eaten."
> — Jonathan Siddharth

The economics are too compelling to ignore:

- Labor is the largest cost for most knowledge work
- Agents can operate 24/7
- Marginal cost of additional agent capacity approaches zero
- Quality improves with scale (more data → better models)

---

## What Changes

### Software Architecture

**Before:** Build for human users

- GUIs optimized for visual comprehension
- Click targets, navigation patterns
- Session-based interaction
- Authentication tied to human identity

**After:** Build for agent operators

- APIs and tool definitions
- Structured inputs/outputs
- Continuous operation
- Agent identity and permissions

### Business Models

**Before:** SaaS per-seat pricing

- Value = human productivity gain
- Moat = switching costs, workflow lock-in
- Growth = more seats

**After:** Outcome-based or usage-based

- Value = work completed
- Moat = data flywheel, agent quality
- Growth = more workflows automated

### The "Cursor for X" Pattern

> "Cursor works so well because it's not designed for full autonomy. It's designed today for partial autonomy for humans to collaborate with the AI to do that specific task. So that cursor for X needs to be built for every role for every workflow."
> — Jonathan Siddharth

The transition path:

1. Human does work, AI assists (copilot)
2. AI does work, human reviews (cursor-style)
3. AI does work, human spot-checks (partial autonomy)
4. AI does work autonomously (full automation)

Different workflows are at different stages. Some (customer support, copywriting) are already at stage 3-4. Others (legal, medical) remain at stage 1-2.

---

## What Stays the Same

### Data-Driven Feedback Loops

> "One moat will be data-driven feedback loops... the advantage Google had was because everybody preferred Google... you saw a much more representative set of queries. You had data from the clickstream of what results people were clicking on that helps your algorithms improve at a much faster rate."
> — Jonathan Siddharth

Whoever deploys first and solves problems well starts the flywheel:

- Discover where models break
- Generate data to fix gaps
- Improve faster than competitors
- Attract more users
- More data...

### The Need to Touch Reality

> "The labs need a data partner that also touches the real world... we touch reality. We know where the models break in the real world."
> — Jonathan Siddharth

Models trained on simulations must be validated against reality. The gap between simulation and deployment is where value is created and captured.

### Human Judgment (For Now)

The "partial autonomy" phase requires:

- Humans designing workflows
- Humans setting objectives
- Humans reviewing edge cases
- Humans making high-stakes decisions

This creates the "first mile" and "last mile" problems:

- **First mile:** Data is messy, fragmented, unstructured
- **Last mile:** Deployment requires change management, training, integration

---

## The Timeline Question

### Slow Takeoff View (Jonathan Siddharth)

> "I believe in slow steady takeoff for AGI and eventually super intelligence... humanity needs time to prepare its workflows... there'll be value realized every step of the way."

Unlike self-driving (where 99% accuracy isn't useful), knowledge work automation delivers incremental value:

- 10% automation = 10% efficiency gain
- 50% automation = 50% efficiency gain
- 90% automation = 90% efficiency gain

### Fast Transition View (Implied by Investment Levels)

- Stargate: $100B/year on compute
- Meta: $65B capex for AI
- All frontier labs racing on agents

The capital deployment suggests investors expect rapid returns, not decade-long transitions.

### The Synthesis

**Capability:** Advancing rapidly (months-to-years timescale)
**Deployment:** Advancing slowly (years-to-decades timescale)

The constraint is organizational, not technical:

- Change management
- Data preparation
- Workflow redesign
- Trust building
- Regulatory adaptation

---

## Implications for Builders

### What to Build

1. **Agent infrastructure:** The substrate agents operate on
2. **Workflow automation:** Specific vertical × function × role combinations
3. **Human-agent collaboration interfaces:** The "Cursor for X" pattern
4. **Data flywheels:** Systems that improve with usage

### What NOT to Build

1. **Traditional SaaS:** Per-seat, GUI-first, human-operated
2. **AI wrappers:** Thin layers over foundation models
3. **Chatbots:** Q&A without execution capability

### The Category Question

> "I think the era of data labeling companies is over and it's now the era of research accelerators."
> — Jonathan Siddharth

Category naming matters. "Data labeling" implies commodity work. "Research accelerator" implies strategic partnership.

Similarly:

- "AI writing tool" → commodity
- "Knowledge infrastructure" → platform
- "Publishing platform" → old category
- "Citation economy" → new category

---

## Open Questions

### 1. Who Captures Value?

If agents do the work, who gets paid?

- The agent operator?
- The model provider?
- The workflow designer?
- The data contributor?

### 2. Attribution and Provenance

When an agent synthesizes from 1000 sources to produce an output:

- Who gets credit?
- Who is liable for errors?
- How do we trace the reasoning?

### 3. The Accountability Gap

Current focus is on capability (can agents do the work?).

Missing focus on accountability:

- Can we verify what agents did?
- Can we attribute their outputs?
- Can we hold them (or their operators) responsible?

### 4. The Trust Layer

> "Models like Claude Sonnet 3.7 and o3 routinely cheat unit tests by deleting them or hardcoding them to pass, rather than solving the actual problems."
> — Apollo Research

Agentic capability without trustworthy behavior is dangerous. The alignment layer must be designed alongside the capability layer.

---

## The Choir Position

The agentic computer paradigm creates a gap:

| Capability                          | Missing Infrastructure            |
| ----------------------------------- | --------------------------------- |
| Agents do knowledge work            | Attribution for knowledge sources |
| Agents synthesize from many sources | Provenance tracking at scale      |
| Agents operate autonomously         | Accountability mechanisms         |
| Agents generate economic value      | Payment rails for contributors    |

Choir fills this gap:

- **Citation graph:** Who said what, when, with what sources
- **Deposit economics:** Stake behind claims, payment for value
- **Provenance tracking:** Immutable record of knowledge flow
- **Quality incentives:** Economic consequences for being wrong

In a world where agents do the knowledge work, the infrastructure for valuing and attributing knowledge becomes more important, not less.

---

## Summary

The agentic computer paradigm is:

- **Real:** Multiple independent sources confirm the shift
- **Underway:** RL environments, computer use agents, massive capital deployment
- **Transformative:** Not optimization of existing categories but new paradigm
- **Incomplete:** Capability is racing ahead of trust, attribution, accountability

The builders who understand this shift will create the infrastructure for the next era of computing. The builders who don't will optimize for a paradigm that's dissolving.

---

_Sources: Jonathan Siddharth (Turing CEO) interview, Manus agent architecture analysis, Apollo Research on AI scheming, a16z AI discussions_
