"""
FastAPI Application Factory
Creates and configures the FastAPI application with all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# Import route modules
from api.routes.chat import router as chat_router
from api.routes.agent import router as agent_router

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
    app.include_router(chat_router, tags=["chat"])
    app.include_router(agent_router, prefix="/api/agent", tags=["agent"])

    # Health check endpoint
    @app.get("/")
    async def root():
        return {"message": "Tuxedo AI Backend is running!"}

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        from agent.core import get_agent_status
        return await get_agent_status()

    return app