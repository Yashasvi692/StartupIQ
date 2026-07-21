from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.business_agent import BusinessAgent
from backend.agents.competition_agent import CompetitionAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.report_agent import ReportAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.reviewer_agent import ReviewerAgent
from backend.execution.execution_manager import ExecutionManager
from backend.execution.execution_mode import ExecutionMode
from backend.models.business_findings import SWOT, BusinessFindings
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


class TestValidationTeamExecutionModes:
    @pytest.mark.asyncio
    async def test_sequential_mode_produces_correct_result(self):
        executor = ExecutionManager(mode=ExecutionMode.SEQUENTIAL)
        team = ValidationTeam(
            planner_agent=_make_mock_agent(PlannerAgent, DUMMY_PLAN),
            research_agent=_make_mock_agent(ResearchAgent, DUMMY_RESEARCH),
            competition_agent=_make_mock_agent(CompetitionAgent, DUMMY_COMPETITION),
            business_agent=_make_mock_agent(BusinessAgent, DUMMY_BUSINESS),
            report_agent=_make_mock_agent(ReportAgent, DUMMY_REPORT),
            reviewer_agent=_make_mock_agent(ReviewerAgent, DUMMY_REVIEW),
            executor=executor,
        )
        result = await team.run_validation(DUMMY_PROFILE)
        assert isinstance(result, ValidationTeamResult)
        assert result.validation_plan is DUMMY_PLAN
        assert result.research_result is DUMMY_RESEARCH
        assert result.competitor_analysis is DUMMY_COMPETITION
        assert result.business_findings is DUMMY_BUSINESS
        assert result.validation_report is DUMMY_REPORT
        assert result.review_result is DUMMY_REVIEW

    @pytest.mark.asyncio
    async def test_parallel_mode_produces_correct_result(self):
        executor = ExecutionManager(mode=ExecutionMode.PARALLEL)
        team = ValidationTeam(
            planner_agent=_make_mock_agent(PlannerAgent, DUMMY_PLAN),
            research_agent=_make_mock_agent(ResearchAgent, DUMMY_RESEARCH),
            competition_agent=_make_mock_agent(CompetitionAgent, DUMMY_COMPETITION),
            business_agent=_make_mock_agent(BusinessAgent, DUMMY_BUSINESS),
            report_agent=_make_mock_agent(ReportAgent, DUMMY_REPORT),
            reviewer_agent=_make_mock_agent(ReviewerAgent, DUMMY_REVIEW),
            executor=executor,
        )
        result = await team.run_validation(DUMMY_PROFILE)
        assert isinstance(result, ValidationTeamResult)
        assert result.validation_plan is DUMMY_PLAN
        assert result.research_result is DUMMY_RESEARCH
        assert result.competitor_analysis is DUMMY_COMPETITION
        assert result.business_findings is DUMMY_BUSINESS
        assert result.validation_report is DUMMY_REPORT
        assert result.review_result is DUMMY_REVIEW

    @pytest.mark.asyncio
    async def test_sequential_and_parallel_produce_same_results(self):
        seq_executor = ExecutionManager(mode=ExecutionMode.SEQUENTIAL)
        par_executor = ExecutionManager(mode=ExecutionMode.PARALLEL)

        seq_team = ValidationTeam(
            planner_agent=_make_mock_agent(PlannerAgent, DUMMY_PLAN),
            research_agent=_make_mock_agent(ResearchAgent, DUMMY_RESEARCH),
            competition_agent=_make_mock_agent(CompetitionAgent, DUMMY_COMPETITION),
            business_agent=_make_mock_agent(BusinessAgent, DUMMY_BUSINESS),
            report_agent=_make_mock_agent(ReportAgent, DUMMY_REPORT),
            reviewer_agent=_make_mock_agent(ReviewerAgent, DUMMY_REVIEW),
            executor=seq_executor,
        )
        par_team = ValidationTeam(
            planner_agent=_make_mock_agent(PlannerAgent, DUMMY_PLAN),
            research_agent=_make_mock_agent(ResearchAgent, DUMMY_RESEARCH),
            competition_agent=_make_mock_agent(CompetitionAgent, DUMMY_COMPETITION),
            business_agent=_make_mock_agent(BusinessAgent, DUMMY_BUSINESS),
            report_agent=_make_mock_agent(ReportAgent, DUMMY_REPORT),
            reviewer_agent=_make_mock_agent(ReviewerAgent, DUMMY_REVIEW),
            executor=par_executor,
        )

        seq_result = await seq_team.run_validation(DUMMY_PROFILE)
        par_result = await par_team.run_validation(DUMMY_PROFILE)

        assert isinstance(seq_result.validation_plan, ValidationPlan)
        assert isinstance(par_result.validation_plan, ValidationPlan)
        assert seq_result.validation_plan.model_dump() == par_result.validation_plan.model_dump()

    @pytest.mark.asyncio
    async def test_both_modes_invoke_all_agents(self):
        agents_seq = {
            "planner": _make_mock_agent(PlannerAgent, DUMMY_PLAN),
            "research": _make_mock_agent(ResearchAgent, DUMMY_RESEARCH),
            "competition": _make_mock_agent(CompetitionAgent, DUMMY_COMPETITION),
            "business": _make_mock_agent(BusinessAgent, DUMMY_BUSINESS),
            "report": _make_mock_agent(ReportAgent, DUMMY_REPORT),
            "reviewer": _make_mock_agent(ReviewerAgent, DUMMY_REVIEW),
        }
        agents_par = {}
        for k, v in agents_seq.items():
            agents_par[k] = _make_mock_agent(type(v), v.run_structured.return_value)

        seq_team = ValidationTeam(
            executor=ExecutionManager(mode=ExecutionMode.SEQUENTIAL),
            **{f"{k}_agent": v for k, v in agents_seq.items()},
        )
        par_team = ValidationTeam(
            executor=ExecutionManager(mode=ExecutionMode.PARALLEL),
            **{f"{k}_agent": v for k, v in agents_par.items()},
        )

        await seq_team.run_validation(DUMMY_PROFILE)
        await par_team.run_validation(DUMMY_PROFILE)

        for name in agents_seq:
            agents_seq[name].run_structured.assert_called_once()
            agents_par[name].run_structured.assert_called_once()
