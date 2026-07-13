from backend.validation.founder_input import (
    FOUNDER_FIELDS,
    REQUIRED_FOUNDER_FIELDS,
    VALID_STAGES,
    is_input_valid,
    normalize_founder_input,
    validate_founder_input,
)


class TestFounderInputConstants:
    def test_required_fields_defined(self):
        assert len(REQUIRED_FOUNDER_FIELDS) >= 6
        assert "startup_name" in REQUIRED_FOUNDER_FIELDS
        assert "problem_statement" in REQUIRED_FOUNDER_FIELDS
        assert "target_customers" in REQUIRED_FOUNDER_FIELDS
        assert "solution" in REQUIRED_FOUNDER_FIELDS
        assert "business_model" in REQUIRED_FOUNDER_FIELDS

    def test_all_founder_fields_defined(self):
        assert len(FOUNDER_FIELDS) >= 10
        assert "tagline" in FOUNDER_FIELDS
        assert "founder_assumptions" in FOUNDER_FIELDS
        assert "validation_objectives" in FOUNDER_FIELDS
        assert "industry" in FOUNDER_FIELDS
        assert "stage" in FOUNDER_FIELDS

    def test_valid_stages(self):
        assert "idea" in VALID_STAGES
        assert "prototype" in VALID_STAGES
        assert "launched" in VALID_STAGES
        assert "revenue" in VALID_STAGES
        assert "growth" in VALID_STAGES
        assert len(VALID_STAGES) == 5


class TestValidateFounderInput:
    def test_valid_input_passes(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        errors = validate_founder_input(data)
        assert errors["missing"] == []
        assert errors["invalid"] == []
        assert is_input_valid(errors)

    def test_missing_required_fields_detected(self):
        data = {
            "startup_name": "TestCo",
        }
        errors = validate_founder_input(data)
        assert "problem_statement" in errors["missing"]
        assert "target_customers" in errors["missing"]
        assert "solution" in errors["missing"]
        assert "business_model" in errors["missing"]
        assert "market_knowledge" in errors["missing"]
        assert "technical_information" in errors["missing"]
        assert not is_input_valid(errors)

    def test_empty_required_fields_detected(self):
        data = {
            "startup_name": "",
            "problem_statement": "",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        errors = validate_founder_input(data)
        assert "startup_name" in errors["missing"]
        assert "problem_statement" in errors["missing"]

    def test_whitespace_only_required_fields_detected(self):
        data = {
            "startup_name": "   ",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        errors = validate_founder_input(data)
        assert "startup_name" in errors["missing"]

    def test_invalid_stage_rejected(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
            "stage": "invalid_stage",
        }
        errors = validate_founder_input(data)
        assert len(errors["invalid"]) == 1
        assert "invalid_stage" in errors["invalid"][0]
        assert not is_input_valid(errors)

    def test_valid_stage_accepted(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
            "stage": "prototype",
        }
        errors = validate_founder_input(data)
        assert errors["invalid"] == []
        assert is_input_valid(errors)

    def test_empty_input_returns_all_missing(self):
        errors = validate_founder_input({})
        assert len(errors["missing"]) == len(REQUIRED_FOUNDER_FIELDS)
        assert not is_input_valid(errors)

    def test_long_field_generates_warning(self):
        data = {
            "startup_name": "x" * 10001,
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        errors = validate_founder_input(data)
        assert len(errors["warnings"]) >= 1
        assert "startup_name" in errors["warnings"][0]

    def test_multiple_long_fields_warned(self):
        data = {
            "startup_name": "x" * 10001,
            "problem_statement": "y" * 10001,
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        errors = validate_founder_input(data)
        assert len(errors["warnings"]) >= 2


class TestNormalizeFounderInput:
    def test_trims_whitespace(self):
        data = {
            "startup_name": "  TestCo  ",
            "problem_statement": "  A big problem  ",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        normalized = normalize_founder_input(data)
        assert normalized["startup_name"] == "TestCo"
        assert normalized["problem_statement"] == "A big problem"

    def test_missing_fields_default_to_empty(self):
        normalized = normalize_founder_input({})
        assert normalized["startup_name"] == ""
        assert normalized["tagline"] == ""

    def test_stage_normalized_to_lowercase(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
            "stage": "PROTOTYPE",
        }
        normalized = normalize_founder_input(data)
        assert normalized["stage"] == "prototype"

    def test_invalid_stage_defaults_to_idea(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
            "stage": "unknown",
        }
        normalized = normalize_founder_input(data)
        assert normalized["stage"] == "idea"

    def test_missing_stage_defaults_to_idea(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        normalized = normalize_founder_input(data)
        assert normalized["stage"] == "idea"

    def test_valid_stage_preserved(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
            "stage": "growth",
        }
        normalized = normalize_founder_input(data)
        assert normalized["stage"] == "growth"

    def test_partial_input_preserves_provided_values(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
        }
        normalized = normalize_founder_input(data)
        assert normalized["startup_name"] == "TestCo"
        assert normalized["problem_statement"] == "A big problem"
        assert normalized["target_customers"] == ""

    def test_non_string_values_preserved(self):
        data = {
            "startup_name": "TestCo",
            "problem_statement": "A big problem",
            "target_customers": "Everyone",
            "solution": "A great solution",
            "business_model": "SaaS",
            "market_knowledge": "Growing market",
            "technical_information": "Python app",
        }
        normalized = normalize_founder_input(data)
        for field in data:
            assert field in normalized


class TestIsInputValid:
    def test_valid_errors_returns_true(self):
        errors = {"missing": [], "invalid": [], "warnings": []}
        assert is_input_valid(errors)

    def test_missing_fields_returns_false(self):
        errors = {"missing": ["startup_name"], "invalid": [], "warnings": []}
        assert not is_input_valid(errors)

    def test_invalid_values_returns_false(self):
        errors = {"missing": [], "invalid": ["Invalid stage"], "warnings": []}
        assert not is_input_valid(errors)

    def test_warnings_do_not_affect_validity(self):
        errors = {"missing": [], "invalid": [], "warnings": ["Long field"]}
        assert is_input_valid(errors)

    def test_both_missing_and_invalid_returns_false(self):
        errors = {
            "missing": ["startup_name"],
            "invalid": ["Invalid stage"],
            "warnings": [],
        }
        assert not is_input_valid(errors)
