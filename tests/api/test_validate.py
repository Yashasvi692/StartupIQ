from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.validate import get_pipeline
from backend.main import app
from backend.models.api.response_models import ValidateResponse
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

VALID_REQUEST = {
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


class TestPostValidate:
    def test_returns_202_with_job_id(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            response = client.post("/validate", json=VALID_REQUEST)
            assert response.status_code == 202
            data = response.json()
            assert data["status"] == "accepted"
            assert data["job_id"].startswith("job_")
            assert data["message"] == "Validation started."
            assert data["estimated_duration_seconds"] == 480
        finally:
            app.dependency_overrides.clear()

    def test_accepts_quick_mode(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            body = {**VALID_REQUEST, "mode": "quick"}
            response = client.post("/validate", json=body)
            assert response.status_code == 202
        finally:
            app.dependency_overrides.clear()

    def test_response_matches_validate_response_model(self, mock_pipeline):
        app.dependency_overrides[get_pipeline] = lambda: mock_pipeline
        client = TestClient(app)
        try:
            response = client.post("/validate", json=VALID_REQUEST)
            data = response.json()
            model = ValidateResponse(**data)
            assert model.job_id.startswith("job_")
        finally:
            app.dependency_overrides.clear()

    def test_returns_422_for_missing_required_fields(self):
        client = TestClient(app)
        response = client.post("/validate", json={})
        assert response.status_code == 422
