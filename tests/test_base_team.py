from pathlib import Path

import pytest

from backend.agents.base_agent import StartupIQAgent
from backend.teams.base_team import StartupIQTeam
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


class TestStartupIQTeamValidation:
    def test_name_required(self):
        class NamelessTeam(StartupIQTeam):
            pass

        with pytest.raises(ValueError, match="name"):
            NamelessTeam()

    def test_team_without_members(self):
        class SoloTeam(StartupIQTeam):
            name = "_test_empty_team"

        team = SoloTeam()
        assert team.team is not None
        assert team.team.name == "_test_empty_team"

    def test_team_logger(self):
        class LoggedTeam(StartupIQTeam):
            name = "_test_logged_team"

        team = LoggedTeam()
        assert team.logger is not None
        assert team.logger.name == "team._test_logged_team"


class TestStartupIQTeamComposition:
    _prompt_agents = ["_test_agent_one", "_test_agent_two"]

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        for p in self._prompt_agents:
            _ensure_test_prompt(p)
        yield
        for p in self._prompt_agents:
            _remove_test_prompt(p)

    def test_team_accepts_startup_iq_agents(self):
        class AgentA(StartupIQAgent):
            name = "_test_agent_one"

        class AgentB(StartupIQAgent):
            name = "_test_agent_two"

        class ComposedTeam(StartupIQTeam):
            name = "_test_composed_team"

        a = AgentA()
        b = AgentB()
        team = ComposedTeam(members=[a, b])

        assert len(team.team.members) == 2
        assert team.team.members[0].name == "_test_agent_one"
        assert team.team.members[1].name == "_test_agent_two"

    def test_team_accepts_raw_agno_agents(self):
        from agno.agent import Agent

        class RawTeam(StartupIQTeam):
            name = "_test_raw_team"

        raw_a = Agent(name="_raw_one")
        raw_b = Agent(name="_raw_two")
        team = RawTeam(members=[raw_a, raw_b])

        assert len(team.team.members) == 2

    def test_team_passes_instructions_to_agno(self):
        class InstructedTeam(StartupIQTeam):
            name = "_test_instructed_team"

        team = InstructedTeam(instructions=["Be thorough", "Cite sources"])
        assert len(team.team.instructions) == 2
        assert "Be thorough" in team.team.instructions

    def test_team_passes_context(self):
        class ContextTeam(StartupIQTeam):
            name = "_test_context_team"

        ctx = {"mode": "quick", "industry": "fintech"}
        team = ContextTeam(context=ctx)
        assert team.team.additional_context == ctx

    def test_team_markdown_setting(self):
        class MdTeam(StartupIQTeam):
            name = "_test_md_team"

        team = MdTeam(markdown=True)
        assert team.team.markdown is True

    def test_team_show_members_responses(self):
        class ShowTeam(StartupIQTeam):
            name = "_test_show_team"

        team = ShowTeam(show_members_responses=True)
        assert team.team.show_members_responses is True
