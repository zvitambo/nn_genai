import asyncio

from langchain_tavily import TavilySearch
from typing import Protocol

from nn_genai.models.search_result import SearchResult

class SearchProvider(Protocol):
    async def search(
        self,
        query: str,
    ) -> list[SearchResult]:
        ...


class TavilySearchProvider:
    """Tavily implementation of the SearchProvider port."""

    def __init__(self, api_key: str, max_results: int = 5) -> None:
        if not api_key:
            raise ValueError("TAVILY_API_KEY is required")

        self._search = TavilySearch(
            max_results=max_results,
            topic="general",
            search_depth="basic",
            tavily_api_key=api_key,
        )

    async def search(self, query: str) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        response = await asyncio.to_thread(
            self._search.invoke,
            {"query": query},
        )

        return self._map_results(response)


    @staticmethod
    def _map_results(response: dict) -> list[SearchResult]:
        if "error" in response:
            raise RuntimeError(
                f"Tavily search failed: {response['error']}"
            )

        results = response.get("results", [])

        return [
            SearchResult(
                title=result["title"],
                url=result["url"],
                snippet=result.get("content", ""),
            )
            for result in results
            if result.get("title") and result.get("url")
        ]
