from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.models.startup_profile import StartupProfile
from backend.teams import DiscoveryTeam, StartupIQTeam
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"

DISCOVERY_AGENT_NAME = "discovery"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{DISCOVERY_AGENT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Discovery prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestDiscoveryTeamStructure:
    def test_inherits_from_startup_iq_team(self):
        assert issubclass(DiscoveryTeam, StartupIQTeam)

    def test_name_set_correctly(self):
        assert DiscoveryTeam.name == "Discovery Team"

    def test_initializes_without_arguments(self):
        team = DiscoveryTeam()
        assert team.team is not None
        assert team.team.name == "Discovery Team"

    def test_creates_default_discovery_agent(self):
        team = DiscoveryTeam()
        assert team._discovery_agent is not None

    def test_has_default_instructions(self):
        team = DiscoveryTeam()
        assert len(team.team.instructions) == 3
        assert any("StartupProfile" in i for i in team.team.instructions)

    def test_accepts_custom_instructions(self):
        team = DiscoveryTeam(instructions=["Custom instruction"])
        assert len(team.team.instructions) == 1
        assert team.team.instructions[0] == "Custom instruction"

    def test_accepts_context(self):
        ctx = {"mode": "basic"}
        team = DiscoveryTeam(context=ctx)
        assert team.team.additional_context == ctx

    def test_logger_configured(self):
        team = DiscoveryTeam()
        assert team.logger is not None
        assert team.logger.name == "team.Discovery Team"

    def test_team_has_one_member(self):
        team = DiscoveryTeam()
        assert len(team.team.members) == 1
        assert team.team.members[0].name == "discovery"

    def test_markdown_setting_default(self):
        team = DiscoveryTeam()
        assert team.team.markdown is True

    def test_markdown_setting_disabled(self):
        team = DiscoveryTeam(markdown=False)
        assert team.team.markdown is False

    def test_show_members_responses_default(self):
        team = DiscoveryTeam()
        assert team.team.show_members_responses is False


class TestDiscoveryTeamRunDiscovery:
    def _make_mock_agent(self, profile: StartupProfile):
        agent = MagicMock()
        agent.run_structured = AsyncMock(return_value=profile)
        return agent

    VALID_INPUT = {
        "startup_name": "TestCo",
        "problem_statement": "A big problem",
        "target_customers": "Developers",
        "solution": "A platform",
        "business_model": "SaaS",
        "market_knowledge": "Growing",
        "technical_information": "Python",
    }

    @pytest.mark.asyncio
    async def test_returns_startup_profile(self):
        expected = StartupProfile(**self.VALID_INPUT)
        team = DiscoveryTeam(discovery_agent=self._make_mock_agent(expected))

        result = await team.run_discovery(self.VALID_INPUT)

        assert isinstance(result, StartupProfile)
        assert result.startup_name == "TestCo"

    @pytest.mark.asyncio
    async def test_required_fields_populated(self):
        input_data = {
            "startup_name": "RequiredCo",
            "problem_statement": "Critical problem",
            "target_customers": "Enterprise",
            "solution": "Enterprise solution",
            "business_model": "Per-seat licensing",
            "market_knowledge": "Fortune 500 demand",
            "technical_information": "Java, Kubernetes",
        }
        expected = StartupProfile(**input_data)
        team = DiscoveryTeam(discovery_agent=self._make_mock_agent(expected))

        result = await team.run_discovery(input_data)

        assert result.startup_name.strip() != ""
        assert result.problem_statement.strip() != ""
        assert result.target_customers.strip() != ""
        assert result.solution.strip() != ""
        assert result.business_model.strip() != ""
        assert result.market_knowledge.strip() != ""
        assert result.technical_information.strip() != ""

    @pytest.mark.asyncio
    async def test_includes_optional_fields(self):
        input_data = {**self.VALID_INPUT}
        input_data["tagline"] = "We do stuff"
        input_data["founder_assumptions"] = "People will pay"
        input_data["stage"] = "prototype"
        input_data["industry"] = "Fintech"

        expected = StartupProfile(**input_data)
        team = DiscoveryTeam(discovery_agent=self._make_mock_agent(expected))

        result = await team.run_discovery(input_data)

        assert result.tagline == "We do stuff"
        assert result.founder_assumptions == "People will pay"
        assert result.stage == "prototype"
        assert result.industry == "Fintech"

    @pytest.mark.asyncio
    async def test_raises_on_missing_required_fields(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception) as exc_info:
            await team.run_discovery({"startup_name": "IncompleteCo"})

        assert "Missing fields" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_raises_on_invalid_stage(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception) as exc_info:
            await team.run_discovery({**self.VALID_INPUT, "stage": "invalid_stage"})

        assert "Invalid" in str(exc_info.value) or "invalid_stage" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_input_raises_error(self):
        team = DiscoveryTeam()

        with pytest.raises(Exception) as exc_info:
            await team.run_discovery({})

        assert "Missing fields" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_passes_normalized_input_to_agent(self):
        expected = StartupProfile(**self.VALID_INPUT)
        mock_agent = MagicMock()
        mock_agent.run_structured = AsyncMock(return_value=expected)

        team = DiscoveryTeam(discovery_agent=mock_agent)
        await team.run_discovery({**self.VALID_INPUT, "stage": "PROTOTYPE"})

        mock_agent.run_structured.assert_awaited_once()
        call_args = mock_agent.run_structured.await_args[0][0]
        assert "prototype" in call_args

    @pytest.mark.asyncio
    async def test_accepts_custom_discovery_agent(self):
        expected = StartupProfile(**self.VALID_INPUT)
        custom_agent = self._make_mock_agent(expected)

        team = DiscoveryTeam(discovery_agent=custom_agent)
        result = await team.run_discovery(self.VALID_INPUT)

        assert team._discovery_agent is custom_agent
        assert isinstance(result, StartupProfile)

    @pytest.mark.asyncio
    async def test_whitespace_only_fields_handled(self):
        input_data = {
            "startup_name": "  WhitespaceCo  ",
            "problem_statement": "  A problem  ",
            "target_customers": "  Everyone  ",
            "solution": "  A solution  ",
            "business_model": "  Free  ",
            "market_knowledge": "  Large  ",
            "technical_information": "  Rust  ",
        }
        expected = StartupProfile(
            startup_name="WhitespaceCo",
            problem_statement="A problem",
            target_customers="Everyone",
            solution="A solution",
            business_model="Free",
            market_knowledge="Large",
            technical_information="Rust",
        )
        team = DiscoveryTeam(discovery_agent=self._make_mock_agent(expected))

        result = await team.run_discovery(input_data)

        assert result.startup_name == "WhitespaceCo"
