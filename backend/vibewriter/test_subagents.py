import sys
from dotenv import load_dotenv

# Load env before importing agent
load_dotenv()

from vibewriter.agent import VibewriterAgent

def test_subagents():
    print("Initializing Vibewriter Agent with Subagents...")
    agent = VibewriterAgent()

    task = (
        "Use your Researcher agent to find the current price of Bitcoin. "
        "Then use your Writer agent to draft a short tweet about it and publish it to Choir."
    )
    print(f"Task: {task}")

    try:
        print("Invoking agent...")
        # Increase recursion limit as subagent calls add steps
        result = agent.invoke(task, config={"recursion_limit": 50})

        print("Agent finished.")

        # Print tool calls and subagent interactions
        messages = result.get("messages", [])
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"Tool Call: {tool_call['name']} args={tool_call['args']}")
            if hasattr(msg, 'content') and msg.content:
                # Truncate long content
                content = msg.content
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"Message ({type(msg).__name__}): {content}")

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        agent.cleanup()

if __name__ == "__main__":
    test_subagents()
