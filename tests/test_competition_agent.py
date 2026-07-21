from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend.agents import CompetitionAgent, StartupIQAgent
from backend.models.competitor_analysis import Competitor, CompetitorAnalysis
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"
COMPETITION_PROMPT_NAME = "competition"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{COMPETITION_PROMPT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Competition Test Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestCompetitionAgentStructure:
    def test_inherits_from_startup_iq_agent(self):
        assert issubclass(CompetitionAgent, StartupIQAgent)

    def test_name_set_correctly(self):
        assert CompetitionAgent.name == "competition"

    def test_initializes_successfully(self):
        agent = CompetitionAgent()
        assert agent.agent is not None
        assert agent.agent.name == "competition"

    def test_has_logger(self):
        agent = CompetitionAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent.competition"

    def test_loads_prompt_dynamically(self):
        agent = CompetitionAgent()
        assert agent.agent.system_message is not None

    def test_system_message_contains_expected_content(self):
        agent = CompetitionAgent()
        msg = agent.agent.system_message or ""
        assert "Competition" in msg or "CompetitorAnalysis" in msg


class TestCompetitionAgentOutputModel:
    def test_output_model_is_competitor_analysis(self):
        agent = CompetitionAgent()
        assert agent._output_model is CompetitorAnalysis

    def test_agno_agent_has_output_schema(self):
        agent = CompetitionAgent()
        assert agent.agent.output_schema is CompetitorAnalysis

    def test_prompt_file_exists(self):
        prompt_file = PROMPTS_DIR / "competition.md"
        assert prompt_file.exists(), "competition.md prompt file must exist"

    def test_prompt_has_required_sections(self):
        prompt = (PROMPTS_DIR / "competition.md").read_text(encoding="utf-8")
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
        agent_path = PROJECT_ROOT / "backend" / "agents" / "competition_agent.py"
        agent_code = agent_path.read_text(encoding="utf-8")
        assert "# Identity" not in agent_code
        assert "# Objective" not in agent_code


class TestCompetitionAgentTools:
    def test_has_duckduckgo_tool_by_default(self):
        agent = CompetitionAgent()
        assert len(agent._tools) == 1
        assert agent._tools[0].name == "duckduckgo_search"

    def test_accepts_custom_tools(self):
        async def custom_tool(**kw):
            return "custom"

        custom_tool.__name__ = "custom_tool"

        agent = CompetitionAgent(tools=[custom_tool])
        assert len(agent._tools) == 1
        assert agent._tools[0].__name__ == "custom_tool"

    def test_agno_agent_has_tools(self):
        agent = CompetitionAgent()
        assert len(agent.agent.tools) >= 1


class TestCompetitionAgentInstructions:
    def test_has_default_instructions(self):
        agent = CompetitionAgent()
        assert len(agent.agent.instructions) >= 1

    def test_competitor_search_instruction_present(self):
        agent = CompetitionAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "competitor" in instructions.lower() or "search" in instructions.lower()

    def test_accepts_custom_instructions(self):
        agent = CompetitionAgent(extra_instructions=["Custom instruction"])
        assert len(agent.agent.instructions) == 7
        assert agent.agent.instructions[0] == "Custom instruction"
        assert "Use tools only when necessary." in agent.agent.instructions


class TestCompetitionAgentRunStructured:
    @pytest.mark.asyncio
    async def test_run_structured_requires_message(self):
        agent = CompetitionAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_returns_competitor_analysis_type(self):
        agent = CompetitionAgent()
        assert agent._output_model is CompetitorAnalysis


class TestCompetitionAgentIntegration:
    def test_can_be_imported_via_agents_package(self):
        from backend.agents import CompetitionAgent as Imported

        assert Imported is CompetitionAgent

    @pytest.mark.asyncio
    async def test_mock_run_structured_returns_competitor_analysis(self):
        agent = CompetitionAgent()
        mock_result = CompetitorAnalysis(
            direct_competitors=[
                Competitor(
                    name="CompA",
                    description="A direct competitor",
                    strengths=["Strong brand"],
                    weaknesses=["Expensive"],
                    pricing="$10/mo",
                    market_share="30%",
                )
            ],
            indirect_competitors=[
                Competitor(
                    name="CompB",
                    description="An indirect competitor",
                    strengths=["Free tier"],
                    weaknesses=["Limited features"],
                )
            ],
            market_gaps=["No solution for small businesses"],
            differentiators=["AI-powered automation"],
            competitive_threat_level="medium",
        )
        agent.run_structured = AsyncMock(return_value=mock_result)
        result = await agent.run_structured("Analyze competition for this startup")

        assert isinstance(result, CompetitorAnalysis)
        assert len(result.direct_competitors) == 1
        assert result.direct_competitors[0].name == "CompA"
        assert len(result.indirect_competitors) == 1
        assert len(result.market_gaps) == 1
        assert result.competitive_threat_level == "medium"

    def test_prompt_file_in_prompts_directory(self):
        prompt_file = Path(PROJECT_ROOT / "backend" / "prompts" / "competition.md")
        assert prompt_file.exists()

    def test_prompt_matches_prompt_specification_template(self):
        prompt = (PROMPTS_DIR / "competition.md").read_text(encoding="utf-8")
        assert prompt.strip().startswith("# Identity")
