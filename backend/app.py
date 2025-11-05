"""
FastAPI Application Factory
Creates and configures the FastAPI application with all routes and middleware.
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import route modules
from api.routes.chat import router as chat_router
from api.routes.agent import router as agent_router
from api.routes.threads import router as threads_router
from api.routes.auth import router as auth_router

# Import agent system
from agent.core import initialize_agent, cleanup_agent

# Import configuration
try:
    from config.settings import settings
    CONFIG_AVAILABLE = True
except ImportError:
    logger.warning("Configuration settings not available, using defaults")
    CONFIG_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Tuxedo AI backend...")

    # Initialize agent system
    await initialize_agent()

    yield

    logger.info("Shutting down Tuxedo AI backend...")

    # Cleanup agent system
    await cleanup_agent()

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Tuxedo AI Backend",
        description="Agent-first DeFi interface for Stellar ecosystem",
        version="1.0.0",
        lifespan=lifespan
    )

    # Setup CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "https://tuxedo.onrender.com",
            "https://tuxedo-frontend.onrender.com"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router, tags=["auth"])
    app.include_router(chat_router, tags=["chat"])
    app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
    app.include_router(threads_router, tags=["threads"])

    # Health check endpoint
    @app.get("/")
    async def root():
        return {"message": "Tuxedo AI Backend is running!"}

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        from agent.core import get_agent_status
        return await get_agent_status()

    @app.get("/stellar-tools/status")
    async def stellar_tools_status():
        """Get available Stellar tools and their status"""
        from datetime import datetime

        try:
            # Check what tools are available
            tools = []
            stellar_tools_ready = False

            try:
                # Try to import and check stellar tools
                import stellar_tools
                tools.extend([
                    "stellar_account_manager",
                    "stellar_trading",
                    "stellar_trustline_manager",
                    "stellar_market_data",
                    "stellar_utilities",
                    "stellar_soroban_operations"
                ])
                stellar_tools_ready = True
            except ImportError:
                logger.warning("Stellar tools not available")

            # Check agent account tools
            agent_account_tools = False
            try:
                from tools.agent.account_management import account_tools
                tools.extend([
                    "agent_create_account",
                    "agent_list_accounts",
                    "agent_get_account_info"
                ])
                agent_account_tools = True
            except ImportError:
                logger.warning("Agent account tools not available")

            # Check DeFindex tools
            try:
                import defindex_tools
                tools.extend([
                    "discover_high_yield_vaults",
                    "get_defindex_vault_details",
                    "prepare_defindex_deposit"
                ])
            except ImportError:
                logger.warning("DeFindex tools not available")

            return {
                "available": stellar_tools_ready,
                "tools_count": len(tools),
                "tools": tools,
                "last_check": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting stellar tools status: {e}")
            return {
                "available": False,
                "tools_count": 0,
                "tools": [],
                "last_check": datetime.now().isoformat()
            }

    @app.post("/stellar-tool/{tool_name}")
    async def call_stellar_tool(tool_name: str, request: Dict[str, Any] = None):
        """Call a specific Stellar tool directly"""
        if request is None:
            request = {}

        try:
            # Try to import and call the stellar tool
            import stellar_tools

            # Map tool names to functions
            tool_mapping = {
                "stellar_account_manager": stellar_tools.account_manager_tool,
                "stellar_trading": stellar_tools.trading_tool,
                "stellar_trustline_manager": stellar_tools.trustline_manager_tool,
                "stellar_market_data": stellar_tools.market_data_tool,
                "stellar_utilities": stellar_tools.utilities_tool,
                "stellar_soroban_operations": stellar_tools.soroban_tool
            }

            if tool_name not in tool_mapping:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

            tool_func = tool_mapping[tool_name]

            # Call the tool with provided arguments
            if hasattr(tool_func, '__call__'):
                result = await tool_func(**request)
            else:
                result = tool_func

            return {
                "success": True,
                "result": result,
                "tool_name": tool_name
            }

        except ImportError:
            return {
                "success": False,
                "error": "Stellar tools not available",
                "tool_name": tool_name
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calling stellar tool {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Error calling tool: {str(e)}",
                "tool_name": tool_name
            }

    return app