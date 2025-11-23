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

# Load environment variables
load_dotenv()

from agent.ghostwriter.openhands_websearch import (
    WebSearchAction,
    get_websearch_executor
)


async def test_websearch():
    """Test WebSearch with a sample query."""

    # Check for API key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ ERROR: TAVILY_API_KEY not found in environment")
        print("Please add your Tavily API key to backend/.env")
        print("Get one from: https://app.tavily.com/")
        return False

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

        if observation.success:
            print("✅ WebSearch successful!")
            print()
            print("=" * 60)
            print("SEARCH RESULTS:")
            print("=" * 60)
            print(observation.content)
            print()
            print("✅ Test passed: WebSearch is working correctly")
            return True
        else:
            print(f"❌ WebSearch failed: {observation.error}")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


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
            cwd="/home/user/tuxedo/backend",
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ CLI tool test passed!")
            print("\nCLI Output:")
            print("-" * 60)
            print(result.stdout)
            return True
        else:
            print(f"❌ CLI tool failed with exit code {result.returncode}")
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ CLI test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("WebSearch Integration Test Suite")
    print("=" * 60)
    print()

    # Test 1: Direct API call
    test1_passed = await test_websearch()

    # Test 2: CLI tool
    test2_passed = await test_cli_tool()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Direct API test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"CLI tool test:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print()

    if test1_passed and test2_passed:
        print("🎉 All tests passed! WebSearch is ready for Ghostwriter.")
        print()
        print("Next steps:")
        print("1. Run the Ghostwriter pipeline with: python -m agent.ghostwriter.test_pipeline")
        print("2. Researchers will now be able to search the web using Tavily API")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
