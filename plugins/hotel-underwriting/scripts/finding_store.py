"""Mechanical validation and persistence for model-produced hotel findings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contract_store import SCHEMA_VERSION, stable_id


SUPPORT_TYPES = {"direct", "calculated", "inferred"}
EXTRACTION_METHODS = {"model_visual_review", "model_text_review", "deterministic"}


@dataclass(frozen=True)
class FindingRecords:
    entity: dict[str, Any]
    evidence: list[dict[str, Any]]
    facts: list[dict[str, Any]]


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _validate_value_type(value: Any, expected: str, field: str) -> None:
    valid = {
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }.get(expected)
    if valid is None:
        raise ValueError(f"field catalog has unsupported value_type {expected!r} for {field}")
    if not valid:
        raise ValueError(f"fact {field} value must be {expected}")


def build_finding_records(
    project: dict[str, Any],
    sources: list[dict[str, Any]],
    bundle: dict[str, Any],
    field_catalog: dict[str, Any],
    *,
    timestamp: str,
) -> FindingRecords:
    if not isinstance(bundle, dict):
        raise ValueError("finding bundle must be a JSON object")
    unknown_bundle_fields = sorted(set(bundle) - {"producer", "entity", "evidence", "facts"})
    if unknown_bundle_fields:
        raise ValueError(f"finding bundle has unsupported fields: {unknown_bundle_fields}")

    producer_input = bundle.get("producer")
    if not isinstance(producer_input, dict):
        raise ValueError("finding bundle producer must be an object")
    producer = {
        "skill": _require_string(producer_input.get("skill"), "producer.skill"),
        "version": _require_string(producer_input.get("version"), "producer.version"),
    }

    entity_input = bundle.get("entity")
    if not isinstance(entity_input, dict):
        raise ValueError("finding bundle entity must be an object")
    entity_type = _require_string(entity_input.get("entity_type"), "entity.entity_type")
    if entity_type != "hotel":
        raise ValueError("the initial finding workflow supports only hotel entities")
    entity_name = _require_string(entity_input.get("name"), "entity.name")
    aliases = entity_input.get("aliases", [])
    if not isinstance(aliases, list) or any(not isinstance(item, str) or not item.strip() for item in aliases):
        raise ValueError("entity.aliases must be non-empty strings")

    project_id = project["project_id"]
    entity_id = stable_id("ent", project_id, entity_type, entity_name.casefold())
    entity: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "entity_id": entity_id,
        "project_id": project_id,
        "entity_type": entity_type,
        "name": entity_name,
    }
    if aliases:
        entity["aliases"] = aliases

    known_source_ids = {source["source_id"] for source in sources}
    evidence_inputs = bundle.get("evidence")
    if not isinstance(evidence_inputs, list) or not evidence_inputs:
        raise ValueError("finding bundle evidence must be a non-empty array")

    evidence_by_ref: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(evidence_inputs):
        if not isinstance(item, dict):
            raise ValueError(f"evidence[{index}] must be an object")
        ref = _require_string(item.get("ref"), f"evidence[{index}].ref")
        if ref in evidence_by_ref:
            raise ValueError(f"duplicate evidence ref: {ref}")
        source_id = _require_string(item.get("source_id"), f"evidence[{index}].source_id")
        if source_id not in known_source_ids:
            raise ValueError(f"evidence ref {ref} references unknown source_id {source_id}")
        locator = item.get("locator")
        if not isinstance(locator, dict):
            raise ValueError(f"evidence ref {ref} locator must be an object")
        locator_kind = _require_string(locator.get("kind"), f"evidence ref {ref} locator.kind")
        locator_value = _require_string(locator.get("value"), f"evidence ref {ref} locator.value")
        normalized_locator: dict[str, str] = {"kind": locator_kind, "value": locator_value}
        if locator.get("label") is not None:
            normalized_locator["label"] = _require_string(
                locator["label"], f"evidence ref {ref} locator.label"
            )
        excerpt = item.get("excerpt")
        data = item.get("data")
        if excerpt is None and data is None:
            raise ValueError(f"evidence ref {ref} requires excerpt or data")
        if excerpt is not None:
            excerpt = _require_string(excerpt, f"evidence ref {ref} excerpt")
            if len(excerpt) > 2000:
                raise ValueError(f"evidence ref {ref} excerpt exceeds 2000 characters")
        if data is not None and not isinstance(data, dict):
            raise ValueError(f"evidence ref {ref} data must be an object")
        extraction_method = item.get("extraction_method", "model_visual_review")
        if extraction_method not in EXTRACTION_METHODS:
            raise ValueError(f"evidence ref {ref} has unsupported extraction_method")

        evidence_id = stable_id(
            "ev",
            project_id,
            source_id,
            normalized_locator,
            excerpt,
            data,
            extraction_method,
        )
        record: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "evidence_id": evidence_id,
            "project_id": project_id,
            "source_id": source_id,
            "locator": normalized_locator,
            "captured_at": timestamp,
            "extraction_method": extraction_method,
        }
        if excerpt is not None:
            record["excerpt"] = excerpt
        if data is not None:
            record["data"] = data
        evidence_by_ref[ref] = record

    catalog_fields = field_catalog.get("fields")
    if not isinstance(catalog_fields, dict):
        raise ValueError("field catalog fields must be an object")
    extension_prefix = field_catalog.get("extension_prefix", "custom.")
    fact_inputs = bundle.get("facts", [])
    if not isinstance(fact_inputs, list):
        raise ValueError("finding bundle facts must be an array when present")

    facts: list[dict[str, Any]] = []
    for index, item in enumerate(fact_inputs):
        if not isinstance(item, dict):
            raise ValueError(f"facts[{index}] must be an object")
        field = _require_string(item.get("field"), f"facts[{index}].field")
        field_definition = catalog_fields.get(field)
        if field_definition is None and not field.startswith(extension_prefix):
            raise ValueError(f"fact field is not in the catalog: {field}")
        if "value" not in item:
            raise ValueError(f"fact {field} is missing value")
        value = item["value"]
        if field_definition is not None:
            _validate_value_type(value, field_definition["value_type"], field)

        evidence_refs = item.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            raise ValueError(f"fact {field} requires evidence_refs")
        missing_refs = [ref for ref in evidence_refs if ref not in evidence_by_ref]
        if missing_refs:
            raise ValueError(f"fact {field} references missing evidence refs: {missing_refs}")
        evidence_ids = [evidence_by_ref[ref]["evidence_id"] for ref in evidence_refs]

        support_type = item.get("support_type", "direct")
        if support_type not in SUPPORT_TYPES:
            raise ValueError(f"fact {field} has unsupported support_type")
        derivation = item.get("derivation")
        if support_type == "calculated" and not derivation:
            raise ValueError(f"calculated fact {field} requires derivation")

        fact_id = stable_id(
            "fact",
            project_id,
            entity_id,
            field,
            value,
            evidence_ids,
            support_type,
            producer,
        )
        fact: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "fact_id": fact_id,
            "project_id": project_id,
            "entity_id": entity_id,
            "field": field,
            "value": value,
            "evidence_ids": evidence_ids,
            "support_type": support_type,
            "review_status": "unreviewed",
            "extracted_at": timestamp,
            "producer": producer,
        }
        for optional in ("unit", "effective_date", "derivation", "uncertainty_reasons", "extensions"):
            if item.get(optional) is not None:
                fact[optional] = item[optional]
        facts.append(fact)

    return FindingRecords(entity=entity, evidence=list(evidence_by_ref.values()), facts=facts)


def merge_by_id(existing: list[dict[str, Any]], additions: list[dict[str, Any]], id_field: str) -> list[dict[str, Any]]:
    merged = list(existing)
    known = {record[id_field] for record in existing}
    for record in additions:
        if record[id_field] not in known:
            merged.append(record)
            known.add(record[id_field])
    return merged
