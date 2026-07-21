from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend.agents import BusinessAgent, StartupIQAgent
from backend.models.business_findings import (
    SWOT,
    BusinessFindings,
    Opportunity,
    Recommendation,
    Risk,
)
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"
BUSINESS_PROMPT_NAME = "business"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{BUSINESS_PROMPT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Business Test Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestBusinessAgentStructure:
    def test_inherits_from_startup_iq_agent(self):
        assert issubclass(BusinessAgent, StartupIQAgent)

    def test_name_set_correctly(self):
        assert BusinessAgent.name == "business"

    def test_initializes_successfully(self):
        agent = BusinessAgent()
        assert agent.agent is not None
        assert agent.agent.name == "business"

    def test_has_logger(self):
        agent = BusinessAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent.business"

    def test_loads_prompt_dynamically(self):
        agent = BusinessAgent()
        assert agent.agent.system_message is not None

    def test_system_message_contains_expected_content(self):
        agent = BusinessAgent()
        msg = agent.agent.system_message or ""
        assert "Business" in msg or "BusinessFindings" in msg


class TestBusinessAgentOutputModel:
    def test_output_model_is_business_findings(self):
        agent = BusinessAgent()
        assert agent._output_model is BusinessFindings

    def test_agno_agent_has_output_schema(self):
        agent = BusinessAgent()
        assert agent.agent.output_schema is BusinessFindings

    def test_prompt_file_exists(self):
        prompt_file = PROMPTS_DIR / "business.md"
        assert prompt_file.exists(), "business.md prompt file must exist"

    def test_prompt_has_required_sections(self):
        prompt = (PROMPTS_DIR / "business.md").read_text(encoding="utf-8")
        sections = [
            "# Identity",
            "# Objective",
            "# Responsibilities",
            "# Constraints",
            "# Inputs",
            "# Available Context",
            "# Reasoning Instructions",
            "# Expected Output",
            "# Quality Checklist",
        ]
        for section in sections:
            assert section in prompt, f"Missing section: {section}"

    def test_no_hardcoded_prompt_in_agent_code(self):
        agent_path = PROJECT_ROOT / "backend" / "agents" / "business_agent.py"
        agent_code = agent_path.read_text(encoding="utf-8")
        assert "# Identity" not in agent_code
        assert "# Objective" not in agent_code


class TestBusinessAgentTools:
    def test_has_no_tools_by_default(self):
        agent = BusinessAgent()
        assert len(agent._tools) == 0

    def test_agno_agent_has_no_tools(self):
        agent = BusinessAgent()
        assert len(agent.agent.tools) == 0

    def test_has_deterministic_search_internally(self):
        from backend.workflows.deterministic_search import DeterministicSearch

        agent = BusinessAgent()
        assert isinstance(agent._search, DeterministicSearch)


class TestBusinessAgentInstructions:
    def test_has_default_instructions(self):
        agent = BusinessAgent()
        assert len(agent.agent.instructions) >= 1

    def test_swot_instruction_present(self):
        agent = BusinessAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "swot" in instructions.lower() or "analysis" in instructions.lower()

    def test_accepts_custom_instructions(self):
        agent = BusinessAgent(extra_instructions=["Custom instruction"])
        assert len(agent.agent.instructions) == 1
        assert agent.agent.instructions[0] == "Custom instruction"


class TestBusinessAgentRunStructured:
    @pytest.mark.asyncio
    async def test_run_structured_requires_message(self):
        agent = BusinessAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_returns_business_findings_type(self):
        agent = BusinessAgent()
        assert agent._output_model is BusinessFindings


class TestBusinessAgentIntegration:
    def test_can_be_imported_via_agents_package(self):
        from backend.agents import BusinessAgent as Imported

        assert Imported is BusinessAgent

    @pytest.mark.asyncio
    async def test_mock_run_structured_returns_business_findings(self):
        agent = BusinessAgent()
        mock_result = BusinessFindings(
            swot=SWOT(
                strengths=["Strong founding team"],
                weaknesses=["No revenue yet"],
                opportunities=["Growing market"],
                threats=["Established competitors"],
            ),
            risks=[
                Risk(
                    risk="Market adoption risk",
                    severity="high",
                    likelihood="medium",
                    mitigation="Early adopter program",
                )
            ],
            opportunities=[
                Opportunity(opportunity="Partnership with distributors", priority="high")
            ],
            business_model_evaluation="Freemium model with strong unit economics",
            strategic_recommendations=[
                Recommendation(
                    recommendation="Launch MVP in 3 months",
                    rationale="Market window closing soon",
                    confidence=0.8,
                )
            ],
            validation_score=72.5,
        )
        agent.run_structured = AsyncMock(return_value=mock_result)
        result = await agent.run_structured("Analyze this startup")

        assert isinstance(result, BusinessFindings)
        assert len(result.swot.strengths) == 1
        assert len(result.risks) == 1
        assert result.risks[0].severity == "high"
        assert len(result.opportunities) == 1
        assert result.validation_score == 72.5
        assert len(result.strategic_recommendations) == 1
        assert result.strategic_recommendations[0].confidence == 0.8

    def test_prompt_file_in_prompts_directory(self):
        prompt_file = Path(PROJECT_ROOT / "backend" / "prompts" / "business.md")
        assert prompt_file.exists()

    def test_prompt_matches_prompt_specification_template(self):
        prompt = (PROMPTS_DIR / "business.md").read_text(encoding="utf-8")
        assert prompt.strip().startswith("# Identity")
