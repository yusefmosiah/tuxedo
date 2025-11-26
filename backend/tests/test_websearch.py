#!/usr/bin/env python3
"""
Test WebSearch functionality for Ghostwriter researchers.

This script tests:
1. Tavily API connection
2. WebSearch CLI tool
3. Search result formatting
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from pathlib import Path
import pytest
import subprocess

# Load environment variables
load_dotenv()

from agent.ghostwriter.openhands_websearch import (
    WebSearchAction,
    get_websearch_executor
)


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("TAVILY_API_KEY"), reason="TAVILY_API_KEY not found in environment")
async def test_websearch():
    """Test WebSearch with a sample query."""

    # Check for API key
    api_key = os.getenv("TAVILY_API_KEY")

    print(f"✅ Tavily API key found: {api_key[:8]}...{api_key[-4:]}")
    print()

    # Create test query
    test_query = "DeFi yield farming on Stellar blockchain"
    print(f"🔍 Testing search query: '{test_query}'")
    print("-" * 60)
    print()

    try:
        # Create action
        action = WebSearchAction(
            query=test_query,
            max_results=3,
            search_depth="advanced"
        )

        # Execute search
        executor = get_websearch_executor()
        observation = await executor.execute(action)

        assert observation.success, f"WebSearch failed: {observation.error}"

        print("✅ WebSearch successful!")
        print()
        print("=" * 60)
        print("SEARCH RESULTS:")
        print("=" * 60)
        print(observation.content)
        print()
        print("✅ Test passed: WebSearch is working correctly")

    except Exception as e:
        pytest.fail(f"Test failed with exception: {str(e)}")


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("TAVILY_API_KEY"), reason="TAVILY_API_KEY not found in environment")
async def test_cli_tool():
    """Test the CLI wrapper."""
    import subprocess

    print("\n" + "=" * 60)
    print("Testing CLI tool...")
    print("=" * 60)
    print()

    try:
        # Test as module
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "agent.ghostwriter.websearch_cli",
                "Stellar blockchain",
                "--max-results",
                "2"
            ],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"CLI tool failed with exit code {result.returncode}\nSTDERR: {result.stderr}"

        print("✅ CLI tool test passed!")
        print("\nCLI Output:")
        print("-" * 60)
        print(result.stdout)

    except Exception as e:
        pytest.fail(f"CLI test failed: {str(e)}")
