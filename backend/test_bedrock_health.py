#!/usr/bin/env python3
"""
Simple health check for Claude Agent SDK with AWS Bedrock.
Uses Haiku for speed.
"""

import asyncio
import os
import sys
from claude_agent_sdk import query, ClaudeAgentOptions


async def health_check():
    """Quick health check using Haiku."""
    print("=" * 60)
    print("Claude Agent SDK + AWS Bedrock Health Check")
    print("=" * 60)

    # Check environment
    print("\n1. Checking environment...")
    use_bedrock = os.getenv("CLAUDE_SDK_USE_BEDROCK", "false").lower() == "true"
    aws_bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not use_bedrock:
        print("   ❌ CLAUDE_SDK_USE_BEDROCK not set to 'true'")
        return False

    if not aws_bearer_token:
        print("   ❌ AWS_BEARER_TOKEN_BEDROCK not set")
        return False

    print(f"   ✅ Bedrock enabled (region: {aws_region})")
    print(f"   ✅ Bearer token configured")

    # Test simple query with Haiku
    print("\n2. Testing Haiku query...")
    try:
        options = ClaudeAgentOptions(
            model="claude-haiku-4-5-20251001",
            allowed_tools=[]  # No tools for speed
        )

        prompt = "Reply with just the number 4. Nothing else."

        print("   Sending query to Haiku...")
        response_text = ""
        async for message in query(prompt=prompt, options=options):
            response_text += str(message)

        print(f"   ✅ Response received: '{response_text.strip()}'")

        print("\n" + "=" * 60)
        print("✅ HEALTH CHECK PASSED")
        print("=" * 60)
        print("\nClaude Agent SDK with AWS Bedrock is working!")
        return True

    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        print("\n" + "=" * 60)
        print("❌ HEALTH CHECK FAILED")
        print("=" * 60)
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(health_check())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Health check failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
