import sys
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage
from vibewriter.agent import VibewriterAgent

def test_ghostwriter():
    print("Initializing Vibewriter Agent...")
    agent = VibewriterAgent()

    task = "Use your Ghostwriter agent to form hypotheses about 'The Future of DeFi on Stellar'. Then save the hypotheses to a file named '/home/user/hypotheses.json'."
    print(f"Task: {task}")

    try:
        print("Streaming agent execution...")
        messages = []
        for chunk in agent.graph.stream(
            {"messages": [HumanMessage(content=task)]},
            config={"recursion_limit": 100}
        ):
            print(f"DEBUG: Chunk keys: {list(chunk.keys())}")
            if "agent" in chunk:
                print(f"--- Agent Step ---")
                for msg in chunk["agent"]["messages"]:
                    print(f"Message ({type(msg).__name__}): {msg.content[:200]}...")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            print(f"Tool Call: {tool_call['name']} args={tool_call['args']}")
            elif "tools" in chunk:
                print(f"--- Tool Step ---")
                for msg in chunk["tools"]["messages"]:
                    print(f"Tool Output ({msg.name}): {msg.content[:200]}...")

            # Accumulate messages for final verification if needed (though stream gives chunks)
            # In a real app we'd maintain state, here we just watch the stream.

        # Verify file creation
        print("\nVerifying file creation...")
        file_content = agent.backend.read("/home/user/hypotheses.json")
        if "Error" not in file_content:
            print("File '/home/user/hypotheses.json' created successfully.")
            print("Content preview:", file_content[:200])
        else:
            print("File '/home/user/hypotheses.json' not found or error reading it.")
            print(file_content)

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        agent.cleanup()

if __name__ == "__main__":
    test_ghostwriter()
