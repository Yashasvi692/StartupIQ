from pathlib import Path

import pytest
from pydantic import BaseModel

from backend.agents.base_agent import StartupIQAgent
from backend.utils.prompt_loader import clear_cache

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "backend" / "prompts"


class TestAgentRunStructuredEdgeCases:
    _prompt = "_test_run_struct_edge"

    @pytest.fixture(autouse=True)
    def setup_prompt(self):
        prompt_file = PROMPTS_DIR / f"{self._prompt}.md"
        prompt_file.write_text("# Edge Case Agent Prompt", encoding="utf-8")
        clear_cache()
        yield
        if prompt_file.exists():
            prompt_file.unlink()
            clear_cache()

    @pytest.mark.asyncio
    async def test_dict_content_parsed_to_model(self):
        class TestOutput(BaseModel):
            result: str
            score: int

        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()
        expected_dict = {"result": "hello", "score": 42}

        async def mock_arun(message, **kw):
            class MockResponse:
                content = expected_dict

            return MockResponse()

        agent.agent.arun = mock_arun
        result = await agent.run_structured("test", output_model=TestOutput)
        assert isinstance(result, TestOutput)
        assert result.result == "hello"
        assert result.score == 42

    @pytest.mark.asyncio
    async def test_missing_message_raises_type_error(self):
        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()
        with pytest.raises(TypeError):
            await agent.run_structured()

    @pytest.mark.asyncio
    async def test_run_structured_without_output_model_raises(self):
        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()
        with pytest.raises(ValueError, match="No output model set"):
            await agent.run_structured("test input")


class TestAgentInstructions:
    _prompt = "_test_agent_instructions"

    @pytest.fixture(autouse=True)
    def setup_prompt(self):
        prompt_file = PROMPTS_DIR / f"{self._prompt}.md"
        prompt_file.write_text("# Instructions Test Prompt", encoding="utf-8")
        clear_cache()
        yield
        if prompt_file.exists():
            prompt_file.unlink()
            clear_cache()

    def test_no_instructions_creates_empty_list(self):
        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()
        assert agent.agent.instructions == []

    def test_single_custom_instruction(self):
        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent(extra_instructions=["Be thorough"])
        assert len(agent.agent.instructions) == 1
        assert agent.agent.instructions[0] == "Be thorough"

    def test_multiple_custom_instructions(self):
        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent(extra_instructions=["Be thorough", "Cite sources", "Be concise"])
        assert len(agent.agent.instructions) == 3

    def test_instructions_are_strings(self):
        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent(extra_instructions=["Do good work"])
        for instr in agent.agent.instructions:
            assert isinstance(instr, str)


class TestAgentOutputModelEdgeCases:
    _prompt = "_test_output_model_agent"

    @pytest.fixture(autouse=True)
    def setup_prompt(self):
        prompt_file = PROMPTS_DIR / f"{self._prompt}.md"
        prompt_file.write_text("# Output Model Test Prompt", encoding="utf-8")
        clear_cache()
        yield
        if prompt_file.exists():
            prompt_file.unlink()
            clear_cache()

    def test_constructor_output_model_set(self):
        class TestOutput(BaseModel):
            value: str

        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent(output_model=TestOutput)
        assert agent._output_model is TestOutput
        assert agent.agent.output_schema is TestOutput

    def test_no_output_model_defaults_to_none(self):
        class TestAgent(StartupIQAgent):
            name = self._prompt

        agent = TestAgent()
        assert agent._output_model is None
        assert agent.agent.output_schema is None
