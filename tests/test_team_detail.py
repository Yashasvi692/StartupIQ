from backend.models.startup_profile import StartupProfile
from backend.models.validation_plan import ValidationPlan
from backend.teams.validation_team import _format_context

SAMPLE_PROFILE = StartupProfile(
    startup_name="TestCo",
    problem_statement="Test problem",
    target_customers="Test customers",
    solution="Test solution",
    business_model="Test model",
    market_knowledge="Test knowledge",
    technical_information="Test tech",
)

SAMPLE_PLAN = ValidationPlan(
    research_depth="quick",
    required_agents=["research"],
    execution_strategy="sequential",
    estimated_completion_seconds=300,
)


class TestFormatContext:
    def test_formats_single_model(self):
        result = _format_context(SAMPLE_PROFILE)
        assert "TestCo" in result
        assert "startup_name" in result

    def test_formats_multiple_models(self):
        result = _format_context(SAMPLE_PROFILE, SAMPLE_PLAN)
        assert "TestCo" in result
        assert "quick" in result
        assert result.count("\n\n") >= 1

    def test_empty_items_returns_empty_string(self):
        result = _format_context()
        assert result == ""

    def test_output_is_valid_json(self):
        import json

        result = _format_context(SAMPLE_PROFILE)
        parsed = json.loads(result)
        assert parsed["startup_name"] == "TestCo"

    def test_includes_all_model_fields(self):
        result = _format_context(SAMPLE_PROFILE)
        assert "problem_statement" in result
        assert "target_customers" in result
        assert "solution" in result
        assert "business_model" in result

    def test_separates_models_with_newlines(self):
        result = _format_context(SAMPLE_PROFILE, SAMPLE_PLAN)
        blocks = result.split("\n\n")
        assert len(blocks) >= 2
