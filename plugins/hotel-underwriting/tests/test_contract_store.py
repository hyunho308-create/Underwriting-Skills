from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from _test_paths import add_scripts_to_path

add_scripts_to_path()

from contract_store import (  # noqa: E402
    build_source_record,
    initialize_project,
    make_source_id,
    read_jsonl,
    stable_id,
    write_jsonl_atomic,
)


class ContractStoreTests(unittest.TestCase):
    def test_stable_id_is_deterministic(self) -> None:
        self.assertEqual(stable_id("src", "a", 1), stable_id("src", "a", 1))
        self.assertNotEqual(stable_id("src", "a", 1), stable_id("src", "a", 2))

    def test_source_id_changes_with_content(self) -> None:
        first = make_source_id(
            "sample-hotel-2026",
            "local_file",
            "relative_path",
            "00. OM/sample.pdf",
            content_sha256="a" * 64,
        )
        second = make_source_id(
            "sample-hotel-2026",
            "local_file",
            "relative_path",
            "00. OM/sample.pdf",
            content_sha256="b" * 64,
        )
        self.assertNotEqual(first, second)

    def test_source_paths_are_normalized(self) -> None:
        record = build_source_record(
            "sample-hotel-2026",
            "local_file",
            "relative_path",
            ".\\00. OM\\sample.pdf",
            content_sha256="a" * 64,
            captured_at="2026-08-18T12:00:00Z",
        )
        self.assertEqual(record["location"]["value"], "00. OM/sample.pdf")

    def test_project_initialization_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first, created_first = initialize_project(root, "sample-hotel-2026", "Sample Hotel 2026")
            project_path = root / ".hotel-underwriting" / "project.json"
            before = project_path.read_text(encoding="utf-8")
            second, created_second = initialize_project(root, "sample-hotel-2026", "Sample Hotel 2026")
            after = project_path.read_text(encoding="utf-8")

            self.assertTrue(created_first)
            self.assertFalse(created_second)
            self.assertEqual(first, second)
            self.assertEqual(before, after)
            self.assertFalse((root / ".hotel-underwriting" / "sources.jsonl").exists())

    def test_project_identity_conflict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            initialize_project(root, "sample-hotel-2026", "Sample Hotel 2026")
            with self.assertRaises(ValueError):
                initialize_project(root, "another-hotel-2026", "Another Hotel")

    def test_jsonl_atomic_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "records.jsonl"
            records = [{"id": "one"}, {"id": "two", "value": 2}]
            write_jsonl_atomic(path, records)
            self.assertEqual(read_jsonl(path), records)
            for line in path.read_text(encoding="utf-8").splitlines():
                self.assertIsInstance(json.loads(line), dict)


if __name__ == "__main__":
    unittest.main()
