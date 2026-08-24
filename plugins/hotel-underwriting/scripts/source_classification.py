"""Mechanical context, validation, and merge helpers for model classifications."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from contract_store import utc_now


CLASSIFICATION_EXTENSION = "hotel_underwriting.classification"
CLASSIFICATION_METHOD = "model_metadata_first"


@dataclass(frozen=True)
class ClassificationResult:
    records: list[dict[str, Any]]
    summary: dict[str, Any]


def validate_catalog(catalog: dict[str, Any]) -> tuple[str, set[str]]:
    version = catalog.get("catalog_version")
    entries = catalog.get("document_types")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("document-type catalog requires catalog_version")
    if not isinstance(entries, list) or not entries:
        raise ValueError("document-type catalog requires document_types")

    identifiers: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"document_types[{index}] must be an object")
        identifier = entry.get("id")
        definition = entry.get("definition")
        if not isinstance(identifier, str) or (
            "." not in identifier and identifier != "unknown"
        ):
            raise ValueError(f"document_types[{index}].id is invalid")
        if not isinstance(definition, str) or not definition.strip():
            raise ValueError(f"document_types[{index}].definition is required")
        identifiers.append(identifier)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("document-type catalog IDs must be unique")
    if "unknown" not in identifiers:
        raise ValueError("document-type catalog must include unknown")
    return version, set(identifiers)


def _classification_metadata(record: dict[str, Any]) -> dict[str, Any] | None:
    extensions = record.get("extensions", {})
    value = (
        extensions.get(CLASSIFICATION_EXTENSION)
        if isinstance(extensions, dict)
        else None
    )
    return value if isinstance(value, dict) else None


def _eligible_local_source(record: dict[str, Any]) -> bool:
    location = record.get("location", {})
    return (
        record.get("source_kind") == "local_file"
        and record.get("availability", "available") == "available"
        and isinstance(location, dict)
        and location.get("kind") == "relative_path"
        and isinstance(location.get("value"), str)
    )


def pending_source_ids(
    records: list[dict[str, Any]],
    catalog: dict[str, Any],
    *,
    reclassify: bool = False,
) -> set[str]:
    version, allowed_types = validate_catalog(catalog)
    pending: set[str] = set()
    for record in records:
        if not _eligible_local_source(record):
            continue
        if reclassify:
            pending.add(record["source_id"])
            continue
        classification = _classification_metadata(record)
        if classification is None and record.get("document_type"):
            continue
        if (
            classification is not None
            and classification.get("catalog_version") == version
            and record.get("document_type") in allowed_types
        ):
            continue
        pending.add(record["source_id"])
    return pending


def build_classification_context(
    project: dict[str, Any],
    records: list[dict[str, Any]],
    catalog: dict[str, Any],
    *,
    reclassify: bool = False,
) -> dict[str, Any]:
    version, _ = validate_catalog(catalog)
    pending = pending_source_ids(records, catalog, reclassify=reclassify)
    sources: list[dict[str, Any]] = []
    eligible_count = 0

    for record in records:
        if not _eligible_local_source(record):
            continue
        eligible_count += 1
        if record["source_id"] not in pending:
            continue
        relative_path = record["location"]["value"].replace("\\", "/")
        path = PurePosixPath(relative_path)
        metadata = record.get("metadata", {})
        item: dict[str, Any] = {
            "source_id": record["source_id"],
            "relative_path": relative_path,
            "filename": path.name,
            "parent_folders": list(path.parts[:-1]),
            "extension": metadata.get("extension", path.suffix.lower()),
        }
        for key in (
            "file_size_bytes",
            "modified_at",
            "is_temporary",
            "exact_duplicate_of",
            "exact_duplicate_count",
        ):
            if key in metadata:
                item[key] = metadata[key]
        sources.append(item)

    project_context = {
        key: project[key]
        for key in ("project_id", "name", "primary_property_name")
        if key in project
    }
    return {
        "catalog_version": version,
        "scope": catalog.get("scope"),
        "project": project_context,
        "document_types": catalog["document_types"],
        "instructions": {
            "decision_fields": [
                "source_id",
                "document_type",
                "uncertainty_reasons",
            ],
            "uncertainty_reasons": "Omit when there is no meaningful ambiguity. Use a non-empty list for unknown.",
            "content_access": (
                "Classify from metadata first. Open only files whose metadata does not support "
                "a defensible type, and inspect only enough content to identify their purpose."
            ),
        },
        "summary": {
            "eligible_sources": eligible_count,
            "pending_sources": len(sources),
            "preserved_classifications": eligible_count - len(sources),
        },
        "sources": sources,
    }


def _normalize_decisions(
    decisions: list[dict[str, Any]],
    pending: set[str],
    allowed_types: set[str],
) -> dict[str, dict[str, Any]]:
    allowed_fields = {"source_id", "document_type", "uncertainty_reasons"}
    normalized: dict[str, dict[str, Any]] = {}
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise ValueError(f"classification decision {index} must be an object")
        extra_fields = sorted(set(decision) - allowed_fields)
        if extra_fields:
            raise ValueError(f"classification decision {index} has unsupported fields: {extra_fields}")
        source_id = decision.get("source_id")
        document_type = decision.get("document_type")
        if not isinstance(source_id, str) or source_id not in pending:
            raise ValueError(f"classification decision {index} has an unexpected source_id")
        if source_id in normalized:
            raise ValueError(f"duplicate classification decision for {source_id}")
        if document_type not in allowed_types:
            raise ValueError(f"classification decision {index} has unsupported document_type")

        raw_reasons = decision.get("uncertainty_reasons", [])
        if not isinstance(raw_reasons, list) or not all(
            isinstance(reason, str) and reason.strip() for reason in raw_reasons
        ):
            raise ValueError(
                f"classification decision {index} uncertainty_reasons must be non-empty strings"
            )
        reasons = [reason.strip() for reason in raw_reasons]
        if document_type == "unknown" and not reasons:
            raise ValueError("unknown classifications require uncertainty_reasons")
        normalized[source_id] = {
            "source_id": source_id,
            "document_type": document_type,
            "uncertainty_reasons": reasons,
        }

    missing = sorted(pending - set(normalized))
    if missing:
        example = ", ".join(missing[:5])
        raise ValueError(
            f"classification decisions are missing {len(missing)} pending sources: {example}"
        )
    return normalized


def apply_classification_decisions(
    records: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    catalog: dict[str, Any],
    *,
    classified_at: str | None = None,
    reclassify: bool = False,
) -> ClassificationResult:
    version, allowed_types = validate_catalog(catalog)
    pending = pending_source_ids(records, catalog, reclassify=reclassify)
    normalized = _normalize_decisions(decisions, pending, allowed_types)
    timestamp = classified_at or utc_now()
    updated_records = deepcopy(records)
    type_counts: Counter[str] = Counter()
    uncertain_count = 0

    for record in updated_records:
        decision = normalized.get(record.get("source_id"))
        if decision is None:
            continue
        record["document_type"] = decision["document_type"]
        extensions = record.setdefault("extensions", {})
        classification: dict[str, Any] = {
            "catalog_version": version,
            "classified_at": timestamp,
            "method": CLASSIFICATION_METHOD,
        }
        if decision["uncertainty_reasons"]:
            classification["uncertainty_reasons"] = decision["uncertainty_reasons"]
            uncertain_count += 1
        extensions[CLASSIFICATION_EXTENSION] = classification
        type_counts[decision["document_type"]] += 1

    return ClassificationResult(
        records=updated_records,
        summary={
            "catalog_version": version,
            "classified_sources": len(normalized),
            "uncertain_sources": uncertain_count,
            "unknown_sources": type_counts["unknown"],
            "document_types": dict(sorted(type_counts.items())),
        },
    )
