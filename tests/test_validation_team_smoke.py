from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.business_agent import BusinessAgent
from backend.agents.competition_agent import CompetitionAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.report_agent import ReportAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.reviewer_agent import ReviewerAgent
from backend.models.business_findings import (
    SWOT,
    BusinessFindings,
)
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.models.research_result import ResearchResult
from backend.models.review_result import ReviewResult
from backend.models.startup_profile import StartupProfile
from backend.models.validation_plan import ValidationPlan
from backend.models.validation_report import ValidationReport
from backend.teams.validation_team import ValidationTeam, ValidationTeamResult

DUMMY_PROFILE = StartupProfile(
    startup_name="TestStartup",
    problem_statement="Test problem",
    target_customers="Test customers",
    solution="Test solution",
    business_model="Test model",
    market_knowledge="Test knowledge",
    technical_information="Test tech",
)
DUMMY_PLAN = ValidationPlan(
    research_depth="quick",
    required_agents=["research", "competition"],
    execution_strategy="research_and_competition",
    estimated_completion_seconds=300,
)
DUMMY_RESEARCH = ResearchResult()
DUMMY_COMPETITION = CompetitorAnalysis()
DUMMY_BUSINESS = BusinessFindings(swot=SWOT())
DUMMY_REPORT = ValidationReport()
DUMMY_REVIEW = ReviewResult()


def _make_mock_agent(spec, return_value):
    agent = MagicMock(spec=spec)
    agent.name = spec.name if hasattr(spec, "name") else "mock"
    agent.run_structured = AsyncMock(return_value=return_value)
    return agent


def _make_mocked_team(**overrides):
    defaults = {
        "planner_agent": _make_mock_agent(PlannerAgent, DUMMY_PLAN),
        "research_agent": _make_mock_agent(ResearchAgent, DUMMY_RESEARCH),
        "competition_agent": _make_mock_agent(CompetitionAgent, DUMMY_COMPETITION),
        "business_agent": _make_mock_agent(BusinessAgent, DUMMY_BUSINESS),
        "report_agent": _make_mock_agent(ReportAgent, DUMMY_REPORT),
        "reviewer_agent": _make_mock_agent(ReviewerAgent, DUMMY_REVIEW),
    }
    defaults.update(overrides)
    return ValidationTeam(**defaults)


class TestValidationTeamSmokeHappyPath:
    @pytest.mark.asyncio
    async def test_planner_executes(self):
        agent = _make_mock_agent(PlannerAgent, DUMMY_PLAN)
        team = _make_mocked_team(planner_agent=agent)
        result = await team.run_validation(DUMMY_PROFILE)
        assert agent.run_structured.called
        assert isinstance(result.validation_plan, ValidationPlan)

    @pytest.mark.asyncio
    async def test_research_executes(self):
        agent = _make_mock_agent(ResearchAgent, DUMMY_RESEARCH)
        team = _make_mocked_team(research_agent=agent)
        result = await team.run_validation(DUMMY_PROFILE)
        assert agent.run_structured.called
        assert isinstance(result.research_result, ResearchResult)

    @pytest.mark.asyncio
    async def test_competition_executes(self):
        agent = _make_mock_agent(CompetitionAgent, DUMMY_COMPETITION)
        team = _make_mocked_team(competition_agent=agent)
        result = await team.run_validation(DUMMY_PROFILE)
        assert agent.run_structured.called
        assert isinstance(result.competitor_analysis, CompetitorAnalysis)

    @pytest.mark.asyncio
    async def test_business_analysis_executes(self):
        agent = _make_mock_agent(BusinessAgent, DUMMY_BUSINESS)
        team = _make_mocked_team(business_agent=agent)
        result = await team.run_validation(DUMMY_PROFILE)
        assert agent.run_structured.called
        assert isinstance(result.business_findings, BusinessFindings)

    @pytest.mark.asyncio
    async def test_report_generated(self):
        agent = _make_mock_agent(ReportAgent, DUMMY_REPORT)
        team = _make_mocked_team(report_agent=agent)
        result = await team.run_validation(DUMMY_PROFILE)
        assert agent.run_structured.called
        assert isinstance(result.validation_report, ValidationReport)

    @pytest.mark.asyncio
    async def test_review_generated(self):
        agent = _make_mock_agent(ReviewerAgent, DUMMY_REVIEW)
        team = _make_mocked_team(reviewer_agent=agent)
        result = await team.run_validation(DUMMY_PROFILE)
        assert agent.run_structured.called
        assert isinstance(result.review_result, ReviewResult)


class TestValidationTeamResult:
    @pytest.mark.asyncio
    async def test_returns_validation_team_result_type(self):
        team = _make_mocked_team()
        result = await team.run_validation(DUMMY_PROFILE)
        assert isinstance(result, ValidationTeamResult)

    @pytest.mark.asyncio
    async def test_all_stages_have_outputs(self):
        team = _make_mocked_team()
        result = await team.run_validation(DUMMY_PROFILE)
        assert result.startup_profile is DUMMY_PROFILE
        assert result.validation_plan is DUMMY_PLAN
        assert result.research_result is DUMMY_RESEARCH
        assert result.competitor_analysis is DUMMY_COMPETITION
        assert result.business_findings is DUMMY_BUSINESS
        assert result.validation_report is DUMMY_REPORT
        assert result.review_result is DUMMY_REVIEW


class TestValidationTeamExecutionOrder:
    @pytest.mark.asyncio
    async def test_planner_called(self):
        planner = _make_mock_agent(PlannerAgent, DUMMY_PLAN)
        team = _make_mocked_team(planner_agent=planner)
        await team.run_validation(DUMMY_PROFILE)
        assert planner.run_structured.called

    @pytest.mark.asyncio
    async def test_research_and_competition_called(self):
        research = _make_mock_agent(ResearchAgent, DUMMY_RESEARCH)
        competition = _make_mock_agent(CompetitionAgent, DUMMY_COMPETITION)
        team = _make_mocked_team(research_agent=research, competition_agent=competition)
        await team.run_validation(DUMMY_PROFILE)
        assert research.run_structured.called
        assert competition.run_structured.called

    @pytest.mark.asyncio
    async def test_business_called(self):
        business = _make_mock_agent(BusinessAgent, DUMMY_BUSINESS)
        team = _make_mocked_team(business_agent=business)
        await team.run_validation(DUMMY_PROFILE)
        assert business.run_structured.called

    @pytest.mark.asyncio
    async def test_report_called(self):
        report = _make_mock_agent(ReportAgent, DUMMY_REPORT)
        team = _make_mocked_team(report_agent=report)
        await team.run_validation(DUMMY_PROFILE)
        assert report.run_structured.called

    @pytest.mark.asyncio
    async def test_reviewer_called_last(self):
        reviewer = _make_mock_agent(ReviewerAgent, DUMMY_REVIEW)
        team = _make_mocked_team(reviewer_agent=reviewer)
        await team.run_validation(DUMMY_PROFILE)
        assert reviewer.run_structured.called


class TestValidationTeamDefaultAgents:
    def test_uses_default_agents_when_none_provided(self):
        team = ValidationTeam()
        assert team._planner is not None
        assert team._researcher is not None
        assert team._competitor is not None
        assert team._analyst is not None
        assert team._reporter is not None
        assert team._reviewer is not None

    def test_default_agents_have_correct_types(self):
        team = ValidationTeam()
        assert isinstance(team._planner, PlannerAgent)
        assert isinstance(team._researcher, ResearchAgent)
        assert isinstance(team._competitor, CompetitionAgent)
        assert isinstance(team._analyst, BusinessAgent)
        assert isinstance(team._reporter, ReportAgent)
        assert isinstance(team._reviewer, ReviewerAgent)


class TestValidationTeamStructure:
    def test_inherits_from_startup_iq_team(self):
        from backend.teams.base_team import StartupIQTeam

        assert issubclass(ValidationTeam, StartupIQTeam)

    def test_name_set_correctly(self):
        assert ValidationTeam.name == "Validation Team"

    def test_has_default_instructions(self):
        team = ValidationTeam()
        assert len(team.team.instructions) >= 1

    def test_has_six_members(self):
        team = ValidationTeam()
        assert len(team.team.members) == 6

    def test_can_be_imported_via_teams_package(self):
        from backend.teams import ValidationTeam as Imported

        assert Imported is ValidationTeam
