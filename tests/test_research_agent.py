from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend.agents import ResearchAgent, StartupIQAgent
from backend.models.research_result import ResearchFinding, ResearchResult
from backend.tools.duckduckgo_tool import DuckDuckGoTool
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"
RESEARCH_PROMPT_NAME = "research"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{RESEARCH_PROMPT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Research Test Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestResearchAgentStructure:
    def test_inherits_from_startup_iq_agent(self):
        assert issubclass(ResearchAgent, StartupIQAgent)

    def test_name_set_correctly(self):
        assert ResearchAgent.name == "research"

    def test_initializes_successfully(self):
        agent = ResearchAgent()
        assert agent.agent is not None
        assert agent.agent.name == "research"

    def test_has_logger(self):
        agent = ResearchAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent.research"

    def test_loads_prompt_dynamically(self):
        agent = ResearchAgent()
        assert agent.agent.system_message is not None

    def test_system_message_contains_expected_content(self):
        agent = ResearchAgent()
        msg = agent.agent.system_message or ""
        assert "Research" in msg
        assert "ResearchResult" in msg


class TestResearchAgentOutputModel:
    def test_output_model_is_research_result(self):
        agent = ResearchAgent()
        assert agent._output_model is ResearchResult

    def test_agno_agent_has_output_schema(self):
        agent = ResearchAgent()
        assert agent.agent.output_schema is ResearchResult

    def test_prompt_file_exists(self):
        prompt_file = PROMPTS_DIR / "research.md"
        assert prompt_file.exists(), "research.md prompt file must exist"

    def test_prompt_has_required_sections(self):
        prompt = (PROMPTS_DIR / "research.md").read_text(encoding="utf-8")
        sections = [
            "# Identity",
            "# Objective",
            "# Responsibilities",
            "# Constraints",
            "# Inputs",
            "# Available Context",
            "# Available Tools",
            "# Reasoning Instructions",
            "# Expected Output",
            "# Quality Checklist",
        ]
        for section in sections:
            assert section in prompt, f"Missing section: {section}"

    def test_no_hardcoded_prompt_in_agent_code(self):
        agent_path = PROJECT_ROOT / "backend" / "agents" / "research_agent.py"
        agent_code = agent_path.read_text(encoding="utf-8")
        assert "# Identity" not in agent_code
        assert "# Objective" not in agent_code


class TestResearchAgentTools:
    def test_has_duckduckgo_tool_by_default(self):
        agent = ResearchAgent()
        assert len(agent._tools) == 1
        assert agent._tools[0].name == "duckduckgo_search"

    def test_accepts_custom_tools(self):
        async def custom_tool(**kw):
            return "custom"

        custom_tool.__name__ = "custom_tool"

        agent = ResearchAgent(tools=[custom_tool])
        assert len(agent._tools) == 1
        assert agent._tools[0].__name__ == "custom_tool"

    def test_agno_agent_has_tools(self):
        agent = ResearchAgent()
        assert len(agent.agent.tools) >= 1


class TestResearchAgentInstructions:
    def test_has_default_instructions(self):
        agent = ResearchAgent()
        assert len(agent.agent.instructions) >= 1

    def test_search_instruction_present(self):
        agent = ResearchAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "search" in instructions.lower()

    def test_accepts_custom_instructions(self):
        agent = ResearchAgent(extra_instructions=["Custom instruction"])
        assert len(agent.agent.instructions) == 1
        assert agent.agent.instructions[0] == "Custom instruction"


class TestResearchAgentRunStructured:
    @pytest.mark.asyncio
    async def test_run_structured_requires_message(self):
        agent = ResearchAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_returns_research_result_type(self):
        agent = ResearchAgent()
        assert agent._output_model is ResearchResult


class TestResearchAgentIntegration:
    def test_can_be_imported_via_agents_package(self):
        from backend.agents import ResearchAgent as Imported

        assert Imported is ResearchAgent

    @pytest.mark.asyncio
    async def test_mock_run_structured_returns_research_result(self):
        agent = ResearchAgent()
        mock_result = ResearchResult(
            market_size_findings=[
                ResearchFinding(
                    finding="Market is growing 15% annually",
                    source="https://example.com/market",
                    confidence=0.8,
                )
            ],
            industry_trends=[
                ResearchFinding(
                    finding="AI adoption increasing",
                    source="https://example.com/trends",
                    confidence=0.7,
                )
            ],
        )
        agent.run_structured = AsyncMock(return_value=mock_result)
        result = await agent.run_structured("Research this startup")

        assert isinstance(result, ResearchResult)
        assert len(result.market_size_findings) == 1
        assert result.market_size_findings[0].confidence == 0.8
        assert len(result.industry_trends) == 1

    def test_prompt_file_in_prompts_directory(self):
        prompt_file = Path(PROJECT_ROOT / "backend" / "prompts" / "research.md")
        assert prompt_file.exists()

    def test_prompt_matches_prompt_specification_template(self):
        prompt = (PROMPTS_DIR / "research.md").read_text(encoding="utf-8")
        assert prompt.strip().startswith("# Identity")


class TestDuckDuckGoToolStructure:
    def test_inherits_from_base_tool(self):
        from backend.tools.base_tool import BaseTool

        assert issubclass(DuckDuckGoTool, BaseTool)

    def test_name_set_correctly(self):
        assert DuckDuckGoTool.name == "duckduckgo_search"

    def test_description_set(self):
        assert len(DuckDuckGoTool.description) > 0

    def test_instantiation(self):
        tool = DuckDuckGoTool()
        assert tool.name == "duckduckgo_search"

    @pytest.mark.asyncio
    async def test_empty_query_returns_error(self):
        tool = DuckDuckGoTool()
        result = await tool.execute(query="")
        assert result.success is False
        assert "non-empty" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_whitespace_query_returns_error(self):
        tool = DuckDuckGoTool()
        result = await tool.execute(query="   ")
        assert result.success is False
        assert "non-empty" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_execute_calls_search(self):
        tool = DuckDuckGoTool()
        expected = [{"title": "Result 1", "body": "Body 1", "href": "https://example.com/1"}]

        async def fake_search(_query, _max):
            return expected

        tool._search = fake_search
        result = await tool.execute(query="test query")
        assert result.success is True
        assert result.data == expected

    @pytest.mark.asyncio
    async def test_search_exception_handled(self):
        tool = DuckDuckGoTool()

        async def failing_search(_query, _max):
            msg = "Connection error"
            raise RuntimeError(msg)

        tool._search = failing_search
        result = await tool.execute(query="test")
        assert result.success is False
        assert "Connection error" in (result.error or "")

    @pytest.mark.asyncio
    async def test_custom_max_results(self):
        tool = DuckDuckGoTool()
        call_kwargs = {}

        async def capture_search(query, max_results):
            call_kwargs["max_results"] = max_results
            return []

        tool._search = capture_search
        await tool.execute(query="test", max_results=10)
        assert call_kwargs["max_results"] == 10

    def test_adapter_works_with_duckduckgo_tool(self):
        from backend.tools.adapter import adapt_tool

        tool = DuckDuckGoTool()
        adapted = adapt_tool(tool)
        assert adapted.name == "duckduckgo_search"
        assert len(adapted.__doc__ or "") > 0
