#!/usr/bin/env python3
"""
Test script to verify that Stellar tool factory generates proper JSON schemas.

Updated for Quantum Leap migration: Uses tool_factory instead of deprecated wrappers.
"""

import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_schema_generation():
    """Test that all tool factory tools generate JSON-serializable schemas"""

    try:
        # Use new tool_factory instead of deprecated wrappers
        from agent.tool_factory import create_user_tools

        # Create tools for a test user
        test_user_id = "test_user_schema_validation"
        tools_list = create_user_tools(test_user_id)

        # Extract tool names from tool objects
        tools = [(getattr(t, 'name', f'Tool {i}'), t) for i, t in enumerate(tools_list)]

        print(f"Testing schema generation for {len(tools)} Stellar tools from tool_factory...")
        print("=" * 60)
        print(f"Using test user_id: {test_user_id}")
        print("=" * 60)

        all_passed = True

        for tool_name, tool in tools:
            try:
                # Get the schema
                schema = tool.args_schema
                print(f"\n✅ {tool_name}: Schema generated successfully")

                # Test JSON serialization
                try:
                    schema_json = json.dumps(schema, default=str)
                    print(f"   Schema is JSON serializable")
                    print(f"   Schema size: {len(schema_json)} characters")
                except Exception as json_error:
                    print(f"   ❌ Schema JSON serialization failed: {json_error}")
                    all_passed = False

                # Test schema structure
                if hasattr(schema, 'properties'):
                    prop_count = len(schema.properties) if schema.properties else 0
                    print(f"   Properties count: {prop_count}")
                    if prop_count > 0:
                        print(f"   Properties: {list(schema.properties.keys())}")

                # Test LangChain tool name
                if hasattr(tool, 'name'):
                    print(f"   Tool name: {tool.name}")
                else:
                    print(f"   Tool name: {tool_name}")

            except Exception as e:
                print(f"\n❌ {tool_name}: Schema generation failed: {e}")
                all_passed = False

        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 All tools generate valid JSON schemas!")
            return True
        else:
            print("❌ Some tools have schema issues")
            return False

    except ImportError as e:
        print(f"❌ Failed to import tool wrappers: {e}")
        return False

def test_openai_function_conversion():
    """Test conversion to OpenAI function format"""

    try:
        from langchain_core.utils.function_calling import convert_to_openai_function
        from agent.stellar_tools_wrappers import stellar_utilities

        print("\nTesting OpenAI function conversion...")
        print("=" * 60)

        # Test with a simple tool first
        tool = stellar_utilities
        openai_schema = convert_to_openai_function(tool)

        print(f"✅ stellar_utilities converted to OpenAI format")
        print(f"   Function name: {openai_schema.get('name', 'N/A')}")
        print(f"   Description length: {len(openai_schema.get('description', ''))}")

        if 'parameters' in openai_schema:
            params = openai_schema['parameters']
            print(f"   Parameters type: {params.get('type', 'N/A')}")
            if 'properties' in params:
                print(f"   Parameter count: {len(params['properties'])}")

        # Test JSON serialization of OpenAI schema
        try:
            schema_json = json.dumps(openai_schema, default=str)
            print(f"   OpenAI schema is JSON serializable")
        except Exception as e:
            print(f"   ❌ OpenAI schema JSON serialization failed: {e}")
            return False

        print("🎉 OpenAI function conversion works!")
        return True

    except Exception as e:
        print(f"❌ OpenAI function conversion failed: {e}")
        return False

def main():
    """Run all schema tests"""

    print("Stellar Tools Schema Validation Test")
    print("=" * 60)

    # Test basic schema generation
    schema_test_passed = test_schema_generation()

    # Test OpenAI function conversion
    openai_test_passed = test_openai_function_conversion()

    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Schema Generation: {'✅ PASSED' if schema_test_passed else '❌ FAILED'}")
    print(f"OpenAI Conversion: {'✅ PASSED' if openai_test_passed else '❌ FAILED'}")

    if schema_test_passed and openai_test_passed:
        print("\n🎉 All tests passed! The tools should work with LangChain.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())