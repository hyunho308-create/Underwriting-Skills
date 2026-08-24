"""Host-independent helpers for hotel underwriting contract records."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterable


SCHEMA_VERSION = "0.1.0"
PROJECT_DATA_DIR = ".hotel-underwriting"
PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SOURCE_KINDS = {"local_file", "web_page", "database_result", "other"}
LOCATION_KINDS = {"relative_path", "url", "external_id"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not PROJECT_ID_RE.fullmatch(slug):
        raise ValueError("project_id must be 3-64 lowercase kebab-case characters")
    return slug


def stable_id(prefix: str, *parts: Any) -> str:
    payload = json.dumps(parts, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def normalize_location(kind: str, value: str) -> str:
    if kind not in LOCATION_KINDS:
        raise ValueError(f"unsupported location kind: {kind}")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("source location cannot be empty")
    if kind == "relative_path":
        if re.match(r"^[A-Za-z]:[\\/]", cleaned) or cleaned.startswith(("/", "\\\\")):
            raise ValueError("local source paths must be relative to the deal-room root")
        cleaned = cleaned.replace("\\", "/")
        while cleaned.startswith("./"):
            cleaned = cleaned[2:]
    return cleaned


def make_source_id(
    project_id: str,
    source_kind: str,
    location_kind: str,
    location_value: str,
    *,
    content_sha256: str | None = None,
    version_token: str | None = None,
) -> str:
    if not PROJECT_ID_RE.fullmatch(project_id):
        raise ValueError("invalid project_id")
    if source_kind not in SOURCE_KINDS:
        raise ValueError(f"unsupported source kind: {source_kind}")
    if content_sha256 is not None and not SHA256_RE.fullmatch(content_sha256):
        raise ValueError("content_sha256 must be 64 lowercase hexadecimal characters")
    location = normalize_location(location_kind, location_value)
    version_identity = content_sha256 or version_token or "unversioned"
    return stable_id("src", project_id, source_kind, location_kind, location, version_identity)


def build_project_record(
    project_id: str,
    name: str,
    *,
    primary_property_name: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    project_id = slugify(project_id)
    if not name.strip():
        raise ValueError("project name cannot be empty")
    created_at = timestamp or utc_now()
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "name": name.strip(),
        "deal_room_root": ".",
        "created_at": created_at,
        "updated_at": created_at,
    }
    if primary_property_name and primary_property_name.strip():
        record["primary_property_name"] = primary_property_name.strip()
    return record


def build_source_record(
    project_id: str,
    source_kind: str,
    location_kind: str,
    location_value: str,
    *,
    content_sha256: str | None = None,
    version_token: str | None = None,
    supersedes_source_id: str | None = None,
    captured_at: str | None = None,
    document_type: str | None = None,
    metadata: dict[str, Any] | None = None,
    extensions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    location = normalize_location(location_kind, location_value)
    source_id = make_source_id(
        project_id,
        source_kind,
        location_kind,
        location,
        content_sha256=content_sha256,
        version_token=version_token,
    )
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_id": source_id,
        "project_id": project_id,
        "source_kind": source_kind,
        "location": {"kind": location_kind, "value": location},
        "captured_at": captured_at or utc_now(),
    }
    if content_sha256:
        record["content_sha256"] = content_sha256
    if version_token:
        record["version_token"] = version_token
    if supersedes_source_id:
        record["supersedes_source_id"] = supersedes_source_id
    if document_type:
        record["document_type"] = document_type
    if metadata:
        record["metadata"] = metadata
    if extensions:
        record["extensions"] = extensions
    return record


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def write_json_atomic(path: Path, record: dict[str, Any]) -> None:
    _atomic_write(path, json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_jsonl_atomic(path: Path, records: Iterable[dict[str, Any]]) -> None:
    lines = [json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True) for record in records]
    _atomic_write(path, "\n".join(lines) + ("\n" if lines else ""))


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} must contain a JSON object")
            records.append(value)
    return records


def initialize_project(
    deal_room: Path,
    project_id: str,
    name: str,
    *,
    primary_property_name: str | None = None,
) -> tuple[dict[str, Any], bool]:
    root = deal_room.resolve()
    if not root.is_dir():
        raise ValueError(f"deal-room directory does not exist: {deal_room}")

    project_path = root / PROJECT_DATA_DIR / "project.json"
    desired = build_project_record(
        project_id,
        name,
        primary_property_name=primary_property_name,
    )
    if project_path.exists():
        existing = read_json(project_path)
        identity_fields = ["project_id", "name", "primary_property_name"]
        conflicts = [
            field
            for field in identity_fields
            if field in desired and existing.get(field) != desired.get(field)
        ]
        if conflicts:
            raise ValueError(f"existing project has conflicting identity fields: {conflicts}")
        return existing, False

    write_json_atomic(project_path, desired)
    return desired, True
