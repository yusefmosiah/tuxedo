"""
OpenHands-compatible WebSearch action using Tavily API.

This creates a custom action that can be used by OpenHands agents
for web research tasks.
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class WebSearchAction:
    """
    WebSearch action for OpenHands agents.

    This action executes web searches using Tavily API and returns
    structured results that agents can use for research.
    """

    query: str
    max_results: int = 5
    search_depth: str = "advanced"

    def __post_init__(self):
        self.action = "web_search"


@dataclass
class WebSearchObservation:
    """
    Observation returned from WebSearch action.

    Contains search results formatted for agent consumption.
    """

    content: str
    success: bool = True
    error: Optional[str] = None

    def __post_init__(self):
        self.observation = "web_search"


class WebSearchExecutor:
    """
    Executor for WebSearch actions.

    This class handles the actual API calls to Tavily and formats
    results for OpenHands agents.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WebSearch executor.

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")

        # Strip quotes if present (common issue with env vars)
        self.api_key = self.api_key.strip('"').strip("'")

        self.base_url = "https://api.tavily.com"
        logger.info("WebSearch executor initialized with Tavily API")

    async def execute(self, action: WebSearchAction) -> WebSearchObservation:
        """
        Execute web search action.

        Args:
            action: WebSearchAction with query and parameters

        Returns:
            WebSearchObservation with formatted results
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "api_key": self.api_key,
                        "query": action.query,
                        "max_results": action.max_results,
                        "search_depth": action.search_depth,
                        "include_raw_content": True,
                        "include_domains": [],
                        "exclude_domains": []
                    }
                )
                response.raise_for_status()

                data = response.json()
                formatted_results = self._format_results(action.query, data)

                return WebSearchObservation(
                    content=formatted_results,
                    success=True
                )

        except httpx.HTTPStatusError as e:
            error_msg = f"Tavily API error: {e.response.status_code}"
            logger.error(f"{error_msg} - {e.response.text}")
            return WebSearchObservation(
                content=f"Search failed: {error_msg}",
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"WebSearch error: {str(e)}"
            logger.error(error_msg)
            return WebSearchObservation(
                content=f"Search failed: {error_msg}",
                success=False,
                error=error_msg
            )

    def _format_results(self, query: str, data: dict) -> str:
        """
        Format Tavily search results for agent consumption.

        Args:
            query: Original search query
            data: Raw Tavily API response

        Returns:
            Formatted string with search results
        """
        results = data.get("results", [])
        if not results:
            return f"No results found for query: {query}"

        output = [f"Search Results for: {query}\n"]
        output.append(f"Found {len(results)} authoritative sources:\n")

        for idx, result in enumerate(results, 1):
            output.append(f"\n{'='*60}")
            output.append(f"Result #{idx}")
            output.append(f"{'='*60}")
            output.append(f"Title: {result.get('title', 'N/A')}")
            output.append(f"URL: {result.get('url', 'N/A')}")
            output.append(f"Relevance Score: {result.get('score', 0.0):.2f}")

            if result.get("published_date"):
                output.append(f"Published: {result['published_date']}")

            content = result.get("content", "")
            if content:
                output.append(f"\nContent Summary:")
                output.append(content[:800])  # First 800 chars
                if len(content) > 800:
                    output.append("... [truncated]")

            output.append("")

        output.append(f"\n{'='*60}")
        output.append(f"Search complete. Use these sources for your research.")
        output.append(f"{'='*60}\n")

        return "\n".join(output)


# Singleton instance for reuse
_executor: Optional[WebSearchExecutor] = None


def get_websearch_executor() -> WebSearchExecutor:
    """Get singleton WebSearch executor instance."""
    global _executor
    if _executor is None:
        _executor = WebSearchExecutor()
    return _executor
