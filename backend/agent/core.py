"""
Agent Core System
Main AI agent logic and lifecycle management.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Global agent state
llm = None
agent_tools = []

async def initialize_agent():
    """Initialize the AI agent system"""
    global llm, agent_tools

    try:
        # Initialize LLM
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.redpill.ai/v1")

        try:
            llm = ChatOpenAI(
                api_key=openai_api_key,
                base_url=openai_base_url,
                model="deepseek/deepseek-v3.1-terminus:exacto",
                temperature=0.7,
                max_tokens=2000,
            )
            logger.info("LLM initialized successfully")
        except Exception as llm_error:
            logger.warning(f"LLM initialization failed: {llm_error}")
            logger.info("Continuing without LLM - agent features will be limited")

        # Initialize agent tools
        await load_agent_tools()

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

async def load_agent_tools():
    """Load all available agent tools"""
    global agent_tools

    agent_tools = []

    # Import stellar tools
    try:
        from stellar_tools import account_manager, trading, trustline_manager, market_data, utilities
        from stellar_soroban import soroban_operations
        agent_tools.extend([
            account_manager,
            trading,
            trustline_manager,
            market_data,
            utilities,
            soroban_operations
        ])
        logger.info("Stellar tools loaded successfully")
    except ImportError as e:
        logger.warning(f"Stellar tools not available: {e}")

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

    # Import DeFindex tools
    try:
        from defindex_tools import discover_high_yield_vaults, get_defindex_vault_details, prepare_defindex_deposit
        agent_tools.extend([
            discover_high_yield_vaults,
            get_defindex_vault_details,
            prepare_defindex_deposit
        ])
        logger.info("DeFindex tools loaded successfully")
    except ImportError as e:
        logger.warning(f"DeFindex tools not available: {e}")

async def get_agent_status() -> Dict[str, Any]:
    """Get current agent system status"""
    return {
        "status": "healthy",
        "llm_configured": llm is not None,
        "tools_count": len(agent_tools),
        "tools_available": [getattr(tool, 'name', getattr(tool, '__name__', str(tool))) for tool in agent_tools],
        "agent_account_tools_available": any(
            getattr(tool, 'name', getattr(tool, '__name__', str(tool))) in ["agent_create_account", "agent_list_accounts", "agent_get_account_info"]
            for tool in agent_tools
        ),
        "stellar_tools_ready": len(agent_tools) > 0,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

async def process_agent_message(
    message: str,
    history: List[Dict[str, str]],
    agent_account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a user message through the AI agent.

    Args:
        message: User message
        history: Conversation history
        agent_account: Active agent account address

    Returns:
        Agent response with metadata
    """
    if not llm:
        raise Exception("Agent not initialized")

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
        tool_schemas = [convert_to_openai_function(t) for t in agent_tools]
        tools = [{"type": "function", "function": schema} for schema in tool_schemas]

        # Create LLM with tools
        llm_with_tools = llm.bind(tools=tools)

        # Get response
        response = await llm_with_tools.ainvoke(messages)

        return {
            "response": response.content,
            "success": True,
            "tools_available": len(agent_tools),
            "agent_account": agent_account
        }

    except Exception as e:
        logger.error(f"Error processing agent message: {e}")
        return {
            "response": f"Error processing your request: {str(e)}",
            "success": False,
            "error": str(e)
        }

def build_agent_system_prompt() -> str:
    """Build the system prompt for the AI agent"""
    return """You are Tuxedo, an AI agent that manages its own Stellar accounts for DeFi operations. You help users discover and understand DeFi opportunities on Stellar including Blend Protocol and DeFindex vaults.

**Agent-First Approach:**
You are an autonomous AI agent that manages your own accounts - you do NOT require users to connect external wallets. You can create and manage your own Stellar accounts for demonstrating DeFi operations.

**Your Available Tools:**
You have access to Stellar blockchain tools that can:
- **Agent Account Management**: Create, list, and get info about your own agent-controlled accounts
- Query market data and orderbooks (market_data)
- Execute trades on the Stellar DEX (trading)
- Manage trustlines for assets (trustline_manager)
- Query network status and fees (utilities)
- Interact with smart contracts (soroban)
- Discover and interact with DeFindex vaults for yield generation

**Agent Instructions:**
1. **Always be helpful** - Use tools to get real-time data instead of making assumptions
2. **Explain your actions** - Tell users what you're querying and why
3. **Interpret results clearly** - Translate blockchain data into understandable insights
4. **Handle gracefully** - If tools fail, explain the issue and suggest alternatives
5. **Security first** - Never expose private keys or sensitive information
6. **Agent Account Management** - When users ask about "my wallet", "my account", "my balance", or similar phrases, use your agent account management tools to create accounts or check balances. You manage your own accounts autonomously.
7. **No external wallets needed** - Emphasize that you are an AI agent that manages its own accounts - users don't need to connect wallets.
8. **Explain trading limitations** - When orderbooks are empty, explain that most trading happens via liquidity pools and testnet has limited activity.
9. **Balance check priority** - When users mention balance or account without being specific, check your agent accounts first using agent_list_accounts.

**Current Context:**
- User is on Stellar testnet for educational purposes
- Focus on Blend Protocol lending opportunities
- Prioritize account balance checks before suggesting operations
- Always explain risks and transaction costs
- Be transparent about testnet liquidity limitations"""

def build_agent_context(agent_account: str) -> str:
    """Build agent account context for the system prompt"""
    return f"""
**Active Agent Account Context:**
You are currently using agent account: {agent_account}
When users ask about "my wallet", "my account", "my balance", or similar phrases:
- This is your active agent account that you manage autonomously
- Use this address for account operations and balance checks
- You can create additional accounts using agent_create_account if needed
- No external wallet connection is required - you manage your own accounts
The address is a Stellar public key starting with 'G'.
"""