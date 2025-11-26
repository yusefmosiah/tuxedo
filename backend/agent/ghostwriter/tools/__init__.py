"""
Ghostwriter autonomous research tools.

Each tool represents a discrete work node in the research workflow.
The autonomous orchestrator decides which tools to call, in what order,
and can loop back to earlier stages as needed.

Tool Categories:
- Research workflow tools: Core research stages (hypotheses, evidence, draft, etc.)
- Meta-cognitive tools: Self-assessment, revision, inspection
- (Future) Live data tools: Somnia integration, real-time blockchain data
"""

from typing import List, Type

# Will be populated as we implement each tool
RESEARCH_TOOLS: List[Type] = []
META_TOOLS: List[Type] = []

# Import tools as they're implemented
# from .hypothesis_former import FormHypothesesTool
# from .hypothesis_revisor import RevisitHypothesesTool
# etc.

ALL_GHOSTWRITER_TOOLS = RESEARCH_TOOLS + META_TOOLS

__all__ = [
    "RESEARCH_TOOLS",
    "META_TOOLS",
    "ALL_GHOSTWRITER_TOOLS",
]
