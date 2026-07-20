import time
from unittest.mock import AsyncMock, MagicMock

import pytest

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
    startup_name="PerfTestCo",
    problem_statement="Performance test problem",
    target_customers="Performance test customers",
    solution="Performance test solution",
    business_model="Performance test model",
    market_knowledge="Performance test knowledge",
    technical_information="Performance test tech",
)

DUMMY_PLAN = ValidationPlan(
    research_depth="quick",
    required_agents=["planner", "research", "competition"],
    execution_strategy="parallel_research",
    estimated_completion_seconds=600,
)

DUMMY_TEAM_RESULT = ValidationTeamResult(
    startup_profile=SAMPLE_PROFILE,
    validation_plan=DUMMY_PLAN,
    research_result=ResearchResult(),
    competitor_analysis=CompetitorAnalysis(),
    business_findings=BusinessFindings(),
    validation_report=ValidationReport(overall_score=78.0),
    review_result=ReviewResult(),
)

FOUNDER_INPUT = {
    "startup_name": "PerfTestCo",
    "problem_statement": "Performance test problem",
    "target_customers": "Performance test customers",
    "solution": "Performance test solution",
    "business_model": "Performance test model",
    "market_knowledge": "Performance test knowledge",
    "technical_information": "Performance test tech",
}


def _make_mock_teams() -> tuple[MagicMock, MagicMock]:
    mock_discovery = MagicMock(spec=DiscoveryTeam)
    mock_discovery.run_discovery = AsyncMock(return_value=SAMPLE_PROFILE)

    mock_validation = MagicMock(spec=ValidationTeam)
    mock_validation.run_validation = AsyncMock(return_value=DUMMY_TEAM_RESULT)

    return mock_discovery, mock_validation


@pytest.mark.asyncio
async def test_quick_validation_runtime():
    mock_discovery, mock_validation = _make_mock_teams()
    pipeline = ValidationPipeline(
        discovery_team=mock_discovery,
        validation_team=mock_validation,
    )

    start = time.perf_counter()
    job = await pipeline.run_full_validation(FOUNDER_INPUT, mode="quick")
    elapsed = time.perf_counter() - start

    assert job.mode == "quick"
    assert job.status == "completed"
    assert job.progress == 100
    assert elapsed >= 0
    assert elapsed < 30


@pytest.mark.asyncio
async def test_deep_validation_runtime():
    mock_discovery, mock_validation = _make_mock_teams()
    pipeline = ValidationPipeline(
        discovery_team=mock_discovery,
        validation_team=mock_validation,
    )

    start = time.perf_counter()
    job = await pipeline.run_full_validation(FOUNDER_INPUT, mode="deep")
    elapsed = time.perf_counter() - start

    assert job.mode == "deep"
    assert job.status == "completed"
    assert job.progress == 100
    assert elapsed >= 0
    assert elapsed < 30


@pytest.mark.asyncio
async def test_quick_validation_sets_mode_on_job():
    mock_discovery, mock_validation = _make_mock_teams()
    pipeline = ValidationPipeline(
        discovery_team=mock_discovery,
        validation_team=mock_validation,
    )

    job = await pipeline.run_full_validation(FOUNDER_INPUT, mode="quick")
    assert job.mode == "quick"
    assert "quick" in str(job)


@pytest.mark.asyncio
async def test_deep_validation_sets_mode_on_job():
    mock_discovery, mock_validation = _make_mock_teams()
    pipeline = ValidationPipeline(
        discovery_team=mock_discovery,
        validation_team=mock_validation,
    )

    job = await pipeline.run_full_validation(FOUNDER_INPUT, mode="deep")
    assert job.mode == "deep"
    assert "deep" in str(job)


@pytest.mark.asyncio
async def test_quick_validation_stages_complete():
    mock_discovery, mock_validation = _make_mock_teams()
    pipeline = ValidationPipeline(
        discovery_team=mock_discovery,
        validation_team=mock_validation,
    )

    job = await pipeline.run_full_validation(FOUNDER_INPUT, mode="quick")
    assert job.current_stage == "Complete"
    assert len(job.completed_stages) == 7
    assert job.remaining_stages == []


@pytest.mark.asyncio
async def test_deep_validation_stages_complete():
    mock_discovery, mock_validation = _make_mock_teams()
    pipeline = ValidationPipeline(
        discovery_team=mock_discovery,
        validation_team=mock_validation,
    )

    job = await pipeline.run_full_validation(FOUNDER_INPUT, mode="deep")
    assert job.current_stage == "Complete"
    assert len(job.completed_stages) == 7
    assert job.remaining_stages == []


@pytest.mark.asyncio
async def test_quick_validation_create_job():
    pipeline = ValidationPipeline()
    profile = SAMPLE_PROFILE

    job = pipeline.create_job(profile, mode="quick")
    assert job.mode == "quick"
    assert job.status == "queued"
    assert job.progress == 0
    assert job.current_stage == "Discovery"


@pytest.mark.asyncio
async def test_deep_validation_create_job():
    pipeline = ValidationPipeline()
    profile = SAMPLE_PROFILE

    job = pipeline.create_job(profile, mode="deep")
    assert job.mode == "deep"
    assert job.status == "queued"
    assert job.progress == 0
    assert job.current_stage == "Discovery"
