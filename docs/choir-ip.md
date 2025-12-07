Here is the comprehensive architectural blueprint and execution plan for **Choir**. This document synthesizes your economic vision (The Thought Bank) with your interface paradigm (The Agentic Computer) and outlines the immediate technical path using `daedalOS`.

---

# Choir: Infrastructure for Sovereign Intelligence

**Domain:** `choir-ip.com` (Current) $\to$ `choiriq.com` (Future)
**Paradigm:** The Agentic Computer & The Thought Bank

## I. Executive Summary

Choir is an operating system for the learning economy. It rejects the "chatbot" model (synchronous, ephemeral) in favor of the **Agentic Computer** model (pansynchronous, persistent).

- **The Interface:** A web-based desktop OS where agents observe your work and assist asynchronously.
- **The Economy:** A "Thought Bank" where every file is an asset. Citations generate income (USDC), and novelty generates ownership (CHIP).
- **The Architecture:** A "User-Entangled" system where a local browser OS syncs state via SQLite to a cloud-based agentic backend.

---

## II. The Core Paradigms

### 1. The Agentic Computer (UX)

Current AI makes you prompt it. The Agentic Computer observes you.

- **Pansynchronous:** Operates across all time scales. You write a note; the agent researches it in the background and appends results an hour later.
- **The OS Metaphor:** Instead of a chat window, users interact with files, windows, and applications. The AI is the infrastructure, not the interlocutor.

### 2. The Thought Bank (Economics)

Intelligence that creates value should share in that value.

- **IP as Money:** Every article, code snippet, or insight published is a distinct asset.
- **Citation Economics:** If Agent A cites User B's article to solve a problem, User B earns USDC.
- **Vindication:** Immutable timestamps prove you had the idea first, allowing for retroactive credit when the mainstream catches up.

---

## III. Technical Architecture: The Entanglement

We do not run heavy agents in the browser. We **entangle** the browser OS with a cloud agent via a shared state primitive.

### 1. The State Primitive: SQLite

The entire OS state lives in a single `workspace.sqlite` file.

- **Tables:** `files`, `action_log`, `agent_tasks`, `citations`.
- **Sync:** The browser runs SQLite (WASM). Changes sync to S3. The Cloud Agent watches S3, processes data, and writes back to SQLite.

### 2. The URL Architecture (Deep Linking)

The URL is the address of the IP.

- **Phase 1: Hard URLs (Deterministic)**
  - `choir-ip.com/@user/read/{uuid}` $\to$ Opens Reader App.
  - `choir-ip.com/@user/edit/{uuid}` $\to$ Opens Vibewriter IDE.
  - _Purpose:_ Essential for the Citation Graph. A citation must point to a specific, immutable hash.

- **Phase 2: Soft URLs (Semantic/CLI)**
  - `choir-ip.com/q/show-me-drafts-about-stellar`
  - _Mechanism:_ URL $\to$ LLM $\to$ SQL Query $\to$ Dynamic View.
  - _Purpose:_ The URL bar becomes the command line for the OS.

---

## IV. Implementation Strategy: The daedalOS Fork

We are bootstrapping the interface by forking `daedalOS`, a web-based desktop environment. We will strip it down and re-wire its brain.

### 1. The Cleanup (De-bloat)

`daedalOS` is a showcase; we need a workspace.

- **Remove:** Emulators (Box86), Games (Doom), Media Players (Winamp).
- **Keep:** Window Manager, File Explorer, Monaco Editor (Code), Markdown Viewer.

### 2. The File System Swap

- **Current:** `BrowserFS` (IndexedDB).
- **New:** `ChoirFS` (SQLite WASM).
- **Logic:** When the "Monaco" app saves a file, it writes to the local SQLite DB and emits an event to the `Action Stream` for the backend agent to ingest.

### 3. The Visual Identity

- **Theme:** Carbon Fiber Kintsugi.
- **Aesthetic:** Dark grey industrial textures (Carbon) repaired with glowing gold joinery (Kintsugi).
- **Metaphor:** The "broken" web is being repaired by value-creating agents.

---

## V. Checklist: Next Steps

### Phase 1: Setup & Cleanup (Morning)

- [ ] **Fork Repo:** Clone `DustinBrett/daedalOS` to a private repo `choir-os`.
- [ ] **Purge Apps:** Delete `games`, `emulators`, `webamp` from `/components/apps`.
- [ ] **Clean Menu:** Remove "Start Menu" entries for deleted apps in `/utils/initialContextState.ts`.
- [ ] **Local Test:** Ensure `yarn dev` runs a clean, empty desktop.
- [ ] **Deploy:** Set up AWS deployment on `choir-ip.com` (dev). Phala TEE is the production target.

### Phase 2: The Visuals (Midday)

- [ ] **Assets:** Generate "Carbon Fiber" background and "Gold Kintsugi" UI assets (using Midjourney/DALL-E).
- [ ] **Theme Engine:** Modify `styled-components` theme (`/styles/defaultTheme.ts`).
  - [ ] Window Title Bars: Dark Grey/Black.
  - [ ] Minimize/Close Buttons: Gold.
  - [ ] Taskbar: Frosted Glass (Blur).
- [ ] **Branding:** Replace the "Start Button" icon with the Choir logo.

### Phase 3: The Architecture (Afternoon)

- [ ] **Database:** Install `sql.js` (SQLite WASM).
- [ ] **Schema:** Create the `workspace` table structure (id, blob, metadata).
- [ ] **Adapter:** Write `ChoirFS` adapter to intercept file reads/writes from the OS and route them to SQLite.
- [ ] **Hard Routing:** Implement logic in `pages/index.tsx` to parse `/app/uuid` and auto-open the corresponding window on load.

### Phase 4: The Agent Entanglement (Evening)

- [ ] **Backend:** Set up a simple Python/FastAPI backend (The Conductor).
- [ ] **Sync:** Implement S3 signed URL upload/download for the SQLite file.
- [ ] **Vibewriter:** Connect the Monaco Editor app to the backend for "Autocomplete" or "Refactor" requests (Agent initiation).
- [ ] **Soft URLs:** Implement `/q/` semantic query routing (URL → LLM → SQL → Dynamic View).

### Phase 5: The Rebrand

- [ ] **Acquire Domain:** Buy `choiriq.com` once soft URLs are working.
- [ ] **Migrate:** Point `choiriq.com` to production deployment.

---

### Immediate Action Item

**Execute Phase 1, Step 1:** Fork `DustinBrett/daedalOS` → `choir-os`.
