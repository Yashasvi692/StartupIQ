from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies import get_pipeline
from backend.main import app
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


class TestApiIntegration:
    def test_full_api_flow_deep_mode(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            response = client.post("/validate", json=VALIDATE_BODY)
            assert response.status_code == 202
            validate_data = response.json()
            assert validate_data["status"] == "accepted"
            assert validate_data["job_id"].startswith("job_")
            assert validate_data["message"] == "Validation started."
            assert validate_data["estimated_duration_seconds"] == 480
            job_id = validate_data["job_id"]
            response = client.get(f"/jobs/{job_id}")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["job_id"] == job_id
            assert status_data["status"] == "completed"
            assert status_data["progress"] == 100
            assert status_data["current_stage"] == "Complete"
            response = client.get(f"/jobs/{job_id}/report")
            assert response.status_code == 200
            report_data = response.json()
            assert report_data["status"] == "completed"
            assert report_data["report"] is not None
            assert report_data["report"]["overall_score"] == 85.0
        finally:
            app.dependency_overrides.clear()

    def test_full_api_flow_quick_mode(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            body = {**VALIDATE_BODY, "mode": "quick"}
            response = client.post("/validate", json=body)
            assert response.status_code == 202
            validate_data = response.json()
            assert validate_data["status"] == "accepted"
            job_id = validate_data["job_id"]
            assert job_id.startswith("job_")
            response = client.get(f"/jobs/{job_id}")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["status"] == "completed"
            response = client.get(f"/jobs/{job_id}/report")
            assert response.status_code == 200
            report_data = response.json()
            assert report_data["status"] == "completed"
            assert report_data["report"]["overall_score"] == 85.0
        finally:
            app.dependency_overrides.clear()
