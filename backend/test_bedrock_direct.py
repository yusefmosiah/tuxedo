#!/usr/bin/env python3
"""
Test AWS Bedrock directly without Claude SDK to isolate the issue.
"""

import os
import json
import requests


def test_bedrock_direct():
    """Test AWS Bedrock API directly using HTTP."""
    print("=" * 70)
    print("Direct AWS Bedrock API Test")
    print("=" * 70)

    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bearer_token:
        print("\n❌ AWS_BEARER_TOKEN_BEDROCK not set")
        return False

    print(f"\n1. Configuration:")
    print(f"   Region: {region}")
    print(f"   Bearer Token: {bearer_token[:20]}...")

    # AWS Bedrock endpoint
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    endpoint = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/invoke"

    print(f"\n2. Testing endpoint:")
    print(f"   URL: {endpoint}")
    print(f"   Model: {model_id}")

    # Prepare request
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "Say 'OK'"
            }
        ]
    }

    print(f"\n3. Sending request...")
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=10
        )

        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print(f"\n✅ SUCCESS!")
            print(f"   Response: {response.text[:200]}")
            return True
        else:
            print(f"\n❌ API Error:")
            print(f"   Response: {response.text}")
            return False

    except requests.Timeout:
        print(f"\n❌ Request timeout (10s)")
        print(f"   This suggests network connectivity issues")
        return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bearer_token_format():
    """Check if bearer token is in correct format."""
    print("\n" + "=" * 70)
    print("Bearer Token Format Check")
    print("=" * 70)

    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

    if not bearer_token:
        print("\n❌ No token found")
        return False

    print(f"\n   Token length: {len(bearer_token)}")
    print(f"   Token prefix: {bearer_token[:20]}...")
    print(f"   Token suffix: ...{bearer_token[-20:]}")

    # Check if it's base64 encoded
    import base64
    try:
        decoded = base64.b64decode(bearer_token)
        print(f"   ✅ Token appears to be base64 encoded")
        print(f"   Decoded length: {len(decoded)}")
    except Exception:
        print(f"   ℹ️  Token is not base64 encoded (may be fine)")

    return True


if __name__ == "__main__":
    test_bearer_token_format()
    success = test_bedrock_direct()

    print("\n" + "=" * 70)
    if success:
        print("✅ Direct API access works!")
        print("   Issue is likely with Claude Agent SDK's Bedrock integration")
    else:
        print("❌ Direct API access failed")
        print("   Check:")
        print("   1. Bearer token has Bedrock permissions")
        print("   2. Model is enabled in AWS Bedrock console")
        print("   3. Region is correct (currently: {})".format(os.getenv("AWS_REGION", "us-east-1")))
        print("   4. Network can reach AWS Bedrock endpoints")
    print("=" * 70)
