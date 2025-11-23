"""
Ghostwriter: Multi-stage AI research and writing system using Claude Agent SDK.

This module implements an 8-stage pipeline for generating well-researched,
fact-checked reports with citations:

1. Research: Parallel Haiku subagents gather sources
2. Draft: Sonnet synthesizes research into coherent document
3. Extract: Haiku extracts atomic claims and citations
4. Verify: 3-layer verification (URL, content, claim verification)
5. Critique: Sonnet analyzes quality and identifies issues
6. Revise: Sonnet fixes unsupported claims
7. Re-verify: Verification of revised claims
8. Style: Sonnet applies style guide

Key features:
- Uses existing Claude SDK infrastructure (no new setup)
- Haiku for cheap/fast tasks, Sonnet for complex reasoning
- Prompt caching for efficiency
- ~$0.67 per 1000-word report
- 3-5 minute generation time

See docs/GHOSTWRITER_ARCHITECTURE_PRACTICAL.md for details.
"""

from .pipeline import GhostwriterPipeline
from .utils import SessionManager
from .api import router as api_router

__all__ = ["GhostwriterPipeline", "SessionManager", "api_router"]
