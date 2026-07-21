from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.workflows.deterministic_search import (
    DeterministicSearch,
    SearchQueryPlan,
)


class TestDeterministicSearchStructure:
    def test_initializes_with_defaults(self):
        search = DeterministicSearch()
        assert search.max_queries == 3
        assert search.max_results == 5
        assert search.max_evidence_chars == 8000

    def test_initializes_with_custom_values(self):
        search = DeterministicSearch(max_queries=5, max_results=10, max_evidence_chars=4000)
        assert search.max_queries == 5
        assert search.max_results == 10
        assert search.max_evidence_chars == 4000

    def test_has_duckduckgo_tool(self):
        search = DeterministicSearch()
        assert search._search_tool is not None
        assert search._search_tool.name == "duckduckgo_search"


class TestDeterministicSearchGenerateQueries:
    @pytest.mark.asyncio
    async def test_returns_queries_from_structured_output(self):
        search = DeterministicSearch()
        agent = AsyncMock()
        agent.arun = AsyncMock(
            return_value=MagicMock(content=SearchQueryPlan(queries=["q1", "q2"]))
        )
        queries = await search._generate_queries(agent, "planning prompt")
        assert queries == ["q1", "q2"]

    @pytest.mark.asyncio
    async def test_respects_max_queries(self):
        search = DeterministicSearch(max_queries=2)
        agent = AsyncMock()
        agent.arun = AsyncMock(
            return_value=MagicMock(content=SearchQueryPlan(queries=[f"q{i}" for i in range(10)]))
        )
        queries = await search._generate_queries(agent, "planning prompt")
        assert len(queries) <= 2

    @pytest.mark.asyncio
    async def test_handles_dict_response(self):
        search = DeterministicSearch()
        agent = AsyncMock()
        agent.arun = AsyncMock(return_value=MagicMock(content={"queries": ["q1", "q2", "q3"]}))
        queries = await search._generate_queries(agent, "planning prompt")
        assert queries == ["q1", "q2", "q3"]

    @pytest.mark.asyncio
    async def test_returns_empty_list_on_failure(self):
        search = DeterministicSearch()
        agent = AsyncMock()
        agent.arun = AsyncMock(return_value=MagicMock(content="I cannot answer that."))
        queries = await search._generate_queries(agent, "planning prompt")
        assert queries == []


class TestDeterministicSearchTryParseQueries:
    def test_parses_json_object(self):
        search = DeterministicSearch()
        result = search._try_parse_queries_from_string('{"queries": ["q1", "q2"]}')
        assert result == ["q1", "q2"]

    def test_parses_json_array(self):
        search = DeterministicSearch()
        result = search._try_parse_queries_from_string('["q1", "q2"]')
        assert result == ["q1", "q2"]

    def test_parses_bullet_list(self):
        search = DeterministicSearch()
        text = "- query one\n- query two\n- query three"
        result = search._try_parse_queries_from_string(text)
        assert len(result) == 3
        assert all(len(q) > 5 for q in result)

    def test_returns_empty_for_nonsense(self):
        search = DeterministicSearch()
        result = search._try_parse_queries_from_string("Hello world")
        assert result == []


class TestDeterministicSearchExecuteSearches:
    @pytest.mark.asyncio
    async def test_executes_valid_queries_only(self):
        search = DeterministicSearch()

        calls = []

        async def mock_search(query, max_results=5):
            calls.append(query)
            url = f"https://ex.com/{query}"
            return MagicMock(
                success=True,
                data=[{"title": "R", "body": "B", "href": url}],
            )

        search._search_tool.execute = mock_search
        results = await search._execute_searches(["q1", "", "q2"])
        assert calls == ["q1", "q2"]
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_deduplicates_by_url(self):
        search = DeterministicSearch()
        search._search_tool.execute = AsyncMock(
            return_value=MagicMock(
                success=True,
                data=[
                    {"title": "A", "body": "B", "href": "https://ex.com/dup"},
                    {"title": "C", "body": "D", "href": "https://ex.com/dup"},
                    {"title": "E", "body": "F", "href": "https://ex.com/unique"},
                ],
            )
        )
        results = await search._execute_searches(["q1"])
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_handles_search_failure_gracefully(self):
        search = DeterministicSearch()
        search._search_tool.execute = AsyncMock(
            return_value=MagicMock(success=False, data=None, error="rate limit")
        )
        results = await search._execute_searches(["q1"])
        assert results == []


class TestDeterministicSearchEvidenceBundle:
    def test_builds_evidence_bundle(self):
        search = DeterministicSearch()
        bundle = search._build_evidence_bundle(
            "Context info",
            [
                {"title": "T1", "href": "https://ex.com/1", "body": "Snippet 1"},
                {"title": "T2", "href": "https://ex.com/2", "body": "Snippet 2"},
            ],
        )
        assert "Context info" in bundle
        assert "Result 1" in bundle
        assert "Result 2" in bundle
        assert "T1" in bundle
        assert "https://ex.com/1" in bundle
        assert "Snippet 1" in bundle

    def test_truncates_at_limit(self):
        search = DeterministicSearch(max_evidence_chars=500)
        many_results = [
            {"title": f"T{i}", "href": f"https://ex.com/{i}", "body": "x" * 200} for i in range(100)
        ]
        bundle = search._build_evidence_bundle("ctx", many_results)
        assert len(bundle) <= 500


class TestDeterministicSearchSynthesize:
    @pytest.mark.asyncio
    async def test_returns_model_from_structured_output(self):
        from pydantic import BaseModel, Field

        class TestOutput(BaseModel):
            result: str = Field(default="")

        search = DeterministicSearch()
        agent = AsyncMock()
        instance = TestOutput(result="done")
        agent.arun = AsyncMock(return_value=MagicMock(content=instance))
        output = await search._synthesize(agent, "evidence", TestOutput)
        assert isinstance(output, TestOutput)
        assert output.result == "done"

    @pytest.mark.asyncio
    async def test_handles_dict_response(self):
        from pydantic import BaseModel, Field

        class TestOutput(BaseModel):
            result: str = Field(default="")

        search = DeterministicSearch()
        agent = AsyncMock()
        agent.arun = AsyncMock(return_value=MagicMock(content={"result": "dict_ok"}))
        output = await search._synthesize(agent, "evidence", TestOutput)
        assert output.result == "dict_ok"


class TestDeterministicSearchFullRun:
    @pytest.mark.asyncio
    async def test_full_run(self):
        from pydantic import BaseModel, Field

        class TestOutput(BaseModel):
            finding: str = Field(default="")

        search = DeterministicSearch()

        agent = AsyncMock()
        agent.arun = AsyncMock()

        query_plan = SearchQueryPlan(queries=["test query"])
        agent.arun.side_effect = [
            MagicMock(content=query_plan),
            MagicMock(content=TestOutput(finding="found it")),
        ]

        async def mock_search(query, max_results=5):
            return MagicMock(
                success=True,
                data=[
                    {
                        "title": "Result",
                        "href": "https://ex.com",
                        "body": "Evidence snippet",
                    }
                ],
            )

        search._search_tool.execute = mock_search

        result = await search.run(
            agent=agent,
            context="test context",
            planning_prompt="generate queries",
            output_model=TestOutput,
            agent_name="test",
        )

        assert isinstance(result, TestOutput)
        assert result.finding == "found it"
        assert agent.arun.call_count == 2
