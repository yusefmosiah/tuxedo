from deepagents.middleware.subagents import SubAgent
from ..tools import cite_article, publish_to_choir

def get_writer_agent() -> SubAgent:
    return {
        "name": "writer",
        "description": "Specialized agent for writing, citing, and publishing content.",
        "system_prompt": (
            "You are the Writer sub-agent for Vibewriter.\n"
            "Your goal is to draft high-quality content based on research.\n"
            "Always cite your sources using 'cite_article'.\n"
            "When the content is finalized, use 'publish_to_choir'."
        ),
        "tools": [cite_article, publish_to_choir]
    }
