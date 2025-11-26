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
os.environ.setdefault("JINJA2_CACHE_DIR", CACHE_DIR)

# Configure Jinja2 bytecode cache directory
# Jinja2 uses tempfile.gettempdir() which respects TMPDIR
# This prevents OpenHands SDK from trying to write to read-only package directories
os.environ.setdefault("TMPDIR", CACHE_DIR)

# Apply the OpenHands SDK patch
from openhands_utils import apply_openhands_patch
apply_openhands_patch()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log cache configuration for debugging
logger.info(f"Cache directory configured: {CACHE_DIR}")
logger.info(f"TMPDIR: {os.environ.get('TMPDIR')}")
logger.info(f"XDG_CACHE_HOME: {os.environ.get('XDG_CACHE_HOME')}")
logger.info(f"LITELLM_CACHE_DIR: {os.environ.get('LITELLM_CACHE_DIR')}")
logger.info(f"JINJA2_CACHE_DIR: {os.environ.get('JINJA2_CACHE_DIR')}")

import tempfile
logger.info(f"tempfile.gettempdir(): {tempfile.gettempdir()}")

# Create app at module level for Docker/uvicorn compatibility
from app import create_app
app = None

def main():
    """Main entry point for the application"""
    global app
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
else:
    # Create app for uvicorn/gunicorn
    app = create_app()
