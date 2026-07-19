import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import get_pipeline
from backend.main import app
from backend.models.startup_profile import StartupProfile
from backend.pipeline.validation_pipeline import ValidationPipeline

SAMPLE_PROFILE = StartupProfile(
    startup_name="TestCo",
    problem_statement="Test problem",
    target_customers="Test customers",
    solution="Test solution",
    business_model="Test model",
    market_knowledge="Test knowledge",
    technical_information="Test tech",
)


@pytest.fixture
def pipeline_with_job():
    pipeline = ValidationPipeline()
    job = pipeline.create_job(SAMPLE_PROFILE)
    pipeline.start_job(job.job_id)
    return pipeline, job.job_id


class TestGetJobStatus:
    def test_returns_job_status_for_existing_job(self, pipeline_with_job):
        pipeline, job_id = pipeline_with_job
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == job_id
            assert data["status"] == "running"
            assert data["progress"] == 0
            assert data["current_stage"] == "Discovery"
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

    def test_returns_all_ac_fields(self, pipeline_with_job):
        pipeline, job_id = pipeline_with_job
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job_id}")
            data = response.json()
            assert "job_id" in data
            assert "status" in data
            assert "progress" in data
            assert "current_stage" in data
            assert "completed_stages" in data
            assert "remaining_stages" in data
        finally:
            app.dependency_overrides.clear()


@pytest.fixture
def pipeline_with_completed_job():
    pipeline = ValidationPipeline()
    from backend.models.validation_report import ValidationReport

    job = pipeline.create_job(SAMPLE_PROFILE)
    pipeline.start_job(job.job_id)
    pipeline.complete_job(job.job_id, report=ValidationReport(overall_score=88.0))
    return pipeline, job.job_id


class TestGetJobReport:
    def test_completed_job_returns_report(self, pipeline_with_completed_job):
        pipeline, job_id = pipeline_with_completed_job
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job_id}/report")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["report"] is not None
            assert data["report"]["overall_score"] == 88.0
        finally:
            app.dependency_overrides.clear()

    def test_running_job_returns_409(self, pipeline_with_job):
        pipeline, job_id = pipeline_with_job
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get(f"/jobs/{job_id}/report")
            assert response.status_code == 409
        finally:
            app.dependency_overrides.clear()

    def test_nonexistent_job_returns_404(self):
        pipeline = ValidationPipeline()
        app.dependency_overrides[get_pipeline] = lambda: pipeline
        client = TestClient(app)
        try:
            response = client.get("/jobs/nonexistent/report")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
