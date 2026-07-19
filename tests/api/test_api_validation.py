from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import get_pipeline
from backend.main import app
from backend.models.api.response_models import (
    ErrorResponse,
    HealthResponse,
    JobStatusResponse,
    ReportResponse,
    ValidateResponse,
    VersionResponse,
)
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


@pytest.fixture
def mock_pipeline():
    pipeline = ValidationPipeline()
    mock_discovery = MagicMock(spec=DiscoveryTeam)
    mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)
    pipeline._discovery_team = mock_discovery
    mock_validation = MagicMock(spec=ValidationTeam)
    mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)
    pipeline._validation_team = mock_validation
    return pipeline


class TestHealthEndpoint:
    def test_returns_200(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_response_matches_health_response_model(self):
        client = TestClient(app)
        response = client.get("/health")
        model = HealthResponse(**response.json())
        assert model.status == "healthy"

    def test_response_body_matches_spec(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}


class TestVersionEndpoint:
    def test_returns_200(self):
        client = TestClient(app)
        response = client.get("/version")
        assert response.status_code == 200

    def test_response_matches_version_response_model(self):
        client = TestClient(app)
        response = client.get("/version")
        model = VersionResponse(**response.json())
        assert model.project == "StartupIQ"
        assert model.version == "1.0.0"

    def test_response_body_matches_spec(self):
        client = TestClient(app)
        response = client.get("/version")
        assert response.json() == {"project": "StartupIQ", "version": "1.0.0"}


class TestPostValidateValidation:
    def test_returns_202(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            response = client.post("/validate", json=VALIDATE_BODY)
            assert response.status_code == 202
        finally:
            app.dependency_overrides.clear()

    def test_response_matches_validate_response_model(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            response = client.post("/validate", json=VALIDATE_BODY)
            model = ValidateResponse(**response.json())
            assert model.job_id.startswith("job_")
            assert model.status == "accepted"
            assert model.message == "Validation started."
        finally:
            app.dependency_overrides.clear()

    def test_returns_422_for_empty_body(self):
        client = TestClient(app)
        response = client.post("/validate", json={})
        assert response.status_code == 422

    def test_returns_422_for_missing_required_fields(self):
        client = TestClient(app)
        response = client.post(
            "/validate",
            json={"startup_profile": {"startup_name": ""}},
        )
        assert response.status_code == 422

    def test_accepts_quick_mode(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            body = {**VALIDATE_BODY, "mode": "quick"}
            response = client.post("/validate", json=body)
            assert response.status_code == 202
        finally:
            app.dependency_overrides.clear()


class TestGetJobStatusValidation:
    def test_returns_200_for_existing_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_response_matches_job_status_response_model(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}")
            model = JobStatusResponse(**response.json())
            assert model.job_id == job.job_id
            assert model.status == "running"
        finally:
            app.dependency_overrides.clear()

    def test_returns_404_for_nonexistent_job(self):
        pipeline = ValidationPipeline()
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get("/jobs/nonexistent")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_error_response_format_for_404(self):
        pipeline = ValidationPipeline()
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get("/jobs/nonexistent")
            data = response.json()
            assert "detail" in data
            error = ErrorResponse(**data["detail"])
            assert error.status == "error"
            assert error.code == "JOB_NOT_FOUND"
        finally:
            app.dependency_overrides.clear()

    def test_includes_all_ac_fields(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}")
            data = response.json()
            assert "job_id" in data
            assert "status" in data
            assert "progress" in data
            assert "current_stage" in data
            assert "completed_stages" in data
            assert "remaining_stages" in data
        finally:
            app.dependency_overrides.clear()


class TestGetJobReportValidation:
    def test_returns_200_for_completed_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.complete_job(job.job_id, report=ValidationReport(overall_score=88.0))
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_response_matches_report_response_model(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        pipeline.complete_job(job.job_id, report=ValidationReport(overall_score=88.0))
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            model = ReportResponse(**response.json())
            assert model.status == "completed"
            assert model.report is not None
            assert model.report["overall_score"] == 88.0
        finally:
            app.dependency_overrides.clear()

    def test_returns_409_for_running_job(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            assert response.status_code == 409
        finally:
            app.dependency_overrides.clear()

    def test_returns_404_for_nonexistent_job(self):
        pipeline = ValidationPipeline()
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get("/jobs/nonexistent/report")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_error_response_format_for_409(self):
        pipeline = ValidationPipeline()
        job = pipeline.create_job(SAMPLE_PROFILE)
        pipeline.start_job(job.job_id)
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job.job_id}/report")
            data = response.json()
            assert "detail" in data
            error = ErrorResponse(**data["detail"])
            assert error.status == "error"
            assert error.code == "REPORT_NOT_READY"
        finally:
            app.dependency_overrides.clear()
