#!/usr/bin/env python3
"""
Test the full Ghostwriter pipeline with WebSearch integration.

This script runs all 8 stages of the Ghostwriter pipeline:
1. Research (parallel Haiku researchers with WebSearch)
2. Draft (Sonnet synthesizes research)
3. Extract (Haiku extracts claims)
4. Verify (Haiku verifies claims)
5. Critique (Sonnet critiques draft)
6. Revise (Sonnet revises based on critique)
7. Re-verify (Haiku re-verifies revised claims)
8. Style (Sonnet applies style guide)
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Setup logging - only show warnings and errors
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from agent.ghostwriter.pipeline import GhostwriterPipeline


async def test_pipeline():
    """Test the full Ghostwriter pipeline."""

    print("=" * 80)
    print("GHOSTWRITER PIPELINE TEST")
    print("Testing with WebSearch integration")
    print("=" * 80)
    print()

    # Configuration
    test_topic = "DeFi yield farming strategies on Stellar blockchain"
    workspace_root = Path("ghostwriter_sessions").resolve()

    print(f"Topic: {test_topic}")
    print(f"Workspace: {workspace_root}")
    print(f"Researchers: 3 (reduced from 5 for faster testing)")
    print()

    try:
        # Create pipeline
        pipeline = GhostwriterPipeline(
            workspace_root=workspace_root,
            aws_region="us-east-1",
            num_researchers=3,  # Reduced for faster testing
            max_revision_iterations=1,  # Reduced for faster testing
            verification_threshold=0.80  # Slightly lower for testing
        )

        print("Pipeline initialized successfully")
        print()

        # Run pipeline
        print("Starting pipeline execution...")
        print("This will take several minutes as agents research, draft, and revise.")
        print()

        start_time = datetime.now()

        result = await pipeline.run_full_pipeline(
            topic=test_topic,
            style_guide="technical"
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print results
        print()
        print("=" * 80)
        print("PIPELINE RESULTS")
        print("=" * 80)
        print()

        print(f"Success: {result.get('success', False)}")
        print(f"Session ID: {result.get('session_id', 'N/A')}")
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print()

        # Stage results
        stages = result.get('stages', {})
        print("Stage Results:")
        print("-" * 80)
        for stage_name, stage_data in stages.items():
            print(f"  {stage_name}:")
            if isinstance(stage_data, dict):
                for key, value in stage_data.items():
                    if key not in ['stage', 'timestamp']:
                        print(f"    {key}: {value}")
            print()

        # Final metrics
        print("Final Metrics:")
        print("-" * 80)
        print(f"  Verification Rate: {result.get('verification_rate', 0):.1%}")
        print(f"  Final Report: {result.get('final_report', 'N/A')}")
        print()

        # Check if report was created
        if result.get('final_report'):
            report_path = Path(result['final_report'])
            if report_path.exists():
                print(f"✅ Final report created successfully")
                print(f"   Location: {report_path}")
                print(f"   Size: {report_path.stat().st_size} bytes")

                # Show first 500 chars of report
                with open(report_path, 'r') as f:
                    content = f.read()
                    print()
                    print("Report Preview:")
                    print("-" * 80)
                    print(content[:500])
                    if len(content) > 500:
                        print("... [truncated]")
                    print()
            else:
                print(f"⚠️  Final report path provided but file not found")

        # Check research sources
        session_id = result.get('session_id')
        if session_id:
            research_dir = Path(workspace_root) / session_id / "00_research"
            if research_dir.exists():
                sources = list(research_dir.glob("source_*.md"))
                print(f"Research Sources: {len(sources)} files")
                for source in sources[:3]:  # Show first 3
                    print(f"  - {source.name}")
                if len(sources) > 3:
                    print(f"  ... and {len(sources) - 3} more")
                print()

        if result.get('success'):
            print("=" * 80)
            print("✅ PIPELINE TEST PASSED")
            print("=" * 80)
            return True
        else:
            print("=" * 80)
            print("❌ PIPELINE TEST FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print("=" * 80)
            return False

    except Exception as e:
        logger.exception("Pipeline test failed with exception")
        print()
        print("=" * 80)
        print("❌ PIPELINE TEST FAILED WITH EXCEPTION")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        return False


async def main():
    """Main test entry point."""
    success = await test_pipeline()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
