from pathlib import Path

import pytest

from backend.agents.base_agent import StartupIQAgent
from backend.tools.adapter import adapt_tool, adapt_tools
from backend.tools.base_tool import BaseTool, ToolResponse
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"


class TestToolAdapter:
    def test_adapts_base_tool(self):
        class EchoTool(BaseTool):
            name = "echo"
            description = "Echoes input back"

            async def execute(self, value: str = "") -> ToolResponse:
                return ToolResponse(success=True, data=value)

        tool = EchoTool()
        adapted = adapt_tool(tool)
        assert adapted.__name__ == "echo"
        assert adapted.__doc__ == "Echoes input back"

    def test_adapt_rejects_non_base_tool(self):
        with pytest.raises(TypeError, match="BaseTool"):
            adapt_tool("not a tool")

    def test_adapt_tools_batch(self):
        class ToolA(BaseTool):
            name = "a"
            description = "Tool A"

            async def execute(self) -> ToolResponse:
                return ToolResponse(success=True, data="a")

        class ToolB(BaseTool):
            name = "b"
            description = "Tool B"

            async def execute(self) -> ToolResponse:
                return ToolResponse(success=True, data="b")

        adapted = adapt_tools([ToolA(), ToolB()])
        assert len(adapted) == 2
        assert adapted[0].__name__ == "a"
        assert adapted[1].__name__ == "b"


class TestToolIntegrationWithAgent:
    _prompt = "_test_tool_agent"

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        prompt_file = PROMPTS_DIR / f"{self._prompt}.md"
        prompt_file.write_text("# Tool Test Agent", encoding="utf-8")
        clear_cache()
        yield
        if prompt_file.exists():
            prompt_file.unlink()
            clear_cache()

    def test_agent_accepts_base_tools_in_constructor(self):
        class SearchTool(BaseTool):
            name = "search"
            description = "Searches the web"

            async def execute(self, query: str = "") -> ToolResponse:
                return ToolResponse(success=True, data=f"results for {query}")

        class ResearchAgent(StartupIQAgent):
            name = self._prompt

        agent = ResearchAgent(tools=[SearchTool()])
        assert len(agent._tools) == 1
        assert agent._tools[0].__name__ == "search"

    def test_agent_accepts_callable_tools(self):
        async def my_tool(**kw):
            return "done"

        my_tool.__name__ = "my_tool"

        class GenericAgent(StartupIQAgent):
            name = self._prompt

        agent = GenericAgent(tools=[my_tool])
        assert len(agent._tools) == 1

    def test_register_tools_post_init(self):
        class ToolX(BaseTool):
            name = "tool_x"
            description = "Tool X"

            async def execute(self) -> ToolResponse:
                return ToolResponse(success=True, data="x")

        class DynamicAgent(StartupIQAgent):
            name = self._prompt

        agent = DynamicAgent()
        assert len(agent._tools) == 0

        agent.register_tools([ToolX()])
        assert len(agent._tools) == 1
        assert agent._tools[0].__name__ == "tool_x"

    def test_register_tools_updates_agno_agent(self):
        class ToolY(BaseTool):
            name = "tool_y"
            description = "Tool Y"

            async def execute(self) -> ToolResponse:
                return ToolResponse(success=True, data="y")

        class UpdatingAgent(StartupIQAgent):
            name = self._prompt

        agent = UpdatingAgent()
        assert len(agent.agent.tools) == 0

        agent.register_tools([ToolY()])
        assert len(agent.agent.tools) == 1
