from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.discovery_agent import DiscoveryAgent
from backend.agents.profile_generator import _build_prompt_from_input
from backend.models.startup_profile import StartupProfile
from backend.teams.discovery_team import DiscoveryTeam
from backend.utils.prompt_loader import clear_cache, get_prompt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"
DISCOVERY_PROMPT_NAME = "discovery"
DISCOVERY_PROMPT_PATH = PROMPTS_DIR / f"{DISCOVERY_PROMPT_NAME}.md"


def setup_module() -> None:
    if not DISCOVERY_PROMPT_PATH.exists():
        DISCOVERY_PROMPT_PATH.write_text("# Discovery Agent Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


VALID_INPUT = {
    "startup_name": "EcoTrack",
    "problem_statement": "People cannot monitor their carbon footprint easily.",
    "target_customers": "Environmentally conscious millennials.",
    "solution": "A mobile app that tracks carbon footprint via purchase receipts.",
    "business_model": "Freemium with premium subscription at $4.99/month.",
    "market_knowledge": "Growing demand for climate-friendly products.",
    "technical_information": "Flutter app, Python backend, ML recommendation engine.",
    "tagline": "Know your impact.",
    "founder_assumptions": "Users will scan receipts daily.",
    "validation_objectives": "Validate willingness to pay.",
    "industry": "Climate Tech",
    "stage": "idea",
}


def _make_mock_agent(result: StartupProfile) -> MagicMock:
    agent = MagicMock(spec=DiscoveryAgent)
    agent.run_structured = AsyncMock(return_value=result)
    agent.name = "discovery"
    return agent


class TestDiscoveryWorkflowHappyPath:
    @pytest.mark.asyncio
    async def test_complete_workflow_returns_startup_profile(self):
        expected = StartupProfile(**VALID_INPUT)
        team = DiscoveryTeam(discovery_agent=_make_mock_agent(expected))

        result = await team.run_discovery(VALID_INPUT)

        assert isinstance(result, StartupProfile)
        assert result.startup_name == "EcoTrack"

    @pytest.mark.asyncio
    async def test_all_required_fields_populated(self):
        expected = StartupProfile(**VALID_INPUT)
        team = DiscoveryTeam(discovery_agent=_make_mock_agent(expected))

        result = await team.run_discovery(VALID_INPUT)

        for field in [
            "startup_name",
            "problem_statement",
            "target_customers",
            "solution",
            "business_model",
            "market_knowledge",
            "technical_information",
        ]:
            value = getattr(result, field, "")
            assert isinstance(value, str) and value.strip(), f"{field} should be non-empty"

    @pytest.mark.asyncio
    async def test_optional_fields_included(self):
        expected = StartupProfile(**VALID_INPUT)
        team = DiscoveryTeam(discovery_agent=_make_mock_agent(expected))

        result = await team.run_discovery(VALID_INPUT)

        assert result.tagline == "Know your impact."
        assert result.founder_assumptions == "Users will scan receipts daily."
        assert result.validation_objectives == "Validate willingness to pay."
        assert result.industry == "Climate Tech"
        assert result.stage == "idea"

    @pytest.mark.asyncio
    async def test_output_validates_as_pydantic_model(self):
        expected = StartupProfile(**VALID_INPUT)
        team = DiscoveryTeam(discovery_agent=_make_mock_agent(expected))

        result = await team.run_discovery(VALID_INPUT)

        dumped = result.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["startup_name"] == "EcoTrack"

    @pytest.mark.asyncio
    async def test_agent_executed_once(self):
        mock_agent = _make_mock_agent(StartupProfile(**VALID_INPUT))
        team = DiscoveryTeam(discovery_agent=mock_agent)

        await team.run_discovery(VALID_INPUT)

        mock_agent.run_structured.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_agent_receives_formatted_message(self):
        mock_agent = _make_mock_agent(StartupProfile(**VALID_INPUT))
        team = DiscoveryTeam(discovery_agent=mock_agent)

        await team.run_discovery(VALID_INPUT)

        msg = mock_agent.run_structured.await_args[0][0]
        assert "EcoTrack" in msg
        assert "carbon footprint" in msg
        assert "StartupProfile" in msg
        assert "confidence" in msg.lower()

    @pytest.mark.asyncio
    async def test_industry_and_stage_passed_to_agent(self):
        mock_agent = _make_mock_agent(StartupProfile(**VALID_INPUT))
        team = DiscoveryTeam(discovery_agent=mock_agent)

        await team.run_discovery(VALID_INPUT)

        msg = mock_agent.run_structured.await_args[0][0]
        assert "Climate Tech" in msg


class TestDiscoveryWorkflowValidation:
    @pytest.mark.asyncio
    async def test_missing_required_field_raises_error(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception, match="Missing fields"):
            await team.run_discovery({"startup_name": "IncompleteCo"})

    @pytest.mark.asyncio
    async def test_multiple_missing_fields_reported(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception) as exc:
            await team.run_discovery({})

        msg = str(exc.value)
        assert "Missing fields" in msg
        assert "startup_name" in msg
        assert "problem_statement" in msg

    @pytest.mark.asyncio
    async def test_invalid_stage_rejected(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception, match="Invalid"):
            await team.run_discovery({**VALID_INPUT, "stage": "pre-seed"})

    @pytest.mark.asyncio
    async def test_empty_string_required_field_rejected(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception, match="Missing fields"):
            await team.run_discovery(
                {
                    **VALID_INPUT,
                    "startup_name": "",
                    "problem_statement": "",
                }
            )

    @pytest.mark.asyncio
    async def test_whitespace_only_field_triggers_validation(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception, match="Missing fields"):
            await team.run_discovery({**VALID_INPUT, "startup_name": "   "})


class TestDiscoveryWorkflowNormalization:
    @pytest.mark.asyncio
    async def test_whitespace_trimmed_before_agent(self):
        agent = _make_mock_agent(
            StartupProfile(
                startup_name="TrimCo",
                problem_statement="Problem",
                target_customers="Users",
                solution="Solution",
                business_model="Free",
                market_knowledge="Big",
                technical_information="Go",
            )
        )
        team = DiscoveryTeam(discovery_agent=agent)

        await team.run_discovery(
            {
                "startup_name": "  TrimCo  ",
                "problem_statement": "  Problem  ",
                "target_customers": "  Users  ",
                "solution": "  Solution  ",
                "business_model": "  Free  ",
                "market_knowledge": "  Big  ",
                "technical_information": "  Go  ",
            }
        )

        msg = agent.run_structured.await_args[0][0]
        assert "  TrimCo  " not in msg
        assert "TrimCo" in msg

    @pytest.mark.asyncio
    async def test_stage_lowercased(self):
        agent = _make_mock_agent(
            StartupProfile(
                startup_name="StageCo",
                problem_statement="Problem",
                target_customers="Users",
                solution="Solution",
                business_model="Free",
                market_knowledge="Big",
                technical_information="Go",
                stage="prototype",
            )
        )
        team = DiscoveryTeam(discovery_agent=agent)

        await team.run_discovery(
            {
                **VALID_INPUT,
                "stage": "PROTOTYPE",
            }
        )

        msg = agent.run_structured.await_args[0][0]
        assert "prototype" in msg

    @pytest.mark.asyncio
    async def test_missing_stage_defaults_to_idea(self):
        agent = _make_mock_agent(
            StartupProfile(
                startup_name="DefaultStage",
                problem_statement="Problem",
                target_customers="Users",
                solution="Solution",
                business_model="Free",
                market_knowledge="Big",
                technical_information="Go",
            )
        )
        team = DiscoveryTeam(discovery_agent=agent)

        input_data = {k: v for k, v in VALID_INPUT.items() if k != "stage"}
        await team.run_discovery(input_data)

        msg = agent.run_structured.await_args[0][0]
        assert "idea" in msg


class TestDiscoveryWorkflowPromptLoading:
    def test_prompt_loaded_from_file(self):
        prompt = get_prompt(DISCOVERY_PROMPT_NAME)
        assert prompt is not None
        assert len(prompt) > 0

    def test_agent_loads_prompt_dynamically(self):
        agent = DiscoveryAgent()
        system_message = agent.agent.system_message or ""
        assert len(system_message) > 0
        assert "# Identity" in system_message or "Discovery" in system_message

    def test_prompt_file_exists(self):
        assert DISCOVERY_PROMPT_PATH.exists()

    def test_prompt_matches_template_structure(self):
        prompt = get_prompt(DISCOVERY_PROMPT_NAME)
        sections = [
            "# Identity",
            "# Objective",
            "# Responsibilities",
            "# Constraints",
            "# Expected Output",
            "# Quality Checklist",
        ]
        for section in sections:
            assert section in prompt, f"Missing section: {section}"

    def test_no_hardcoded_prompt_in_agent_code(self):
        agent_path = PROJECT_ROOT / "backend" / "agents" / "discovery_agent.py"
        agent_code = agent_path.read_text(encoding="utf-8")
        assert "# Identity" not in agent_code
        assert "# Objective" not in agent_code


class TestDiscoveryWorkflowIntegration:
    @pytest.mark.asyncio
    async def test_workflow_uses_real_prompt_file(self):
        expected = StartupProfile(**VALID_INPUT)
        agent = _make_mock_agent(expected)
        team = DiscoveryTeam(discovery_agent=agent)

        await team.run_discovery(VALID_INPUT)

        msg = agent.run_structured.await_args[0][0]
        sections_in_msg = msg.count("## ")
        assert sections_in_msg >= 5

    @pytest.mark.asyncio
    async def test_valid_input_with_minimal_fields(self):
        minimal = {
            "startup_name": "MinimalCo",
            "problem_statement": "Minimal problem",
            "target_customers": "Minimal users",
            "solution": "Minimal solution",
            "business_model": "Minimal model",
            "market_knowledge": "Minimal knowledge",
            "technical_information": "Minimal tech",
        }
        expected = StartupProfile(**minimal)
        team = DiscoveryTeam(discovery_agent=_make_mock_agent(expected))

        result = await team.run_discovery(minimal)

        assert result.startup_name == "MinimalCo"
        assert result.tagline == ""
        assert result.stage == "idea"

    @pytest.mark.asyncio
    async def test_build_prompt_omits_empty_optionals(self):
        minimal = {
            "startup_name": "MinimalCo",
            "problem_statement": "Problem",
            "target_customers": "Users",
            "solution": "Solution",
            "business_model": "Free",
            "market_knowledge": "Big",
            "technical_information": "Go",
        }
        prompt = _build_prompt_from_input(minimal)
        assert "## Tagline" not in prompt
        assert "## Founder Assumptions" not in prompt
        assert "## Validation Objectives" not in prompt


class TestDiscoveryWorkflowEdgeCases:
    @pytest.mark.asyncio
    async def test_very_long_field_value(self):
        agent = _make_mock_agent(
            StartupProfile(
                startup_name="LongCo",
                problem_statement="x" * 500,
                target_customers="Users",
                solution="Solution",
                business_model="Free",
                market_knowledge="Big",
                technical_information="Go",
            )
        )
        team = DiscoveryTeam(discovery_agent=agent)

        result = await team.run_discovery(
            {
                **VALID_INPUT,
                "startup_name": "LongCo",
                "problem_statement": "x" * 500,
            }
        )

        assert isinstance(result, StartupProfile)
        assert result.startup_name == "LongCo"
