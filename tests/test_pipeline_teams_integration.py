from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.models.business_findings import BusinessFindings
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.models.research_result import ResearchResult
from backend.models.review_result import ReviewResult
from backend.models.startup_profile import StartupProfile
from backend.models.validation_plan import ValidationPlan
from backend.models.validation_report import ValidationReport
from backend.pipeline.validation_pipeline import STAGE_ORDER, ValidationPipeline
from backend.teams.discovery_team import DiscoveryTeam
from backend.teams.validation_team import ValidationTeam, ValidationTeamResult

SAMPLE_PROFILE = StartupProfile(
    startup_name="IntegrateCo",
    problem_statement="Integration test problem",
    target_customers="Integration test customers",
    solution="Integration test solution",
    business_model="Integration test model",
    market_knowledge="Integration test knowledge",
    technical_information="Integration test tech",
)

DUMMY_TEAM_RESULT = ValidationTeamResult(
    startup_profile=SAMPLE_PROFILE,
    validation_plan=ValidationPlan(
        research_depth="deep",
        required_agents=["planner", "research", "competition"],
        execution_strategy="parallel_research",
        estimated_completion_seconds=600,
    ),
    research_result=ResearchResult(),
    competitor_analysis=CompetitorAnalysis(),
    business_findings=BusinessFindings(),
    validation_report=ValidationReport(overall_score=78.0),
    review_result=ReviewResult(),
)


FOUNDER_INPUT = {
    "startup_name": "IntegrateCo",
    "problem_statement": "Integration test problem",
    "target_customers": "Integration test customers",
    "solution": "Integration test solution",
    "business_model": "Integration test model",
    "market_knowledge": "Integration test knowledge",
    "technical_information": "Integration test tech",
}


class TestPipelineTeamIntegration:
    @pytest.mark.asyncio
    async def test_pipeline_runs_discovery_then_validation(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(FOUNDER_INPUT)

        mock_discovery.run_discovery.assert_awaited_once_with(FOUNDER_INPUT)
        mock_validation.run_validation.assert_awaited_once_with(SAMPLE_PROFILE)
        assert job.status == "completed"

    @pytest.mark.asyncio
    async def test_pipeline_passes_correct_profile_to_validation(self):
        expected_name = "PipelineFlowCo"
        custom_profile = StartupProfile(
            startup_name=expected_name,
            problem_statement="Test problem",
            target_customers="Test customers",
            solution="Test solution",
            business_model="Test model",
            market_knowledge="Test knowledge",
            technical_information="Test tech",
        )
        custom_result = ValidationTeamResult(
            startup_profile=custom_profile,
            validation_plan=ValidationPlan(
                research_depth="quick",
                required_agents=["planner"],
                execution_strategy="sequential",
                estimated_completion_seconds=10,
            ),
            research_result=ResearchResult(),
            competitor_analysis=CompetitorAnalysis(),
            business_findings=BusinessFindings(),
            validation_report=ValidationReport(overall_score=82.0),
            review_result=ReviewResult(),
        )

        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=custom_profile)
        pipeline._discovery_team = mock_discovery
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=custom_result)
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(FOUNDER_INPUT)

        assert job.startup_profile.startup_name == expected_name
        assert job.report.overall_score == 82.0

    @pytest.mark.asyncio
    async def test_run_validation_extracts_report_from_team_result(self):
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline = ValidationPipeline()
        pipeline._validation_team = mock_validation

        report = await pipeline.run_validation(SAMPLE_PROFILE)

        assert report.overall_score == 78.0
        assert isinstance(report, ValidationReport)


class TestPipelineStageProgression:
    @pytest.mark.asyncio
    async def test_stages_progress_in_correct_order(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(FOUNDER_INPUT)

        assert job.completed_stages == STAGE_ORDER
        assert job.remaining_stages == []
        assert job.current_stage == "Complete"

    @pytest.mark.asyncio
    async def test_job_tracks_discovery_input_in_startup_profile(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(FOUNDER_INPUT)

        assert job.startup_profile is not None
        assert job.startup_profile.startup_name == "IntegrateCo"
        assert job.startup_profile.problem_statement == "Integration test problem"


class TestPipelineErrorPropagation:
    @pytest.mark.asyncio
    async def test_discovery_error_propagates_before_job_creation(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(
            side_effect=RuntimeError("Discovery crashed"),
        )
        pipeline._discovery_team = mock_discovery

        with pytest.raises(RuntimeError, match="Discovery crashed"):
            await pipeline.run_full_validation(FOUNDER_INPUT)

    @pytest.mark.asyncio
    async def test_validation_error_captured_in_job(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(
            side_effect=RuntimeError("Validation crashed"),
        )
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(FOUNDER_INPUT)

        assert job.status == "failed"
        assert "Validation crashed" in job.error_message
        assert job.startup_profile is not None
