from pathlib import Path

from backend.agents.base_agent import StartupIQAgent
from backend.llm.factory import create_llm
from backend.llm.providers import AgnoProvider
from backend.teams.base_team import StartupIQTeam
from backend.teams.discovery_team import DiscoveryTeam
from backend.utils.prompt_loader import clear_cache, get_prompt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"

SMOKE_PROMPT_NAME = "_smoke_test_prompt"


def setup_module() -> None:
    prompt_file = PROMPTS_DIR / f"{SMOKE_PROMPT_NAME}.md"
    prompt_file.write_text("# Smoke Test Agent", encoding="utf-8")
    clear_cache()


def teardown_module() -> None:
    prompt_file = PROMPTS_DIR / f"{SMOKE_PROMPT_NAME}.md"
    if prompt_file.exists():
        prompt_file.unlink()
    clear_cache()


class TestAIInfrastructureSmoke:
    def test_llm_factory_works(self):
        llm = create_llm()
        assert llm is not None

    def test_agno_provider_default(self):
        from backend.llm.config import LLMConfig

        config = LLMConfig()
        provider = AgnoProvider(config)
        assert provider is not None

    def test_startup_iq_agent_works(self):
        class SmokeAgent(StartupIQAgent):
            name = SMOKE_PROMPT_NAME

        agent = SmokeAgent()
        assert agent.agent is not None
        assert agent.agent.system_message is not None

    def test_startup_iq_team_works(self):
        class SmokeTeam(StartupIQTeam):
            name = "_smoke_test_team"

        team = SmokeTeam()
        assert team.team is not None

    def test_prompt_loading_works(self):
        prompt = get_prompt(SMOKE_PROMPT_NAME)
        assert "# Smoke Test Agent" in prompt

    def test_structured_output_schema_registered(self):
        from pydantic import BaseModel

        class TestModel(BaseModel):
            result: str

        class SchemaAgent(StartupIQAgent):
            name = SMOKE_PROMPT_NAME

        agent = SchemaAgent(output_model=TestModel)
        assert agent._output_model is TestModel
        assert agent.agent.output_schema is TestModel

    def test_tool_registration_works(self):
        from backend.tools.base_tool import BaseTool, ToolResponse

        class SmokeTool(BaseTool):
            name = "smoke_tool"
            description = "A smoke test tool"

            async def execute(self) -> ToolResponse:
                return ToolResponse(success=True, data="smoke")

        class ToolAgent(StartupIQAgent):
            name = SMOKE_PROMPT_NAME

        agent = ToolAgent(tools=[SmokeTool()])
        assert len(agent._tools) == 1

    def test_discovery_team_initializes(self):
        team = DiscoveryTeam()
        assert team.team is not None
        assert team.team.name == "Discovery Team"

    def test_agno_importable(self):
        import agno

        assert agno is not None

    def test_llm_created_with_custom_provider(self):
        from backend.llm.config import LLMConfig

        config = LLMConfig(model="openai/gpt-4o-mini", temperature=0.7, max_tokens=4096)
        llm = create_llm(config=config)
        assert llm is not None

    def test_prompt_cache_clears(self):
        clear_cache()
        prompt = get_prompt(SMOKE_PROMPT_NAME)
        assert prompt is not None
        clear_cache()
