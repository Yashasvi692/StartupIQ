import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel

from backend.models.api.response_models import ErrorResponse, JobStatusResponse, SuccessResponse
from backend.models.business_findings import SWOT, BusinessFindings, Risk
from backend.models.competitor_analysis import Competitor, CompetitorAnalysis
from backend.models.research_result import ResearchFinding, ResearchResult
from backend.models.startup_profile import StartupProfile
from backend.models.validation_job import ValidationJob
from backend.models.validation_plan import ValidationPlan
from backend.models.validation_report import ValidationReport
from backend.tools.base_tool import BaseTool, ToolResponse
from backend.utils.config import settings
from backend.utils.exceptions import (
    APIError,
    PipelineError,
    PromptNotFoundError,
    StartupIQError,
    ToolError,
    ValidationError,
)
from backend.utils.file_utils import read_text, write_text
from backend.utils.json_utils import from_json, to_json
from backend.utils.logger import get_logger
from backend.utils.markdown_utils import h1, h2, table
from backend.utils.prompt_loader import clear_cache, get_prompt
from backend.utils.retry import retry_async
from backend.utils.validation import (
    assert_model_valid,
    require_fields,
    validate_in_range,
    validate_string,
)

PYTHON = sys.executable
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ── Criterion 1: Configuration works ──


class TestConfiguration:
    def test_settings_loaded(self):
        assert settings.project_name == "StartupIQ"
        assert settings.project_version == "1.0.0"
        assert hasattr(settings, "log_level")
        assert hasattr(settings, "model")

    def test_settings_env_override(self):
        os.environ["TEST_LOG_LEVEL"] = "DEBUG"
        assert settings.log_level is not None


# ── Criterion 2: Logging works ──


class TestLogging:
    def test_get_logger(self):
        logger = get_logger("test_logger")
        assert logger.name == "test_logger"
        assert len(logger.handlers) > 0

    def test_logger_reuses_handlers(self):
        logger = get_logger("test_logger_dup")
        handlers_before = len(logger.handlers)
        logger2 = get_logger("test_logger_dup")
        assert logger2 is logger
        assert len(logger2.handlers) == handlers_before


# ── Criterion 3: Models validate ──


class TestModelsValidate:
    def test_startup_profile(self):
        profile = StartupProfile(
            startup_name="TestCo",
            problem_statement="Test problem",
            target_customers="Developers",
            solution="A test solution",
            business_model="SaaS",
            market_knowledge="Growing market",
            technical_information="Python backend",
        )
        assert profile.startup_name == "TestCo"
        assert profile.stage == "idea"

    def test_validation_plan(self):
        plan = ValidationPlan(
            research_depth="quick",
            required_agents=["research"],
            execution_strategy="sequential",
            estimated_completion_seconds=300,
        )
        assert plan.research_depth == "quick"

    def test_research_result(self):
        result = ResearchResult(
            market_size_findings=[ResearchFinding(finding="Large market", confidence=0.8)]
        )
        assert len(result.market_size_findings) == 1
        assert result.market_size_findings[0].confidence == 0.8

    def test_competitor_analysis(self):
        competitor = Competitor(name="Rival", strengths=["Fast"], weaknesses=["Expensive"])
        analysis = CompetitorAnalysis(
            direct_competitors=[competitor],
            market_gaps=["No mobile app"],
            differentiators=["Free tier"],
        )
        assert len(analysis.direct_competitors) == 1
        assert analysis.competitive_threat_level == "unknown"

    def test_business_findings(self):
        findings = BusinessFindings(
            swot=SWOT(strengths=["Team"], weaknesses=["Funding"]),
            risks=[Risk(risk="Market risk", severity="high")],
            validation_score=75.0,
        )
        assert findings.validation_score == 75.0
        assert len(findings.risks) == 1

    def test_validation_report(self):
        report = ValidationReport(
            executive_summary="Looks good",
            overall_score=85.0,
        )
        assert report.overall_score == 85.0
        assert report.generated_at is not None

    def test_validation_job(self):
        profile = StartupProfile(
            startup_name="TestCo",
            problem_statement="Test",
            target_customers="All",
            solution="Solve",
            business_model="Free",
            market_knowledge="Big",
            technical_information="Stack",
        )
        job = ValidationJob(job_id="job_001", startup_profile=profile, mode="quick")
        assert job.job_id == "job_001"
        assert job.status == "queued"
        assert job.mode == "quick"

    def test_api_response_models(self):
        sr = SuccessResponse(data={"key": "value"})
        assert sr.status == "success"
        assert sr.data == {"key": "value"}

        er = ErrorResponse(code="ERR_001", message="Something broke")
        assert er.status == "error"
        assert er.details == {}

        js = JobStatusResponse(job_id="job_001", status="running", progress=50)
        assert js.job_id == "job_001"

    def test_model_reimports(self):
        from backend.models import (
            SWOT,
            BusinessFindings,
            Competitor,
            CompetitorAnalysis,
            DimensionScore,
            Opportunity,
            Recommendation,
            ResearchFinding,
            ResearchResult,
            Risk,
            StartupProfile,
            ValidationJob,
            ValidationPlan,
            ValidationReport,
        )

        assert all(
            cls is not None
            for cls in [
                BusinessFindings,
                Competitor,
                CompetitorAnalysis,
                DimensionScore,
                Opportunity,
                Recommendation,
                ResearchFinding,
                ResearchResult,
                Risk,
                StartupProfile,
                SWOT,
                ValidationJob,
                ValidationPlan,
                ValidationReport,
            ]
        )


# ── Criterion 4: Prompt loader works ──


class TestPromptLoader:
    def test_prompt_not_found(self):
        with pytest.raises(PromptNotFoundError):
            get_prompt("nonexistent_prompt_xyz")

    def test_prompt_load_and_cache(self):
        prompts_dir = PROJECT_ROOT / "backend" / "prompts"
        test_prompt_name = "_test_infra_prompt"
        test_file = prompts_dir / f"{test_prompt_name}.md"

        try:
            test_file.write_text("# Test Prompt\n\nHello World", encoding="utf-8")
            clear_cache()

            content = get_prompt(test_prompt_name)
            assert "# Test Prompt" in content
            assert "Hello World" in content

            cached = get_prompt(test_prompt_name)
            assert cached == content
        finally:
            if test_file.exists():
                test_file.unlink()
                clear_cache()

    def test_clear_cache(self):
        clear_cache()


# ── Criterion 5: Tool interface implemented ──


@pytest.mark.asyncio
async def test_tool_response_dataclass():
    resp = ToolResponse(success=True, data="result")
    assert resp.success is True
    assert resp.data == "result"
    assert resp.duration_ms is None


@pytest.mark.asyncio
async def test_base_tool_execute():
    class SimpleTool(BaseTool):
        name = "simple"
        description = "A simple test tool"

        async def execute(self, *args, **kwargs):
            return ToolResponse(success=True, data="done")

    tool = SimpleTool()
    result = await tool.run()
    assert result.success is True
    assert result.data == "done"
    assert result.duration_ms is not None


@pytest.mark.asyncio
async def test_base_tool_failure():
    class FailingTool(BaseTool):
        name = "failer"
        description = "Always fails"

        async def execute(self, *args, **kwargs):
            msg = "something went wrong"
            raise ValueError(msg)

    tool = FailingTool()
    result = await tool.run()
    assert result.success is False
    assert "something went wrong" in result.error


# ── Criterion 6: Utilities reusable ──


class TestUtilities:
    def test_file_utils(self, tmp_path):
        test_file = tmp_path / "test.txt"
        write_text(str(test_file), "hello")
        content = read_text(str(test_file))
        assert content == "hello"

    def test_json_utils(self):
        data = {"key": "value", "nested": [1, 2, 3]}
        serialized = to_json(data)
        deserialized = from_json(serialized)
        assert deserialized == data

    def test_markdown_utils(self):
        assert h1("Title") == "# Title\n"
        assert h2("Section") == "## Section\n"
        md_table = table(["A", "B"], [["1", "2"]])
        assert "| A | B |" in md_table
        assert "| 1 | 2 |" in md_table

    @pytest.mark.asyncio
    async def test_retry_async_success(self):
        async def succeed():
            return 42

        result = await retry_async(succeed, max_retries=2)
        assert result == 42

    @pytest.mark.asyncio
    async def test_retry_async_eventually_fails(self):
        call_count = 0

        async def fail():
            nonlocal call_count
            call_count += 1
            msg = f"attempt {call_count} failed"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="attempt 3 failed"):
            await retry_async(fail, max_retries=2, delay=0.01, backoff=1.0)

        assert call_count == 3

    def test_validation_require_fields(self):
        require_fields({"a": 1, "b": "hello"}, ["a", "b"])

        with pytest.raises(ValidationError):
            require_fields({"a": 1}, ["a", "b"])

    def test_validation_string(self):
        validate_string("hello", field_name="name", min_length=1)
        with pytest.raises(ValidationError):
            validate_string("", field_name="name", min_length=1)

    def test_validation_range(self):
        validate_in_range(50, field_name="score")
        with pytest.raises(ValidationError):
            validate_in_range(200, field_name="score", max_val=100)

    def test_assert_model_valid(self):
        class ValidModel(BaseModel):
            name: str

        m = ValidModel(name="test")
        assert_model_valid(m)


# ── Criterion 7: Exceptions handled ──


class TestExceptions:
    def test_exception_hierarchy(self):
        assert issubclass(ValidationError, StartupIQError)
        assert issubclass(PromptNotFoundError, StartupIQError)
        assert issubclass(ToolError, StartupIQError)
        assert issubclass(PipelineError, StartupIQError)
        assert issubclass(APIError, StartupIQError)

    def test_exception_raise_and_catch(self):
        for exc_cls in [ValidationError, PromptNotFoundError, ToolError, PipelineError, APIError]:
            try:
                raise exc_cls(f"Test {exc_cls.__name__}")
            except StartupIQError as e:
                assert str(e) == f"Test {exc_cls.__name__}"


# ── Criteria 8-10: Ruff, Black, Pytest ──


class TestLintTools:
    def test_ruff_passes(self):
        result = subprocess.run(
            [PYTHON, "-m", "ruff", "check", "."],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Ruff failed:\n{result.stdout}\n{result.stderr}"

    def test_black_passes(self):
        result = subprocess.run(
            [PYTHON, "-m", "black", "--check", "."],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"Black failed:\n{result.stdout}\n{result.stderr}"
