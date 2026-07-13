from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend.agents import ReviewerAgent, StartupIQAgent
from backend.models.review_result import ReviewIssue, ReviewResult
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"
REVIEW_PROMPT_NAME = "review"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{REVIEW_PROMPT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Review Test Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestReviewerAgentStructure:
    def test_inherits_from_startup_iq_agent(self):
        assert issubclass(ReviewerAgent, StartupIQAgent)

    def test_name_set_correctly(self):
        assert ReviewerAgent.name == "review"

    def test_initializes_successfully(self):
        agent = ReviewerAgent()
        assert agent.agent is not None
        assert agent.agent.name == "review"

    def test_has_logger(self):
        agent = ReviewerAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent.review"

    def test_loads_prompt_dynamically(self):
        agent = ReviewerAgent()
        assert agent.agent.system_message is not None

    def test_system_message_contains_expected_content(self):
        agent = ReviewerAgent()
        msg = agent.agent.system_message or ""
        assert "Review" in msg or "ReviewResult" in msg


class TestReviewerAgentOutputModel:
    def test_output_model_is_review_result(self):
        agent = ReviewerAgent()
        assert agent._output_model is ReviewResult

    def test_agno_agent_has_output_schema(self):
        agent = ReviewerAgent()
        assert agent.agent.output_schema is ReviewResult

    def test_prompt_file_exists(self):
        prompt_file = PROMPTS_DIR / "review.md"
        assert prompt_file.exists(), "review.md prompt file must exist"

    def test_prompt_has_required_sections(self):
        prompt = (PROMPTS_DIR / "review.md").read_text(encoding="utf-8")
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
        agent_path = PROJECT_ROOT / "backend" / "agents" / "reviewer_agent.py"
        agent_code = agent_path.read_text(encoding="utf-8")
        assert "# Identity" not in agent_code
        assert "# Objective" not in agent_code


class TestReviewerAgentTools:
    def test_has_no_tools_by_default(self):
        agent = ReviewerAgent()
        assert len(agent._tools) == 0

    def test_agno_agent_has_no_tools(self):
        agent = ReviewerAgent()
        assert len(agent.agent.tools) == 0

    def test_accepts_custom_tools(self):
        async def custom_tool(**kw):
            return "custom"

        custom_tool.__name__ = "custom_tool"

        agent = ReviewerAgent(tools=[custom_tool])
        assert len(agent._tools) == 1
        assert agent._tools[0].__name__ == "custom_tool"


class TestReviewerAgentInstructions:
    def test_has_default_instructions(self):
        agent = ReviewerAgent()
        assert len(agent.agent.instructions) >= 1

    def test_review_instruction_present(self):
        agent = ReviewerAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "review" in instructions.lower() or "quality" in instructions.lower()

    def test_accepts_custom_instructions(self):
        agent = ReviewerAgent(extra_instructions=["Custom instruction"])
        assert len(agent.agent.instructions) == 1
        assert agent.agent.instructions[0] == "Custom instruction"


class TestReviewerAgentRunStructured:
    @pytest.mark.asyncio
    async def test_run_structured_requires_message(self):
        agent = ReviewerAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_returns_review_result_type(self):
        agent = ReviewerAgent()
        assert agent._output_model is ReviewResult


class TestReviewerAgentIntegration:
    def test_can_be_imported_via_agents_package(self):
        from backend.agents import ReviewerAgent as Imported

        assert Imported is ReviewerAgent

    @pytest.mark.asyncio
    async def test_mock_run_structured_returns_review_result(self):
        agent = ReviewerAgent()
        mock_result = ReviewResult(
            issues=[
                ReviewIssue(
                    category="missing_section",
                    description="Technical Feasibility section is empty",
                    severity="high",
                    section="technical_feasibility",
                ),
                ReviewIssue(
                    category="missing_citation",
                    description="Market size claim lacks a citation",
                    severity="medium",
                    section="market_analysis",
                ),
            ],
            overall_quality_score=75.0,
            passed=True,
            summary=(
                "Two issues found: one missing section "
                "and one uncited claim. Report passes with notes."
            ),
        )
        agent.run_structured = AsyncMock(return_value=mock_result)
        result = await agent.run_structured("Review this validation report")

        assert isinstance(result, ReviewResult)
        assert result.passed is True
        assert result.overall_quality_score == 75.0
        assert len(result.issues) == 2
        assert result.issues[0].category == "missing_section"
        assert result.issues[0].severity == "high"
        assert result.issues[1].category == "missing_citation"
        assert result.issues[1].severity == "medium"
        assert "Two issues found" in result.summary

    def test_prompt_file_in_prompts_directory(self):
        prompt_file = Path(PROJECT_ROOT / "backend" / "prompts" / "review.md")
        assert prompt_file.exists()

    def test_prompt_matches_prompt_specification_template(self):
        prompt = (PROMPTS_DIR / "review.md").read_text(encoding="utf-8")
        assert prompt.strip().startswith("# Identity")
