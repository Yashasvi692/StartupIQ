from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.models.api.response_models import JobStatusResponse
from backend.models.business_findings import BusinessFindings
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.models.research_result import ResearchResult
from backend.models.review_result import ReviewResult
from backend.models.startup_profile import StartupProfile
from backend.models.validation_job import ValidationJob
from backend.models.validation_plan import ValidationPlan
from backend.models.validation_report import ValidationReport
from backend.pipeline.validation_pipeline import (
    ALLOWED_TRANSITIONS,
    PIPELINE_STAGES,
    STAGE_ORDER,
    STAGE_PROGRESS_MAP,
    VALID_JOB_STATUSES,
    PipelineStage,
    ValidationPipeline,
)
from backend.teams.discovery_team import DiscoveryTeam
from backend.teams.validation_team import ValidationTeam, ValidationTeamResult
from backend.utils.exceptions import PipelineError

SAMPLE_PROFILE = StartupProfile(
    startup_name="TestCo",
    problem_statement="Test problem",
    target_customers="Test customers",
    solution="Test solution",
    business_model="Test model",
    market_knowledge="Test knowledge",
    technical_information="Test tech",
)


class TestValidationPipeline:
    def test_pipeline_initializes_with_default_teams(self):
        pipeline = ValidationPipeline()
        assert pipeline.name == "Validation Pipeline"
        assert isinstance(pipeline._discovery_team, DiscoveryTeam)
        assert isinstance(pipeline._validation_team, ValidationTeam)

    def test_pipeline_initializes_with_custom_teams(self):
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_validation = MagicMock(spec=ValidationTeam)
        pipeline = ValidationPipeline(
            discovery_team=mock_discovery,
            validation_team=mock_validation,
        )
        assert pipeline._discovery_team is mock_discovery
        assert pipeline._validation_team is mock_validation


class TestPipelineStage:
    def test_pipeline_stages_enum_values(self):
        assert PipelineStage.DISCOVERY.value == "Discovery"
        assert PipelineStage.PLANNING.value == "Planning"
        assert PipelineStage.RESEARCH.value == "Research"
        assert PipelineStage.COMPETITION.value == "Competition"
        assert PipelineStage.ANALYSIS.value == "Analysis"
        assert PipelineStage.REPORTING.value == "Reporting"
        assert PipelineStage.REVIEW.value == "Review"
        assert PipelineStage.COMPLETE.value == "Complete"

    def test_pipeline_stages_order(self):
        expected = [
            PipelineStage.DISCOVERY,
            PipelineStage.PLANNING,
            PipelineStage.RESEARCH,
            PipelineStage.COMPETITION,
            PipelineStage.ANALYSIS,
            PipelineStage.REPORTING,
            PipelineStage.REVIEW,
            PipelineStage.COMPLETE,
        ]
        assert PIPELINE_STAGES == expected

    def test_all_stages_are_strings(self):
        for stage in PipelineStage:
            assert isinstance(stage.value, str)


class TestStageProgressMap:
    def test_stage_progress_values_match_spec(self):
        assert STAGE_PROGRESS_MAP == {
            "Discovery": 10,
            "Planning": 20,
            "Research": 50,
            "Competition": 65,
            "Analysis": 80,
            "Reporting": 95,
            "Review": 100,
        }


class TestValidJobStatuses:
    def test_all_valid_statuses_defined(self):
        expected = {"queued", "running", "completed", "failed", "cancelled"}
        assert set(VALID_JOB_STATUSES) == expected

    def test_allowed_transitions_only_to_valid_statuses(self):
        for current, next_set in ALLOWED_TRANSITIONS.items():
            assert current in VALID_JOB_STATUSES
            for n in next_set:
                assert n in VALID_JOB_STATUSES

    def test_queued_can_transition_to_running_or_cancelled(self):
        assert ALLOWED_TRANSITIONS["queued"] == {"running", "cancelled"}

    def test_running_can_transition_to_completed_failed_or_cancelled(self):
        assert ALLOWED_TRANSITIONS["running"] == {"completed", "failed", "cancelled"}

    def test_terminal_states_have_no_transitions(self):
        assert ALLOWED_TRANSITIONS["completed"] == set()
        assert ALLOWED_TRANSITIONS["failed"] == set()
        assert ALLOWED_TRANSITIONS["cancelled"] == set()


class TestJobCreation:
    def test_create_job_returns_validation_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE, mode="deep")
        assert job.job_id.startswith("job_")
        assert job.status == "queued"
        assert job.mode == "deep"
        assert job.startup_profile == SAMPLE_PROFILE
        assert job.progress == 0
        assert job.current_stage == "Discovery"
        assert job.completed_stages == []
        assert job.remaining_stages == STAGE_ORDER
        assert job.error_message is None
        assert job.report is None
        assert job.completed_at is None

    def test_create_job_accepts_quick_mode(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE, mode="quick")
        assert job.mode == "quick"

    def test_create_job_defaults_to_deep_mode(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        assert job.mode == "deep"

    def test_create_job_stores_job_in_pipeline(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        assert pipeline.get_job(job.job_id) is job

    def test_create_job_raises_error_on_empty_startup_name(self):
        pipeline = ValidationPipeline()
        profile = StartupProfile(
            startup_name="",
            problem_statement="Test",
            target_customers="Test",
            solution="Test",
            business_model="Test",
            market_knowledge="Test",
            technical_information="Test",
        )
        with pytest.raises(PipelineError, match="startup_name"):
            pipeline.create_job(profile)

    def test_generates_unique_job_ids(self):
        pipeline = ValidationPipeline()
        job1 = pipeline.create_job(SAMPLE_PROFILE)
        job2 = pipeline.create_job(SAMPLE_PROFILE)
        assert job1.job_id != job2.job_id


class TestGetJob:
    def test_get_job_returns_job_when_found(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        assert pipeline.get_job(job.job_id) is job

    def test_get_job_returns_none_when_not_found(self):
        pipeline = ValidationPipeline()
        assert pipeline.get_job("nonexistent") is None


class TestStartJob:
    def test_start_job_transitions_to_running(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        result = pipeline.start_job(job.job_id)
        assert result.status == "running"
        assert result.current_stage == "Discovery"
        assert result.progress == 0
        assert result.remaining_stages == STAGE_ORDER
        assert result.completed_stages == []

    def test_start_job_returns_same_job_object(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        result = pipeline.start_job(job.job_id)
        assert result is job

    def test_start_job_raises_on_nonexistent_job(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found"):
            pipeline.start_job("invalid")

    def test_start_job_raises_on_already_running(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        with pytest.raises(PipelineError, match="Invalid status transition: running -> running"):
            pipeline.start_job(job.job_id)

    def test_start_job_raises_on_completed_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.complete_job(job.job_id, ValidationReport())
        with pytest.raises(PipelineError, match="Invalid status transition"):
            pipeline.start_job(job.job_id)


class TestCompleteJob:
    def test_complete_job_sets_status_and_report(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        report = ValidationReport(overall_score=85.0)
        result = pipeline.complete_job(job.job_id, report)
        assert result.status == "completed"
        assert result.progress == 100
        assert result.current_stage == "Complete"
        assert result.report is report
        assert result.completed_at is not None

    def test_complete_job_without_report(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        result = pipeline.complete_job(job.job_id)
        assert result.status == "completed"
        assert result.report is None

    def test_complete_job_sets_all_stages_completed(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        result = pipeline.complete_job(job.job_id)
        assert result.completed_stages == STAGE_ORDER
        assert result.remaining_stages == []

    def test_complete_job_raises_on_queued_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        with pytest.raises(PipelineError, match="Invalid status transition: queued -> completed"):
            pipeline.complete_job(job.job_id)

    def test_complete_job_raises_on_nonexistent_job(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found"):
            pipeline.complete_job("invalid")


class TestFailJob:
    def test_fail_job_sets_failed_status_and_message(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        result = pipeline.fail_job(job.job_id, "Something went wrong")
        assert result.status == "failed"
        assert result.error_message == "Something went wrong"
        assert result.completed_at is not None

    def test_fail_job_raises_on_queued_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        with pytest.raises(PipelineError, match="Invalid status transition: queued -> failed"):
            pipeline.fail_job(job.job_id, "error")

    def test_fail_job_raises_on_nonexistent_job(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found"):
            pipeline.fail_job("invalid", "error")


class TestCancelJob:
    def test_cancel_queued_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        result = pipeline.cancel_job(job.job_id)
        assert result.status == "cancelled"
        assert result.completed_at is not None

    def test_cancel_running_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        result = pipeline.cancel_job(job.job_id)
        assert result.status == "cancelled"

    def test_cancel_completed_job_raises(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.complete_job(job.job_id)
        with pytest.raises(PipelineError, match="Invalid status transition"):
            pipeline.cancel_job(job.job_id)

    def test_cancel_nonexistent_job_raises(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found"):
            pipeline.cancel_job("invalid")


class TestUpdateStage:
    def test_update_stage_sets_current_stage_and_progress(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline._update_stage(job.job_id, "Research")
        assert job.current_stage == "Research"
        assert job.progress == 50

    def test_update_stage_adds_to_completed(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline._update_stage(job.job_id, "Discovery")
        assert "Discovery" in job.completed_stages

    def test_update_stage_removes_from_remaining(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline._update_stage(job.job_id, "Discovery")
        assert "Discovery" not in job.remaining_stages

    def test_update_stage_raises_on_nonexistent_job(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found"):
            pipeline._update_stage("invalid", "Discovery")


class TestFullLifecycle:
    def test_complete_lifecycle_queued_to_completed(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        assert job.status == "queued"

        pipeline.start_job(job.job_id)
        assert job.status == "running"

        pipeline._update_stage(job.job_id, "Discovery")
        pipeline._update_stage(job.job_id, "Planning")
        pipeline._update_stage(job.job_id, "Research")
        pipeline._update_stage(job.job_id, "Competition")
        pipeline._update_stage(job.job_id, "Analysis")
        pipeline._update_stage(job.job_id, "Reporting")
        pipeline._update_stage(job.job_id, "Review")

        report = ValidationReport(overall_score=90.0)
        pipeline.complete_job(job.job_id, report)
        assert job.status == "completed"
        assert job.progress == 100
        assert job.report is report

    def test_complete_lifecycle_queued_to_failed(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.fail_job(job.job_id, "Research failed")
        assert job.status == "failed"
        assert job.error_message == "Research failed"

    def test_complete_lifecycle_queued_to_cancelled(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.cancel_job(job.job_id)
        assert job.status == "cancelled"

    def test_multiple_jobs_can_exist_simultaneously(self):
        pipeline = ValidationPipeline()
        job_a = pipeline.create_job(SAMPLE_PROFILE)
        job_b = pipeline.create_job(SAMPLE_PROFILE)
        assert len(pipeline._jobs) == 2
        assert job_a.job_id != job_b.job_id


class TestAdvanceStage:
    def test_advance_stage_moves_to_next_stage(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        next_stage = pipeline.advance_stage(job.job_id)
        assert next_stage == "Planning"
        assert job.current_stage == "Planning"
        assert job.progress == 20

    def test_advance_stage_raises_on_queued_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        with pytest.raises(PipelineError, match="Cannot advance stage"):
            pipeline.advance_stage(job.job_id)

    def test_advance_stage_raises_on_completed_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.complete_job(job.job_id)
        with pytest.raises(PipelineError, match="Cannot advance stage"):
            pipeline.advance_stage(job.job_id)

    def test_advance_stage_raises_on_failed_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.fail_job(job.job_id, "error")
        with pytest.raises(PipelineError, match="Cannot advance stage"):
            pipeline.advance_stage(job.job_id)

    def test_advance_stage_raises_on_cancelled_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.cancel_job(job.job_id)
        with pytest.raises(PipelineError, match="Cannot advance stage"):
            pipeline.advance_stage(job.job_id)

    def test_advance_stage_raises_on_nonexistent_job(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found"):
            pipeline.advance_stage("invalid")

    def test_advance_all_stages_in_order(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)

        expected_order = [
            ("Discovery", 10),
            ("Planning", 20),
            ("Research", 50),
            ("Competition", 65),
            ("Analysis", 80),
            ("Reporting", 95),
            ("Review", 100),
        ]

        for stage_name, expected_progress in expected_order:
            pipeline._update_stage(job.job_id, stage_name)
            assert job.current_stage == stage_name
            assert job.progress == expected_progress

    def test_advance_stage_updates_completed_and_remaining(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)

        pipeline._update_stage(job.job_id, "Discovery")
        assert job.completed_stages == ["Discovery"]
        assert "Discovery" not in job.remaining_stages

        next_stage = pipeline.advance_stage(job.job_id)
        assert next_stage == "Planning"
        assert "Discovery" in job.completed_stages
        assert "Planning" in job.completed_stages
        assert "Planning" not in job.remaining_stages

    def test_advance_stage_raises_when_past_review(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)

        for stage in STAGE_ORDER:
            pipeline._update_stage(job.job_id, stage)

        with pytest.raises(PipelineError, match="No more stages"):
            pipeline.advance_stage(job.job_id)


class TestProgressTracking:
    def test_get_job_returns_correct_progress(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline._update_stage(job.job_id, "Research")

        fetched = pipeline.get_job(job.job_id)
        assert fetched is not None
        assert fetched.current_stage == "Research"
        assert fetched.progress == 50

    def test_progress_matches_api_spec_after_all_stages(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)

        pipeline._update_stage(job.job_id, "Discovery")
        assert job.progress == 10
        pipeline._update_stage(job.job_id, "Planning")
        assert job.progress == 20
        pipeline._update_stage(job.job_id, "Research")
        assert job.progress == 50
        pipeline._update_stage(job.job_id, "Competition")
        assert job.progress == 65
        pipeline._update_stage(job.job_id, "Analysis")
        assert job.progress == 80
        pipeline._update_stage(job.job_id, "Reporting")
        assert job.progress == 95
        pipeline._update_stage(job.job_id, "Review")
        assert job.progress == 100

    def test_progress_starts_at_zero_for_new_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        assert job.progress == 0

    def test_progress_is_zero_at_start_of_running(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        assert job.progress == 0

    def test_progress_is_one_hundred_on_completion(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.complete_job(job.job_id)
        assert job.progress == 100

    def test_stage_progress_map_contains_all_expected_stages(self):
        for stage in STAGE_ORDER:
            assert stage in STAGE_PROGRESS_MAP

    def test_stage_progress_map_no_extra_stages(self):
        assert len(STAGE_PROGRESS_MAP) == len(STAGE_ORDER)

    def test_job_status_response_has_valid_progress(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.advance_stage(job.job_id)

        response = JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            current_stage=job.current_stage,
            completed_stages=job.completed_stages,
            remaining_stages=job.remaining_stages,
        )
        assert response.job_id == job.job_id
        assert response.progress == 20
        assert response.current_stage == "Planning"
        assert "Discovery" in response.completed_stages
        assert "Review" in response.remaining_stages


VALID_FOUNDER_INPUT = {
    "startup_name": "EcoTrack",
    "problem_statement": "People cannot monitor their carbon footprint easily.",
    "target_customers": "Environmentally conscious millennials.",
    "solution": "A mobile app that tracks carbon footprint via purchase receipts.",
    "business_model": "Freemium with premium subscription at $4.99/month.",
    "market_knowledge": "Growing demand for climate-friendly products.",
    "technical_information": "Flutter app, Python backend, ML recommendation engine.",
}


class TestRunDiscovery:
    @pytest.mark.asyncio
    async def test_run_discovery_returns_startup_profile(self):
        pipeline = ValidationPipeline()
        mock_team = MagicMock(spec=DiscoveryTeam)
        mock_team.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_team

        profile = await pipeline.run_discovery(VALID_FOUNDER_INPUT)
        assert profile == SAMPLE_PROFILE
        assert profile.startup_name == "TestCo"

    @pytest.mark.asyncio
    async def test_run_discovery_passes_input_to_team(self):
        pipeline = ValidationPipeline()
        mock_team = MagicMock(spec=DiscoveryTeam)
        mock_team.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_team

        await pipeline.run_discovery(VALID_FOUNDER_INPUT)
        mock_team.run_discovery.assert_awaited_once_with(VALID_FOUNDER_INPUT)

    @pytest.mark.asyncio
    async def test_run_discovery_team_not_called_with_default_construction(self):
        pipeline = ValidationPipeline()
        assert isinstance(pipeline._discovery_team, DiscoveryTeam)

    @pytest.mark.asyncio
    async def test_run_discovery_handles_invalid_input(self):
        pipeline = ValidationPipeline()
        from backend.utils.exceptions import ValidationError

        with pytest.raises(ValidationError):
            await pipeline.run_discovery({})


DUMMY_TEAM_RESULT = ValidationTeamResult(
    startup_profile=SAMPLE_PROFILE,
    validation_plan=ValidationPlan(
        research_depth="quick",
        required_agents=["planner"],
        execution_strategy="sequential",
        estimated_completion_seconds=10,
    ),
    research_result=ResearchResult(),
    competitor_analysis=CompetitorAnalysis(),
    business_findings=BusinessFindings(),
    validation_report=ValidationReport(overall_score=85.0),
    review_result=ReviewResult(),
)


class TestRunValidation:
    @pytest.mark.asyncio
    async def test_run_validation_returns_validation_report(self):
        pipeline = ValidationPipeline()
        mock_team = MagicMock(spec=ValidationTeam)
        mock_team.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline._validation_team = mock_team

        report = await pipeline.run_validation(SAMPLE_PROFILE)
        assert isinstance(report, ValidationReport)
        assert report.overall_score == 85.0

    @pytest.mark.asyncio
    async def test_run_validation_passes_profile_to_team(self):
        pipeline = ValidationPipeline()
        mock_team = MagicMock(spec=ValidationTeam)
        mock_team.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline._validation_team = mock_team

        await pipeline.run_validation(SAMPLE_PROFILE)
        mock_team.run_validation.assert_awaited_once_with(SAMPLE_PROFILE)

    @pytest.mark.asyncio
    async def test_run_validation_team_not_called_with_default_construction(self):
        pipeline = ValidationPipeline()
        assert isinstance(pipeline._validation_team, ValidationTeam)


class TestRunFullValidation:
    @pytest.mark.asyncio
    async def test_run_full_validation_returns_completed_job(self):
        pipeline = ValidationPipeline()

        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery

        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(VALID_FOUNDER_INPUT)

        assert isinstance(job, ValidationJob)
        assert job.status == "completed"
        assert job.progress == 100
        assert job.startup_profile == SAMPLE_PROFILE
        assert job.report is not None
        assert job.report.overall_score == 85.0

    @pytest.mark.asyncio
    async def test_run_full_validation_invokes_both_teams(self):
        pipeline = ValidationPipeline()

        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery

        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
        pipeline._validation_team = mock_validation

        await pipeline.run_full_validation(VALID_FOUNDER_INPUT)

        mock_discovery.run_discovery.assert_awaited_once_with(VALID_FOUNDER_INPUT)
        mock_validation.run_validation.assert_awaited_once_with(SAMPLE_PROFILE)

    @pytest.mark.asyncio
    async def test_run_full_validation_default_team_construction(self):
        pipeline = ValidationPipeline()
        assert isinstance(pipeline._discovery_team, DiscoveryTeam)
        assert isinstance(pipeline._validation_team, ValidationTeam)


class TestRunFullValidationErrorHandling:
    @pytest.mark.asyncio
    async def test_validation_failure_fails_job_gracefully(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery

        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(
            side_effect=RuntimeError("Search API timeout"),
        )
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(VALID_FOUNDER_INPUT)

        assert job.status == "failed"
        assert job.error_message == "Search API timeout"
        assert job.progress < 100

    @pytest.mark.asyncio
    async def test_discovery_failure_propagates(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(
            side_effect=RuntimeError("Discovery failed"),
        )
        pipeline._discovery_team = mock_discovery

        mock_validation = MagicMock(spec=ValidationTeam)
        pipeline._validation_team = mock_validation

        with pytest.raises(RuntimeError, match="Discovery failed"):
            await pipeline.run_full_validation(VALID_FOUNDER_INPUT)

    @pytest.mark.asyncio
    async def test_tool_failure_fails_job_gracefully(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery

        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(
            side_effect=ConnectionError("DuckDuckGo rate limited"),
        )
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(VALID_FOUNDER_INPUT)

        assert job.status == "failed"
        assert "rate limited" in job.error_message

    @pytest.mark.asyncio
    async def test_prompt_failure_fails_job_gracefully(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery

        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(
            side_effect=ValueError("Prompt template rendering failed"),
        )
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(VALID_FOUNDER_INPUT)

        assert job.status == "failed"
        assert "Prompt template" in job.error_message


DUMMY_RESEARCH_STARTUP_PROFILE = StartupProfile(
    startup_name="GreenStartup",
    problem_statement="Lack of eco-friendly packaging",
    target_customers="Small e-commerce businesses",
    solution="Biodegradable packaging from algae",
    business_model="B2B subscription per 1000 units",
    market_knowledge="Growing regulatory pressure on plastic",
    technical_information="Patent-pending algae processing",
)


class TestEndToEndPipeline:
    END_TO_END_INPUT = {
        "startup_name": "GreenStartup",
        "problem_statement": "Lack of eco-friendly packaging",
        "target_customers": "Small e-commerce businesses",
        "solution": "Biodegradable packaging from algae",
        "business_model": "B2B subscription per 1000 units",
        "market_knowledge": "Growing regulatory pressure on plastic",
        "technical_information": "Patent-pending algae processing",
    }

    @pytest.mark.asyncio
    async def test_complete_pipeline_flow_deep_mode(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=DUMMY_RESEARCH_STARTUP_PROFILE)
        pipeline._discovery_team = mock_discovery

        dummy_validation = ValidationTeamResult(
            startup_profile=DUMMY_RESEARCH_STARTUP_PROFILE,
            validation_plan=ValidationPlan(
                research_depth="deep",
                required_agents=["planner"],
                execution_strategy="sequential",
                estimated_completion_seconds=100,
            ),
            research_result=ResearchResult(),
            competitor_analysis=CompetitorAnalysis(),
            business_findings=BusinessFindings(),
            validation_report=ValidationReport(overall_score=72.5),
            review_result=ReviewResult(),
        )
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=dummy_validation)
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(self.END_TO_END_INPUT)

        assert job.status == "completed"
        assert job.progress == 100
        assert job.mode == "deep"
        assert job.current_stage == "Complete"
        assert job.report is not None
        assert job.report.overall_score == 72.5
        assert job.startup_profile.startup_name == "GreenStartup"
        assert job.error_message is None
        assert job.created_at is not None
        assert job.completed_at is not None

    @pytest.mark.asyncio
    async def test_complete_pipeline_flow_quick_mode(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=DUMMY_RESEARCH_STARTUP_PROFILE)
        pipeline._discovery_team = mock_discovery

        dummy_validation = ValidationTeamResult(
            startup_profile=DUMMY_RESEARCH_STARTUP_PROFILE,
            validation_plan=ValidationPlan(
                research_depth="quick",
                required_agents=["planner"],
                execution_strategy="sequential",
                estimated_completion_seconds=30,
            ),
            research_result=ResearchResult(),
            competitor_analysis=CompetitorAnalysis(),
            business_findings=BusinessFindings(),
            validation_report=ValidationReport(overall_score=60.0),
            review_result=ReviewResult(),
        )
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(return_value=dummy_validation)
        pipeline._validation_team = mock_validation

        job = await pipeline.run_full_validation(self.END_TO_END_INPUT, mode="quick")

        assert job.status == "completed"
        assert job.mode == "quick"
        assert job.report.overall_score == 60.0
        assert job.startup_profile.startup_name == "GreenStartup"
