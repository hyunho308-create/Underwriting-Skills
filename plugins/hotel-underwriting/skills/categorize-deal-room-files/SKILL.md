---
name: categorize-deal-room-files
description: Categorize inventoried hotel deal-room files with the controlled document-type catalog, using metadata first and minimal content inspection only for ambiguous files. Use after `inventory-deal-room-files` to prepare sources for downstream skills. Do not extract evidence or facts.
---

# Categorize Deal Room Files

Assign one controlled document type to each pending local source.

## Workflow

1. Confirm `.hotel-underwriting/project.json` and `sources.jsonl` exist. Otherwise use `inventory-deal-room-files` first.
2. Locate `scripts/contracts_cli.py` relative to this installed skill, use an available Python 3 executable, and generate the classification context:

```text
<python> <plugin-root>/scripts/contracts_cli.py classification-context --deal-room <path> --output <path>/.hotel-underwriting/derived/classification-context.json
```

3. Use the supplied catalog and each source's entire relative path to decide every pending source from metadata. Inspect only the minimum content needed when metadata leaves a material ambiguity. If still unresolved, use `unknown` with a concise reason.
4. Write exactly one decision per pending source to `.hotel-underwriting/derived/classification-decisions.jsonl`, then apply it:

```json
{"source_id":"src_...","document_type":"financials.budget"}
{"source_id":"src_...","document_type":"unknown","uncertainty_reasons":["The filename and folder do not identify the document's purpose."]}
```

```text
<python> <plugin-root>/scripts/contracts_cli.py apply-classifications --deal-room <path> --input <path>/.hotel-underwriting/derived/classification-decisions.jsonl
```

5. Validate the contracts. Report counts by type, files inspected, and unresolved sources requiring assistance.

```text
<python> <plugin-root>/scripts/contracts_cli.py validate --deal-room <path>
```

## Decision rules

- Use only types supplied by the generated catalog; never invent a type or deterministic filename rule.
- Omit `uncertainty_reasons` when the classification is defensible. `unknown` requires at least one source-specific reason.
- Do not emit confidence scores, percentages, or high/medium/low labels.
- Preserve existing classifications. Use `--reclassify` during both context generation and application only when the user explicitly requests replacement.

## Guardrails

- Do not inspect contents when metadata is sufficient.
- Do not turn ambiguity checks into substantive extraction or extract evidence, facts, reporting periods, property references, or version families.
