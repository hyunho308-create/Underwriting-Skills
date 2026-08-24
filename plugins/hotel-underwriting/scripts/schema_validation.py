"""Small JSON Schema subset used by the Phase 0 contract validators."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any


class SchemaValidationError(ValueError):
    """Raised when a record does not match its contract schema."""


def _is_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise SchemaValidationError(f"Unsupported schema type: {expected}")


def _validate_datetime(value: str, path: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SchemaValidationError(f"{path} must be an ISO 8601 date-time") from exc


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    """Validate the subset of JSON Schema used by this plugin."""
    if "const" in schema and instance != schema["const"]:
        raise SchemaValidationError(f"{path} must equal {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaValidationError(f"{path} must be one of {schema['enum']!r}")

    expected_type = schema.get("type")
    if expected_type and not _is_type(instance, expected_type):
        raise SchemaValidationError(f"{path} must be {expected_type}")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            raise SchemaValidationError(f"{path} is shorter than minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            raise SchemaValidationError(f"{path} is longer than maxLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            raise SchemaValidationError(f"{path} does not match {schema['pattern']!r}")
        if schema.get("format") == "date-time":
            _validate_datetime(instance, path)

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        missing = [key for key in schema.get("required", []) if key not in instance]
        if missing:
            raise SchemaValidationError(f"{path} is missing required properties: {missing}")

        if schema.get("additionalProperties") is False:
            unknown = sorted(set(instance) - set(properties))
            if unknown:
                raise SchemaValidationError(f"{path} has unsupported properties: {unknown}")

        for key, value in instance.items():
            if key in properties:
                validate(value, properties[key], f"{path}.{key}")

    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            validate(item, schema["items"], f"{path}[{index}]")
