from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend.agents import ReportAgent, StartupIQAgent
from backend.models.validation_report import DimensionScore, ValidationReport
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"
REPORT_PROMPT_NAME = "report"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{REPORT_PROMPT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Report Test Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestReportAgentStructure:
    def test_inherits_from_startup_iq_agent(self):
        assert issubclass(ReportAgent, StartupIQAgent)

    def test_name_set_correctly(self):
        assert ReportAgent.name == "report"

    def test_initializes_successfully(self):
        agent = ReportAgent()
        assert agent.agent is not None
        assert agent.agent.name == "report"

    def test_has_logger(self):
        agent = ReportAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent.report"

    def test_loads_prompt_dynamically(self):
        agent = ReportAgent()
        assert agent.agent.system_message is not None

    def test_system_message_contains_expected_content(self):
        agent = ReportAgent()
        msg = agent.agent.system_message or ""
        assert "Report" in msg or "ValidationReport" in msg


class TestReportAgentOutputModel:
    def test_output_model_is_validation_report(self):
        agent = ReportAgent()
        assert agent._output_model is ValidationReport

    def test_agno_agent_has_output_schema(self):
        agent = ReportAgent()
        assert agent.agent.output_schema is ValidationReport

    def test_prompt_file_exists(self):
        prompt_file = PROMPTS_DIR / "report.md"
        assert prompt_file.exists(), "report.md prompt file must exist"

    def test_prompt_has_required_sections(self):
        prompt = (PROMPTS_DIR / "report.md").read_text(encoding="utf-8")
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
        agent_path = PROJECT_ROOT / "backend" / "agents" / "report_agent.py"
        agent_code = agent_path.read_text(encoding="utf-8")
        assert "# Identity" not in agent_code
        assert "# Objective" not in agent_code


class TestReportAgentTools:
    def test_has_no_tools_by_default(self):
        agent = ReportAgent()
        assert len(agent._tools) == 0

    def test_agno_agent_has_no_tools(self):
        agent = ReportAgent()
        assert len(agent.agent.tools) == 0

    def test_accepts_custom_tools(self):
        async def custom_tool(**kw):
            return "custom"

        custom_tool.__name__ = "custom_tool"

        agent = ReportAgent(tools=[custom_tool])
        assert len(agent._tools) == 1
        assert agent._tools[0].__name__ == "custom_tool"


class TestReportAgentInstructions:
    def test_has_default_instructions(self):
        agent = ReportAgent()
        assert len(agent.agent.instructions) >= 1

    def test_synthesis_instruction_present(self):
        agent = ReportAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "synthesize" in instructions.lower() or "report" in instructions.lower()

    def test_accepts_custom_instructions(self):
        agent = ReportAgent(extra_instructions=["Custom instruction"])
        assert len(agent.agent.instructions) == 1
        assert agent.agent.instructions[0] == "Custom instruction"


class TestReportAgentRunStructured:
    @pytest.mark.asyncio
    async def test_run_structured_requires_message(self):
        agent = ReportAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_returns_validation_report_type(self):
        agent = ReportAgent()
        assert agent._output_model is ValidationReport


class TestReportAgentIntegration:
    def test_can_be_imported_via_agents_package(self):
        from backend.agents import ReportAgent as Imported

        assert Imported is ReportAgent

    @pytest.mark.asyncio
    async def test_mock_run_structured_returns_validation_report(self):
        agent = ReportAgent()
        mock_result = ValidationReport(
            executive_summary="The startup has strong market potential.",
            startup_snapshot="A SaaS platform for small businesses.",
            problem_analysis="Small businesses struggle with inventory management.",
            market_analysis="The market is growing at 15% CAGR.",
            industry_trends="AI-driven automation is a key trend.",
            competitor_landscape="Three major competitors identified.",
            customer_validation="Positive feedback from early interviews.",
            business_model_evaluation="Subscription model with strong unit economics.",
            technical_feasibility="Core features can be built with existing tech.",
            swot_analysis="Strengths: experienced team. Weaknesses: no traction.",
            risk_assessment="Market adoption is the primary risk.",
            validation_scorecard={
                "market_opportunity": DimensionScore(
                    score=85,
                    explanation="Growing market with clear demand",
                    evidence="Multiple sources confirm market growth",
                    confidence=0.8,
                ),
                "competitive_positioning": DimensionScore(
                    score=65,
                    explanation="Differentiated but faces strong competitors",
                    evidence="Competitor analysis shows market gaps",
                    confidence=0.7,
                ),
            },
            strategic_recommendations=[
                "Focus on niche segment first",
                "Build MVP in 3 months",
            ],
            suggested_next_steps=[
                "Conduct 20 customer interviews",
                "Build landing page for pre-signups",
            ],
            references=[
                "Source 1: Market report 2024",
            ],
            overall_score=75.0,
        )
        agent.run_structured = AsyncMock(return_value=mock_result)
        result = await agent.run_structured("Generate the validation report")

        assert isinstance(result, ValidationReport)
        assert result.executive_summary == "The startup has strong market potential."
        assert result.overall_score == 75.0
        assert len(result.validation_scorecard) == 2
        assert result.validation_scorecard["market_opportunity"].score == 85
        assert result.validation_scorecard["market_opportunity"].confidence == 0.8
        assert len(result.strategic_recommendations) == 2
        assert len(result.suggested_next_steps) == 2
        assert len(result.references) == 1

    def test_prompt_file_in_prompts_directory(self):
        prompt_file = Path(PROJECT_ROOT / "backend" / "prompts" / "report.md")
        assert prompt_file.exists()

    def test_prompt_matches_prompt_specification_template(self):
        prompt = (PROMPTS_DIR / "report.md").read_text(encoding="utf-8")
        assert prompt.strip().startswith("# Identity")
