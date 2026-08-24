from __future__ import annotations

from pathlib import Path
import sys


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def add_scripts_to_path() -> None:
    scripts = str(PLUGIN_ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
