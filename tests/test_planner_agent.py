from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend.agents import PlannerAgent, StartupIQAgent
from backend.models.validation_plan import ValidationPlan
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"
PLANNER_PROMPT_NAME = "planner"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{PLANNER_PROMPT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Planner Test Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestPlannerAgentStructure:
    def test_inherits_from_startup_iq_agent(self):
        assert issubclass(PlannerAgent, StartupIQAgent)

    def test_name_set_correctly(self):
        assert PlannerAgent.name == "planner"

    def test_initializes_successfully(self):
        agent = PlannerAgent()
        assert agent.agent is not None
        assert agent.agent.name == "planner"

    def test_has_logger(self):
        agent = PlannerAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent.planner"

    def test_loads_prompt_dynamically(self):
        agent = PlannerAgent()
        assert agent.agent.system_message is not None

    def test_system_message_contains_expected_content(self):
        agent = PlannerAgent()
        msg = agent.agent.system_message or ""
        assert "ValidationPlan" in msg or "Planner" in msg


class TestPlannerAgentOutputModel:
    def test_output_model_is_validation_plan(self):
        agent = PlannerAgent()
        assert agent._output_model is ValidationPlan

    def test_agno_agent_has_output_schema(self):
        agent = PlannerAgent()
        assert agent.agent.output_schema is ValidationPlan

    def test_prompt_file_exists(self):
        prompt_file = PROMPTS_DIR / "planner.md"
        assert prompt_file.exists(), "planner.md prompt file must exist"

    def test_prompt_has_required_sections(self):
        prompt = (PROMPTS_DIR / "planner.md").read_text(encoding="utf-8")
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
        agent_path = PROJECT_ROOT / "backend" / "agents" / "planner_agent.py"
        agent_code = agent_path.read_text(encoding="utf-8")
        assert "# Identity" not in agent_code
        assert "# Objective" not in agent_code


class TestPlannerAgentInstructions:
    def test_has_default_instructions(self):
        agent = PlannerAgent()
        assert len(agent.agent.instructions) >= 1

    def test_validation_strategy_instruction_present(self):
        agent = PlannerAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "validation" in instructions.lower()
        assert "strategy" in instructions.lower()

    def test_accepts_custom_instructions(self):
        agent = PlannerAgent(extra_instructions=["Custom instruction"])
        assert len(agent.agent.instructions) == 1
        assert agent.agent.instructions[0] == "Custom instruction"


class TestPlannerAgentRunStructured:
    @pytest.mark.asyncio
    async def test_run_structured_requires_message(self):
        agent = PlannerAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_returns_validation_plan_type(self):
        agent = PlannerAgent()
        assert agent._output_model is ValidationPlan


class TestPlannerAgentIntegration:
    def test_can_be_imported_via_agents_package(self):
        from backend.agents import PlannerAgent as ImportedPlanner

        assert ImportedPlanner is PlannerAgent

    @pytest.mark.asyncio
    async def test_mock_run_structured_returns_validation_plan(self):
        agent = PlannerAgent()
        mock_result = ValidationPlan(
            research_depth="quick",
            required_agents=["research", "competition"],
            execution_strategy="Basic validation with market research",
            estimated_completion_seconds=120,
            research_categories=["market size", "industry trends"],
        )
        agent.run_structured = AsyncMock(return_value=mock_result)
        result = await agent.run_structured("Analyze this startup")

        assert isinstance(result, ValidationPlan)
        assert result.research_depth == "quick"
        assert "research" in result.required_agents
        assert result.estimated_completion_seconds == 120

    def test_prompt_file_in_prompts_directory(self):
        prompt_file = Path(PROJECT_ROOT / "backend" / "prompts" / "planner.md")
        assert prompt_file.exists()

    def test_prompt_matches_prompt_specification_template(self):
        prompt = (PROMPTS_DIR / "planner.md").read_text(encoding="utf-8")
        assert prompt.strip().startswith("# Identity")
        assert "## Reasoning Instructions" not in prompt
