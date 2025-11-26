#!/usr/bin/env python3
"""
WebSearch CLI tool for OpenHands researchers.

This script can be called by OpenHands agents via TerminalTool to perform
web searches using Tavily API.

Usage:
    python -m agent.ghostwriter.websearch_cli "your search query" [--max-results 5]
    OR
    python websearch_cli.py "your search query" [--max-results 5]
"""

import sys
import os
import asyncio
import argparse
import logging
from pathlib import Path

# To support running as a script and a module, we need to adjust the path
# This allows us to import our patch utility from the backend root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from openhands_utils import apply_openhands_patch

# Apply the patch *before* any OpenHands modules are imported
apply_openhands_patch()

# Now we can safely import the OpenHands-dependent modules
from agent.ghostwriter.openhands_websearch import WebSearchAction, get_websearch_executor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="WebSearch CLI for OpenHands researchers"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of results (default: 20)"
    )
    parser.add_argument(
        "--search-depth",
        type=str,
        default="advanced",
        choices=["basic", "advanced"],
        help="Search depth (default: advanced)"
    )

    args = parser.parse_args()

    # Check for API key
    if not os.getenv("TAVILY_API_KEY"):
        print("ERROR: TAVILY_API_KEY environment variable not set", file=sys.stderr)
        print("Please set your Tavily API key in .env file", file=sys.stderr)
        sys.exit(1)

    # Create search action
    action = WebSearchAction(
        query=args.query,
        max_results=args.max_results,
        search_depth=args.search_depth
    )

    # Execute search
    try:
        executor = get_websearch_executor()
        observation = await executor.execute(action)

        if observation.success:
            print(observation.content)
            sys.exit(0)
        else:
            print(f"ERROR: {observation.error}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        logger.exception("WebSearch CLI error")
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
