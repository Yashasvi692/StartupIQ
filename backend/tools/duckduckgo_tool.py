from typing import Any

from duckduckgo_search import DDGS

from backend.tools.base_tool import BaseTool, ToolResponse
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MAX_RESULTS: int = 5


class DuckDuckGoTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo. Returns text results with source URLs."

    async def execute(self, query: str = "", max_results: int = MAX_RESULTS) -> ToolResponse:
        if not query or not query.strip():
            return ToolResponse(success=False, error="Query must be a non-empty string")

        try:
            results = await self._search(query, max_results)
            return ToolResponse(success=True, data=results)
        except Exception as e:
            logger.error("DuckDuckGo search failed: %s", str(e))
            return ToolResponse(success=False, error=str(e))

    async def _search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        from asyncio import to_thread

        def _sync_search() -> list[dict[str, Any]]:
            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", ""),
                }
                for r in raw
            ]

        return await to_thread(_sync_search)
