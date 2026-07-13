from pathlib import Path

import pytest

from backend.agents.base_agent import StartupIQAgent
from backend.llm import LLMConfig
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"


class TestStartupIQAgentValidation:
    def test_name_required(self):
        class NamelessAgent(StartupIQAgent):
            pass

        with pytest.raises(ValueError, match="name"):
            NamelessAgent()

    def test_subclass_with_name(self):
        class TestAgent(StartupIQAgent):
            name = "_test_agent_validate"

        assert TestAgent.name == "_test_agent_validate"

    def test_prompt_missing_raises_error(self):
        class MissingPromptAgent(StartupIQAgent):
            name = "_nonexistent_prompt_agent"

        with pytest.raises(Exception):
            MissingPromptAgent()


class TestStartupIQAgentComposition:
    @pytest.fixture(autouse=True)
    def setup_prompt(self):
        prompt_name = "_test_siq_agent"
        prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
        prompt_file.write_text("# Test Agent Prompt", encoding="utf-8")
        clear_cache()
        yield
        if prompt_file.exists():
            prompt_file.unlink()
            clear_cache()

    def test_agent_creates_agno_agent(self):
        class TestAgent(StartupIQAgent):
            name = "_test_siq_agent"

        agent = TestAgent()
        assert agent.agent is not None
        assert agent.agent.name == "_test_siq_agent"
        assert agent.agent.system_message == "# Test Agent Prompt"

    def test_agent_has_logger(self):
        class TestAgent(StartupIQAgent):
            name = "_test_siq_agent"

        agent = TestAgent()
        assert agent.logger is not None
        assert agent.logger.name == "agent._test_siq_agent"

    def test_agent_uses_llm_factory(self):
        class TestAgent(StartupIQAgent):
            name = "_test_siq_agent"

        config = LLMConfig(model="google/gemma-4-26b-a4b-it:free")
        agent = TestAgent(llm_config=config)
        assert agent.agent.model is not None
        assert agent.agent.model.id == "google/gemma-4-26b-a4b-it:free"

    def test_agent_accepts_instructions(self):
        class TestAgent(StartupIQAgent):
            name = "_test_siq_agent"

        agent = TestAgent(extra_instructions=["Use markdown", "Be concise"])
        assert len(agent.agent.instructions) == 2

    def test_agent_accepts_output_schema(self):
        from pydantic import BaseModel

        class TestOutput(BaseModel):
            result: str

        class TestAgent(StartupIQAgent):
            name = "_test_siq_agent"

        agent = TestAgent(output_model=TestOutput)
        assert agent.agent.output_schema is TestOutput


class TestStartupIQAgentStructuredOutput:
    _prompt = "_test_siq_struct"

    @pytest.fixture(autouse=True)
    def setup_prompt(self):
        prompt_file = PROMPTS_DIR / f"{self._prompt}.md"
        prompt_file.write_text("# Test Agent Prompt", encoding="utf-8")
        clear_cache()
        yield
        if prompt_file.exists():
            prompt_file.unlink()
            clear_cache()

    @pytest.mark.asyncio
    async def test_run_structured_requires_model(self):
        from pydantic import BaseModel

        class TestOutput(BaseModel):
            result: str

        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()
        with pytest.raises(ValueError, match="No output model set"):
            await agent.run_structured("test input")

    @pytest.mark.asyncio
    async def test_run_structured_with_constructor_model(self):
        from pydantic import BaseModel

        class TestOutput(BaseModel):
            result: str
            score: int

        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent(output_model=TestOutput)

        async def mock_arun(message, **kw):
            return _MockRunOutput(content={"result": "hello", "score": 42})

        agent.agent.arun = mock_arun
        result = await agent.run_structured("test input")
        assert isinstance(result, TestOutput)
        assert result.result == "hello"
        assert result.score == 42

    @pytest.mark.asyncio
    async def test_run_structured_with_per_call_model(self):
        from pydantic import BaseModel

        class PerCallOutput(BaseModel):
            value: str

        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()

        async def mock_arun(message, **kw):
            return _MockRunOutput(content={"value": "per-call"})

        agent.agent.arun = mock_arun
        result = await agent.run_structured("test", output_model=PerCallOutput)
        assert isinstance(result, PerCallOutput)
        assert result.value == "per-call"

    @pytest.mark.asyncio
    async def test_run_structured_accepts_base_model_content(self):
        from pydantic import BaseModel

        class TestOutput(BaseModel):
            result: str

        class TestAgent(StartupIQAgent):
            name = self._prompt

        instance = TestOutput(result="already_parsed")

        agent = TestAgent()

        async def mock_arun(message, **kw):
            return _MockRunOutput(content=instance)

        agent.agent.arun = mock_arun
        result = await agent.run_structured("test", output_model=TestOutput)
        assert result is instance

    @pytest.mark.asyncio
    async def test_run_structured_rejects_invalid_content(self):
        from pydantic import BaseModel

        class TestOutput(BaseModel):
            result: str

        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()

        async def mock_arun(message, **kw):
            return _MockRunOutput(content=42)

        agent.agent.arun = mock_arun
        with pytest.raises(TypeError):
            await agent.run_structured("test", output_model=TestOutput)


class _MockRunOutput:
    def __init__(self, content):
        self.content = content
