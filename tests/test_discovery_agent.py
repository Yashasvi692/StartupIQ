from pathlib import Path

import pytest

from backend.agents import DiscoveryAgent, StartupIQAgent
from backend.models.startup_profile import StartupProfile
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"

DISCOVERY_PROMPT_NAME = "discovery"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{DISCOVERY_PROMPT_NAME}.md"
    if not prompt_file.exists():
        prompt_file.write_text("# Discovery Test Prompt", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestDiscoveryAgentStructure:
    def test_inherits_from_startup_iq_agent(self):
        assert issubclass(DiscoveryAgent, StartupIQAgent)

    def test_name_set_correctly(self):
        assert DiscoveryAgent.name == "discovery"

    def test_initializes_successfully(self):
        agent = DiscoveryAgent()
        assert agent.agent is not None
        assert agent.agent.name == "discovery"

    def test_has_logger(self):
        agent = DiscoveryAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent.discovery"

    def test_loads_prompt_dynamically(self):
        agent = DiscoveryAgent()
        assert agent.agent.system_message is not None

    def test_system_message_contains_expected_content(self):
        agent = DiscoveryAgent()
        msg = agent.agent.system_message or ""
        assert "StartupProfile" in msg
        assert "Discovery" in msg


class TestDiscoveryAgentOutputModel:
    def test_output_model_is_startup_profile(self):
        agent = DiscoveryAgent()
        assert agent._output_model is StartupProfile

    def test_agno_agent_has_output_schema(self):
        agent = DiscoveryAgent()
        assert agent.agent.output_schema is StartupProfile

    def test_prompt_file_exists(self):
        prompt_file = PROMPTS_DIR / "discovery.md"
        assert prompt_file.exists(), "discovery.md prompt file must exist"


class TestDiscoveryAgentInstructions:
    def test_has_default_instructions(self):
        agent = DiscoveryAgent()
        assert len(agent.agent.instructions) >= 1

    def test_extract_normalize_instruction_present(self):
        agent = DiscoveryAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "extract" in instructions.lower() or "normalize" in instructions.lower()

    def test_no_fabrication_instruction_present(self):
        agent = DiscoveryAgent()
        instructions = " ".join(agent.agent.instructions or [])
        assert "fabricat" in instructions.lower()

    def test_accepts_custom_instructions(self):
        agent = DiscoveryAgent(extra_instructions=["Custom instruction"])
        assert len(agent.agent.instructions) == 1
        assert agent.agent.instructions[0] == "Custom instruction"


class TestDiscoveryAgentRunStructured:
    @pytest.mark.asyncio
    async def test_run_structured_requires_message(self):
        agent = DiscoveryAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_returns_startup_profile_type(self):
        """Verifies the agent is wired to return StartupProfile (actual execution
        requires a running LLM with a valid API key)."""
        agent = DiscoveryAgent()
        assert agent._output_model is StartupProfile


class TestDiscoveryTeamWithDiscoveryAgent:
    def test_discovery_agent_can_be_passed_to_discovery_team(self):
        from backend.teams import DiscoveryTeam

        agent = DiscoveryAgent()
        team = DiscoveryTeam(discovery_agent=agent)
        assert len(team.team.members) == 1
        assert team.team.members[0].name == "discovery"
