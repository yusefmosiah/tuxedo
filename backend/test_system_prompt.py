#!/usr/bin/env python3
"""
Test the system prompt to verify mainnet messaging
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_system_prompt():
    """Test the system prompt content"""
    from agent.core import build_agent_system_prompt, import_agent_account_if_exists

    print("=" * 60)
    print("SYSTEM PROMPT TEST")
    print("=" * 60)

    # Import agent account if exists
    await import_agent_account_if_exists()

    # Build system prompt
    prompt = build_agent_system_prompt()

    print("\nSYSTEM PROMPT:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)

    # Check for testnet references
    if "testnet" in prompt.lower():
        print("\n❌ ISSUE: Prompt contains 'testnet' references!")
        lines = prompt.split("\n")
        for i, line in enumerate(lines, 1):
            if "testnet" in line.lower():
                print(f"   Line {i}: {line.strip()}")
    else:
        print("\n✅ No 'testnet' references found in prompt")

    # Check for mainnet references
    if "mainnet" in prompt.lower():
        print("\n✅ Prompt contains 'mainnet' references")
        lines = prompt.split("\n")
        for i, line in enumerate(lines, 1):
            if "mainnet" in line.lower():
                print(f"   Line {i}: {line.strip()}")
    else:
        print("\n❌ WARNING: No 'mainnet' references found in prompt")

if __name__ == "__main__":
    asyncio.run(test_system_prompt())
