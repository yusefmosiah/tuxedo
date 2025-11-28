import os
from typing import Optional
from langchain_core.tools import tool
from tavily import TavilyClient
from .choir_account import get_choir_account_tools

# Initialize Tavily client if key is available
tavily_api_key = os.environ.get("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

@tool
def search_choir_kb(query: str) -> str:
    """
    Search the Choir knowledge base for information about the platform, protocols, and existing content.
    Use this to ground your writing in the specific context of the Choir ecosystem.
    """
    # Mock implementation for now
    return f"[Mock Result] Found 3 articles related to '{query}' in Choir KB:\n1. Choir Protocol V1 Overview\n2. Content Staking Mechanisms\n3. User Reputation System"

@tool
def cite_article(url: str, title: str, snippet: Optional[str] = None) -> str:
    """
    Record a citation for the content being written.
    Always use this when referencing external sources to ensure proper attribution.
    """
    # Mock implementation - in real version this might add to a structured citation list in state
    return f"Citation recorded: '{title}' ({url})"

@tool
def publish_to_choir(content: str, title: str, tags: list[str] = []) -> str:
    """
    Publish the final content to the Choir platform.
    Only use this when the content is complete and verified.
    """
    # Mock implementation
    return f"Successfully published '{title}' to Choir with tags: {', '.join(tags)}"

@tool
def web_search(query: str) -> str:
    """
    Search the web for real-time information using Tavily.
    Use this to find current events, market data, or external references.
    """
    if not tavily_client:
        return "Error: Web search is not enabled (TAVILY_API_KEY missing)."

    try:
        response = tavily_client.search(query=query, search_depth="basic")
        results = response.get("results", [])
        formatted_results = "\n".join([
            f"- {r['title']} ({r['url']}): {r['content'][:200]}..."
            for r in results[:3]
        ])
        return f"Web Search Results for '{query}':\n{formatted_results}"
    except Exception as e:
        return f"Error performing web search: {str(e)}"

def get_vibewriter_tools():
    return [search_choir_kb, cite_article, publish_to_choir, web_search] + get_choir_account_tools()
