"""Deterministic local-file inventory for hotel underwriting deal rooms."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from typing import Any

from contract_store import build_source_record, normalize_location, utc_now


MANAGED_METADATA_KEYS = {
    "exact_duplicate_count",
    "exact_duplicate_of",
    "extension",
    "file_size_bytes",
    "inventory_error",
    "is_symlink",
    "is_temporary",
    "modified_at",
}
TEMPORARY_SUFFIXES = {
    ".bak",
    ".crdownload",
    ".download",
    ".part",
    ".partial",
    ".swp",
    ".swo",
    ".temp",
    ".tmp",
}


@dataclass(frozen=True)
class FileSnapshot:
    relative_path: str
    content_sha256: str | None
    version_token: str | None
    availability: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class InventoryResult:
    records: list[dict[str, Any]]
    summary: dict[str, Any]
    manifest_changed: bool


def _as_utc(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat().replace("+00:00", "Z")


def _is_temporary(name: str) -> bool:
    lowered = name.lower()
    return (
        name.startswith("~$")
        or lowered.startswith(".tmp")
        or lowered.endswith("~")
        or Path(lowered).suffix in TEMPORARY_SUFFIXES
    )


def _hash_stable_file(path: Path) -> tuple[str, os.stat_result]:
    """Hash a byte stream, retrying once if the file changes during the read."""
    for _ in range(2):
        before = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns):
            return digest.hexdigest(), after
    raise OSError("file changed while it was being hashed")


def _snapshot_file(root: Path, path: Path) -> FileSnapshot:
    relative_path = normalize_location("relative_path", path.relative_to(root).as_posix())
    base_metadata: dict[str, Any] = {
        "extension": path.suffix.lower(),
        "is_symlink": path.is_symlink(),
        "is_temporary": _is_temporary(path.name),
    }
    try:
        content_sha256, stat = _hash_stable_file(path)
        base_metadata.update(
            {
                "file_size_bytes": stat.st_size,
                "modified_at": _as_utc(stat.st_mtime),
            }
        )
        return FileSnapshot(relative_path, content_sha256, None, "available", base_metadata)
    except OSError as exc:
        try:
            stat = path.stat()
            base_metadata.update(
                {
                    "file_size_bytes": stat.st_size,
                    "modified_at": _as_utc(stat.st_mtime),
                }
            )
            version_token = f"inaccessible:{stat.st_size}:{stat.st_mtime_ns}"
        except OSError:
            version_token = "inaccessible"
        base_metadata["inventory_error"] = f"{type(exc).__name__}: {exc}"
        return FileSnapshot(relative_path, None, version_token, "inaccessible", base_metadata)


def scan_deal_room(root: Path) -> tuple[list[FileSnapshot], list[str]]:
    """Collect file-system metadata and hashes without parsing file contents."""
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"deal-room directory does not exist: {root}")

    snapshots: list[FileSnapshot] = []
    inaccessible_directories: list[str] = []

    def handle_walk_error(error: OSError) -> None:
        filename = getattr(error, "filename", None)
        if filename:
            try:
                relative = Path(filename).resolve().relative_to(root).as_posix()
            except (OSError, ValueError):
                relative = str(filename)
        else:
            relative = "<unknown>"
        inaccessible_directories.append(relative)

    for current, directories, filenames in os.walk(
        root,
        topdown=True,
        followlinks=False,
        onerror=handle_walk_error,
    ):
        directories[:] = sorted(
            (name for name in directories if name != ".hotel-underwriting"),
            key=str.casefold,
        )
        for filename in sorted(filenames, key=str.casefold):
            snapshots.append(_snapshot_file(root, Path(current) / filename))

    snapshots.sort(key=lambda item: (item.relative_path.casefold(), item.relative_path))
    return snapshots, sorted(set(inaccessible_directories), key=str.casefold)


def _is_managed_local_source(record: dict[str, Any], project_id: str) -> bool:
    location = record.get("location", {})
    return (
        record.get("project_id") == project_id
        and record.get("source_kind") == "local_file"
        and location.get("kind") == "relative_path"
        and isinstance(location.get("value"), str)
    )


def _record_path(record: dict[str, Any]) -> str:
    return normalize_location("relative_path", record["location"]["value"])


def _latest_record(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None
    return max(records, key=lambda item: (item.get("captured_at", ""), item["source_id"]))


def _merge_inventory_metadata(
    existing: dict[str, Any] | None,
    inventory_metadata: dict[str, Any],
) -> dict[str, Any]:
    metadata = dict((existing or {}).get("metadata", {}))
    for key in MANAGED_METADATA_KEYS:
        metadata.pop(key, None)
    metadata.update(inventory_metadata)
    return metadata


def _under_inaccessible_directory(path: str, directories: list[str]) -> bool:
    lowered = path.casefold()
    for directory in directories:
        normalized = directory.replace("\\", "/").strip("/")
        if normalized and (
            lowered == normalized.casefold()
            or lowered.startswith(normalized.casefold() + "/")
        ):
            return True
    return False


def _record_sort_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    location = record.get("location", {})
    return (
        str(record.get("source_kind", "")),
        str(location.get("value", "")).casefold(),
        str(record.get("captured_at", "")),
        str(record.get("source_id", "")),
    )


def build_inventory(
    root: Path,
    project: dict[str, Any],
    existing_records: list[dict[str, Any]],
    *,
    captured_at: str | None = None,
) -> InventoryResult:
    """Build a refreshed manifest while retaining prior source versions."""
    project_id = project["project_id"]
    run_timestamp = captured_at or utc_now()
    snapshots, inaccessible_directories = scan_deal_room(root)

    managed_existing = [
        record for record in existing_records if _is_managed_local_source(record, project_id)
    ]
    unmanaged_existing = [
        dict(record) for record in existing_records if not _is_managed_local_source(record, project_id)
    ]
    existing_by_id = {record["source_id"]: record for record in managed_existing}
    existing_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in managed_existing:
        existing_by_path[_record_path(record)].append(record)

    current_records: list[dict[str, Any]] = []
    current_ids: set[str] = set()
    scanned_paths = {snapshot.relative_path for snapshot in snapshots}
    counters = Counter()

    for snapshot in snapshots:
        candidate = build_source_record(
            project_id,
            "local_file",
            "relative_path",
            snapshot.relative_path,
            content_sha256=snapshot.content_sha256,
            version_token=snapshot.version_token,
            captured_at=run_timestamp,
            metadata=snapshot.metadata,
        )
        source_id = candidate["source_id"]
        prior_same_version = existing_by_id.get(source_id)

        if prior_same_version is not None:
            record = dict(prior_same_version)
            was_available = record.get("availability", "available") == "available"
            record["availability"] = snapshot.availability
            record["metadata"] = _merge_inventory_metadata(prior_same_version, snapshot.metadata)
            if was_available:
                counters["unchanged_files"] += 1
            else:
                counters["reappeared_files"] += 1
        else:
            previous = _latest_record(existing_by_path.get(snapshot.relative_path, []))
            if previous is not None:
                candidate["supersedes_source_id"] = previous["source_id"]
                counters["changed_files"] += 1
            else:
                counters["new_files"] += 1
            candidate["availability"] = snapshot.availability
            record = candidate

        if snapshot.availability == "inaccessible":
            counters["inaccessible_files"] += 1
        current_records.append(record)
        current_ids.add(source_id)

    historical_records: list[dict[str, Any]] = []
    missing_paths: set[str] = set()
    for existing in managed_existing:
        if existing["source_id"] in current_ids:
            continue
        record = dict(existing)
        path = _record_path(record)
        if path in scanned_paths:
            record["availability"] = "missing"
        elif _under_inaccessible_directory(path, inaccessible_directories):
            record["availability"] = "inaccessible"
        else:
            record["availability"] = "missing"
            missing_paths.add(path)
        historical_records.append(record)

    duplicate_groups: list[list[dict[str, Any]]] = []
    by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in current_records:
        metadata = record.setdefault("metadata", {})
        metadata.pop("exact_duplicate_of", None)
        metadata.pop("exact_duplicate_count", None)
        if record.get("availability") == "available" and record.get("content_sha256"):
            by_hash[record["content_sha256"]].append(record)

    for records in by_hash.values():
        if len(records) < 2:
            continue
        records.sort(
            key=lambda item: (
                bool(item.get("metadata", {}).get("is_temporary")),
                _record_path(item).casefold(),
                _record_path(item),
            )
        )
        canonical = records[0]
        canonical["metadata"]["exact_duplicate_count"] = len(records)
        for duplicate in records[1:]:
            duplicate["metadata"]["exact_duplicate_of"] = canonical["source_id"]
        duplicate_groups.append(records)

    all_records = sorted(
        unmanaged_existing + historical_records + current_records,
        key=_record_sort_key,
    )
    manifest_changed = all_records != existing_records

    extension_counts: Counter[str] = Counter()
    directory_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"file_count": 0, "bytes": 0}
    )
    total_bytes = 0
    temporary_paths: list[str] = []
    for snapshot in snapshots:
        extension = snapshot.metadata.get("extension") or "[no extension]"
        extension_counts[extension] += 1
        size = int(snapshot.metadata.get("file_size_bytes", 0))
        total_bytes += size
        top_directory = snapshot.relative_path.split("/", 1)[0]
        directory_counts[top_directory]["file_count"] += 1
        directory_counts[top_directory]["bytes"] += size
        if snapshot.metadata.get("is_temporary"):
            temporary_paths.append(snapshot.relative_path)

    top_extensions = [
        {"extension": extension, "file_count": count}
        for extension, count in sorted(
            extension_counts.items(), key=lambda item: (-item[1], item[0])
        )[:10]
    ]
    top_directories = [
        {"path": path, **values}
        for path, values in sorted(
            directory_counts.items(),
            key=lambda item: (-item[1]["file_count"], item[0].casefold()),
        )[:10]
    ]
    duplicate_examples = [
        [_record_path(record) for record in group]
        for group in sorted(
            duplicate_groups,
            key=lambda group: (-len(group), _record_path(group[0]).casefold()),
        )[:5]
    ]

    summary: dict[str, Any] = {
        "project_id": project_id,
        "current_files": len(snapshots),
        "current_bytes": total_bytes,
        "source_versions": len(managed_existing) + counters["new_files"] + counters["changed_files"],
        "new_files": counters["new_files"],
        "changed_files": counters["changed_files"],
        "unchanged_files": counters["unchanged_files"],
        "reappeared_files": counters["reappeared_files"],
        "missing_files": len(missing_paths),
        "inaccessible_files": counters["inaccessible_files"],
        "temporary_files": len(temporary_paths),
        "exact_duplicate_groups": len(duplicate_groups),
        "top_extensions": top_extensions,
        "top_directories": top_directories,
    }
    if temporary_paths:
        summary["temporary_examples"] = temporary_paths[:10]
    if duplicate_examples:
        summary["duplicate_examples"] = duplicate_examples
    if inaccessible_directories:
        summary["inaccessible_directories"] = inaccessible_directories[:10]

    return InventoryResult(all_records, summary, manifest_changed)
