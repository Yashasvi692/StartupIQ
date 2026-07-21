import json
from typing import Any

from pydantic import BaseModel, Field

from backend.tools.duckduckgo_tool import DuckDuckGoTool
from backend.utils.exceptions import PipelineError
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MAX_SEARCH_QUERIES = 3
MAX_RESULTS_PER_QUERY = 5
MAX_EVIDENCE_CHARS = 8000


class SearchQueryPlan(BaseModel):
    queries: list[str] = Field(
        default_factory=list,
        description=f"Up to {MAX_SEARCH_QUERIES} DuckDuckGo search queries",
    )


class DeterministicSearch:
    def __init__(
        self,
        max_queries: int = MAX_SEARCH_QUERIES,
        max_results: int = MAX_RESULTS_PER_QUERY,
        max_evidence_chars: int = MAX_EVIDENCE_CHARS,
    ) -> None:
        self._search_tool = DuckDuckGoTool()
        self.max_queries = max_queries
        self.max_results = max_results
        self.max_evidence_chars = max_evidence_chars

    async def run(
        self,
        agent: Any,
        context: str,
        planning_prompt: str,
        output_model: type[BaseModel],
        agent_name: str = "",
    ) -> BaseModel:
        logger.info("Agent %s Phase 1: Generating search queries", agent_name)

        queries = await self._generate_queries(agent, planning_prompt)

        logger.info(
            "Agent %s Phase 2: Executing %d DuckDuckGo searches",
            agent_name,
            len(queries),
        )
        evidence = await self._execute_searches(queries)
        self._log_search_results(agent_name, queries, evidence)

        logger.info("Agent %s Phase 3: Synthesizing final report", agent_name)
        evidence_bundle = self._build_evidence_bundle(context, evidence)
        return await self._synthesize(agent, evidence_bundle, output_model)

    async def _generate_queries(self, agent: Any, planning_prompt: str) -> list[str]:
        response = await agent.arun(planning_prompt, output_schema=SearchQueryPlan)
        content = response.content

        if isinstance(content, SearchQueryPlan):
            return content.queries[: self.max_queries]

        if isinstance(content, dict):
            return SearchQueryPlan.model_validate(content).queries[: self.max_queries]

        if isinstance(content, str):
            parsed = self._try_parse_queries_from_string(content)
            if parsed:
                return parsed[: self.max_queries]

        logger.warning(
            "Unexpected query plan response type: %s — content=%s",
            type(content).__name__,
            str(content)[:200],
        )
        return []

    def _try_parse_queries_from_string(self, text: str) -> list[str]:
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "queries" in data:
                return data["queries"]
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, TypeError):
            pass

        lines = [
            line.strip().lstrip("-*0123456789).\"'").strip()
            for line in text.strip().split("\n")
            if line.strip()
        ]
        valid = [line for line in lines if len(line) > 5 and not line.startswith("#")]
        if len(valid) >= 2:
            return valid

        return []

    async def _execute_searches(self, queries: list[str]) -> list[dict[str, Any]]:
        all_results: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for query in queries:
            if not query or not query.strip():
                continue
            logger.debug("Searching DuckDuckGo for: %s", query)
            result = await self._search_tool.execute(query=query, max_results=self.max_results)
            if result.success and result.data:
                for item in result.data:
                    url = item.get("href", "") or ""
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(item)
                    elif not url:
                        all_results.append(item)

        logger.debug("Collected %d unique search results", len(all_results))
        return all_results

    def _log_search_results(
        self,
        agent_name: str,
        queries: list[str],
        evidence: list[dict[str, Any]],
    ) -> None:
        successful = sum(1 for q in queries if q and q.strip())
        unique_urls = len({e.get("href", "") for e in evidence if e.get("href")})
        logger.info(
            "Retrieved: %d successful searches, %d documents, %d unique sources",
            successful,
            len(evidence),
            unique_urls,
        )

    def _build_evidence_bundle(
        self,
        context: str,
        evidence: list[dict[str, Any]],
    ) -> str:
        parts: list[str] = [
            "## Context",
            "",
            context,
            "",
            "## Search Results",
            "",
        ]

        total_chars = len(context)

        for i, item in enumerate(evidence, 1):
            title = item.get("title", "")
            url = item.get("href", "")
            body = item.get("body", "")

            entry = f"### Result {i}\n"
            if title:
                entry += f"Title: {title}\n"
            if url:
                entry += f"URL: {url}\n"
            if body:
                entry += f"Snippet: {body}\n"

            entry += "\n"

            if total_chars + len(entry) > self.max_evidence_chars:
                logger.debug(
                    "Truncating evidence at result %d (%.0f%% of limit)",
                    i,
                    (total_chars / self.max_evidence_chars) * 100,
                )
                break

            parts.append(entry)
            total_chars += len(entry)

        return "".join(parts)

    async def _synthesize(
        self,
        agent: Any,
        evidence_bundle: str,
        output_model: type[BaseModel],
    ) -> BaseModel:
        response = await agent.arun(evidence_bundle, output_schema=output_model)
        content = response.content
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, dict):
            return output_model.model_validate(content)
        if isinstance(content, str):
            raise PipelineError(
                f"LLM provider returned an error instead of structured output: {content[:300]}"
            )
        raise TypeError(
            f"Expected structured output as {output_model.__name__}, "
            f"got {type(content).__name__}: {content[:200]}"
        )
