from __future__ import annotations

import json
import unittest

from _test_paths import PLUGIN_ROOT, add_scripts_to_path

add_scripts_to_path()

from contract_store import build_project_record, build_source_record  # noqa: E402
from schema_validation import SchemaValidationError, validate  # noqa: E402


def load_schema(name: str) -> dict:
    with (PLUGIN_ROOT / "schemas" / name).open("r", encoding="utf-8") as stream:
        return json.load(stream)


class SchemaValidationTests(unittest.TestCase):
    def _evidence_record(self) -> dict:
        return {
            "schema_version": "0.1.0",
            "evidence_id": "ev_" + "a" * 16,
            "project_id": "sample-hotel-2026",
            "source_id": "src_" + "b" * 16,
            "locator": {"kind": "pdf_page", "value": "14"},
            "excerpt": "The hotel completed a comprehensive renovation.",
            "data": {
                "information_primitive": {
                    "type": "swot.strength",
                    "subject": "Sample Hotel",
                    "statement": "Recently renovated guestrooms reduce near-term capital exposure.",
                    "attributes": {"theme": "recent_capex"},
                }
            },
            "captured_at": "2026-08-18T12:00:00Z",
            "extraction_method": "model_text_review",
        }

    def test_project_record_matches_schema(self) -> None:
        record = build_project_record(
            "sample-hotel-2026",
            "Sample Hotel 2026",
            primary_property_name="Sample Hotel",
            timestamp="2026-08-18T12:00:00Z",
        )
        validate(record, load_schema("project.schema.json"))

    def test_source_record_matches_schema(self) -> None:
        record = build_source_record(
            "sample-hotel-2026",
            "local_file",
            "relative_path",
            "00. OM/sample.pdf",
            content_sha256="a" * 64,
            captured_at="2026-08-18T12:00:00Z",
        )
        validate(record, load_schema("source.schema.json"))

    def test_unknown_project_field_fails(self) -> None:
        record = build_project_record(
            "sample-hotel-2026",
            "Sample Hotel 2026",
            timestamp="2026-08-18T12:00:00Z",
        )
        record["speculative_field"] = True
        with self.assertRaises(SchemaValidationError):
            validate(record, load_schema("project.schema.json"))

    def test_extensions_allow_flexible_fields(self) -> None:
        record = build_project_record(
            "sample-hotel-2026",
            "Sample Hotel 2026",
            timestamp="2026-08-18T12:00:00Z",
        )
        record["extensions"] = {"custom.example": {"enabled": True}}
        validate(record, load_schema("project.schema.json"))

    def test_bad_datetime_fails(self) -> None:
        record = build_project_record(
            "sample-hotel-2026",
            "Sample Hotel 2026",
            timestamp="not-a-date",
        )
        with self.assertRaises(SchemaValidationError):
            validate(record, load_schema("project.schema.json"))

    def test_information_primitive_has_flexible_attributes(self) -> None:
        record = self._evidence_record()
        record["data"]["information_primitive"]["attributes"] = {
            "value": 559,
            "unit": "rooms",
            "theme": "scale",
            "room_types": [{"name": "King", "count": 227}],
        }
        validate(record, load_schema("evidence.schema.json"))

    def test_information_primitive_requires_core_fields(self) -> None:
        record = self._evidence_record()
        del record["data"]["information_primitive"]["statement"]
        with self.assertRaisesRegex(SchemaValidationError, "statement"):
            validate(record, load_schema("evidence.schema.json"))

    def test_information_primitive_puts_extensions_in_attributes(self) -> None:
        record = self._evidence_record()
        record["data"]["information_primitive"]["theme"] = "recent_capex"
        with self.assertRaisesRegex(SchemaValidationError, "theme"):
            validate(record, load_schema("evidence.schema.json"))


if __name__ == "__main__":
    unittest.main()
