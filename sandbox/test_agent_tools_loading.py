#!/usr/bin/env python3
"""
Test agent tools loading
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_agent_tools_loading():
    print("Testing agent tools loading...")

    try:
        # Import and initialize the agent system
        from agent.core import initialize_agent, agent_tools

        # Initialize the agent
        await initialize_agent()

        print(f"Total tools loaded: {len(agent_tools)}")

        for i, tool in enumerate(agent_tools, 1):
            print(f"{i}. Tool: {tool}")
            print(f"   Type: {type(tool)}")
            if hasattr(tool, 'name'):
                print(f"   Name: {tool.name}")
            if hasattr(tool, 'description'):
                desc = tool.description
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                print(f"   Description: {desc}")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_tools_loading())