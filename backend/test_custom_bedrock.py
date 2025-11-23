#!/usr/bin/env python3
"""Test custom Bedrock client."""

import asyncio
import sys
sys.path.insert(0, '/home/user/tuxedo/backend')

from agent.ghostwriter.bedrock_client import BedrockClient, BEDROCK_MODEL_HAIKU


async def test_custom_client():
    """Test the custom Bedrock client."""
    print("=" * 60)
    print("Custom Bedrock Client Test")
    print("=" * 60)

    try:
        # Initialize client
        print("\n1. Initializing client...")
        client = BedrockClient()
        print("   ✅ Client initialized")

        # Test simple query
        print("\n2. Testing simple query with Haiku...")
        response = await client.query_simple(
            prompt="Say 'Hello from Bedrock!'",
            model_id=BEDROCK_MODEL_HAIKU,
            max_tokens=100
        )

        print(f"   ✅ Response received: '{response}'")

        print("\n" + "=" * 60)
        print("✅ CUSTOM CLIENT WORKS!")
        print("=" * 60)
        print("\nThis custom client bypasses the buggy Claude Agent SDK")
        print("and makes direct HTTP calls to Bedrock, which work perfectly.")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_custom_client())
    sys.exit(0 if success else 1)
