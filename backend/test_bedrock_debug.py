#!/usr/bin/env python3
"""
Debug AWS Bedrock configuration step by step.
"""

import asyncio
import os
import sys
from claude_agent_sdk import query, ClaudeAgentOptions


async def test_bedrock_models():
    """Test different model IDs that AWS Bedrock supports."""
    print("=" * 70)
    print("AWS Bedrock Configuration Debug")
    print("=" * 70)

    # Check environment
    print("\n1. Environment Check:")
    use_bedrock = os.getenv("CLAUDE_SDK_USE_BEDROCK", "false").lower() == "true"
    aws_bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    print(f"   CLAUDE_SDK_USE_BEDROCK: {use_bedrock}")
    print(f"   AWS_REGION: {aws_region}")
    print(f"   AWS_BEARER_TOKEN_BEDROCK: {'Set ✅' if aws_bearer_token else 'Not set ❌'}")

    if not use_bedrock or not aws_bearer_token:
        print("\n❌ Bedrock not properly configured")
        return False

    # AWS Bedrock uses different model IDs than direct Anthropic API
    # Format: anthropic.claude-{model-version}
    test_models = [
        # Bedrock format model IDs
        ("anthropic.claude-3-5-haiku-20241022-v1:0", "Haiku 3.5 (Bedrock format)"),
        ("anthropic.claude-3-5-sonnet-20241022-v2:0", "Sonnet 3.5 (Bedrock format)"),
        ("anthropic.claude-3-haiku-20240307-v1:0", "Haiku 3 (Bedrock format)"),

        # Try direct Anthropic format (might work)
        ("claude-3-5-haiku-20241022", "Haiku 3.5 (Direct format)"),
        ("claude-3-haiku-20240307", "Haiku 3 (Direct format)"),

        # Original model IDs from code
        ("claude-haiku-4-5-20251001", "Haiku 4.5 (Original)"),
        ("claude-sonnet-4-5-20250929", "Sonnet 4.5 (Original)"),
    ]

    print("\n2. Testing Model IDs:")
    print("   AWS Bedrock uses format: anthropic.claude-{model}-{version}:{revision}")
    print()

    for model_id, description in test_models:
        print(f"\n   Testing: {description}")
        print(f"   Model ID: {model_id}")

        try:
            # Very simple prompt
            options = ClaudeAgentOptions(
                model=model_id,
                allowed_tools=[]  # No tools for speed
            )

            prompt = "Say 'OK'"

            print(f"   Querying with timeout=10s...")

            # Add timeout
            response_text = ""
            try:
                async with asyncio.timeout(10):
                    async for message in query(prompt=prompt, options=options):
                        response_text += str(message)

                print(f"   ✅ SUCCESS! Response: '{response_text.strip()}'")
                print(f"   ✅ Working model: {model_id}")
                return True

            except asyncio.TimeoutError:
                print(f"   ❌ Timeout (10s) - model may not be available")
                continue

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            continue

    print("\n" + "=" * 70)
    print("❌ No working model found")
    print("=" * 70)
    print("\nTroubleshooting:")
    print("1. Check AWS Bedrock console to see which models are enabled")
    print("2. Verify model access in your AWS account region")
    print("3. Try a different AWS region (set AWS_REGION)")
    print("4. Check bearer token permissions")

    return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_bedrock_models())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
