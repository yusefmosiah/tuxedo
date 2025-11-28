import sys
from dotenv import load_dotenv

# Load env before importing agent
load_dotenv()

from vibewriter.agent import VibewriterAgent

def test_choir_tools():
    print("Initializing Vibewriter Agent...")
    agent = VibewriterAgent()

    task = "List all my agent accounts."
    print(f"Task: {task}")

    try:
        print("Invoking agent...")
        result = agent.invoke(task, config={"recursion_limit": 20})

        print("Agent finished.")

        messages = result.get("messages", [])
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"Tool Call: {tool_call['name']} args={tool_call['args']}")
            if hasattr(msg, 'content') and msg.content:
                print(f"Message ({type(msg).__name__}): {msg.content[:200]}...")

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        agent.cleanup()

if __name__ == "__main__":
    test_choir_tools()
