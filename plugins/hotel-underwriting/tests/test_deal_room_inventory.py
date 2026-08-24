from __future__ import annotations

from pathlib import Path
import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
import tempfile
import unittest

from _test_paths import add_scripts_to_path

add_scripts_to_path()

from contract_store import (  # noqa: E402
    build_project_record,
    build_source_record,
    initialize_project,
    read_jsonl,
)
from contracts_cli import _cmd_inventory_deal_room  # noqa: E402
from deal_room_inventory import build_inventory  # noqa: E402


class DealRoomInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = build_project_record(
            "sample-hotel-2026",
            "Sample Hotel 2026",
            timestamp="2026-08-18T12:00:00Z",
        )

    def test_inventory_records_metadata_duplicates_and_temporary_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "00. OM").mkdir()
            (root / "00. OM" / "offering.pdf").write_bytes(b"same")
            (root / "00. OM" / "copy.pdf").write_bytes(b"same")
            (root / "notes.txt").write_text("notes", encoding="utf-8")
            (root / "~$working.xlsx").write_bytes(b"temporary")
            (root / ".hotel-underwriting").mkdir()
            (root / ".hotel-underwriting" / "project.json").write_text(
                "derived data must be excluded", encoding="utf-8"
            )

            result = build_inventory(
                root,
                self.project,
                [],
                captured_at="2026-08-18T13:00:00Z",
            )

            self.assertEqual(result.summary["current_files"], 4)
            self.assertEqual(result.summary["temporary_files"], 1)
            self.assertEqual(result.summary["exact_duplicate_groups"], 1)
            self.assertEqual(result.summary["new_files"], 4)
            self.assertTrue(result.manifest_changed)
            paths = {record["location"]["value"] for record in result.records}
            self.assertNotIn(".hotel-underwriting/project.json", paths)

            duplicate_records = [
                record
                for record in result.records
                if record["location"]["value"]
                in {"00. OM/copy.pdf", "00. OM/offering.pdf"}
            ]
            self.assertEqual(len(duplicate_records), 2)
            self.assertEqual(
                sum("exact_duplicate_of" in record["metadata"] for record in duplicate_records),
                1,
            )

    def test_repeated_inventory_is_idempotent_and_preserves_owned_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "offering.pdf"
            source.write_bytes(b"version one")
            first = build_inventory(
                root,
                self.project,
                [],
                captured_at="2026-08-18T13:00:00Z",
            )
            first.records[0]["document_type"] = "offering_memorandum"
            first.records[0]["metadata"]["classification_confidence"] = "high"

            second = build_inventory(
                root,
                self.project,
                first.records,
                captured_at="2026-08-18T14:00:00Z",
            )

            self.assertFalse(second.manifest_changed)
            self.assertEqual(second.summary["unchanged_files"], 1)
            self.assertEqual(second.records[0]["captured_at"], "2026-08-18T13:00:00Z")
            self.assertEqual(second.records[0]["document_type"], "offering_memorandum")
            self.assertEqual(second.records[0]["metadata"]["classification_confidence"], "high")

    def test_changed_file_creates_version_and_supersedes_prior_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "offering.pdf"
            source.write_bytes(b"version one")
            first = build_inventory(
                root,
                self.project,
                [],
                captured_at="2026-08-18T13:00:00Z",
            )
            prior_id = first.records[0]["source_id"]

            source.write_bytes(b"version two")
            second = build_inventory(
                root,
                self.project,
                first.records,
                captured_at="2026-08-18T14:00:00Z",
            )

            self.assertEqual(second.summary["changed_files"], 1)
            self.assertEqual(second.summary["missing_files"], 0)
            self.assertEqual(len(second.records), 2)
            active = [r for r in second.records if r["availability"] == "available"]
            historical = [r for r in second.records if r["availability"] == "missing"]
            self.assertEqual(active[0]["supersedes_source_id"], prior_id)
            self.assertEqual(historical[0]["source_id"], prior_id)

    def test_missing_and_reappearing_file_retains_source_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "offering.pdf"
            source.write_bytes(b"version one")
            first = build_inventory(
                root,
                self.project,
                [],
                captured_at="2026-08-18T13:00:00Z",
            )
            source_id = first.records[0]["source_id"]

            source.unlink()
            missing = build_inventory(
                root,
                self.project,
                first.records,
                captured_at="2026-08-18T14:00:00Z",
            )
            self.assertEqual(missing.summary["missing_files"], 1)
            self.assertEqual(missing.records[0]["availability"], "missing")

            source.write_bytes(b"version one")
            reappeared = build_inventory(
                root,
                self.project,
                missing.records,
                captured_at="2026-08-18T15:00:00Z",
            )
            self.assertEqual(reappeared.summary["reappeared_files"], 1)
            self.assertEqual(reappeared.records[0]["source_id"], source_id)
            self.assertEqual(reappeared.records[0]["availability"], "available")

    def test_non_file_sources_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            web_source = build_source_record(
                "sample-hotel-2026",
                "web_page",
                "url",
                "https://example.com/hotel",
                version_token="retrieved-2026-08-18",
                captured_at="2026-08-18T13:00:00Z",
                metadata={"owner": "web-research-skill"},
            )
            result = build_inventory(
                root,
                self.project,
                [web_source],
                captured_at="2026-08-18T14:00:00Z",
            )
            self.assertEqual(result.records, [web_source])
            self.assertFalse(result.manifest_changed)

    def test_cli_persists_manifest_then_reports_idempotent_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            initialize_project(root, "sample-hotel-2026", "Sample Hotel 2026")
            (root / "offering.pdf").write_bytes(b"version one")
            args = argparse.Namespace(deal_room=str(root), read_only=False)

            first_output = StringIO()
            with redirect_stdout(first_output):
                self.assertEqual(_cmd_inventory_deal_room(args), 0)
            first_summary = json.loads(first_output.getvalue())
            sources_path = root / ".hotel-underwriting" / "sources.jsonl"
            self.assertTrue(first_summary["persisted"])
            self.assertEqual(len(read_jsonl(sources_path)), 1)

            second_output = StringIO()
            with redirect_stdout(second_output):
                self.assertEqual(_cmd_inventory_deal_room(args), 0)
            second_summary = json.loads(second_output.getvalue())
            self.assertFalse(second_summary["manifest_changed"])
            self.assertFalse(second_summary["persisted"])

    def test_cli_read_only_needs_no_existing_project_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="Sample Hotel ") as temp_dir:
            root = Path(temp_dir)
            (root / "offering.pdf").write_bytes(b"version one")
            args = argparse.Namespace(deal_room=str(root), read_only=True)

            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(_cmd_inventory_deal_room(args), 0)
            summary = json.loads(output.getvalue())
            self.assertFalse(summary["project_exists"])
            self.assertFalse(summary["persisted"])
            self.assertFalse((root / ".hotel-underwriting").exists())


if __name__ == "__main__":
    unittest.main()
