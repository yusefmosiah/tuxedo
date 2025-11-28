import sys
from dotenv import load_dotenv

# Load env before importing agent
load_dotenv()

from vibewriter.agent import VibewriterAgent

def test_tools():
    print("Initializing Vibewriter Agent...")
    agent = VibewriterAgent()

    # Task that requires using multiple tools
    task = (
        "Research 'Choir Protocol' using the KB, then search the web for 'latest crypto trends 2025'. "
        "Write a short summary combining both, cite a source, and publish it to Choir with title 'Future of Choir'."
    )
    print(f"Task: {task}")

    try:
        print("Invoking agent...")
        result = agent.invoke(task, config={"recursion_limit": 50})

        print("Agent finished.")
        # We can inspect the messages to see tool calls if we want,
        # but for now just successful completion is a good sign.

        # Print tool calls
        messages = result.get("messages", [])
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"Tool Call: {tool_call['name']} args={tool_call['args']}")
            if hasattr(msg, 'content') and msg.content:
                print(f"Message ({type(msg).__name__}): {msg.content[:100]}...")

        if messages:
            last_msg = messages[-1]
            print("Final Response:")
            print(last_msg.content)

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        agent.cleanup()

if __name__ == "__main__":
    test_tools()
