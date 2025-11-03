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
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == "__main__":
    main()