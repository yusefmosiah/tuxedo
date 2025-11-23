
import asyncio
import json
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

# Add backend to path
import sys
sys.path.append("/Users/wiz/tuxedo/backend")

from agent.ghostwriter.verify import VerificationEngine

async def main():
    print("Setting up test environment...")
    test_dir = Path("/tmp/ghostwriter_verification_test")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)

    # Mock claims
    claims_data = {
        "claims": [
            {
                "claim": "Example Domain is for use in illustrative examples in documents.",
                "url": "https://example.com"
            },
            {
                "claim": "This claim should fail because the URL is invalid.",
                "url": "https://this-url-definitely-does-not-exist-12345.com"
            }
        ]
    }

    claims_path = test_dir / "claims.json"
    with open(claims_path, "w") as f:
        json.dump(claims_data, f)

    output_path = test_dir / "report.json"

    # Mock LLM to avoid API calls/costs during test
    # We just want to verify the engine logic (URL check, content fetch, orchestration)
    mock_llm = MagicMock()

    print("Initializing VerificationEngine...")
    engine = VerificationEngine(mock_llm, test_dir)

    # Mock verify_claim to avoid actual LLM call which would fail with MagicMock
    # We inject a side effect to simulate LLM response
    async def mock_verify_claim(claim, url, content):
        print(f"Mock verifying: {claim[:30]}...")
        return {
            "supported": True,
            "confidence": 0.9,
            "reasoning": "Mock verification"
        }

    engine.verify_claim = mock_verify_claim

    print("Running verification...")
    report = await engine.run_verification(claims_path, output_path)

    print("\nVerification Report:")
    print(json.dumps(report, indent=2))

    # Assertions
    assert report["total_claims"] == 2
    assert report["results"][0]["layers"]["url_check"]["accessible"] == True
    assert report["results"][0]["layers"]["content_fetch"]["success"] == True
    assert report["results"][0]["verified"] == True

    assert report["results"][1]["layers"]["url_check"]["accessible"] == False
    assert report["results"][1]["verified"] == False

    print("\nSUCCESS: Verification engine logic verified!")

if __name__ == "__main__":
    asyncio.run(main())
