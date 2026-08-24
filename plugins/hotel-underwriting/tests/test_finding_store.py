from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from _test_paths import add_scripts_to_path


add_scripts_to_path()

from contract_store import (  # noqa: E402
    build_project_record,
    build_source_record,
    initialize_project,
    write_json_atomic,
    write_jsonl_atomic,
)
from contracts_cli import _cmd_apply_findings  # noqa: E402
from finding_store import build_finding_records  # noqa: E402


class FindingStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = build_project_record(
            "example-hotel",
            "Example Hotel",
            primary_property_name="Example Hotel",
            timestamp="2026-08-18T00:00:00Z",
        )
        self.source = build_source_record(
            "example-hotel",
            "local_file",
            "relative_path",
            "00. OM/example.pdf",
            content_sha256="a" * 64,
            captured_at="2026-08-18T00:00:00Z",
            document_type="marketing.offering_materials",
        )
        self.catalog = {
            "fields": {
                "property.keys": {
                    "value_type": "integer",
                    "unit": "rooms",
                }
            },
            "extension_prefix": "custom.",
        }
        self.bundle = {
            "producer": {
                "skill": "extract-om-data",
                "version": "0.1.0",
            },
            "entity": {"entity_type": "hotel", "name": "Example Hotel"},
            "evidence": [
                {
                    "ref": "summary",
                    "source_id": self.source["source_id"],
                    "locator": {"kind": "pdf_page", "value": "9"},
                    "excerpt": "Keys 559",
                }
            ],
            "facts": [
                {
                    "field": "property.keys",
                    "value": 559,
                    "unit": "rooms",
                    "support_type": "direct",
                    "evidence_refs": ["summary"],
                }
            ],
        }

    def test_builds_linked_records_with_stable_ids(self) -> None:
        first = build_finding_records(
            self.project,
            [self.source],
            self.bundle,
            self.catalog,
            timestamp="2026-08-18T01:00:00Z",
        )
        second = build_finding_records(
            self.project,
            [self.source],
            self.bundle,
            self.catalog,
            timestamp="2026-08-18T02:00:00Z",
        )

        self.assertEqual(first.entity["entity_id"], second.entity["entity_id"])
        self.assertEqual(first.evidence[0]["evidence_id"], second.evidence[0]["evidence_id"])
        self.assertEqual(first.facts[0]["fact_id"], second.facts[0]["fact_id"])
        self.assertEqual(first.facts[0]["evidence_ids"], [first.evidence[0]["evidence_id"]])

    def test_rejects_catalog_type_mismatch(self) -> None:
        self.bundle["facts"][0]["value"] = "559"
        with self.assertRaisesRegex(ValueError, "must be integer"):
            build_finding_records(
                self.project,
                [self.source],
                self.bundle,
                self.catalog,
                timestamp="2026-08-18T01:00:00Z",
            )

    def test_rejects_missing_evidence_reference(self) -> None:
        self.bundle["facts"][0]["evidence_refs"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "missing evidence refs"):
            build_finding_records(
                self.project,
                [self.source],
                self.bundle,
                self.catalog,
                timestamp="2026-08-18T01:00:00Z",
            )

    def test_allows_evidence_only_bundle(self) -> None:
        self.bundle.pop("facts")
        self.bundle["evidence"][0]["data"] = {
            "information_primitive": {
                "type": "property.keys",
                "subject": "Example Hotel",
                "statement": "The hotel has 559 keys.",
                "attributes": {"value": 559, "unit": "rooms"},
            }
        }

        built = build_finding_records(
            self.project,
            [self.source],
            self.bundle,
            self.catalog,
            timestamp="2026-08-18T01:00:00Z",
        )

        self.assertEqual(len(built.evidence), 1)
        self.assertEqual(built.facts, [])
        self.assertEqual(
            built.evidence[0]["data"]["information_primitive"]["type"],
            "property.keys",
        )

    def test_apply_evidence_only_bundle_does_not_create_facts_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            initialize_project(
                root,
                "example-hotel",
                "Example Hotel",
                primary_property_name="Example Hotel",
            )
            data_dir = root / ".hotel-underwriting"
            write_jsonl_atomic(data_dir / "sources.jsonl", [self.source])
            bundle = dict(self.bundle)
            bundle.pop("facts")
            bundle_path = data_dir / "derived" / "evidence-bundle.json"
            write_json_atomic(bundle_path, bundle)

            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    _cmd_apply_findings(
                        argparse.Namespace(
                            deal_room=str(root),
                            input=str(bundle_path),
                        )
                    ),
                    0,
                )

            summary = json.loads(output.getvalue())
            self.assertEqual(summary["facts_added"], 0)
            self.assertTrue((data_dir / "evidence.jsonl").exists())
            self.assertFalse((data_dir / "facts.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
