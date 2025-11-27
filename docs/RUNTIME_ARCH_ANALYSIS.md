# Runtime Architecture Analysis: ERA vs. RunLoop

**Date**: November 26, 2025
**Context**: Jazzhands Implementation (OpenHands Fork)
**Objective**: Evaluate BinSquare/ERA as a self-hosted alternative to RunLoop for the Jazzhands remote runtime.

---

## 1. Jazzhands Runtime Requirements

Based on `JAZZHANDS_FORK_STRATEGY.md` and `JAZZHANDS_3DAY_SPRINT.md`, the runtime must provide:

1.  **Strict Isolation**: Each user gets a private environment (Docker/VM). Malicious code in one session must not affect others.
2.  **Stateful Persistence**: Users work on research over days. The filesystem (`/workspace`) must persist between sessions.
3.  **Full Terminal Access**: The agent needs a real shell (`/bin/bash`) to install tools (`pip`, `npm`), run scripts, and manage files.
4.  **Interactive Streaming**: OpenHands uses a WebSocket connection to stream `stdout`/`stderr` in real-time. "Fire and forget" script execution is insufficient.
5.  **Low Latency**: Agent-computer interaction loops are tight. Spin-up time should be seconds, not minutes.

---

## 2. BinSquare/ERA Analysis

**Source**: https://github.com/BinSquare/ERA
**Type**: Open Source, Self-Hosted Sandbox Platform

### Architecture
- **Control Plane**: Cloudflare Workers + Durable Objects (for session state).
- **Data Plane**: `era-agent` (Go binary) running on your own infrastructure (bare metal, K8s, or cloud VMs).
- **Storage**: Cloudflare R2 (S3-compatible) for file persistence.

### Capability Mapping

| Requirement | ERA Capability | Fit for Jazzhands |
|:---|:---|:---|
| **Isolation** | Uses "VM primitives" (likely Firecracker or gVisor via the Go agent). | ✅ High |
| **Persistence** | Uses R2 for storage. Likely syncs files on start/stop. | ✅ High (but verify latency) |
| **Terminal Access** | Demo shows "running code and agents". | ❓ **Unclear**. Needs PTY support. |
| **Streaming** | Cloudflare Workers support WebSockets. | ✅ Probable |
| **Latency** | Dependent on your `era-agent` fleet capacity. | ⚠️ Dependent on Ops |

### Operational Complexity (The Hidden Cost)

To use ERA, Jazzhands (Choir) becomes an infrastructure provider. We must:
1.  **Manage a Fleet**: Provision and monitor servers running `era-agent`.
2.  **Handle Scaling**: Auto-scale the fleet based on demand (or pay for idle capacity).
3.  **Security Updates**: Patch the host OS and `era-agent` binaries.
4.  **Cloudflare Setup**: Maintain Workers, DOs, and R2 buckets.

**Contrast with RunLoop**:
- RunLoop: `api_key = "..."` (Zero Ops)
- ERA: DevOps team required (or significant time from the solo dev).

---

## 3. The "Ship Fast" Conflict

The **Jazzhands 3-Day Sprint** philosophy is:
> "Aggressive (solo dev + AI agents). Ship fast, improve later."

**Using ERA contradicts this philosophy for Day 1.**
- Integrating RunLoop takes ~2 hours (API Integration).
- Deploying and stabilizing ERA takes ~2-5 days (Infra setup, testing, debugging edge cases).

**However, the user preference is clear**:
> "I’d prefer it, if it works, to paying a saas like runloop"

---

## 4. Recommendation

We should adopt a **"Buy then Build"** strategy to satisfy both the timeline and the long-term preference.

### Phase 1: The Sprint (Days 1-3) -> Use RunLoop
- **Why**: It guarantees we ship the product (Vibewriter with economics) in 3 days.
- **Cost**: RunLoop has a free tier or low starting cost. We won't burn cash immediately.
- **Action**: Implement `RunLoopRuntime` as planned.

### Phase 2: The Optimization (Week 2+) -> Evaluate/Migrate to ERA
- **Why**: Reduce COGS (Cost of Goods Sold) and gain sovereignty.
- **Action**:
    1.  Deploy ERA on a test server.
    2.  Verify PTY/Terminal streaming support (critical path).
    3.  Implement `EraRuntime` adapter in Jazzhands.
    4.  Switch users over transparently.

## 5. Architectural Safeguard: The `ChoirRuntime` Interface

To make this swap painless, we will strictly abstract the runtime in our code.

**Do NOT couple tightly to RunLoop.**

```python
# choir/runtime/base.py
class ChoirRuntime(ABC):
    @abstractmethod
    async def connect(self): ...
    @abstractmethod
    async def run_command(self, cmd: str): ...
    @abstractmethod
    async def upload_file(self, path: str, content: bytes): ...

# choir/runtime/factory.py
async def create_runtime(user_id: str) -> ChoirRuntime:
    if settings.RUNTIME_PROVIDER == "runloop":
        return RunLoopRuntime(user_id)
    elif settings.RUNTIME_PROVIDER == "era":
        return EraRuntime(user_id)
```

## 6. Conclusion

**ERA is a viable long-term infrastructure target**, but it is a **distraction for the 3-day sprint**.

**Decision (Confirmed)**:
1.  **Proceed with RunLoop** for the immediate fork (Sprint Days 1-3).
2.  **Architect for ERA** by strictly using the `ChoirRuntime` interface and Factory pattern (Day 1).
3.  **Schedule ERA Migration** as a documented Refactor Step (Week 4) to achieve infrastructure sovereignty.
