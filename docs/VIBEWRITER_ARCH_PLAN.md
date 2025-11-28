# Vibewriter Architecture: Deep Agents & MicroVMs

**Status:** Planned
**Date:** November 28, 2025

## Executive Summary

Vibewriter is a specialized AI research agent that operates with "full computer control" within a secure, hardware-isolated MicroVM. It uses the **LangChain Deep Agent** architecture (built on LangGraph) to plan, research, and execute complex financial and publication tasks.

This document details the architecture and specifically addresses how to bridge the LangChain agent (running on a host or orchestrator) to a self-hosted MicroVM sandbox (running via ERA or Firecracker).

---

## 1. Core Architecture

### High-Level Components

1.  **The "Brain" (Host/Orchestrator):**
    *   **Runtime:** Python application running `langgraph` / `langchain`.
    *   **Agent Logic:** A "Deep Agent" with a planner (`write_todos`), memory, and tool definitions.
    *   **Role:** Reasoning, planning, parsing LLM outputs, and deciding *what* to do next. It does **not** execute user code or dangerous tools locally.

2.  **The "Body" (Sandbox):**
    *   **Technology:** MicroVM (ERA/Firecracker).
    *   **Role:** Execution environment. It holds the file system, runs shell commands, and stores private keys (if using TEE/Enclave pattern).
    *   **Isolation:** Hardware-level virtualization (KVM).

3.  **The Bridge (Sandbox Connector):**
    *   **Role:** The interface between the Brain and the Body.
    *   **Function:** Intercepts tool calls (e.g., `Terminal.run("ls")`, `FileEditor.write(...)`) and routes them to the MicroVM.

---

## 2. Connecting the Self-Hosted Sandbox

The user asked: *"We can use their runloop connector easily but how do we connect a self hosted sandbox?"*

**The Solution: A Custom Sandbox Backend**

LangChain Deep Agents use a "Backend" abstraction (or simply a set of Tools) to interact with the environment. To support a self-hosted ERA/Firecracker setup, we implement a custom `SandboxBackend` class.

### Interface Definition

We define a standard interface that our Deep Agent tools will use:

```python
class SandboxInterface(ABC):
    @abstractmethod
    def execute(self, command: str) -> Tuple[int, str, str]:
        """Run a shell command. Returns (exit_code, stdout, stderr)."""
        pass

    @abstractmethod
    def read_file(self, path: str) -> str:
        """Read file content."""
        pass

    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        """Write content to file."""
        pass
```

### Implementation: `EraSandbox`

This implementation wraps the local `era-agent` CLI or API to control the MicroVMs.

```python
import subprocess

class EraSandbox(SandboxInterface):
    def __init__(self, vm_id: str):
        self.vm_id = vm_id

    def execute(self, command: str):
        # Shell out to the local ERA CLI
        # Usage: agent vm exec <command>
        cmd = ["agent", "vm", "exec", "--", command]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr

    def read_file(self, path: str):
        # ERA might have a specific 'cat' or 'pull' command, or we use exec
        code, out, err = self.execute(f"cat {path}")
        if code != 0:
            raise FileNotFoundError(err)
        return out

    def write_file(self, path: str, content: str):
        # Write via echo/cat or specific ERA file push command
        # Ideally use a safer method than echo for large files
        self.execute(f"cat > {path} <<EOF\n{content}\nEOF")
```

### Integration with LangChain

We then configure the LangChain tools to use this sandbox instance instead of `subprocess` (local) or `RunLoop` (SaaS).

```python
from langchain_community.tools import ShellTool

# Instantiate the sandbox
sandbox = EraSandbox(vm_id="user_123_session_abc")

# Create a custom ShellTool that uses the sandbox
class SandboxedShellTool(BaseTool):
    def _run(self, command: str):
        code, out, err = sandbox.execute(command)
        return out if code == 0 else f"Error: {err}"

# Pass this tool to the Deep Agent
agent = create_deep_agent(tools=[SandboxedShellTool(), ...])
```

---

## 3. Directory Structure Refactor

We will move from `backend/agent/ghostwriter` to `backend/vibewriter`.

```
backend/
└── vibewriter/
    ├── __init__.py
    ├── main.py              # Entry point for the agent
    ├── agent/               # LangGraph Agent Logic
    │   ├── graph.py         # The StateGraph definition
    │   ├── planner.py       # The Planning logic
    │   └── prompt.py
    ├── sandbox/             # The Sandbox Bridge
    │   ├── interface.py     # Abstract Base Class
    │   ├── era.py           # ERA Implementation
    │   └── runloop.py       # RunLoop Implementation (optional fallback)
    └── tools/               # Choir-Specific Tools
        ├── economics.py     # Publish, Cite
        └── knowledge.py     # Vector Search
```

## 4. Migration Steps

1.  **Scaffold:** Create the `backend/vibewriter` structure.
2.  **Bridge:** Implement `sandbox/era.py`.
3.  **Agent:** Port the Ghostwriter pipeline logic (Hypothesis -> Design -> Research) into the `agent/planner.py` as a "Plan Template" that the agent can adopt.
4.  **Tools:** Rewrite `ChoirTools` to be standard LangChain tools.
5.  **Switch:** Update `backend/main.py` to use `Vibewriter` instead of `Ghostwriter`.
