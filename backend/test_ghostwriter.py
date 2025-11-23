"""
Test script for Ghostwriter pipeline.

Run this to test the multi-stage research and writing system.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.ghostwriter.pipeline import GhostwriterPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_simple_report():
    """Test generating a simple research report."""
    logger.info("=" * 80)
    logger.info("Ghostwriter Pipeline Test: DeFi Yields on Stellar")
    logger.info("=" * 80)

    # Initialize pipeline
    pipeline = GhostwriterPipeline(
        workspace_root="/workspace/sessions",
        num_researchers=3,  # Start with 3 for testing
        max_revision_iterations=2
    )

    # Topic for research
    topic = "DeFi yield farming opportunities on Stellar blockchain in 2025"

    # Run pipeline
    result = await pipeline.run_full_pipeline(
        topic=topic,
        style_guide="defi_report"
    )

    # Print results
    logger.info("=" * 80)
    logger.info("PIPELINE RESULTS")
    logger.info("=" * 80)
    logger.info(f"Success: {result.get('success')}")
    logger.info(f"Session ID: {result.get('session_id')}")
    logger.info(f"Topic: {result.get('topic')}")
    logger.info(f"Final Report: {result.get('final_report')}")
    logger.info(f"Verification Rate: {result.get('verification_rate', 0):.1%}")
    logger.info(f"Revision Iterations: {result.get('revision_iterations', 0)}")

    if result.get("success"):
        logger.info("\n✅ Report generated successfully!")
        logger.info(f"📄 View report at: {result.get('final_report')}")
    else:
        logger.error(f"\n❌ Pipeline failed: {result.get('error')}")

    return result


async def test_stage_1_only():
    """Test only the research stage (Stage 1)."""
    logger.info("=" * 80)
    logger.info("Testing Stage 1: Research (Parallel Haiku Subagents)")
    logger.info("=" * 80)

    pipeline = GhostwriterPipeline(
        workspace_root="/workspace/sessions",
        num_researchers=2  # Just 2 for quick test
    )

    # Create session manually
    topic = "Blend Capital lending protocol overview"
    session_id = pipeline.session_manager.create_session(topic)

    logger.info(f"Created session: {session_id}")
    logger.info(f"Topic: {topic}")

    # Run only Stage 1
    result = await pipeline.stage_1_research(topic)

    logger.info("=" * 80)
    logger.info("STAGE 1 RESULTS")
    logger.info("=" * 80)
    logger.info(f"Researchers launched: {result.get('num_researchers')}")
    logger.info(f"Successful: {result.get('successful')}")
    logger.info(f"Output directory: {result.get('output_dir')}")

    return result


async def test_stages_1_to_3():
    """Test research → draft → extract pipeline."""
    logger.info("=" * 80)
    logger.info("Testing Stages 1-3: Research → Draft → Extract")
    logger.info("=" * 80)

    pipeline = GhostwriterPipeline(
        workspace_root="/workspace/sessions",
        num_researchers=2
    )

    topic = "Stellar blockchain consensus mechanism"
    session_id = pipeline.session_manager.create_session(topic)

    # Stage 1: Research
    logger.info("\n[1/3] Running research stage...")
    research_result = await pipeline.stage_1_research(topic)
    logger.info(f"✅ Research: {research_result.get('successful')}/{research_result.get('num_researchers')} succeeded")

    # Stage 2: Draft
    logger.info("\n[2/3] Running draft stage...")
    draft_result = await pipeline.stage_2_draft()
    logger.info(f"✅ Draft created from {draft_result.get('num_sources')} sources")

    # Stage 3: Extract
    logger.info("\n[3/3] Running extraction stage...")
    extract_result = await pipeline.stage_3_extract()
    logger.info(f"✅ Extracted {extract_result.get('num_claims')} atomic claims")

    logger.info("\n" + "=" * 80)
    logger.info("STAGES 1-3 COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Session: {session_id}")
    logger.info(f"Claims extracted: {extract_result.get('num_claims')}")

    return {
        "session_id": session_id,
        "research": research_result,
        "draft": draft_result,
        "extract": extract_result
    }


def print_usage():
    """Print usage instructions."""
    print("""
Ghostwriter Pipeline Test Script
=================================

Usage:
    python test_ghostwriter.py [test_name]

Available tests:
    full            - Run complete 8-stage pipeline (default)
    stage1          - Test only research stage (quick)
    stages123       - Test research → draft → extract
    help            - Show this help message

Examples:
    python test_ghostwriter.py                # Run full pipeline
    python test_ghostwriter.py stage1         # Quick research test
    python test_ghostwriter.py stages123      # Test first 3 stages

Notes:
    - Ensure CLAUDE_SDK_USE_BEDROCK=true and AWS_BEARER_TOKEN_BEDROCK are set
    - Full pipeline may take 5-10 minutes and cost ~$0.70
    - Stage 1 test is fastest (~1 minute, ~$0.05)
    - Results saved to /workspace/sessions/session_YYYYMMDD_HHMMSS/
""")


async def main():
    """Main test runner."""
    # Parse command line arguments
    test_name = sys.argv[1] if len(sys.argv) > 1 else "full"

    if test_name == "help":
        print_usage()
        return

    # Run selected test
    try:
        if test_name == "stage1":
            await test_stage_1_only()
        elif test_name == "stages123":
            await test_stages_1_to_3()
        elif test_name == "full":
            await test_simple_report()
        else:
            logger.error(f"Unknown test: {test_name}")
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\nTest failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
