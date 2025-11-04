#!/usr/bin/env python3
"""
Debug agent tools loading issue
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def debug_agent_tools():
    print("=== Debugging Agent Tools Loading ===")

    try:
        # Import the tools directly to test
        from defindex_tools import discover_high_yield_vaults, get_defindex_vault_details, prepare_defindex_deposit
        print(f"✅ Direct import successful:")
        print(f"  discover_high_yield_vaults: {discover_high_yield_vaults}")
        print(f"  get_defindex_vault_details: {get_defindex_vault_details}")
        print(f"  prepare_defindex_deposit: {prepare_defindex_deposit}")

        # Now test agent core loading
        from agent.core import initialize_agent, agent_tools
        await initialize_agent()

        print(f"\n✅ Agent initialized successfully")
        print(f"📊 Agent tools count: {len(agent_tools)}")

        # Debug each tool
        for i, tool in enumerate(agent_tools, 1):
            print(f"\n{i}. Tool Analysis:")
            print(f"   Object: {tool}")
            print(f"   Type: {type(tool)}")
            print(f"   Has name attr: {hasattr(tool, 'name')}")
            if hasattr(tool, 'name'):
                print(f"   Name: {tool.name}")
            print(f"   Has func attr: {hasattr(tool, 'func')}")
            if hasattr(tool, 'func'):
                print(f"   Func: {tool.func}")
            print(f"   Has coroutine attr: {hasattr(tool, 'coroutine')}")
            if hasattr(tool, 'coroutine'):
                print(f"   Coroutine: {tool.coroutine}")

        # Test tool finding logic (mimic agent core)
        print(f"\n🔍 Testing tool finding logic:")
        tool_name_to_find = "discover_high_yield_vaults"
        tool_func = None
        for t in agent_tools:
            if hasattr(t, 'name') and t.name == tool_name_to_find:
                tool_func = t
                break

        print(f"Looking for tool: {tool_name_to_find}")
        print(f"Found tool_func: {tool_func}")

        # Test execution if found
        if tool_func:
            print(f"✅ Tool found! Testing execution...")
            try:
                # Test proper LangChain execution
                if hasattr(tool_func, 'ainvoke'):
                    result = await tool_func.ainvoke({'min_apy': 25.0})
                    print(f"✅ Execution successful! Result length: {len(result)}")
                else:
                    print(f"❌ Tool doesn't have ainvoke method")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Tool not found in agent_tools!")

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent_tools())