import os
import asyncio
import logging
from dotenv import load_dotenv

# Import the new Vibewriter agent
from backend.vibewriter.agent.main import run_vibewriter_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def main():
    """
    Main entry point for the Vibewriter Agent.
    """
    # Get configuration from environment
    topic = os.getenv("RESEARCH_TOPIC", "The future of Agentic Economics")
    vm_id = os.getenv("ERA_VM_ID", "default_session")

    logger.info(f"Starting Vibewriter Agent")
    logger.info(f"Target VM: {vm_id}")
    logger.info(f"Topic: {topic}")

    try:
        result = await run_vibewriter_task(topic, vm_id)

        last_message = result["messages"][-1]
        print("\n--- Final Agent Output ---")
        print(last_message.content)

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    import sys
    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    asyncio.run(main())
