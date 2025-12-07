# The Agentic Computer: Implementation Vision

_From research to action — December 2025_

---

## The Decision: Fork DaedalOS

After evaluating browser-based desktop environments against our criteria (mobile responsiveness, performance on slow devices, codebase quality), **DaedalOS** emerged as the clear choice.

### Why DaedalOS

| Criterion              | DaedalOS                         | Puter (rejected)                      |
| ---------------------- | -------------------------------- | ------------------------------------- |
| **Mobile**             | ✅ Works fast on phone/iPad      | ❌ Blocks mobile signups              |
| **Performance**        | ✅ Smooth even on mobile         | —                                     |
| **License**            | ✅ MIT (maximum freedom)         | ⚠️ AGPL (copyleft)                    |
| **Business conflict**  | ✅ None (solo dev project)       | ❌ Compute credits, app store lock-in |
| **Distribution model** | ✅ 1000+ forks as personal sites | ❌ Walled garden app store            |

### DaedalOS Advantages

- **Recursion**: Built-in browser enables DaedalOS-inside-DaedalOS. `alice.computer` can visit `bob.computer`.
- **Fork-as-distribution**: Each fork is a personal website. Every workspace is marketing.
- **Modern stack**: Next.js 15, React 19, TypeScript, WebLLM, isomorphic-git
- **Already works**: File system, terminal, text editors, AI — all functional

---

## Three Pillars

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   MULTITENANT   │  │     AGENTIC     │  │  VIBE-DESIGNED  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • User accounts │  │ • Background    │  │ • Prompt-based  │
│ • Permissions   │  │   agents        │  │   theming       │
│ • Relationship- │  │ • Action stream │  │ • Design = files│
│   based access  │  │ • File-as-memory│  │ • CSS/wallpaper │
│ • S3 sync per   │  │ • Pansynchronous│  │   via agent     │
│   user          │  │   operation     │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 1. Multitenant

Transform single-user desktop into multi-user platform:

- User authentication
- SQLite state per user
- S3 sync for cloud persistence
- Relationship-based permissions (spouse sees all, doctor sees medical, stranger sees public bio)

### 2. Agentic

The paradigm shift from apps to agents:

- **Action stream**: Observe file/app events, not just explicit invocation
- **Background agents**: Process while user doesn't
- **File-as-memory**: Agents write to files, files ARE the state
- **Pansynchronous**: Operate at all timescales (instant to indefinite)

### 3. Vibe-Designed

Users customize via prompts, not menus:

- Design is just files (CSS, wallpapers, icons, colors)
- Agent modifies theme files based on natural language
- No manual redesign — agent redesigns for each user

---

## Vibe-Design as Onboarding

The first interaction teaches the paradigm:

1. User arrives at default desktop
2. Prompt: "Describe your ideal workspace"
3. Agent modifies theme files
4. User sees result immediately

**This is the teaching moment**: "I prompted → the computer changed."

Sets the expectation for all future interaction: **prompt, not click**. This is the computing pattern of 2025-2050.

---

## Implementation Phases

### Phase 1: Strip to Core

- Remove heavy emulators (DOSBox, Virtual x86)
- Remove games (Quake, Pinball, ClassiCube)
- Keep: File system, Terminal, Text editors, WebLLM, Browser
- **Target**: Fast initial load on any device

### Phase 2: Add Multitenancy

- User authentication
- SQLite state per user
- S3 sync for persistence
- Permission/relationship model

### Phase 3: Add Agent Infrastructure

- Action stream processor
- Background agent runner
- Vibe-design agent (theming via prompts)
- Pansynchronous operation

### Phase 4: Choir Integration

- Citation graph
- Deposit economics
- Fork-as-distribution network
- `alice.computer` ↔ `bob.computer`

---

## What DaedalOS Already Has

| Feature                             | Status      |
| ----------------------------------- | ----------- |
| Web UI as OS                        | ✅ Complete |
| File system (BrowserFS + IndexedDB) | ✅ Complete |
| App ecosystem                       | ✅ Rich     |
| Mobile support                      | ✅ Working  |
| AI integration (WebLLM)             | ✅ Built-in |
| Git support (isomorphic-git)        | ✅ Built-in |
| Browser (recursion capable)         | ✅ Built-in |

## What We Add

| Gap              | Solution                            |
| ---------------- | ----------------------------------- |
| Backend sync     | SQLite + S3 per user                |
| Action stream    | Event processor for file/app events |
| Agent runner     | Background agent execution          |
| Permission model | Relationship-based access           |
| Theming agent    | Vibe-design via prompts             |
| Citation graph   | Choir integration                   |

---

## Distribution Model

**Fork-as-distribution beats app-store-as-distribution.**

Puter's app store doesn't make economic sense: why would a dev deploy inside Puter when they can deploy on the open web for free?

DaedalOS's model works:

- Developers fork, don't deploy "inside"
- Each fork is a personal website/identity
- No platform permission needed
- Network grows through forks
- Every workspace is marketing

This is the organic distribution the web was designed for.

---

## Alignment with Position Paper

| Position Paper Spec              | Implementation                        |
| -------------------------------- | ------------------------------------- |
| "Entanglement model" cloud sync  | S3 sync per user                      |
| "SQLite as state primitive"      | SQLite per user (replacing IndexedDB) |
| "Action stream" event processing | Event processor for file/app changes  |
| "Pansynchronous" multi-timescale | Background agent scheduler            |
| "Permission model" relationships | Relationship-based access control     |
| "Web UI as OS"                   | DaedalOS (already complete)           |
| "The device is the workspace"    | Fork-as-identity                      |
| "Every workspace is marketing"   | Fork-as-distribution                  |

---

## Next Steps

1. Clone DaedalOS
2. Identify stripping targets (emulators, games)
3. Measure bundle size before/after
4. Design SQLite schema for user state
5. Prototype S3 sync
6. Build vibe-design agent

---

_See also: [agentic_computer_paradigm.md](./agentic_computer_paradigm.md), [agentic_computer_position_paper.md](./agentic_computer_position_paper.md)_
