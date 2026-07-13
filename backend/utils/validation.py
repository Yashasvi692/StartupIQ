from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ValidationError

from backend.utils.exceptions import ValidationError as StartupIQValidationError


def validate_required(data: dict[str, Any], fields: Sequence[str]) -> list[str]:
    missing = []
    for field in fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing


def require_fields(data: dict[str, Any], fields: Sequence[str]) -> None:
    missing = validate_required(data, fields)
    if missing:
        raise StartupIQValidationError(f"Missing required fields: {', '.join(missing)}")


def validate_string(
    value: Any,
    field_name: str = "",
    min_length: int = 0,
    max_length: int | None = None,
) -> None:
    if not isinstance(value, str):
        raise StartupIQValidationError(f"{field_name} must be a string, got {type(value).__name__}")
    if len(value) < min_length:
        raise StartupIQValidationError(f"{field_name} must be at least {min_length} characters")
    if max_length is not None and len(value) > max_length:
        raise StartupIQValidationError(f"{field_name} must be at most {max_length} characters")


def validate_in_range(
    value: Any, field_name: str = "", min_val: float = 0, max_val: float = 100
) -> None:
    if not isinstance(value, (int, float)):
        raise StartupIQValidationError(f"{field_name} must be a number, got {type(value).__name__}")
    if value < min_val or value > max_val:
        raise StartupIQValidationError(f"{field_name} must be between {min_val} and {max_val}")


def validate_model(model: BaseModel) -> list[str]:
    try:
        model.model_validate(model.model_dump())
        return []
    except ValidationError as e:
        return [str(err) for err in e.errors()]


def assert_model_valid(model: BaseModel) -> None:
    errors = validate_model(model)
    if errors:
        raise StartupIQValidationError(f"Model validation failed: {'; '.join(errors)}")


def validate_dict_schema(data: dict[str, Any], schema: dict[str, type]) -> list[str]:
    errors = []
    for field, expected_type in schema.items():
        if field not in data:
            errors.append(f"Missing field: {field}")
            continue
        value = data[field]
        if not isinstance(value, expected_type):
            errors.append(
                f"Field '{field}' expected {expected_type.__name__}, " f"got {type(value).__name__}"
            )
    return errors


def assert_dict_schema(data: dict[str, Any], schema: dict[str, type]) -> None:
    errors = validate_dict_schema(data, schema)
    if errors:
        raise StartupIQValidationError("; ".join(errors))
