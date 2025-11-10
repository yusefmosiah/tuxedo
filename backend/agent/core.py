"""
Agent Core System
Main AI agent logic and lifecycle management.
"""

import asyncio
import os
import json
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

# Import settings
from config.settings import settings

logger = logging.getLogger(__name__)

# Global agent state
llm = None
agent_tools = []

async def initialize_agent():
    """Initialize the AI agent system"""
    global llm, agent_tools

    try:
        # Initialize LLM
        try:
            llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                model=settings.primary_model,
                temperature=0.7,
                max_tokens=2000,
            )
            logger.info("LLM initialized successfully")
        except Exception as llm_error:
            logger.warning(f"LLM initialization failed: {llm_error}")
            logger.info("Continuing without LLM - agent features will be limited")

        # Initialize agent tools
        await load_agent_tools()

        # Import agent account secret if provided
        await import_agent_account_if_exists()

        logger.info("Agent system initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

async def cleanup_agent():
    """Cleanup agent resources"""
    global llm, agent_tools

    llm = None
    agent_tools = []
    logger.info("Agent system cleaned up")

async def import_agent_account_if_exists():
    """
    Import AGENT_STELLAR_SECRET from environment if it exists.
    This allows the agent to have a pre-funded account ready to use.
    """
    agent_secret = os.getenv("AGENT_STELLAR_SECRET")

    if not agent_secret:
        logger.info("No AGENT_STELLAR_SECRET found - agent will create accounts as needed")
        return

    try:
        from account_manager import AccountManager
        from stellar_sdk import Keypair

        # Parse the secret key to get the public key
        keypair = Keypair.from_secret(agent_secret)
        public_key = keypair.public_key

        # Use a system user ID for the agent's own account
        system_user_id = "system_agent"

        account_manager = AccountManager()

        # Check if this account is already imported
        existing_accounts = account_manager.get_user_accounts(
            user_id=system_user_id,
            chain="stellar"
        )

        already_imported = any(
            acc.get("public_key") == public_key
            for acc in existing_accounts
        )

        if already_imported:
            logger.info(f"Agent account {public_key[:8]}... already imported")
            return

        # Import the account
        result = account_manager.import_account(
            user_id=system_user_id,
            chain="stellar",
            private_key=agent_secret,
            name="System Agent Account",
            network="mainnet",
            metadata={
                "type": "agent",
                "source": "environment",
                "network": "mainnet"
            }
        )

        if result.get("success"):
            logger.info(f"✅ Agent account imported successfully: {result['address']}")
            logger.info(f"   Account ID: {result['account_id']}")
        else:
            logger.error(f"❌ Failed to import agent account: {result.get('error')}")

    except Exception as e:
        logger.error(f"Error importing agent account secret: {e}")

async def load_agent_tools():
    """
    Load global agent tools (for backward compatibility).

    NOTE: New code should use per-request tools via tool_factory.create_user_tools()
    for proper user isolation. Global tools are only loaded as fallback for
    routes that don't yet use the new pattern.
    """
    global agent_tools

    agent_tools = []

    # REMOVED: Anonymous tools fallback - all users must be authenticated
    # Stellar tools are now created per-request in chat endpoints
    logger.info("Agent system initialized - tools will be created per-request for authenticated users")

    # Import agent account management tools
    try:
        from agent.tools import agent_create_account, agent_list_accounts, agent_get_account_info
        agent_tools.extend([
            agent_create_account,
            agent_list_accounts,
            agent_get_account_info
        ])
        logger.info("Agent account management tools loaded successfully")
    except ImportError as e:
        logger.warning(f"Agent account management tools not available: {e}")

    # NOTE: Blend Capital and other protocol tools are loaded via tool_factory pattern
    # This ensures proper user_id injection and AccountManager integration
    # See agent/tool_factory.py for the implementation
    logger.info("Protocol tools (Blend Capital) loaded via tool_factory pattern with user_id injection")

async def get_agent_status() -> Dict[str, Any]:
    """Get current agent system status"""
    # Debug environment variables (remove sensitive data)
    api_key = settings.openai_api_key
    api_key_debug = f"{api_key[:8]}...{api_key[-8:]}" if api_key and len(api_key) > 16 else "EMPTY_OR_TOO_SHORT"

    logger.info(f"Health check debug - API key: {api_key_debug}, Base URL: {settings.openai_base_url}, Model: {settings.primary_model}")

    return {
        "status": "healthy",
        "llm_configured": llm is not None,
        "tools_count": len(agent_tools),
        "tools_available": [getattr(t, 'name', getattr(t, '__name__', str(t))) for t in agent_tools],
        "agent_account_tools_available": any(
            getattr(t, 'name', getattr(t, '__name__', str(t))) in ["agent_create_account", "agent_list_accounts", "agent_get_account_info"]
            for t in agent_tools
        ),
        "stellar_tools_ready": len(agent_tools) > 0,
        "openai_configured": bool(settings.openai_api_key),
        "live_summary_ready": True,  # TODO: Make this configurable based on actual availability
        "database_ready": True,  # TODO: Check actual database connectivity
        "blend_tools_ready": len([t for t in agent_tools if 'blend' in getattr(t, 'name', getattr(t, '__name__', str(t))).lower()]) > 0,
        # Debug fields (remove these in production)
        "debug_api_key_prefix": api_key_debug,
        "debug_base_url": settings.openai_base_url,
        "debug_model": settings.primary_model
    }

async def process_agent_message_streaming(
    message: str,
    history: List[Dict[str, str]],
    agent_account: Optional[str] = None,
    tools: Optional[List] = None
):
    """
    Process a user message through the AI agent with multi-step reasoning and streaming output.

    Args:
        message: User message
        history: Conversation history
        agent_account: Active agent account address
        tools: List of LangChain tools (if None, uses global agent_tools)

    Yields dictionaries representing different stages of the agent execution.
    """
    if not llm:
        yield {
            "type": "error",
            "content": "Agent not initialized",
            "iteration": 0
        }
        return

    # Use provided tools or fall back to global agent_tools
    active_tools = tools if tools is not None else agent_tools

    try:
        # Build system prompt
        system_prompt = build_agent_system_prompt()

        # Build message history
        messages = [SystemMessage(content=system_prompt)]

        # Add agent account context if available
        if agent_account:
            agent_context = build_agent_context(agent_account)
            messages.append(SystemMessage(content=agent_context))

        # Add conversation history
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=message))

        # Convert tools to OpenAI format
        from langchain_core.utils.function_calling import convert_to_openai_function
        tool_schemas = [convert_to_openai_function(t) for t in active_tools]
        tools_formatted = [{"type": "function", "function": schema} for schema in tool_schemas]

        # Create LLM with tools
        llm_with_tools = llm.bind(tools=tools_formatted)

        # Agent loop with multi-step reasoning and streaming
        max_iterations = 25
        iteration = 0

        yield {
            "type": "agent_start",
            "content": f"🚀 Starting AI agent with {len(active_tools)} tools available...",
            "iteration": 0,
            "tools_available": len(active_tools),
            "max_iterations": max_iterations
        }

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            yield {
                "type": "iteration_start",
                "content": f"🤔 Thinking... (iteration {iteration}/{max_iterations})",
                "iteration": iteration,
                "max_iterations": max_iterations,
                "progress": round((iteration - 1) / max_iterations * 100, 0)
            }

            # Get LLM response with potential tool calls
            response = await llm_with_tools.ainvoke(messages)

            # Add response to message history
            messages.append(response)

            # Check if LLM wants to call tools (handle both new and old LangChain formats)
            tool_calls = []

            # New LangChain format
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = response.tool_calls
                logger.info(f"LLM wants to call {len(tool_calls)} tools (new format)")
            # Old LangChain format with function_call in additional_kwargs
            elif (hasattr(response, 'additional_kwargs') and
                  response.additional_kwargs.get('function_call')):
                function_call = response.additional_kwargs['function_call']
                tool_calls = [{
                    "name": function_call["name"],
                    "args": json.loads(function_call["arguments"]),
                    "id": f"call_{function_call['name']}"
                }]
                logger.info(f"LLM wants to call {len(tool_calls)} tools (old format)")

            if response.content and response.content.strip():
                # Yield AI thinking/response
                yield {
                    "type": "llm_response",
                    "content": response.content,
                    "iteration": iteration,
                    "isStreaming": False
                }

            if tool_calls:
                # Execute each tool call with streaming feedback
                for tool_call in tool_calls:
                    tool_name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
                    tool_args = tool_call.get("args") if isinstance(tool_call, dict) else tool_call.args
                    tool_id = tool_call.get("id") if isinstance(tool_call, dict) else getattr(tool_call, 'id', f"call_{tool_name}")

                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                    # Find and execute the tool
                    tool_func = None
                    logger.info(f"Looking for tool '{tool_name}' among {len(active_tools)} tools")
                    for i, t in enumerate(active_tools):
                        tool_name_attr = getattr(t, 'name', 'NO_NAME')
                        logger.info(f"  Tool {i}: '{tool_name_attr}' == '{tool_name}'? {tool_name_attr == tool_name}")
                        if tool_name_attr == tool_name:
                            tool_func = t
                            logger.info(f"✅ Found tool: {tool_func}")
                            break

                    if tool_func is None:
                        logger.error(f"❌ Tool '{tool_name}' not found! Available tools: {[getattr(t, 'name', 'NO_NAME') for t in active_tools]}")

                    yield {
                        "type": "tool_call_start",
                        "content": f"🔧 Executing {tool_name}...",
                        "tool_name": tool_name,
                        "iteration": iteration,
                        "tools_remaining": len(tool_calls) - tool_calls.index(tool_call)
                    }

                    if tool_func:
                        try:
                            # Execute tool function - handle different tool types using LangChain v2+ patterns
                            result = None

                            # Modern LangChain v2+ tool execution patterns
                            if hasattr(tool_func, 'ainvoke') and callable(tool_func.ainvoke):
                                # Modern LangChain async tool - use ainvoke with structured input
                                logger.info(f"Using ainvoke for tool {tool_name}")
                                result = await tool_func.ainvoke(tool_args)
                            elif hasattr(tool_func, 'invoke') and callable(tool_func.invoke):
                                # Modern LangChain sync tool - use invoke with structured input
                                logger.info(f"Using invoke for tool {tool_name}")
                                result = tool_func.invoke(tool_args)
                            elif hasattr(tool_func, '_run') and callable(tool_func._run):
                                # Tool with _run method (legacy pattern)
                                logger.info(f"Using _run for tool {tool_name}")
                                if asyncio.iscoroutinefunction(tool_func._run):
                                    result = await tool_func._run(**tool_args)
                                else:
                                    result = tool_func._run(**tool_args)
                            elif asyncio.iscoroutinefunction(tool_func):
                                # Direct async function (decorated functions)
                                logger.info(f"Using direct async call for tool {tool_name}")
                                result = await tool_func(**tool_args)
                            elif callable(tool_func):
                                # Regular callable function
                                logger.info(f"Using direct call for tool {tool_name}")
                                result = tool_func(**tool_args)
                            else:
                                raise ValueError(f"Cannot determine how to execute tool {tool_name}. Tool attributes: {dir(tool_func)}")

                            logger.info(f"Tool {tool_name} executed successfully")

                            # Yield tool result
                            yield {
                                "type": "tool_result",
                                "content": str(result),
                                "tool_name": tool_name,
                                "iteration": iteration,
                                "success": True
                            }

                            # Add tool result to message history for next iteration
                            tool_message = {
                                "role": "tool",
                                "content": str(result),
                                "tool_call_id": tool_id,
                                "name": tool_name
                            }
                            messages.append(tool_message)

                        except Exception as tool_error:
                            logger.error(f"Error executing tool {tool_name}: {tool_error}")

                            # Yield tool error
                            yield {
                                "type": "tool_error",
                                "content": f"Error in {tool_name}: {str(tool_error)}",
                                "tool_name": tool_name,
                                "iteration": iteration,
                                "success": False
                            }

                            # Add tool error to message history for next iteration
                            tool_message = {
                                "role": "tool",
                                "content": f"Error: {str(tool_error)}",
                                "tool_call_id": tool_id,
                                "name": tool_name
                            }
                            messages.append(tool_message)
                    else:
                        logger.error(f"Tool {tool_name} not found")

                        # Yield tool not found error
                        yield {
                            "type": "tool_error",
                            "content": f"Tool {tool_name} not found",
                            "tool_name": tool_name,
                            "iteration": iteration,
                            "success": False
                        }

                        # Add tool not found error to message history
                        tool_message = {
                            "role": "tool",
                            "content": f"Error: Tool {tool_name} not found",
                            "tool_call_id": tool_id,
                            "name": tool_name
                        }
                        messages.append(tool_message)

            else:
                # No more tool calls, exit loop
                logger.info(f"No more tool calls requested, ending loop after {iteration} iterations")
                break

        else:
            # Max iterations reached
            logger.warning(f"Agent reached maximum iterations ({max_iterations}) without completion")
            yield {
                "type": "warning",
                "content": f"⚠️ Reached maximum iterations ({max_iterations}) without completion",
                "iteration": iteration,
                "max_iterations_reached": True
            }

        # Extract final response (last AI message that's not a tool call)
        final_response = "I'm sorry, I couldn't complete your request."
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content and not hasattr(msg, 'tool_call_id'):
                final_response = msg.content
                break

        yield {
            "type": "agent_complete",
            "content": f"✅ Completed in {iteration} iterations!\n\n{final_response}",
            "iteration": iteration,
            "iterations_used": iteration,
            "success": True,
            "agent_account": agent_account,
            "final_response": final_response
        }

    except Exception as e:
        logger.error(f"Error processing agent message: {e}")
        yield {
            "type": "error",
            "content": f"Error processing your request: {str(e)}",
            "iteration": iteration if 'iteration' in locals() else 0,
            "success": False,
            "error": str(e)
        }


async def process_agent_message(
    message: str,
    history: List[Dict[str, str]],
    agent_account: Optional[str] = None,
    tools: Optional[List] = None
) -> Dict[str, Any]:
    """
    Process a user message through the AI agent with multi-step reasoning.

    Args:
        message: User message
        history: Conversation history
        agent_account: Active agent account address
        tools: List of LangChain tools (if None, uses global agent_tools)

    Returns:
        Agent response with metadata
    """
    if not llm:
        raise Exception("Agent not initialized")

    # Use provided tools or fall back to global agent_tools
    active_tools = tools if tools is not None else agent_tools

    try:
        # Auto-select agent account if not provided
        if not agent_account:
            agent_account = get_default_agent_account()

        # Build system prompt
        system_prompt = build_agent_system_prompt()

        # Build message history
        messages = [SystemMessage(content=system_prompt)]

        # Add agent account context if available
        if agent_account:
            agent_context = build_agent_context(agent_account)
            messages.append(SystemMessage(content=agent_context))

        # Add conversation history
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=message))

        # Convert tools to OpenAI format
        from langchain_core.utils.function_calling import convert_to_openai_function
        tool_schemas = [convert_to_openai_function(t) for t in active_tools]
        tools_formatted = [{"type": "function", "function": schema} for schema in tool_schemas]

        # Create LLM with tools
        llm_with_tools = llm.bind(tools=tools_formatted)

        # Agent loop with multi-step reasoning
        max_iterations = 25
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            # Get LLM response with potential tool calls
            response = await llm_with_tools.ainvoke(messages)

            # Add response to message history
            messages.append(response)

            # Check if LLM wants to call tools (handle both new and old LangChain formats)
            tool_calls = []

            # New LangChain format
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = response.tool_calls
                logger.info(f"LLM wants to call {len(tool_calls)} tools (new format)")
            # Old LangChain format with function_call in additional_kwargs
            elif (hasattr(response, 'additional_kwargs') and
                  response.additional_kwargs.get('function_call')):
                function_call = response.additional_kwargs['function_call']
                tool_calls = [{
                    "name": function_call["name"],
                    "args": json.loads(function_call["arguments"]),
                    "id": f"call_{function_call['name']}"
                }]
                logger.info(f"LLM wants to call {len(tool_calls)} tools (old format)")

            if tool_calls:
                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
                    tool_args = tool_call.get("args") if isinstance(tool_call, dict) else tool_call.args
                    tool_id = tool_call.get("id") if isinstance(tool_call, dict) else getattr(tool_call, 'id', f"call_{tool_name}")

                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                    # Find and execute the tool
                    tool_func = None
                    logger.info(f"[NON-STREAMING] Looking for tool '{tool_name}' among {len(active_tools)} tools")
                    for i, t in enumerate(active_tools):
                        tool_name_attr = getattr(t, 'name', 'NO_NAME')
                        logger.info(f"  [NON-STREAMING] Tool {i}: '{tool_name_attr}' == '{tool_name}'? {tool_name_attr == tool_name}")
                        if tool_name_attr == tool_name:
                            tool_func = t
                            logger.info(f"✅ [NON-STREAMING] Found tool: {tool_func}")
                            break

                    if tool_func is None:
                        logger.error(f"❌ [NON-STREAMING] Tool '{tool_name}' not found! Available tools: {[getattr(t, 'name', 'NO_NAME') for t in active_tools]}")

                    if tool_func:
                        try:
                            # Execute tool function using LangChain v2+ patterns
                            if hasattr(tool_func, 'ainvoke') and callable(tool_func.ainvoke):
                                result = await tool_func.ainvoke(tool_args)
                            elif hasattr(tool_func, 'invoke') and callable(tool_func.invoke):
                                result = tool_func.invoke(tool_args)
                            elif hasattr(tool_func, '_run') and callable(tool_func._run):
                                if asyncio.iscoroutinefunction(tool_func._run):
                                    result = await tool_func._run(**tool_args)
                                else:
                                    result = tool_func._run(**tool_args)
                            elif asyncio.iscoroutinefunction(tool_func):
                                result = await tool_func(**tool_args)
                            elif callable(tool_func):
                                result = tool_func(**tool_args)
                            else:
                                raise ValueError(f"Cannot determine how to execute tool {tool_name}. Tool attributes: {dir(tool_func)}")

                            logger.info(f"Tool {tool_name} executed successfully")

                            # Add tool result to message history for next iteration
                            tool_message = {
                                "role": "tool",
                                "content": str(result),
                                "tool_call_id": tool_id,
                                "name": tool_name
                            }
                            messages.append(tool_message)

                        except Exception as tool_error:
                            logger.error(f"Error executing tool {tool_name}: {tool_error}")
                            # Add tool error to message history for next iteration
                            tool_message = {
                                "role": "tool",
                                "content": f"Error: {str(tool_error)}",
                                "tool_call_id": tool_id,
                                "name": tool_name
                            }
                            messages.append(tool_message)
                    else:
                        logger.error(f"Tool {tool_name} not found")
                        # Add tool not found error to message history
                        tool_message = {
                            "role": "tool",
                            "content": f"Error: Tool {tool_name} not found",
                            "tool_call_id": tool_id,
                            "name": tool_name
                        }
                        messages.append(tool_message)

            else:
                # No more tool calls, exit loop
                logger.info(f"No more tool calls requested, ending loop after {iteration} iterations")
                break

        else:
            # Max iterations reached
            logger.warning(f"Agent reached maximum iterations ({max_iterations}) without completion")

        # Extract final response (last AI message that's not a tool call)
        final_response = "I'm sorry, I couldn't complete your request."
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content and not hasattr(msg, 'tool_call_id'):
                final_response = msg.content
                break

        return {
            "response": final_response,
            "success": True,
            "tools_available": len(active_tools),
            "iterations_used": iteration,
            "agent_account": agent_account
        }

    except Exception as e:
        logger.error(f"Error processing agent message: {e}")
        return {
            "response": f"Error processing your request: {str(e)}",
            "success": False,
            "error": str(e),
            "iterations_used": iteration if 'iteration' in locals() else 0
        }

def get_agent_own_account() -> Optional[Dict]:
    """
    Get the agent's own system account (imported from AGENT_ACCOUNT_SECRET).

    Returns account info if available, None otherwise.
    """
    try:
        from account_manager import AccountManager

        system_user_id = "system_agent"
        account_manager = AccountManager()

        accounts = account_manager.get_user_accounts(
            user_id=system_user_id,
            chain="stellar"
        )

        # Find the agent account (marked with type="agent" in metadata)
        for account in accounts:
            metadata = account.get("metadata", {})
            if metadata.get("type") == "agent" and metadata.get("source") == "environment":
                return {
                    "address": account.get("public_key"),
                    "balance": account.get("balance", 0),
                    "account_id": account.get("id"),
                    "network": metadata.get("network", "mainnet")
                }

        return None

    except Exception as e:
        logger.error(f"Error getting agent own account: {e}")
        return None

def build_agent_system_prompt() -> str:
    """Build the system prompt for the AI agent"""

    # Check if agent has its own funded account
    agent_account_info = get_agent_own_account()
    agent_account_context = ""

    if agent_account_info:
        agent_account_context = f"""

**YOUR OWN FUNDED ACCOUNT:**
You have your own mainnet Stellar account that is already funded and ready to use:
- Address: {agent_account_info['address']}
- Balance: {agent_account_info.get('balance', 'Unknown')} XLM
- Network: {agent_account_info.get('network', 'Mainnet')}
- This account is managed by you (the AI agent) and can be used for DeFi operations

When users ask about your capabilities or accounts, mention that you already have a funded mainnet account ready to use.
"""

    # Load system prompt from markdown file
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.md")
    try:
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
        return prompt_template.format(agent_account_context=agent_account_context)
    except Exception as e:
        logger.error(f"Error loading system prompt from {prompt_path}: {e}")
        # Fallback to basic prompt if file loading fails
        return f"You are Tuxedo, an AI agent for Stellar DeFi operations.{agent_account_context}"

def get_default_agent_account() -> Optional[str]:
    """
    Get the default agent account to use.

    Priority order:
    1. Agent's own imported account from AGENT_STELLAR_SECRET
    2. First account with a meaningful balance (at least 1 XLM)
    3. First available account
    Returns None if no accounts exist.
    """
    try:
        from tools.agent.account_management import list_agent_accounts

        # Use system user ID for agent's own accounts
        system_user_id = "system_agent"
        accounts = list_agent_accounts(user_id=system_user_id)

        if not accounts:
            return None

        # First, try to find the agent's own imported account from environment
        agent_own_account = get_agent_own_account()
        if agent_own_account and agent_own_account.get('address'):
            return agent_own_account['address']

        # Second, find first account with a meaningful balance (at least 1 XLM)
        for account in accounts:
            if account.get('balance', 0) >= 1.0:
                return account['address']

        # Finally, return the first available account
        if accounts:
            return accounts[0]['address']

        return None

    except Exception as e:
        logger.error(f"Error getting default agent account: {e}")
        return None


def build_agent_context(agent_account: str) -> str:
    """Build agent account context for the system prompt"""
    return f"""
**Active Agent Account Context:**
You are currently using agent account: {agent_account}
When users ask about "my wallet", "my account", "my balance", or similar phrases:
- This is your active agent account that you manage autonomously
- Use this address for account operations and balance checks
- Check existing accounts using agent_list_accounts before creating new ones
- Only create new accounts when explicitly requested or if no suitable accounts exist
- No external wallet connection is required - you manage your own accounts
The address is a Stellar public key starting with 'G'.
"""