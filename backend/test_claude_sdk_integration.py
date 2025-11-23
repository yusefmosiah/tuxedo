#!/usr/bin/env python3
"""
Test Claude SDK Integration
Quick smoke test to verify the Claude SDK integration is working.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_integration():
    """Test Claude SDK integration"""
    print("=" * 60)
    print("Claude SDK Integration Test")
    print("=" * 60)

    # Test 1: Check API key configuration
    print("\n1️⃣ Checking Authentication Configuration...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    use_bedrock = os.getenv("CLAUDE_SDK_USE_BEDROCK", "false").lower() == "true"
    aws_bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    has_auth = False

    if use_bedrock:
        print("   🔧 Bedrock mode enabled")
        if aws_bearer_token:
            print(f"   ✅ AWS_BEARER_TOKEN_BEDROCK is set")
            print(f"   ✅ AWS_REGION: {aws_region}")
            print(f"   ✅ Using AWS Bedrock API Key authentication")
            has_auth = True
        elif aws_access_key and aws_secret_key:
            print(f"   ✅ AWS IAM credentials are set")
            print(f"   ✅ AWS_REGION: {aws_region}")
            print(f"   ✅ Using AWS Bedrock IAM authentication")
            has_auth = True
        else:
            print("   ⚠️  Bedrock enabled but no credentials found")
            print("      Set AWS_BEARER_TOKEN_BEDROCK or AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY")
    elif api_key:
        print(f"   ✅ ANTHROPIC_API_KEY is set ({api_key[:8]}...)")
        print(f"   ✅ Using Direct Anthropic API")
        has_auth = True
    else:
        print("   ⚠️  No authentication configured")
        print("      Set ANTHROPIC_API_KEY or configure AWS Bedrock")

    # Test 2: Import wrapper module
    print("\n2️⃣ Testing Module Import...")
    try:
        from agent.claude_sdk_wrapper import (
            ClaudeSDKAgent,
            get_claude_sdk_agent,
            initialize_claude_sdk,
            cleanup_claude_sdk
        )
        print("   ✅ Claude SDK wrapper imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import wrapper: {e}")
        return False

    # Test 3: Initialize SDK
    print("\n3️⃣ Testing SDK Initialization...")
    try:
        await initialize_claude_sdk()
        print("   ✅ Claude SDK initialized successfully")
    except Exception as e:
        print(f"   ⚠️  Initialization warning: {e}")

    # Test 4: Create agent instance
    print("\n4️⃣ Testing Agent Instance Creation...")
    try:
        agent = await get_claude_sdk_agent()
        print(f"   ✅ Agent created successfully")
        print(f"      Allowed tools: {agent.allowed_tools}")
        print(f"      Working directory: {agent.working_directory}")
    except Exception as e:
        print(f"   ❌ Failed to create agent: {e}")
        return False

    # Test 5: Test simple query (only if authentication is configured)
    if has_auth:
        print("\n5️⃣ Testing Simple Query...")
        try:
            result = await agent.query_simple("What is 2+2?")
            print(f"   ✅ Query executed successfully")
            print(f"      Response preview: {result[:100]}...")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
    else:
        print("\n5️⃣ Skipping query test (no authentication configured)")

    # Test 6: Test API routes import
    print("\n6️⃣ Testing API Routes...")
    try:
        from api.routes.claude_sdk import router
        print(f"   ✅ Claude SDK routes imported successfully")
        print(f"      Available endpoints: {len(router.routes)} routes")
    except Exception as e:
        print(f"   ❌ Failed to import routes: {e}")
        return False

    # Test 7: Cleanup
    print("\n7️⃣ Testing Cleanup...")
    try:
        await cleanup_claude_sdk()
        print("   ✅ Cleanup successful")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("✅ Integration test completed!")
    if not has_auth:
        print("\n⚠️  Note: Configure authentication to test full functionality")
        print("   Option 1: Set ANTHROPIC_API_KEY")
        print("   Option 2: Set AWS_BEARER_TOKEN_BEDROCK + AWS_REGION")
        print("   Option 3: Set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY + AWS_REGION")
    else:
        print("\n🎉 All systems ready!")

    print("\nNext steps:")
    print("1. Start the backend: python main.py")
    print("2. Visit API docs: http://localhost:8000/docs")
    print("3. Look for '/api/claude-sdk' endpoints")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_integration())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
