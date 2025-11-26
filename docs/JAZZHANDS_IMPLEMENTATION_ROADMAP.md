# Jazzhands Implementation Roadmap

**3-Day Sprint: Fork to Production**

**Version 2.0 - November 26, 2025**

---

## Update: See JAZZHANDS_3DAY_SPRINT.md

This document has been replaced by **JAZZHANDS_3DAY_SPRINT.md**, which contains the actual implementation plan.

**Timeline**: 3 days (not 16 weeks)
**Approach**: Aggressive (solo dev + AI agents)
**Philosophy**: Ship fast, improve later

---

## Why The Change

**v1.0 Assumptions** (WRONG):
- 16-week phased migration
- Remove OpenHands UI components
- Hide coding agent from users
- Build custom research interface
- Team of 2-3 engineers

**v2.0 Reality** (CORRECT):
- 3-day sprint
- Keep OpenHands UI as-is
- Users see agent work
- Add economics on top
- Solo dev + AI agents

**The Realization**: All agents are coding agents. OpenHands provides exactly what we need. Don't fight it.

---

## The 3-Day Plan

See **JAZZHANDS_3DAY_SPRINT.md** for full details.

### Day 1: Fork + Remote Runtime + Choir Tools
- Fork OpenHands, delete `enterprise/`
- Integrate RunLoop remote runtime
- Add 3 Choir tools (search_choir_kb, cite_article, publish_to_choir)

**Deliverable**: Agent can research and produce drafts with full computer control

### Day 2: Crypto Economic Integrations
- Database schema (users, balances, articles, citations)
- Semantic novelty scoring (Qdrant + OpenAI)
- Publishing + citation system (CHIP rewards, USDC payments)

**Deliverable**: Publishing earns CHIP, citations pay USDC

### Day 3: UX Improvements
- Economic header (CHIP/USDC/compute balances)
- Publish button (appears when draft ready)
- My Research page (articles, citations, earnings)

**Deliverable**: Usable Choir/Jazzhands with economic UI

---

## What We're NOT Doing

Based on v1.0 incorrect assumptions:

❌ **Phase 1-4 Migration** (16 weeks)
❌ **Component Removal** (terminal, code editor, file explorer)
❌ **Frontend Transformation** (research workbench UI)
❌ **Event Stream Sanitization** (hiding code from users)
❌ **Dual-Mode Operation** (parallel old/new systems)
❌ **Phased User Migration** (10% → 50% → 100%)

**None of that is necessary.** Just fork, add economics, ship.

---

## Timeline Comparison

| Task | v1.0 (Wrong) | v2.0 (Correct) |
|------|--------------|----------------|
| **Fork & Setup** | Week 1-2 | Day 1, Hour 1-2 |
| **Runtime Integration** | Week 2-3 | Day 1, Hour 3-4 |
| **Agent Tools** | Week 3-4 | Day 1, Hour 5-8 |
| **Economics** | Week 5-8 | Day 2, Hour 1-8 |
| **Frontend Changes** | Week 9-12 | Day 3, Hour 1-8 |
| **Testing** | Week 13-14 | Ongoing |
| **Deployment** | Week 15-16 | Day 3, end |
| **Total** | **16 weeks** | **3 days** |

---

## Why 3 Days Is Realistic

1. **No major refactoring** - Keep OpenHands codebase mostly intact
2. **No UI rebuild** - Just add 3 components on top
3. **No component removal** - Zero surgery on OpenHands frontend
4. **Solo dev + AI agents** - Parallel work, fast iteration
5. **Ship MVP** - Polish later, based on user feedback

---

## Risk Mitigation

**If Day 1 fails** (runtime integration):
- Fall back to local Docker (less secure, works for MVP)

**If Day 2 fails** (novelty scoring):
- Use fixed CHIP rewards (add semantic scoring later)

**If Day 3 fails** (UX too rough):
- Ship without polish (users use OpenHands UI directly)

**Every day is a checkpoint.** Can ship at any point.

---

## Post-Sprint (Week 2+)

**Week 2**: Polish UX, add onboarding, invite first users
**Week 3**: Optimize novelty scoring, tune CHIP rewards
**Week 4**: Add features based on feedback
**Month 2+**: Mobile app, advanced features

But get v1 out in 3 days first.

---

## Success Criteria

**Day 3 Complete When**:
- [ ] Fork builds and runs
- [ ] Remote runtime spawns per user
- [ ] Agent can research autonomously
- [ ] Publishing earns CHIP (semantic novelty)
- [ ] Citations pay USDC
- [ ] Users see balances and can publish

**That's the MVP.** Ship it, iterate from there.

---

**Document Status**: v2.0 (Simplified)
**Replaces**: v1.0 (16-week enterprise migration plan)
**See**: JAZZHANDS_3DAY_SPRINT.md for implementation details
