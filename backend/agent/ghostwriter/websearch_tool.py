"""
WebSearch tool for OpenHands SDK using Tavily API.

Tavily is optimized for AI research tasks and provides structured, authoritative sources.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Web search tool using Tavily API for research-focused queries.

    Tavily is specifically designed for AI agents and provides:
    - Authoritative, structured search results
    - Source verification and relevance scoring
    - Content extraction from search results
    """

    name = "web_search"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WebSearch tool.

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")

        # Strip quotes if present (common issue with env vars)
        self.api_key = self.api_key.strip('"').strip("'")

        self.base_url = "https://api.tavily.com"
        logger.info("WebSearch tool initialized with Tavily API")

    async def search(
        self,
        query: str,
        max_results: int = 20,
        search_depth: str = "advanced",
        include_raw_content: bool = True
    ) -> Dict[str, Any]:
        """
        Execute web search using Tavily API.

        Args:
            query: Search query
            max_results: Maximum number of results (1-20, default: 20)
            search_depth: "basic" or "advanced" (default: "advanced")
            include_raw_content: Include full page content (default: True)

        Returns:
            Search results with URLs, titles, content, and scores
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "max_results": max_results,
                        "search_depth": search_depth,
                        "include_raw_content": include_raw_content,
                        "include_domains": [],
                        "exclude_domains": []
                    }
                )
                response.raise_for_status()

                data = response.json()

                # Format results for agent consumption
                results = {
                    "query": query,
                    "num_results": len(data.get("results", [])),
                    "results": []
                }

                for idx, result in enumerate(data.get("results", []), 1):
                    results["results"].append({
                        "rank": idx,
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "raw_content": result.get("raw_content", ""),
                        "score": result.get("score", 0.0),
                        "published_date": result.get("published_date")
                    })

                logger.info(f"WebSearch: '{query}' returned {results['num_results']} results")
                return results

        except httpx.HTTPStatusError as e:
            logger.error(f"Tavily API error: {e.response.status_code} - {e.response.text}")
            return {
                "query": query,
                "error": f"Search failed: {e.response.status_code}",
                "num_results": 0,
                "results": []
            }
        except Exception as e:
            logger.error(f"WebSearch error: {str(e)}")
            return {
                "query": query,
                "error": f"Search failed: {str(e)}",
                "num_results": 0,
                "results": []
            }

    def format_for_agent(self, results: Dict[str, Any]) -> str:
        """
        Format search results for agent readability.

        Args:
            results: Search results from search()

        Returns:
            Formatted string for agent consumption
        """
        if "error" in results:
            return f"Search Error: {results['error']}"

        if results["num_results"] == 0:
            return f"No results found for query: {results['query']}"

        output = [f"Search Results for: {results['query']}\n"]
        output.append(f"Found {results['num_results']} results:\n")

        for result in results["results"]:
            output.append(f"\n--- Result {result['rank']} ---")
            output.append(f"Title: {result['title']}")
            output.append(f"URL: {result['url']}")
            output.append(f"Score: {result['score']:.2f}")
            if result.get("published_date"):
                output.append(f"Published: {result['published_date']}")
            output.append(f"\nContent:\n{result['content'][:500]}...")
            output.append("")

        return "\n".join(output)


# OpenHands Tool wrapper
class OpenHandsWebSearchTool:
    """
    OpenHands-compatible WebSearch tool wrapper.

    This wraps the WebSearchTool for use in OpenHands Agent SDK.
    """

    name = "web_search"
    description = "Search the web for authoritative sources using Tavily API"

    def __init__(self, api_key: Optional[str] = None):
        self.search_tool = WebSearchTool(api_key)

    async def execute(self, query: str, max_results: int = 20) -> str:
        """
        Execute web search and return formatted results.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            Formatted search results string
        """
        results = await self.search_tool.search(query, max_results)
        return self.search_tool.format_for_agent(results)


# Singleton instance
_web_search_instance: Optional[WebSearchTool] = None


def get_web_search_tool() -> WebSearchTool:
    """Get singleton WebSearch tool instance."""
    global _web_search_instance
    if _web_search_instance is None:
        _web_search_instance = WebSearchTool()
    return _web_search_instance
