"""
Ghostwriter: Multi-stage AI research and writing system

This module implements an 8-stage pipeline for generating comprehensive,
fact-checked research reports with 90%+ verification rate.

Architecture based on:
- docs/GHOSTWRITER_ARCHITECTURE_OPENHANDS_SDK.md (R&D/design)
- docs/GHOSTWRITER_ARCHITECTURE_PRACTICAL.md (implementation guide)

Stages:
1. Research: Parallel web research with Haiku subagents
2. Draft: Synthesis into coherent document with Sonnet
3. Extract: Atomic claims and citations extraction
4. Verify: 3-layer verification (URL, content, Claude verification)
5. Critique: Quality assessment and issue identification
6. Revise: Fix unsupported claims with web research
7. Re-verify: Verify revised claims
8. Style: Apply style guide transformation

Usage:
    from ghostwriter import GhostwriterPipeline

    pipeline = GhostwriterPipeline()
    result = await pipeline.run_full_pipeline(
        topic="DeFi yields on Stellar blockchain",
        style_guide="defi_report"
    )
"""

from .pipeline import GhostwriterPipeline

__version__ = "0.1.0"
__all__ = ["GhostwriterPipeline"]
