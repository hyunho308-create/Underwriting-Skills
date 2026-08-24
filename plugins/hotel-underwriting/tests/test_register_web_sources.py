from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from _test_paths import PLUGIN_ROOT, add_scripts_to_path

add_scripts_to_path()

from contract_store import initialize_project, read_jsonl


def test_register_web_sources_is_idempotent(tmp_path: Path) -> None:
    deal_room = tmp_path / "Example Hotel"
    deal_room.mkdir()
    initialize_project(deal_room, "example-hotel", "Example Hotel")
    bundle_path = tmp_path / "web-sources.json"
    bundle_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "url": "https://example.gov/property-tax",
                        "version_token": "accessed-2026-08-19",
                        "metadata": {
                            "title": "Property Tax",
                            "publisher": "Example Assessor",
                            "accessed_at": "2026-08-19",
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    command = [
        sys.executable,
        str(PLUGIN_ROOT / "scripts" / "contracts_cli.py"),
        "register-web-sources",
        "--deal-room",
        str(deal_room),
        "--input",
        str(bundle_path),
    ]

    first = subprocess.run(command, check=True, capture_output=True, text=True)
    second = subprocess.run(command, check=True, capture_output=True, text=True)

    assert json.loads(first.stdout)["sources_added"] == 1
    assert json.loads(second.stdout)["sources_added"] == 0
    records = read_jsonl(deal_room / ".hotel-underwriting" / "sources.jsonl")
    assert len(records) == 1
    assert records[0]["source_kind"] == "web_page"
    assert records[0]["location"]["value"] == "https://example.gov/property-tax"
