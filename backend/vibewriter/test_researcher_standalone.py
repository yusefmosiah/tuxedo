import os
import sys
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware

load_dotenv()

from vibewriter.subagents.researcher import get_researcher_agent

def test_researcher_standalone():
    print("Testing Researcher Agent Standalone...")

    # Setup model
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    model = ChatOpenAI(
        model="anthropic/claude-3.5-sonnet",
        api_key=api_key,
        base_url=base_url
    )

    # Get agent config
    agent_config = get_researcher_agent()

    # Create agent
    agent = create_agent(
        model,
        system_prompt=agent_config["system_prompt"],
        tools=agent_config["tools"],
        middleware=[PatchToolCallsMiddleware()], # Add middleware if needed
    )

    task = "Find the current price of Bitcoin."
    print(f"Task: {task}")

    try:
        result = agent.invoke({"messages": [HumanMessage(content=task)]})
        print("Result:")
        for msg in result["messages"]:
             if hasattr(msg, 'content') and msg.content:
                print(f"{type(msg).__name__}: {msg.content}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_researcher_standalone()
