"""Command-line entry point for hotel underwriting source contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from contract_store import (
    PROJECT_DATA_DIR,
    build_source_record,
    build_project_record,
    initialize_project,
    read_json,
    read_jsonl,
    slugify,
    utc_now,
    write_json_atomic,
    write_jsonl_atomic,
)
from deal_room_inventory import build_inventory
from finding_store import build_finding_records, merge_by_id
from schema_validation import SchemaValidationError, validate
from source_classification import (
    apply_classification_decisions,
    build_classification_context,
    validate_catalog,
)
from str_report_parser import extract_str_findings


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PLUGIN_ROOT / "schemas"
DOCUMENT_TYPES_PATH = PLUGIN_ROOT / "references" / "document-types.json"
FIELD_CATALOG_PATH = PLUGIN_ROOT / "references" / "field-catalog.json"


def _load_schema(name: str) -> dict:
    with (SCHEMA_DIR / name).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _load_document_types() -> dict:
    with DOCUMENT_TYPES_PATH.open("r", encoding="utf-8") as stream:
        catalog = json.load(stream)
    validate_catalog(catalog)
    return catalog


def _load_field_catalog() -> dict:
    with FIELD_CATALOG_PATH.open("r", encoding="utf-8") as stream:
        catalog = json.load(stream)
    if not isinstance(catalog.get("fields"), dict):
        raise ValueError("field catalog fields must be an object")
    return catalog


def _load_deal_room_contracts(deal_room: Path) -> tuple[Path, dict, list[dict]]:
    root = deal_room.resolve()
    data_dir = root / PROJECT_DATA_DIR
    project_path = data_dir / "project.json"
    sources_path = data_dir / "sources.jsonl"
    if not project_path.exists():
        raise ValueError(f"missing project contract: {project_path}")
    if not sources_path.exists():
        raise ValueError(f"missing source manifest: {sources_path}")

    project = read_json(project_path)
    records = read_jsonl(sources_path)
    validate(project, _load_schema("project.schema.json"))
    source_schema = _load_schema("source.schema.json")
    for index, record in enumerate(records):
        validate(record, source_schema, f"sources[{index}]")
    return data_dir, project, records


def _cmd_init_project(args: argparse.Namespace) -> int:
    record, created = initialize_project(
        Path(args.deal_room),
        args.project_id,
        args.name,
        primary_property_name=args.primary_property_name,
    )
    validate(record, _load_schema("project.schema.json"))
    print(json.dumps({"created": created, "project": record}, indent=2, sort_keys=True))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    data_dir = Path(args.deal_room).resolve() / PROJECT_DATA_DIR
    project_path = data_dir / "project.json"
    if not project_path.exists():
        raise ValueError(f"missing project contract: {project_path}")

    validate(read_json(project_path), _load_schema("project.schema.json"))
    source_count = 0
    sources_path = data_dir / "sources.jsonl"
    if sources_path.exists():
        source_schema = _load_schema("source.schema.json")
        for source_count, record in enumerate(read_jsonl(sources_path), start=1):
            validate(record, source_schema, f"sources[{source_count - 1}]")

    counts = {"project": "valid", "sources": source_count}
    for collection, schema_name in (
        ("entities", "entity.schema.json"),
        ("evidence", "evidence.schema.json"),
        ("facts", "fact.schema.json"),
    ):
        path = data_dir / f"{collection}.jsonl"
        count = 0
        if path.exists():
            schema = _load_schema(schema_name)
            for count, record in enumerate(read_jsonl(path), start=1):
                validate(record, schema, f"{collection}[{count - 1}]")
        counts[collection] = count

    print(json.dumps(counts, sort_keys=True))
    return 0


def _cmd_register_web_sources(args: argparse.Namespace) -> int:
    deal_room = Path(args.deal_room).resolve()
    data_dir = deal_room / PROJECT_DATA_DIR
    project_path = data_dir / "project.json"
    if not project_path.exists():
        raise ValueError(f"missing project contract: {project_path}")

    project = read_json(project_path)
    validate(project, _load_schema("project.schema.json"))
    bundle = read_json(Path(args.input).resolve())
    if set(bundle) != {"sources"} or not isinstance(bundle["sources"], list) or not bundle["sources"]:
        raise ValueError("web-source bundle must contain one non-empty sources array")

    run_timestamp = utc_now()
    additions: list[dict] = []
    for index, item in enumerate(bundle["sources"]):
        if not isinstance(item, dict):
            raise ValueError(f"sources[{index}] must be an object")
        allowed = {
            "url",
            "version_token",
            "supersedes_source_id",
            "document_type",
            "metadata",
            "extensions",
        }
        unknown = sorted(set(item) - allowed)
        if unknown:
            raise ValueError(f"sources[{index}] has unsupported fields: {unknown}")
        url = item.get("url")
        version_token = item.get("version_token")
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"sources[{index}].url must be a non-empty string")
        if not isinstance(version_token, str) or not version_token.strip():
            raise ValueError(f"sources[{index}].version_token must be a non-empty string")
        for optional_object in ("metadata", "extensions"):
            value = item.get(optional_object)
            if value is not None and not isinstance(value, dict):
                raise ValueError(f"sources[{index}].{optional_object} must be an object")
        additions.append(
            build_source_record(
                project["project_id"],
                "web_page",
                "url",
                url,
                version_token=version_token,
                supersedes_source_id=item.get("supersedes_source_id"),
                captured_at=run_timestamp,
                document_type=item.get("document_type"),
                metadata=item.get("metadata"),
                extensions=item.get("extensions"),
            )
        )

    source_schema = _load_schema("source.schema.json")
    for index, record in enumerate(additions):
        validate(record, source_schema, f"sources[{index}]")
    sources_path = data_dir / "sources.jsonl"
    existing = read_jsonl(sources_path) if sources_path.exists() else []
    merged = merge_by_id(existing, additions, "source_id")
    for index, record in enumerate(merged):
        validate(record, source_schema, f"sources[{index}]")
    write_jsonl_atomic(sources_path, merged)

    project = dict(project)
    project["updated_at"] = run_timestamp
    validate(project, _load_schema("project.schema.json"))
    write_json_atomic(project_path, project)
    print(
        json.dumps(
            {
                "sources_added": len(merged) - len(existing),
                "sources_total": len(merged),
                "source_ids": [record["source_id"] for record in additions],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _cmd_apply_findings(args: argparse.Namespace) -> int:
    data_dir, project, sources = _load_deal_room_contracts(Path(args.deal_room))
    bundle = read_json(Path(args.input).resolve())
    run_timestamp = utc_now()
    built = build_finding_records(
        project,
        sources,
        bundle,
        _load_field_catalog(),
        timestamp=run_timestamp,
    )

    entity_schema = _load_schema("entity.schema.json")
    evidence_schema = _load_schema("evidence.schema.json")
    fact_schema = _load_schema("fact.schema.json")
    validate(built.entity, entity_schema, "entity")
    for index, record in enumerate(built.evidence):
        validate(record, evidence_schema, f"evidence[{index}]")
    for index, record in enumerate(built.facts):
        validate(record, fact_schema, f"facts[{index}]")

    entities_path = data_dir / "entities.jsonl"
    evidence_path = data_dir / "evidence.jsonl"
    facts_path = data_dir / "facts.jsonl"
    existing_entities = read_jsonl(entities_path) if entities_path.exists() else []
    existing_evidence = read_jsonl(evidence_path) if evidence_path.exists() else []
    existing_facts = read_jsonl(facts_path) if facts_path.exists() else []
    entities = merge_by_id(existing_entities, [built.entity], "entity_id")
    evidence = merge_by_id(existing_evidence, built.evidence, "evidence_id")
    facts = merge_by_id(existing_facts, built.facts, "fact_id")

    for index, record in enumerate(entities):
        validate(record, entity_schema, f"entities[{index}]")
    for index, record in enumerate(evidence):
        validate(record, evidence_schema, f"evidence[{index}]")
    for index, record in enumerate(facts):
        validate(record, fact_schema, f"facts[{index}]")

    write_jsonl_atomic(entities_path, entities)
    write_jsonl_atomic(evidence_path, evidence)
    if built.facts:
        write_jsonl_atomic(facts_path, facts)
    project = dict(project)
    project["updated_at"] = run_timestamp
    validate(project, _load_schema("project.schema.json"))
    write_json_atomic(data_dir / "project.json", project)
    print(
        json.dumps(
            {
                "entity_id": built.entity["entity_id"],
                "evidence_added": len(evidence) - len(existing_evidence),
                "facts_added": len(facts) - len(existing_facts),
                "evidence_total": len(evidence),
                "facts_total": len(facts),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _cmd_extract_str_data(args: argparse.Namespace) -> int:
    if not args.read_only and not args.entity_name:
        raise ValueError(
            "--entity-name is required for persisted STR extraction; the model must resolve the canonical hotel name"
        )
    data_dir, project, sources = _load_deal_room_contracts(Path(args.deal_room))
    source_ids = set(args.source_id) if args.source_id else None
    bundles, coverage = extract_str_findings(
        Path(args.deal_room),
        sources,
        source_ids=source_ids,
        entity_name=args.entity_name,
    )
    run_timestamp = utc_now()
    coverage = dict(coverage)
    coverage["generated_at"] = run_timestamp
    coverage["read_only"] = bool(args.read_only)

    built_entities: list[dict] = []
    built_evidence: list[dict] = []
    for bundle in bundles:
        built = build_finding_records(
            project,
            sources,
            bundle,
            _load_field_catalog(),
            timestamp=run_timestamp,
        )
        if built.facts:
            raise ValueError("STR extraction must not produce facts")
        built_entities.append(built.entity)
        built_evidence.extend(built.evidence)

    entity_schema = _load_schema("entity.schema.json")
    evidence_schema = _load_schema("evidence.schema.json")
    for index, record in enumerate(built_entities):
        validate(record, entity_schema, f"entities[{index}]")
    for index, record in enumerate(built_evidence):
        validate(record, evidence_schema, f"evidence[{index}]")

    entities_path = data_dir / "entities.jsonl"
    evidence_path = data_dir / "evidence.jsonl"
    existing_entities = read_jsonl(entities_path) if entities_path.exists() else []
    existing_evidence = read_jsonl(evidence_path) if evidence_path.exists() else []
    entities = merge_by_id(existing_entities, built_entities, "entity_id")
    def str_replacement_key(record: dict) -> tuple[str | None, str | None, str | None]:
        primitive = record.get("data", {}).get("information_primitive", {})
        attributes = primitive.get("attributes", {})
        return (
            record.get("source_id"),
            attributes.get("comp_set_key"),
            attributes.get("observation_kind"),
        )

    replacement_keys = {str_replacement_key(record) for record in built_evidence}
    retained_evidence = [
        record
        for record in existing_evidence
        if not (
            record.get("data", {}).get("information_primitive", {}).get("type") == "property.str"
            and str_replacement_key(record) in replacement_keys
        )
    ]
    evidence = merge_by_id(retained_evidence, built_evidence, "evidence_id")
    for index, record in enumerate(entities):
        validate(record, entity_schema, f"entities[{index}]")
    for index, record in enumerate(evidence):
        validate(record, evidence_schema, f"evidence[{index}]")

    coverage["entities_added"] = len(entities) - len(existing_entities)
    coverage["evidence_added"] = len(evidence) - len(existing_evidence)
    coverage["facts_added"] = 0
    coverage["evidence_total"] = len(evidence)
    persisted = False
    coverage_path = (
        Path(args.coverage_output).resolve()
        if args.coverage_output
        else data_dir / "derived" / "str-information-evidence-coverage.json"
    )
    if not args.read_only:
        if built_entities:
            write_jsonl_atomic(entities_path, entities)
        if built_evidence:
            write_jsonl_atomic(evidence_path, evidence)
        if built_entities or built_evidence:
            project = dict(project)
            project["updated_at"] = run_timestamp
            validate(project, _load_schema("project.schema.json"))
            write_json_atomic(data_dir / "project.json", project)
        write_json_atomic(coverage_path, coverage)
        persisted = True

    summary = {
        "status": coverage["status"],
        "sources_considered": coverage["sources_considered"],
        "comp_sets_selected": coverage["comp_sets_selected"],
        "evidence_prepared": coverage["evidence_prepared"],
        "entities_added": coverage["entities_added"],
        "evidence_added": coverage["evidence_added"],
        "facts_added": 0,
        "read_only": bool(args.read_only),
        "persisted": persisted,
        "comp_sets": [
            {
                "subject": item["subject"],
                "label": item["comp_set_label"],
                "version_id": item["comp_set_version_id"],
                "report_month": item["report_month"],
                "monthly_period_start": item["monthly_period_start"],
                "monthly_period_end": item["monthly_period_end"],
                "status": item["status"],
                "source_id": item["source_id"],
            }
            for item in coverage["comp_sets"]
        ],
    }
    if persisted:
        summary["coverage_output"] = str(coverage_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _cmd_inventory_deal_room(args: argparse.Namespace) -> int:
    deal_room = Path(args.deal_room).resolve()
    data_dir = deal_room / PROJECT_DATA_DIR
    project_path = data_dir / "project.json"
    project_exists = project_path.exists()
    if project_exists:
        project = read_json(project_path)
    elif args.read_only:
        project = build_project_record(slugify(deal_room.name), deal_room.name)
    else:
        raise ValueError(
            f"missing project contract: {project_path}; initialize the project before inventorying"
        )

    validate(project, _load_schema("project.schema.json"))
    sources_path = data_dir / "sources.jsonl"
    existing_records = read_jsonl(sources_path) if sources_path.exists() else []

    run_timestamp = utc_now()
    result = build_inventory(
        deal_room,
        project,
        existing_records,
        captured_at=run_timestamp,
    )
    source_schema = _load_schema("source.schema.json")
    for index, record in enumerate(result.records):
        validate(record, source_schema, f"sources[{index}]")

    persisted = False
    if not args.read_only and result.manifest_changed:
        if result.records:
            write_jsonl_atomic(sources_path, result.records)
        project = dict(project)
        project["updated_at"] = run_timestamp
        validate(project, _load_schema("project.schema.json"))
        write_json_atomic(project_path, project)
        persisted = True

    output = dict(result.summary)
    output["manifest_changed"] = result.manifest_changed
    output["persisted"] = persisted
    output["read_only"] = bool(args.read_only)
    output["project_exists"] = project_exists
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def _cmd_classification_context(args: argparse.Namespace) -> int:
    _, project, records = _load_deal_room_contracts(Path(args.deal_room))
    context = build_classification_context(
        project,
        records,
        _load_document_types(),
        reclassify=args.reclassify,
    )
    if args.output:
        output_path = Path(args.output).resolve()
        write_json_atomic(output_path, context)
        print(
            json.dumps(
                {"output": str(output_path), **context["summary"]},
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(context, indent=2, sort_keys=True))
    return 0


def _cmd_apply_classifications(args: argparse.Namespace) -> int:
    data_dir, project, records = _load_deal_room_contracts(Path(args.deal_room))
    decisions = read_jsonl(Path(args.input).resolve())
    run_timestamp = utc_now()
    result = apply_classification_decisions(
        records,
        decisions,
        _load_document_types(),
        classified_at=run_timestamp,
        reclassify=args.reclassify,
    )

    source_schema = _load_schema("source.schema.json")
    for index, record in enumerate(result.records):
        validate(record, source_schema, f"sources[{index}]")

    write_jsonl_atomic(data_dir / "sources.jsonl", result.records)
    project = dict(project)
    project["updated_at"] = run_timestamp
    validate(project, _load_schema("project.schema.json"))
    write_json_atomic(data_dir / "project.json", project)
    print(json.dumps(result.summary, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage hotel underwriting source contracts")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-project", help="create project.json in a deal room")
    init_parser.add_argument("--deal-room", required=True)
    init_parser.add_argument("--project-id", required=True)
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--primary-property-name")
    init_parser.set_defaults(handler=_cmd_init_project)

    validate_parser = subparsers.add_parser("validate", help="validate present source contracts")
    validate_parser.add_argument("--deal-room", required=True)
    validate_parser.set_defaults(handler=_cmd_validate)

    web_sources_parser = subparsers.add_parser(
        "register-web-sources",
        help="validate and merge versioned webpage sources into sources.jsonl",
    )
    web_sources_parser.add_argument("--deal-room", required=True)
    web_sources_parser.add_argument("--input", required=True)
    web_sources_parser.set_defaults(handler=_cmd_register_web_sources)

    inventory_parser = subparsers.add_parser(
        "inventory-deal-room",
        help="create or refresh sources.jsonl from local file metadata",
    )
    inventory_parser.add_argument("--deal-room", required=True)
    inventory_parser.add_argument(
        "--read-only",
        action="store_true",
        dest="read_only",
        help="scan and summarize without writing project or source records",
    )
    inventory_parser.set_defaults(handler=_cmd_inventory_deal_room)

    context_parser = subparsers.add_parser(
        "classification-context",
        help="prepare metadata-first source context for model classification",
    )
    context_parser.add_argument("--deal-room", required=True)
    context_parser.add_argument("--output")
    context_parser.add_argument(
        "--reclassify",
        action="store_true",
        help="include sources that already have a classification",
    )
    context_parser.set_defaults(handler=_cmd_classification_context)

    apply_parser = subparsers.add_parser(
        "apply-classifications",
        help="validate model decisions and merge them into sources.jsonl",
    )
    apply_parser.add_argument("--deal-room", required=True)
    apply_parser.add_argument("--input", required=True)
    apply_parser.add_argument(
        "--reclassify",
        action="store_true",
        help="allow explicit replacement of existing classifications",
    )
    apply_parser.set_defaults(handler=_cmd_apply_classifications)

    findings_parser = subparsers.add_parser(
        "apply-findings",
        help="validate a model-produced evidence and fact bundle and merge it into the deal contracts",
    )
    findings_parser.add_argument("--deal-room", required=True)
    findings_parser.add_argument("--input", required=True)
    findings_parser.set_defaults(handler=_cmd_apply_findings)

    str_parser = subparsers.add_parser(
        "extract-str-data",
        help="extract standardized STR workbooks into property.str evidence",
    )
    str_parser.add_argument("--deal-room", required=True)
    str_parser.add_argument(
        "--entity-name",
        help="canonical hotel name chosen by the model; required when persisting",
    )
    str_parser.add_argument(
        "--source-id",
        action="append",
        help="limit extraction to one or more source IDs; may be repeated",
    )
    str_parser.add_argument(
        "--read-only",
        action="store_true",
        dest="read_only",
        help="parse and validate without changing authoritative or derived files",
    )
    str_parser.add_argument("--coverage-output")
    str_parser.set_defaults(handler=_cmd_extract_str_data)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError, json.JSONDecodeError, SchemaValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
