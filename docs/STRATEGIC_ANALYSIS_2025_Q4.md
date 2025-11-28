# Strategic Analysis: Agent Architecture, Sandboxing, and the Citation Economy

**Status:** Active Strategy
**Date:** November 28, 2025

## Executive Summary

The project is executing a strategic pivot converging on three domains: **Deep Agent Architecture**, **MicroVM Sandboxing**, and **Decentralized Economics**. The core insight is the shift from a container-based, pipeline-driven agent model to a **MicroVM-isolated, full-computer-control agent** (Vibewriter) that acts as a **financial delegate** within a **Citation Economy**.

| Component | Architecture | Justification |
| :--- | :--- | :--- |
| **Agent Model** | **LangChain Deep Agents** (LangGraph) | Deep Agents offer hierarchical planning, memory, and filesystem backends, aligning with the "full computer control" requirement for autonomous research and financial tasks. |
| **Sandbox** | **MicroVMs (ERA / Firecracker)** | Essential for **hardware-level isolation** of private keys and financial assets. Containers are insufficient for financial delegation. |
| **Data Infrastructure** | **NATS JetStream** | Provides **persistent memory** for Deep Agents and a **secure, high-speed backbone** for agent-to-agent citation communication. |
| **Economics** | **Citation Economy** | Rewards semantic novelty (CHIP) and citations (USDC). Funded by a dual-stream treasury model. |

---

## I. Agent Architecture: Deep Agents

We are moving away from general-purpose agent frameworks to a specialized implementation using **LangChain Deep Agents**.

### A. The "Vibewriter" Agent
The `tuxedo` documentation (`UNIFIED_VISION.md`) defines the agent as having **"terminal access for custom scripts, a file system for managing sources, and the ability to call specialized tools."**

The **LangChain Deep Agent** pattern fits this perfectly:
*   **Hierarchical Planning:** Uses a `write_todos` tool to break down complex research/publishing tasks.
*   **Filesystem Backend:** Manages "unpublished drafts" and "user's keys" within the isolated environment.
*   **Tool-Use Specialization:** Augmented with Choir-specific tools (`search_choir_kb`, `cite_article`, `publish_to_choir`).

---

## II. Sandbox Security: MicroVMs

**Container escape = bank robbery.**
For an agent to act as a financial delegate (signing transactions), container isolation is insufficient.

### A. The Solution: BinSquare/ERA
We utilize **ERA** (BinSquare/ERA) for local sandboxing. ERA provides:
*   **MicroVMs:** Hardware-enforced isolation (KVM) for the guest kernel.
*   **Developer Experience:** Docker-like CLI for managing Firecracker VMs.
*   **Safety:** Protects the host machine and other agents from compromised or malicious agent code.

---

## III. Data Infrastructure: NATS

NATS JetStream provides the persistence and messaging layer required for a robust multi-agent system.

*   **Agent Memory:** Agent state (LangGraph checkpoints) is persisted to JetStream, allowing agents to "sleep" and "wake up" without losing context.
*   **Economic Signaling:** Citations and payments are modeled as messages on the NATS bus, enabling real-time processing by the Treasury and Reputation services.

---

## IV. The Economic Context

The technical architecture serves the **Citation Economy**:
*   **Principal Protection:** Users deposit USDC; principal is safe.
*   **Novelty = Ownership (CHIP):** Users earn governance tokens for contributing unique knowledge.
*   **Citations = Income (USDC):** Users earn stablecoin income when their work is cited by others.

The **Vibewriter** agent automates the labor in this economy: researching, writing, citing, and earning on behalf of the user.
