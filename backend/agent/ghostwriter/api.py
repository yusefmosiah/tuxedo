"""
FastAPI routes for Ghostwriter integration.

Add these routes to the main FastAPI app in backend/main.py
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .pipeline import GhostwriterPipeline

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ghostwriter", tags=["ghostwriter"])


# Request/Response models
class GenerateReportRequest(BaseModel):
    """Request to generate a research report."""
    topic: str = Field(..., description="Research topic", min_length=10, max_length=500)
    style_guide: str = Field(
        default="technical",
        description="Style guide to apply (technical, conversational, academic, defi_report)"
    )
    num_researchers: int = Field(
        default=5,
        description="Number of parallel research agents",
        ge=1,
        le=10
    )
    max_revisions: int = Field(
        default=3,
        description="Maximum revision iterations",
        ge=1,
        le=5
    )


class GenerateReportResponse(BaseModel):
    """Response from report generation."""
    success: bool
    session_id: str
    topic: str
    final_report: Optional[str] = None
    verification_rate: Optional[float] = None
    revision_iterations: Optional[int] = None
    error: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """Response for session status check."""
    session_id: str
    status: str  # initialized, running, completed, failed
    current_stage: Optional[str] = None
    last_updated: Optional[str] = None


# Endpoints

@router.post("/generate", response_model=GenerateReportResponse)
async def generate_report(request: GenerateReportRequest):
    """
    Generate a research report using the Ghostwriter pipeline.

    This endpoint runs the full 8-stage pipeline:
    1. Research: Parallel Haiku subagents gather sources
    2. Draft: Sonnet synthesizes research
    3. Extract: Haiku extracts atomic claims
    4. Verify: 3-layer claim verification
    5. Critique: Sonnet analyzes quality
    6. Revise: Sonnet fixes issues
    7. Re-verify: Verify revised claims
    8. Style: Sonnet applies style guide

    **Estimated time**: 3-5 minutes
    **Estimated cost**: $0.67 - $1.50 (depending on revisions)

    Args:
        request: Report generation parameters

    Returns:
        Report generation results with final report path
    """
    try:
        logger.info(f"Generating report: topic='{request.topic}', style={request.style_guide}")

        # Initialize pipeline
        pipeline = GhostwriterPipeline(
            workspace_root="/workspace/sessions",
            num_researchers=request.num_researchers,
            max_revision_iterations=request.max_revisions
        )

        # Run pipeline
        result = await pipeline.run_full_pipeline(
            topic=request.topic,
            style_guide=request.style_guide
        )

        return GenerateReportResponse(**result)

    except Exception as e:
        logger.error(f"Report generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """
    Get status of a ghostwriter session.

    Args:
        session_id: Session identifier

    Returns:
        Session status information
    """
    try:
        from .utils import SessionManager

        session_manager = SessionManager()
        session_manager.load_session(session_id)

        # Load metadata
        metadata = session_manager.load_json("metadata.json")

        return SessionStatusResponse(
            session_id=session_id,
            status=metadata.get("status", "unknown"),
            current_stage=metadata.get("current_stage"),
            last_updated=metadata.get("last_updated")
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    except Exception as e:
        logger.error(f"Error getting session status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/report")
async def get_final_report(session_id: str):
    """
    Retrieve final report from completed session.

    Args:
        session_id: Session identifier

    Returns:
        Final report content as markdown
    """
    try:
        from .utils import SessionManager

        session_manager = SessionManager()
        session_manager.load_session(session_id)

        # Try to load final report
        try:
            report = session_manager.load_text("07_style/final_report.md")
        except FileNotFoundError:
            # Fallback to draft if style stage not complete
            try:
                report = session_manager.load_text("05_revision/revised_draft.md")
            except FileNotFoundError:
                report = session_manager.load_text("01_draft/initial_draft.md")

        return {
            "session_id": session_id,
            "content": report,
            "format": "markdown"
        }

    except ValueError:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Report not found for session: {session_id}")
    except Exception as e:
        logger.error(f"Error retrieving report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions():
    """
    List all ghostwriter sessions.

    Returns:
        List of session IDs
    """
    try:
        from .utils import SessionManager

        session_manager = SessionManager()
        sessions = session_manager.list_sessions()

        return {
            "sessions": sessions,
            "total": len(sessions)
        }

    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/style-guides")
async def list_style_guides():
    """
    List available style guides.

    Returns:
        Available style guides with descriptions
    """
    return {
        "style_guides": [
            {
                "name": "technical",
                "description": "For engineers and developers. Technical jargon, precise specifications.",
                "audience": "Software engineers, blockchain developers"
            },
            {
                "name": "conversational",
                "description": "For general audience. Friendly, simple language with analogies.",
                "audience": "Crypto enthusiasts, newcomers"
            },
            {
                "name": "academic",
                "description": "For research and formal publications. Scholarly rigor, evidence-based.",
                "audience": "Researchers, academics, policy makers"
            },
            {
                "name": "defi_report",
                "description": "For DeFi investors. Data-driven with APY/TVL metrics and risk assessment.",
                "audience": "Yield farmers, crypto analysts"
            }
        ]
    }


# Example integration into main.py:
"""
from agent.ghostwriter.api import router as ghostwriter_router

app = FastAPI()
app.include_router(ghostwriter_router)
"""
