from deepagents.middleware.subagents import SubAgent
from ..tools import search_choir_kb, web_search

def get_researcher_agent() -> SubAgent:
    return {
        "name": "researcher",
        "description": "Specialized agent for researching topics using the web and Choir knowledge base.",
        "system_prompt": (
            "You are the Researcher sub-agent for Vibewriter.\n"
            "Your goal is to gather accurate and relevant information to answer the user's request.\n"
            "Use 'search_choir_kb' for internal Choir protocol information.\n"
            "Use 'web_search' for external real-time information.\n"
            "Summarize your findings clearly."
        ),
        "tools": [search_choir_kb, web_search]
    }
