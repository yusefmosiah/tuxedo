# Vibewriter Architecture Update: Unified Deep Agent & Skills

**Date:** 2025-05-15
**Status:** Approved for Implementation

## Executive Summary

We are consolidating the "Code Tuxedo Agent" (DeFi/Stellar) and "Ghostwriter" (Research/Writing) into a single, unified **Deep Agent** named **Vibewriter**. This agent operates within a secure **MicroVM Sandbox** and utilizes a new capability paradigm called **Skills**.

Previously, the architecture relied on a complex chain of `Tuxedo -> MCP -> Ghostwriter`. This introduced latency, fragility in JSON schema handoffs, and context loss. The new architecture flattens this into a single agent loop that has "full computer control" of its sandbox, allowing it to read documentation and execute scripts—just like a human engineer.

## The "Skill" Paradigm

A **Skill** is defined not as a function schema (MCP/OpenAI Tool), but as **Docs + Scripts** residing in the sandbox.

### Definition
A Skill consists of:
1.  **Documentation (`README.md`):** High-level instructions explaining *how* to use the skill, its parameters, and its expected output.
2.  **Scripts (`scripts/*.py`):** Robust, standalone Python or Bash scripts that perform the actual logic.

### Interaction Model
Instead of the LLM formulating a JSON object to match a strict schema, the LLM:
1.  **Reads** the `skills/<skill_name>/README.md`.
2.  **Formulates** a bash command to run the script (e.g., `python skills/research/run.py "DeFi Yields" --depth 2`).
3.  **Executes** the command in the sandbox.
4.  **Reads** the output (stdout or a generated file).

### Benefits
*   **Resilience:** Scripts are easier to test and debug than prompt-dependent function calls.
*   **Extensibility:** Adding a new skill is just "dropping files" into the sandbox. No server restart or schema update required.
*   **Agentic Native:** Aligns with "Agents as Engineers" who use tools via CLI.

## Proposed Architecture

### 1. The Unified Deep Agent (Vibewriter)
The Vibewriter is a single LangGraph/DeepAgents instance. It does not "call" other agents; it *becomes* them by loading the appropriate context/skills.

*   **Runtime:** Firecracker MicroVM (via ERA/Sandbox Protocol).
*   **Interface:** `run_bash_command`, `read_file`, `write_file`.
*   **Memory:** NATS JetStream (for long-term state).

### 2. Directory Structure (In Sandbox)

```text
/home/agent/
├── skills/
│   ├── research/              <-- Former Ghostwriter
│   │   ├── README.md          <-- "How to research topics"
│   │   ├── run.py             <-- The orchestration script
│   │   └── web_search.py      <-- Helper tool
│   ├── stellar/               <-- Former Tuxedo/Stellar Tools
│   │   ├── README.md          <-- "How to trade/check balance"
│   │   ├── check_balance.py
│   │   └── trade.py
│   └── writing/
│       ├── README.md
│       └── draft.py
└── workspace/                 <-- User artifacts
```

## Migration Implementation

### Step 1: Porting Ghostwriter to a Skill

**`skills/research/README.md`**
```markdown
# Research Skill

Use this skill to research complex topics using web search and synthesis.

## Usage
Run the python script with the topic and optional depth.

```bash
python skills/research/run.py --topic "Future of Stellar DeFi" --depth 2 --output "report.md"
```

## Outputs
- `report.md`: The final synthesized report.
- `sources.json`: List of cited sources.
```

**`skills/research/run.py`**
```python
import argparse
from vibewriter.tools import web_search  # Shared internal lib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--output", default="report.md")
    args = parser.parse_args()

    print(f"Starting research on: {args.topic}")
    # ... logic from old ghostwriter pipeline ...

    with open(args.output, "w") as f:
        f.write("# Research Report\n...")

if __name__ == "__main__":
    main()
```

### Step 2: Porting Stellar Tools to a Skill

**`skills/stellar/README.md`**
```markdown
# Stellar DeFi Skill

Use this skill to interact with the Stellar blockchain.

## Commands

### Check Balance
```bash
python skills/stellar/balance.py --account <ACCOUNT_ID>
```

### Execute Trade
```bash
python skills/stellar/trade.py --buy USDC --sell XLM --amount 100
```
```

## Implementation Plan

1.  **Create `backend/vibewriter/`**: This will house the new Deep Agent logic.
2.  **Create `backend/skills/`**: Source of truth for skills. These will be copied into the Sandbox at runtime.
3.  **Refactor Ghostwriter**: Move logic from `backend/agent/ghostwriter/` to `backend/skills/research/`.
4.  **Refactor Stellar Tools**: Move logic from `backend/stellar_tools.py` to `backend/skills/stellar/`.
5.  **Update Agent System Prompt**: Teach the agent to look in `skills/` for capabilities.

## Code Snippet: Agent System Prompt

```python
SYSTEM_PROMPT = """
You are Vibewriter, an autonomous AI researcher and DeFi delegate.
You run inside a secure sandbox with full terminal access.

Your capabilities are defined as "Skills" located in the `/home/agent/skills/` directory.

To learn how to do something:
1. List the skills directory: `ls -F /home/agent/skills/`
2. Read the instructions for a specific skill: `cat /home/agent/skills/<skill_name>/README.md`
3. Execute the skill using the command line as instructed.

DO NOT hallucinate commands. Always read the README.md first.
"""
```

## Conclusion

This architecture removes the "Tuxedo vs Ghostwriter" distinction. There is only **Vibewriter**, and it picks up the "Research Skill" or "Stellar Skill" as needed. This simplifies the stack, improves reliability, and leverages the full power of the sandbox environment.
