from typing import Any

from backend.utils.validation import validate_required

REQUIRED_FOUNDER_FIELDS: list[str] = [
    "startup_name",
    "problem_statement",
    "target_customers",
    "solution",
    "business_model",
    "market_knowledge",
    "technical_information",
]

FOUNDER_FIELDS: list[str] = [
    "startup_name",
    "tagline",
    "problem_statement",
    "target_customers",
    "solution",
    "business_model",
    "market_knowledge",
    "technical_information",
    "founder_assumptions",
    "validation_objectives",
    "industry",
    "stage",
]

VALID_STAGES: list[str] = [
    "idea",
    "prototype",
    "launched",
    "revenue",
    "growth",
]

MAX_FIELD_LENGTH: int = 10000


def validate_founder_input(data: dict[str, Any]) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {
        "missing": [],
        "invalid": [],
        "warnings": [],
    }

    missing = validate_required(data, REQUIRED_FOUNDER_FIELDS)
    errors["missing"] = missing

    stage = data.get("stage", "")
    if stage and isinstance(stage, str) and stage.strip().lower() not in VALID_STAGES:
        errors["invalid"].append(
            f"Invalid stage '{stage}'. Must be one of: {', '.join(VALID_STAGES)}"
        )

    for field in FOUNDER_FIELDS:
        value = data.get(field)
        if isinstance(value, str) and len(value) > MAX_FIELD_LENGTH:
            errors["warnings"].append(
                f"Field '{field}' is very long ({len(value)} characters). " f"Consider summarizing."
            )

    return errors


def normalize_founder_input(data: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for field in FOUNDER_FIELDS:
        value = data.get(field, "")
        if isinstance(value, str):
            value = value.strip()
        normalized[field] = value

    stage = normalized.get("stage", "")
    if isinstance(stage, str):
        stage = stage.strip().lower()
        normalized["stage"] = stage if stage in VALID_STAGES else "idea"

    return normalized


def is_input_valid(errors: dict[str, list[str]]) -> bool:
    return not errors["missing"] and not errors["invalid"]
