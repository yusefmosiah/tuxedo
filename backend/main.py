#!/usr/bin/env python3
"""
Tuxedo AI Backend - Simplified Entry Point
Uses the app factory pattern for clean modular architecture.
"""

import os
import logging
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure cache directories for LiteLLM/OpenHands before any imports
# This prevents permission errors when writing to package directories
CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/tuxedo_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", CACHE_DIR)
os.environ.setdefault("LITELLM_CACHE_DIR", CACHE_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app at module level for Docker/uvicorn compatibility
from app import create_app
app = create_app()

def main():
    """Main entry point for the application"""
    try:
        # Import app factory
        from app import create_app

        # Create FastAPI application
        app = create_app()

        # Get configuration from environment or use defaults
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        debug = os.getenv("DEBUG", "false").lower() == "true"

        logger.info(f"Starting Tuxedo AI Backend on {host}:{port}")
        logger.info(f"Debug mode: {debug}")

        # Run the application
        if debug:
            # Use import string for reload mode
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                reload=debug,
                log_level="info"
            )
        else:
            # Direct app import for production mode
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=False,
                log_level="info"
            )

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == "__main__":
    main()