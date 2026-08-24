from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from _test_paths import PLUGIN_ROOT, add_scripts_to_path

add_scripts_to_path()

from contract_store import (  # noqa: E402
    build_project_record,
    build_source_record,
    initialize_project,
    read_json,
    read_jsonl,
    write_jsonl_atomic,
)
from contracts_cli import (  # noqa: E402
    _cmd_apply_classifications,
    _cmd_classification_context,
)
from source_classification import (  # noqa: E402
    CLASSIFICATION_EXTENSION,
    apply_classification_decisions,
    build_classification_context,
    pending_source_ids,
    validate_catalog,
)


def load_catalog() -> dict:
    return read_json(PLUGIN_ROOT / "references" / "document-types.json")


def local_source(
    path: str,
    *,
    content: str,
    metadata: dict | None = None,
) -> dict:
    record = build_source_record(
        "sample-hotel-2026",
        "local_file",
        "relative_path",
        path,
        content_sha256=content * 64,
        captured_at="2026-08-18T12:00:00Z",
        metadata=metadata,
    )
    record["availability"] = "available"
    return record


class SourceClassificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_catalog()
        self.project = build_project_record(
            "sample-hotel-2026",
            "Sample Hotel 2026",
            primary_property_name="Sample Hotel",
            timestamp="2026-08-18T12:00:00Z",
        )

    def test_catalog_is_small_unique_and_contains_agreed_types(self) -> None:
        version, identifiers = validate_catalog(self.catalog)
        self.assertEqual(version, "0.3.0")
        self.assertEqual(len(identifiers), 35)
        self.assertIn("marketing.offering_materials", identifiers)
        self.assertIn("financials.balance_sheet", identifiers)
        self.assertIn("financials.other", identifiers)
        self.assertIn("agreements.condo", identifiers)
        self.assertIn("agreements.other", identifiers)
        self.assertIn("performance.ood", identifiers)
        self.assertIn("performance.market_reports", identifiers)
        self.assertIn("property.third_party_reports", identifiers)
        self.assertNotIn("marketing.offering_memorandum", identifiers)
        self.assertNotIn("financials.financial_summary", identifiers)
        self.assertNotIn("financials.accounting_policy", identifiers)

    def test_context_is_metadata_first_with_targeted_content_fallback(self) -> None:
        source = local_source(
            "01. Financials/Sample Hotel - 2026 Budget.xlsx",
            content="a",
            metadata={
                "extension": ".xlsx",
                "file_size_bytes": 1234,
                "modified_at": "2026-08-18T11:00:00Z",
                "is_temporary": False,
            },
        )
        context = build_classification_context(self.project, [source], self.catalog)
        item = context["sources"][0]
        self.assertEqual(item["filename"], "Sample Hotel - 2026 Budget.xlsx")
        self.assertEqual(item["parent_folders"], ["01. Financials"])
        self.assertEqual(item["file_size_bytes"], 1234)
        self.assertNotIn("content_sha256", item)
        self.assertNotIn("content", item)
        self.assertEqual(context["summary"]["pending_sources"], 1)
        self.assertIn("metadata first", context["instructions"]["content_access"])
        self.assertIn("Open only files", context["instructions"]["content_access"])

    def test_apply_decisions_preserves_other_metadata_and_has_no_confidence(self) -> None:
        source = local_source(
            "01. Financials/Sample Hotel - 2026 Budget.xlsx",
            content="b",
            metadata={"extension": ".xlsx", "owner": "inventory"},
        )
        source["extensions"] = {"custom.keep": {"value": True}}
        decision = {
            "source_id": source["source_id"],
            "document_type": "financials.budget",
        }
        result = apply_classification_decisions(
            [source],
            [decision],
            self.catalog,
            classified_at="2026-08-18T13:00:00Z",
        )
        record = result.records[0]
        classification = record["extensions"][CLASSIFICATION_EXTENSION]
        self.assertEqual(record["document_type"], "financials.budget")
        self.assertEqual(record["metadata"]["owner"], "inventory")
        self.assertTrue(record["extensions"]["custom.keep"]["value"])
        self.assertEqual(classification["method"], "model_metadata_first")
        self.assertNotIn("confidence", classification)
        self.assertNotIn("uncertainty_reasons", classification)

    def test_uncertainty_reasons_are_preserved(self) -> None:
        source = local_source("Updated/Summary.xlsx", content="c")
        reason = "The path does not distinguish a budget from a forecast."
        result = apply_classification_decisions(
            [source],
            [
                {
                    "source_id": source["source_id"],
                    "document_type": "financials.forecast",
                    "uncertainty_reasons": [reason],
                }
            ],
            self.catalog,
        )
        classification = result.records[0]["extensions"][CLASSIFICATION_EXTENSION]
        self.assertEqual(classification["uncertainty_reasons"], [reason])
        self.assertEqual(result.summary["uncertain_sources"], 1)

    def test_unknown_requires_a_reason(self) -> None:
        source = local_source("Misc/Document.pdf", content="d")
        with self.assertRaises(ValueError):
            apply_classification_decisions(
                [source],
                [{"source_id": source["source_id"], "document_type": "unknown"}],
                self.catalog,
            )

    def test_decisions_must_cover_every_pending_source(self) -> None:
        first = local_source("Financials/2025 P&L.xlsx", content="e")
        second = local_source("STR/2025 STR.xlsx", content="f")
        with self.assertRaises(ValueError):
            apply_classification_decisions(
                [first, second],
                [
                    {
                        "source_id": first["source_id"],
                        "document_type": "financials.operating_statement",
                    }
                ],
                self.catalog,
            )

    def test_current_and_external_classifications_are_preserved(self) -> None:
        current = local_source("Financials/2025 P&L.xlsx", content="1")
        current["document_type"] = "financials.operating_statement"
        current["extensions"] = {
            CLASSIFICATION_EXTENSION: {
                "catalog_version": "0.3.0",
                "classified_at": "2026-08-18T13:00:00Z",
                "method": "model_metadata_only",
            }
        }
        external = local_source("STR/2025 STR.xlsx", content="2")
        external["document_type"] = "performance.str_report"
        old = local_source("Budget/2026 Budget.xlsx", content="3")
        old["document_type"] = "financials.budget"
        old["extensions"] = {
            CLASSIFICATION_EXTENSION: {
                "catalog_version": "0.1.0",
                "classified_at": "2026-08-17T13:00:00Z",
                "method": "model_metadata_only",
            }
        }
        pending = pending_source_ids([current, external, old], self.catalog)
        self.assertEqual(pending, {old["source_id"]})

    def test_cli_context_and_apply_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            initialize_project(root, "sample-hotel-2026", "Sample Hotel 2026")
            source = local_source("Financials/2026 Budget.xlsx", content="4")
            data_dir = root / ".hotel-underwriting"
            write_jsonl_atomic(data_dir / "sources.jsonl", [source])
            context_path = data_dir / "derived" / "classification-context.json"
            decisions_path = data_dir / "derived" / "classification-decisions.jsonl"

            with redirect_stdout(StringIO()):
                self.assertEqual(
                    _cmd_classification_context(
                        argparse.Namespace(
                            deal_room=str(root),
                            output=str(context_path),
                            reclassify=False,
                        )
                    ),
                    0,
                )
            context = read_json(context_path)
            self.assertEqual(context["summary"]["pending_sources"], 1)
            write_jsonl_atomic(
                decisions_path,
                [
                    {
                        "source_id": source["source_id"],
                        "document_type": "financials.budget",
                    }
                ],
            )

            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    _cmd_apply_classifications(
                        argparse.Namespace(
                            deal_room=str(root),
                            input=str(decisions_path),
                            reclassify=False,
                        )
                    ),
                    0,
                )
            summary = json.loads(output.getvalue())
            stored = read_jsonl(data_dir / "sources.jsonl")
            self.assertEqual(summary["classified_sources"], 1)
            self.assertEqual(stored[0]["document_type"], "financials.budget")


if __name__ == "__main__":
    unittest.main()
