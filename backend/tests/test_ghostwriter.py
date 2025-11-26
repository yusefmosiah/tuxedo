#!/usr/bin/env python3
"""
Test script for Ghostwriter pipeline.

Generates a comprehensive research report using the 8-stage pipeline.
"""

import asyncio
import sys
import logging
from pathlib import Path
import pytest
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.ghostwriter import GhostwriterPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("AWS_ACCESS_KEY_ID"), reason="AWS credentials not found")
async def test_ghostwriter_pipeline():
    """
    Test the Ghostwriter pipeline with a DeFi research topic.

    This will:
    1. Create a session
    2. Run all 8 stages
    3. Generate a comprehensive report
    4. Display results and metrics
    """
    logger.info("=" * 80)
    logger.info("Ghostwriter Pipeline Test")
    logger.info("=" * 80)

    # Create pipeline
    pipeline = GhostwriterPipeline(
        workspace_root="/tmp/ghostwriter_test_sessions",
        aws_region="us-east-1",
        num_researchers=3,  # Start with 3 for faster testing
        max_revision_iterations=2,
        verification_threshold=0.90
    )

    # Test topic - DeFi yields on Stellar (relevant to Tuxedo)
    topic = "DeFi yield opportunities on Stellar blockchain with Blend Capital protocol in 2025"
    style_guide = "defi_report"  # Use DeFi report style

    logger.info(f"\nTopic: {topic}")
    logger.info(f"Style: {style_guide}")
    logger.info(f"Researchers: {pipeline.num_researchers}")
    logger.info(f"Verification threshold: {pipeline.verification_threshold:.0%}")
    logger.info("")

    try:
        # Run full pipeline
        result = await pipeline.run_full_pipeline(
            topic=topic,
            style_guide=style_guide
        )

        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("RESULTS")
        logger.info("=" * 80)

        assert result.get("success"), f"Pipeline failed: {result.get('error', 'Unknown error')}"

        logger.info("✅ Pipeline completed successfully!")
        logger.info(f"\nSession ID: {result['session_id']}")
        logger.info(f"Final Report: {result.get('final_report', 'N/A')}")
        logger.info(f"Verification Rate: {result.get('verification_rate', 0):.1%}")

        # Display stage breakdown
        logger.info("\n--- Stage Results ---")
        stages = result.get("stages", {})

        if "research" in stages:
            logger.info(f"Research: {stages['research']['num_sources']} sources gathered")

        if "extract" in stages:
            logger.info(f"Extraction: {stages['extract']['num_claims']} claims extracted")

        if "verify" in stages:
            verify = stages['verify']['report']
            logger.info(
                f"Verification: {verify['verified_claims']}/{verify['total_claims']} "
                f"claims verified ({verify['verification_rate']:.1%})"
            )

        # Read and display final report preview
        final_report_path = Path(result.get('final_report', ''))
        if final_report_path.exists():
            logger.info("\n--- Final Report Preview (first 500 chars) ---")
            report_content = final_report_path.read_text()
            logger.info(report_content[:500] + "...\n")

            logger.info(f"Full report available at: {final_report_path}")
            logger.info(f"Report length: {len(report_content)} characters")

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}", exc_info=True)
        pytest.fail(f"Test failed with exception: {e}")
