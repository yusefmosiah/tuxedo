"""Simple test of Claude Agent SDK."""
import asyncio
from claude_agent_sdk import query

async def test_simple():
    """Test basic Claude SDK query."""
    print("Testing simple Claude SDK query...")

    prompt = "What is 2+2? Answer briefly."

    response_text = ""
    async for message in query(prompt=prompt):
        print(f"Message type: {type(message)}")
        print(f"Message: {message}")
        response_text += str(message)

    print(f"\nFinal response: {response_text}")
    return response_text

if __name__ == "__main__":
    result = asyncio.run(test_simple())
    print(f"\nTest completed. Result: {result}")
