# Contract conventions

## Purpose

Keep contracts small. Skills contain the underwriting intelligence; records preserve identity, provenance, normalized findings, and lifecycle state between skills.

## Implemented scope

`project.json` and `sources.jsonl` support project setup, inventory, and classification. Evidence-producing skills introduce `entities.jsonl` and `evidence.jsonl`. Current extraction and research skills do not write facts; reserve `facts.jsonl` for a later reconciliation workflow and continue to create every collection lazily. Introduce questions only when a workflow emits them.

Evidence records localize a short observation to exactly one source. A future fact record may normalize a supported conclusion about one entity and reference one or more evidence records; model-produced facts start as `unreviewed`. Missing profile items belong in a reproducible coverage report rather than as empty records.

## Storage

Store authoritative records under `<deal-room>/.hotel-underwriting/`. Store `deal_room_root` as `.` so a project remains portable when its folder moves.

Use JSON for the singleton project record and JSONL for collections. Omit empty optional properties. Put experimental fields under `extensions` with a namespaced key such as `custom.example`.

## IDs

Use lowercase kebab-case project IDs. Generate technical record IDs deterministically from their stable identity inputs.

A source version ID includes:

- Project ID
- Source kind
- Normalized location
- Content SHA-256 or an explicit version token

Do not use timestamps alone as source identity.

## Source versions

Treat a changed file, refreshed webpage, or new database result as a new source version. Add `supersedes_source_id` to the new record and retain the prior record. Do not mutate evidence to point at a newer version.

Use paths relative to the deal-room root for local files. Store canonical URLs for webpages. Keep content hashes lowercase.

## Source classification

Store the controlled primary type in `document_type`. Store workflow metadata under the namespaced `extensions["hotel_underwriting.classification"]` object. Metadata-first model classification records the catalog version, classification timestamp, method, and only meaningful uncertainty reasons. Inspect source content only for files that remain genuinely ambiguous after the metadata pass. Do not store confidence scores.

Preserve classifications created outside the classification workflow unless a user explicitly requests reclassification. Treat `unknown` as a valid, explainable result rather than expanding the controlled catalog during a run.

## Writes

Write JSON and JSONL atomically by creating a temporary file in the destination directory and replacing the target only after serialization succeeds. Preserve stable ordering where practical so diffs remain readable.

Do not create empty contract files in anticipation of future skills.

An evidence-only `apply-findings` run must not create or rewrite `facts.jsonl`. That collection is written only when a bundle actually contains facts.

## Schema growth

Add a core field only when a real skill produces it and a human, validator, downstream skill, or output consumes it. Prefer additive optional fields. Keep source-specific details in `metadata` or namespaced `extensions` until repeated workflows establish stable shared meaning.
