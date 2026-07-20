from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from backend.api.dependencies import get_pipeline
from backend.main import app
from backend.models.api.response_models import ErrorResponse
from backend.models.business_findings import BusinessFindings
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.models.research_result import ResearchResult
from backend.models.review_result import ReviewResult
from backend.models.startup_profile import StartupProfile
from backend.models.validation_plan import ValidationPlan
from backend.models.validation_report import ValidationReport
from backend.pipeline.validation_pipeline import ValidationPipeline
from backend.teams.discovery_team import DiscoveryTeam
from backend.teams.validation_team import ValidationTeam, ValidationTeamResult

SAMPLE_PROFILE = StartupProfile(
    startup_name="TestCo",
    problem_statement="Test problem",
    target_customers="Test customers",
    solution="Test solution",
    business_model="Test model",
    market_knowledge="Test knowledge",
    technical_information="Test tech",
)

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

VALIDATE_BODY = {
    "startup_profile": {
        "startup_name": "TestCo",
        "problem_statement": "Test problem",
        "target_customers": "Test customers",
        "solution": "Test solution",
        "business_model": "Test model",
        "market_knowledge": "Test knowledge",
        "technical_information": "Test tech",
    },
}


class TestApiFailedJob:
    def test_failed_job_returns_error_report(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.fail_job(job.job_id, "Validation failed due to search error")
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "failed"
            assert data["job_id"] == job.job_id
        finally:
            app.dependency_overrides.clear()

    def test_failed_job_report_returns_409(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.fail_job(job.job_id, "Search API timeout")
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            assert response.status_code == 409
            error = ErrorResponse(**response.json()["detail"])
            assert error.code == "REPORT_NOT_READY"
        finally:
            app.dependency_overrides.clear()


class TestApiQueuedJob:
    def test_queued_job_returns_correct_status(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
            assert data["progress"] == 0
        finally:
            app.dependency_overrides.clear()

    def test_queued_job_report_returns_409(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            assert response.status_code == 409
        finally:
            app.dependency_overrides.clear()


class TestApiCancelledJob:
    def test_cancelled_job_returns_correct_status(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.cancel_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "cancelled"
        finally:
            app.dependency_overrides.clear()

    def test_cancelled_job_report_returns_409(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.cancel_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            assert response.status_code == 409
        finally:
            app.dependency_overrides.clear()


class TestApiPipelineFailure:
    def test_validation_pipeline_failure_returns_accepted_but_failed(self):
        pipeline = ValidationPipeline()
        mock_discovery = MagicMock(spec=DiscoveryTeam)
        mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
        pipeline._discovery_team = mock_discovery
        mock_validation = MagicMock(spec=ValidationTeam)
        mock_validation.run_validation = AsyncMock(
            side_effect=RuntimeError("Pipeline execution error"),
        )
        pipeline._validation_team = mock_validation
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.post("/validate", json=VALIDATE_BODY)
            assert response.status_code == 202
            data = response.json()
            job_id = data["job_id"]
            status_resp = client.get(f"/jobs/{job_id}")
            assert status_resp.status_code == 200
            assert status_resp.json()["status"] == "failed"
        finally:
            app.dependency_overrides.clear()


class TestApiJobStatusTransitions:
    def test_job_progresses_from_queued_to_running(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}")
            assert response.json()["status"] == "queued"
            pipeline.start_job(job.job_id)
            response = client.get(f"/jobs/{job.job_id}")
            assert response.json()["status"] == "running"
        finally:
            app.dependency_overrides.clear()

    def test_job_progresses_from_running_to_completed(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            pipeline.complete_job(job.job_id, report=ValidationReport(overall_score=90.0))
            response = client.get(f"/jobs/{job.job_id}")
            data = response.json()
            assert data["status"] == "completed"
            assert data["progress"] == 100
        finally:
            app.dependency_overrides.clear()


class TestApiErrorResponseFormat:
    def test_404_has_correct_error_format(self):
        pipeline = ValidationPipeline()
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get("/jobs/nonexistent")
            error = ErrorResponse(**response.json()["detail"])
            assert error.status == "error"
            assert error.code == "JOB_NOT_FOUND"
            assert len(error.message) > 0
        finally:
            app.dependency_overrides.clear()

    def test_409_has_correct_error_format(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            error = ErrorResponse(**response.json()["detail"])
            assert error.status == "error"
            assert error.code == "REPORT_NOT_READY"
            assert len(error.message) > 0
        finally:
            app.dependency_overrides.clear()
