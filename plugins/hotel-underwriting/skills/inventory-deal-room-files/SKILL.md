---
name: inventory-deal-room-files
description: Create or refresh a hotel deal room's traceable local source manifest, including file identity, changes, exact duplicates, and version history. Use for initial orientation or later inventory refreshes. Do not use for document classification, content extraction, web research, or underwriting analysis.
---

# Inventory Deal Room Files

Create a mechanical, traceable inventory without interpreting document contents.

## Workflow

1. Confirm the target is one hotel deal-room root. If `.hotel-underwriting/project.json` is absent, use `create-underwriting-folder`; infer identity only from the folder name or user input.
2. Locate `scripts/contracts_cli.py` relative to this installed skill and use an available Python 3 executable. Run:

```text
<python> <plugin-root>/scripts/contracts_cli.py inventory-deal-room --deal-room <path>
```

3. Use `--read-only` only for a user-requested preview or reference-workspace test. Otherwise validate the updated contracts:

```text
<python> <plugin-root>/scripts/contracts_cli.py validate --deal-room <path>
```

4. Report the command's concise orientation summary: current files and bytes; new, changed, missing, inaccessible, and temporary files; exact-duplicate groups; and leading extensions and directories.

## Interpretation

- `content_sha256` establishes byte identity only; it does not validate document assertions.
- `exact_duplicate_of` means exact byte equality. Similar names or sizes are insufficient.
- A changed file creates a new record linked by `supersedes_source_id`; retain the prior unavailable record. Preserve non-file sources and metadata owned by later skills.

## Guardrails

- Do not inspect substantive contents, classify documents, search the web, or extract evidence or facts. Reading bytes for hashing is permitted.
- Do not delete historical source records.
- Do not inventory `.hotel-underwriting/`; it contains derived project data and would create self-referential churn.
- Inventory underwriting models like any other file; do not rely on or special-case them.
- Stop on a conflicting project identity instead of replacing `project.json`.

## Contract details

Read `../../references/contracts.md` only when source identity, versioning, extensions, or record-retention behavior needs clarification.
