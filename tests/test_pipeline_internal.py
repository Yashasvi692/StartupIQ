import pytest

from backend.models.startup_profile import StartupProfile
from backend.pipeline.validation_pipeline import (
    ALLOWED_TRANSITIONS,
    PipelineError,
    ValidationPipeline,
)


class TestValidateTransition:
    def test_valid_queued_to_running(self):
        pipeline = ValidationPipeline()
        pipeline._validate_transition("queued", "running")

    def test_valid_queued_to_cancelled(self):
        pipeline = ValidationPipeline()
        pipeline._validate_transition("queued", "cancelled")

    def test_valid_running_to_completed(self):
        pipeline = ValidationPipeline()
        pipeline._validate_transition("running", "completed")

    def test_valid_running_to_failed(self):
        pipeline = ValidationPipeline()
        pipeline._validate_transition("running", "failed")

    def test_valid_running_to_cancelled(self):
        pipeline = ValidationPipeline()
        pipeline._validate_transition("running", "cancelled")

    def test_invalid_queued_to_completed_raises(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Invalid status transition: queued -> completed"):
            pipeline._validate_transition("queued", "completed")

    def test_invalid_queued_to_failed_raises(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Invalid status transition: queued -> failed"):
            pipeline._validate_transition("queued", "failed")

    def test_invalid_completed_to_running_raises(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Invalid status transition: completed -> running"):
            pipeline._validate_transition("completed", "running")

    def test_invalid_failed_to_completed_raises(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Invalid status transition: failed -> completed"):
            pipeline._validate_transition("failed", "completed")

    def test_invalid_cancelled_to_running_raises(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Invalid status transition: cancelled -> running"):
            pipeline._validate_transition("cancelled", "running")

    def test_all_transitions_covered(self):
        pipeline = ValidationPipeline()
        for current in ["queued", "running", "completed", "failed", "cancelled"]:
            allowed = ALLOWED_TRANSITIONS.get(current, set())
            for new in ["queued", "running", "completed", "failed", "cancelled"]:
                if new in allowed:
                    pipeline._validate_transition(current, new)
                else:
                    with pytest.raises(PipelineError, match="Invalid status transition"):
                        pipeline._validate_transition(current, new)


SAMPLE_PROFILE = StartupProfile(
    startup_name="TestCo",
    problem_statement="Test problem",
    target_customers="Test customers",
    solution="Test solution",
    business_model="Test model",
    market_knowledge="Test knowledge",
    technical_information="Test tech",
)


class TestGetJobOrRaise:
    def test_returns_job_when_found(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        result = pipeline._get_job_or_raise(job.job_id)
        assert result is job

    def test_raises_when_not_found(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found: nonexistent"):
            pipeline._get_job_or_raise("nonexistent")

    def test_raises_with_empty_job_id(self):
        pipeline = ValidationPipeline()
        with pytest.raises(PipelineError, match="Job not found"):
            pipeline._get_job_or_raise("")


class TestCompleteCurrentStage:
    def test_completes_current_discovery_stage(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        assert "Discovery" not in job.completed_stages

        pipeline._complete_current_stage(job)
        assert "Discovery" in job.completed_stages
        assert job.progress >= 0

    def test_idempotent_when_stage_already_completed(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)

        pipeline._complete_current_stage(job)
        completed_before = list(job.completed_stages)
        progress_before = job.progress

        pipeline._complete_current_stage(job)
        assert job.completed_stages == completed_before
        assert job.progress == progress_before

    def test_updates_progress_for_valid_stage(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)

        from backend.pipeline.validation_pipeline import STAGE_PROGRESS_MAP

        pipeline._complete_current_stage(job)
        expected_progress = STAGE_PROGRESS_MAP.get("Discovery", 0)
        assert job.progress == expected_progress

    def test_does_not_raise_for_complete_stage(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        job.current_stage = "Complete"
        pipeline._complete_current_stage(job)
        assert "Discovery" not in job.completed_stages
