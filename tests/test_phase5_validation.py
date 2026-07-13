from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents import (
    BusinessAgent,
    CompetitionAgent,
    PlannerAgent,
    ReportAgent,
    ResearchAgent,
    ReviewerAgent,
    StartupIQAgent,
)
from backend.agents.base_agent import StartupIQAgent as StartupIQAgentBase
from backend.models import (
    BusinessFindings,
    CompetitorAnalysis,
    ResearchResult,
    ReviewResult,
    StartupProfile,
    ValidationPlan,
    ValidationReport,
)
from backend.teams import DiscoveryTeam, ValidationTeam
from backend.teams.base_team import StartupIQTeam
from backend.teams.validation_team import ValidationTeamResult
from backend.utils.prompt_loader import clear_cache, get_prompt

ALL_AGENTS: list[tuple[str, type[StartupIQAgent], type]] = [
    ("planner", PlannerAgent, ValidationPlan),
    ("research", ResearchAgent, ResearchResult),
    ("competition", CompetitionAgent, CompetitorAnalysis),
    ("business", BusinessAgent, BusinessFindings),
    ("report", ReportAgent, ValidationReport),
    ("review", ReviewerAgent, ReviewResult),
]

ALL_MODELS: list[type] = [
    ValidationPlan,
    ResearchResult,
    CompetitorAnalysis,
    BusinessFindings,
    ValidationReport,
    ReviewResult,
    ValidationTeamResult,
]


def _valid_plan() -> ValidationPlan:
    return ValidationPlan(
        research_depth="quick",
        required_agents=["research", "competition"],
        execution_strategy="parallel",
        estimated_completion_seconds=300,
    )


def setup_module() -> None:
    clear_cache()


def teardown_module() -> None:
    clear_cache()


class TestEveryAgentImplemented:
    def test_all_six_agents_defined(self):
        assert len(ALL_AGENTS) == 6

    @pytest.mark.parametrize("name,agent_cls,output_model", ALL_AGENTS)
    def test_agent_inherits_startup_iq_agent(
        self, name: str, agent_cls: type[StartupIQAgent], output_model: type
    ) -> None:
        assert issubclass(agent_cls, StartupIQAgentBase)

    @pytest.mark.parametrize("name,agent_cls,output_model", ALL_AGENTS)
    def test_agent_initializes(
        self, name: str, agent_cls: type[StartupIQAgent], output_model: type
    ) -> None:
        agent = agent_cls()
        assert agent.agent is not None
        assert agent.name == name

    @pytest.mark.parametrize("name,agent_cls,output_model", ALL_AGENTS)
    def test_agent_exported_via_agents_package(
        self, name: str, agent_cls: type[StartupIQAgent], output_model: type
    ) -> None:
        module_name = agent_cls.__module__
        assert module_name.startswith("backend.agents")


class TestTeamExecutesSuccessfully:
    def test_validation_team_inherits_startup_iq_team(self):
        assert issubclass(ValidationTeam, StartupIQTeam)

    def test_validation_team_name_set(self):
        assert ValidationTeam.name == "Validation Team"

    def test_validation_team_has_six_members(self):
        team = ValidationTeam()
        assert len(team.team.members) == 6

    def test_validation_team_exported_via_teams_package(self):
        from backend.teams import ValidationTeam as ValidationTeamImported

        assert ValidationTeamImported is ValidationTeam

    def test_discovery_team_also_available(self):
        assert DiscoveryTeam.name == "Discovery Team"
        assert issubclass(DiscoveryTeam, StartupIQTeam)

    @pytest.mark.asyncio
    async def test_run_validation_with_mocked_agents(self):
        profile = StartupProfile(
            startup_name="Test",
            problem_statement="Test",
            target_customers="Test",
            solution="Test",
            business_model="Test",
            market_knowledge="Test",
            technical_information="Test",
        )

        def mock_agent(spec, ret):
            a = MagicMock(spec=spec)
            a.name = spec.name if hasattr(spec, "name") else "mock"
            a.run_structured = AsyncMock(return_value=ret)
            return a

        team = ValidationTeam(
            planner_agent=mock_agent(PlannerAgent, _valid_plan()),
            research_agent=mock_agent(ResearchAgent, ResearchResult()),
            competition_agent=mock_agent(CompetitionAgent, CompetitorAnalysis()),
            business_agent=mock_agent(BusinessAgent, BusinessFindings()),
            report_agent=mock_agent(ReportAgent, ValidationReport()),
            reviewer_agent=mock_agent(ReviewerAgent, ReviewResult()),
        )

        result = await team.run_validation(profile)

        assert isinstance(result, ValidationTeamResult)
        assert result.startup_profile is profile
        assert isinstance(result.validation_plan, ValidationPlan)
        assert isinstance(result.research_result, ResearchResult)
        assert isinstance(result.competitor_analysis, CompetitorAnalysis)
        assert isinstance(result.business_findings, BusinessFindings)
        assert isinstance(result.validation_report, ValidationReport)
        assert isinstance(result.review_result, ReviewResult)


class TestStructuredOutputsValidated:
    @pytest.mark.parametrize("name,agent_cls,output_model", ALL_AGENTS)
    def test_agent_has_output_model(
        self, name: str, agent_cls: type[StartupIQAgent], output_model: type
    ) -> None:
        agent = agent_cls()
        assert agent._output_model is not None
        assert agent._output_model is output_model

    @pytest.mark.parametrize("model_cls", ALL_MODELS)
    def test_model_is_pydantic(self, model_cls: type) -> None:
        import pydantic

        assert issubclass(model_cls, pydantic.BaseModel)

    @pytest.mark.parametrize("model_cls", ALL_MODELS)
    def test_model_instantiable(self, model_cls: type) -> None:
        if model_cls is ValidationPlan:
            instance = _valid_plan()
        elif model_cls is ValidationTeamResult:
            profile = StartupProfile(
                startup_name="T",
                problem_statement="T",
                target_customers="T",
                solution="T",
                business_model="T",
                market_knowledge="T",
                technical_information="T",
            )
            instance = ValidationTeamResult(
                startup_profile=profile,
                validation_plan=_valid_plan(),
                research_result=ResearchResult(),
                competitor_analysis=CompetitorAnalysis(),
                business_findings=BusinessFindings(),
                validation_report=ValidationReport(),
                review_result=ReviewResult(),
            )
        else:
            instance = model_cls()
        assert instance is not None

    def test_validation_team_result_contains_all_fields(self):
        profile = StartupProfile(
            startup_name="T",
            problem_statement="T",
            target_customers="T",
            solution="T",
            business_model="T",
            market_knowledge="T",
            technical_information="T",
        )
        result = ValidationTeamResult(
            startup_profile=profile,
            validation_plan=_valid_plan(),
            research_result=ResearchResult(),
            competitor_analysis=CompetitorAnalysis(),
            business_findings=BusinessFindings(),
            validation_report=ValidationReport(),
            review_result=ReviewResult(),
        )
        assert result.validation_plan is not None
        assert result.research_result is not None
        assert result.competitor_analysis is not None
        assert result.business_findings is not None
        assert result.validation_report is not None
        assert result.review_result is not None


class TestPromptLoadingVerified:
    @pytest.mark.parametrize("name,agent_cls,output_model", ALL_AGENTS)
    def test_prompt_loads_via_get_prompt(
        self, name: str, agent_cls: type[StartupIQAgent], output_model: type
    ) -> None:
        clear_cache()
        content = get_prompt(name)
        assert isinstance(content, str)
        assert len(content) > 100

    @pytest.mark.parametrize("name,agent_cls,output_model", ALL_AGENTS)
    def test_prompt_loaded_by_agent_constructor(
        self, name: str, agent_cls: type[StartupIQAgent], output_model: type
    ) -> None:
        clear_cache()
        agent = agent_cls()
        assert agent.agent.system_message is not None
        assert len(agent.agent.system_message) > 100

    def test_dynamic_loading_raises_for_missing_prompt(self):
        clear_cache()
        with pytest.raises(Exception):
            get_prompt("nonexistent_agent")


ALL_AGENT_NAMES = [name for name, _, _ in ALL_AGENTS]


class TestSmokeTestsPass:
    def test_all_agents_have_prompt_files(self):
        from pathlib import Path

        prompts_dir = Path(__file__).resolve().parent.parent / "backend" / "prompts"
        for name in ALL_AGENT_NAMES:
            prompt_path = prompts_dir / f"{name}.md"
            assert prompt_path.exists(), f"Missing prompt: {name}.md"

    def test_all_agent_names_match_prompts(self):
        for name, agent_cls, _ in ALL_AGENTS:
            assert agent_cls.name == name, (
                f"Agent {agent_cls.__name__}.name " f"is '{agent_cls.name}', expected '{name}'"
            )

    def test_prompt_count_matches_agent_count(self):
        from pathlib import Path

        prompts_dir = Path(__file__).resolve().parent.parent / "backend" / "prompts"
        prompt_files = [p for p in prompts_dir.iterdir() if p.suffix == ".md"]
        expected_count = len(ALL_AGENTS) + 1
        assert len(prompt_files) == expected_count, (
            f"Expected {expected_count} prompt files "
            f"({len(ALL_AGENTS)} Validation Team + 1 Discovery), "
            f"found {len(prompt_files)}"
        )
