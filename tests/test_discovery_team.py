from pathlib import Path

from backend.teams import DiscoveryTeam, StartupIQTeam
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"


def _ensure_test_prompt(name: str) -> None:
    prompt_file = PROMPTS_DIR / f"{name}.md"
    if not prompt_file.exists():
        prompt_file.write_text(f"# {name} prompt", encoding="utf-8")
    clear_cache()


def _remove_test_prompt(name: str) -> None:
    prompt_file = PROMPTS_DIR / f"{name}.md"
    if prompt_file.exists():
        prompt_file.unlink()
    clear_cache()


class TestDiscoveryTeam:
    def test_inherits_from_startup_iq_team(self):
        assert issubclass(DiscoveryTeam, StartupIQTeam)

    def test_name_set_correctly(self):
        assert DiscoveryTeam.name == "Discovery Team"

    def test_initializes_without_members(self):
        team = DiscoveryTeam()
        assert team.team is not None
        assert team.team.name == "Discovery Team"

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

    def test_accepts_startup_iq_agent_member(self):
        from backend.agents.base_agent import StartupIQAgent

        _ensure_test_prompt("_test_discovery_member")

        class MockAgent(StartupIQAgent):
            name = "_test_discovery_member"

        agent = MockAgent()
        team = DiscoveryTeam(members=[agent])
        assert len(team.team.members) == 1
        assert team.team.members[0].name == "_test_discovery_member"

        _remove_test_prompt("_test_discovery_member")

    def test_markdown_setting_default(self):
        team = DiscoveryTeam()
        assert team.team.markdown is True

    def test_markdown_setting_disabled(self):
        team = DiscoveryTeam(markdown=False)
        assert team.team.markdown is False

    def test_show_members_responses_default(self):
        team = DiscoveryTeam()
        assert team.team.show_members_responses is False
