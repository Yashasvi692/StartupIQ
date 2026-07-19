from pathlib import Path

import pytest

from backend.agents import (
    BusinessAgent,
    CompetitionAgent,
    DiscoveryAgent,
    PlannerAgent,
    ReportAgent,
    ResearchAgent,
    ReviewerAgent,
    StartupIQAgent,
)
from backend.models import (
    BusinessFindings,
    CompetitorAnalysis,
    ResearchResult,
    ReviewResult,
    StartupProfile,
    ValidationPlan,
    ValidationReport,
)
from backend.utils.prompt_loader import clear_cache, get_prompt

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "backend" / "prompts"

REQUIRED_SECTIONS = [
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

AGENT_PROMPT_MAP: list[tuple[str, type[StartupIQAgent], type]] = [
    ("discovery", DiscoveryAgent, StartupProfile),
    ("planner", PlannerAgent, ValidationPlan),
    ("research", ResearchAgent, ResearchResult),
    ("competition", CompetitionAgent, CompetitorAnalysis),
    ("business", BusinessAgent, BusinessFindings),
    ("report", ReportAgent, ValidationReport),
    ("review", ReviewerAgent, ReviewResult),
]


def _agent_path(agent_cls: type[StartupIQAgent]) -> Path:
    module_path = agent_cls.__module__.replace(".", "/")
    return Path(__file__).resolve().parent.parent / f"{module_path}.py"


def setup_module() -> None:
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestPromptFilesExist:
    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_prompt_file_exists(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        prompt_path = PROMPTS_DIR / f"{prompt_name}.md"
        assert prompt_path.exists(), f"Prompt file {prompt_name}.md must exist"


class TestPromptFollowsSpecification:
    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_has_all_required_sections(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        prompt = (PROMPTS_DIR / f"{prompt_name}.md").read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            assert section in prompt, f"Prompt '{prompt_name}.md' missing section: {section}"

    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_starts_with_identity(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        prompt = (PROMPTS_DIR / f"{prompt_name}.md").read_text(encoding="utf-8")
        assert prompt.strip().startswith(
            "# Identity"
        ), f"Prompt '{prompt_name}.md' must start with # Identity"


class TestDynamicLoadingWorks:
    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_loads_via_sync_get_prompt(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        clear_cache()
        content = get_prompt(prompt_name)
        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    @pytest.mark.asyncio
    async def test_loads_via_agent_constructor(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        clear_cache()
        agent = agent_cls()
        assert agent.agent.system_message is not None
        assert len(agent.agent.system_message) > 0


class TestNoEmbeddedPrompts:
    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_no_hardcoded_sections_in_agent_code(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        agent_path = _agent_path(agent_cls)
        agent_code = agent_path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            assert (
                section not in agent_code
            ), f"Hardcoded prompt section '{section}' found in {agent_path.name}"

    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_agent_loads_prompt_dynamically(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        clear_cache()
        agent = agent_cls()
        dynamic_content = get_prompt(prompt_name)
        assert (
            agent.agent.system_message == dynamic_content
        ), f"Agent '{prompt_name}' system_message does not match dynamically loaded prompt"


class TestOutputMatchesContract:
    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_prompt_mentions_output_model(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        prompt = (PROMPTS_DIR / f"{prompt_name}.md").read_text(encoding="utf-8")
        model_name = output_model.__name__
        assert (
            model_name in prompt
        ), f"Prompt '{prompt_name}.md' must mention '{model_name}' in Expected Output"

    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_agent_output_model_matches_prompt(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        clear_cache()
        agent = agent_cls()
        assert agent._output_model is output_model, (
            f"Agent '{prompt_name}' output_model must be "
            f"{output_model.__name__}, got {agent._output_model.__name__}"
        )

    @pytest.mark.parametrize("prompt_name,agent_cls,output_model", AGENT_PROMPT_MAP)
    def test_agent_name_matches_prompt_filename(
        self,
        prompt_name: str,
        agent_cls: type[StartupIQAgent],
        output_model: type,
    ) -> None:
        assert (
            agent_cls.name == prompt_name
        ), f"Agent name '{agent_cls.name}' must match prompt name '{prompt_name}'"
