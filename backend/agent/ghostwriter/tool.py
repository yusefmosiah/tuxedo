"""
Ghostwriter Tool
Exposes the Ghostwriter research pipeline as a LangChain tool.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from langchain.tools import tool
from agent.ghostwriter.pipeline import GhostwriterPipeline
from agent.context import AgentContext

logger = logging.getLogger(__name__)

@tool
def ghostwriter_research(
    topic: str,
    style_guide: str = "general_report",
    verification_threshold: float = 0.8,
    max_iterations: int = 3
):
    """
    Conduct deep research and generate a comprehensive report on a specific topic.

    Use this tool when the user asks for:
    - "Research X"
    - "Write a report about Y"
    - "Investigate Z"
    - "Deep dive into topic A"

    This is a long-running process that involves:
    1. Planning research questions
    2. Searching the web for sources
    3. Extracting and verifying claims
    4. Writing a structured report

    Args:
        topic: The research topic or question to investigate. Be specific.
        style_guide: The style of report to generate. Options: "general_report", "defi_report", "technical_brief". Default: "general_report".
        verification_threshold: Minimum confidence score for verified claims (0.0 to 1.0). Default: 0.8.
        max_iterations: Maximum number of refinement iterations. Default: 3.

    Returns:
        A summary of the research session, including the final report content or a path to it.
    """
    # Note: This tool is synchronous in signature but runs async code internally
    # because LangChain tools are often called synchronously by the agent executor.
    # However, since we are in an async environment, we might need to handle this carefully.
    # Based on other tools in tool_factory.py, they seem to use asyncio.run() or similar if needed,
    # or are defined as async functions if the executor supports it.
    # The tool_factory.py uses @tool on functions that return futures or run async code.

    # Let's try to match the pattern in tool_factory.py where they define the tool function
    # and then use asyncio.run or a thread pool if needed, OR just define it as async
    # if the agent framework supports async tools (which it seems to, given `ainvoke` usage in core.py).

    # However, the `tool_factory.py` examples show `@tool` decorating synchronous functions
    # that use `asyncio.run` or `ThreadPoolExecutor` to run async code.
    # BUT `core.py` checks for `ainvoke` and `asyncio.iscoroutinefunction`.
    # Let's define it as an async function to be modern and efficient.

    return _run_ghostwriter_async(topic, style_guide, verification_threshold, max_iterations)

async def _run_ghostwriter_async(
    topic: str,
    style_guide: str,
    verification_threshold: float,
    max_iterations: int
) -> Dict[str, Any]:
    """Async implementation of the ghostwriter tool."""
    try:
        logger.info(f"Starting Ghostwriter research on: {topic}")

        # Initialize pipeline
        # We might want to make workspace_root configurable or dynamic
        pipeline = GhostwriterPipeline(
            workspace_root="/tmp/ghostwriter_sessions",
            verification_threshold=verification_threshold,
            max_revision_iterations=max_iterations
        )

        # Run pipeline
        result = await pipeline.run_full_pipeline(
            topic=topic,
            style_guide=style_guide
        )

        if result.get("success"):
            # Read the final report content to return it directly if it's not too huge
            # or just return the summary and path.
            final_report_path = result.get("final_report")
            report_content = "Report generated successfully."

            if final_report_path:
                try:
                    with open(final_report_path, "r") as f:
                        content = f.read()
                        # Truncate if too long for context window, but ideally we return the whole thing
                        # or a summary. For now, let's return a preview and the path.
                        preview = content[:2000] + ("..." if len(content) > 2000 else "")
                        report_content = f"## Research Report\n\n{preview}\n\nFull report saved to: {final_report_path}"
                except Exception as e:
                    logger.warning(f"Could not read final report file: {e}")

            return {
                "success": True,
                "session_id": result.get("session_id"),
                "report_preview": report_content,
                "verification_rate": result.get("verification_rate"),
                "message": f"Research completed successfully. Session ID: {result.get('session_id')}"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error during research pipeline execution")
            }

    except Exception as e:
        logger.error(f"Error in ghostwriter tool: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
