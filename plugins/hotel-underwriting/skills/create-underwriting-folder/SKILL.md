---
name: create-underwriting-folder
description: Initialize the lightweight, project-local data layer for a hotel underwriting deal room. Use when starting a new hotel underwriting project or adding `.hotel-underwriting/project.json` to an existing local deal room. Do not use this skill to inventory files, perform online research, extract evidence or facts, or create underwriting outputs.
---

# Create Underwriting Folder

Create only the minimum project scaffold. Leave inventory and analysis to later skills.

## Workflow

1. Confirm the target is the root of one hotel deal room. Choose a stable lowercase kebab-case `project_id`, a human-readable name, and, when known, the primary property name.
2. Locate `scripts/contracts_cli.py` relative to this installed skill. Use an available Python 3 executable rather than assuming the current working directory or a machine-specific path.
3. Initialize the project:

```text
<python> <plugin-root>/scripts/contracts_cli.py init-project --deal-room <path> --project-id <id> --name <name> [--primary-property-name <name>]
```

4. Validate the result and report the project ID and `.hotel-underwriting` directory:

```text
<python> <plugin-root>/scripts/contracts_cli.py validate --deal-room <path>
```

## Guardrails

- Do not create empty `sources.jsonl`, `evidence.jsonl`, `facts.jsonl`, or `questions.jsonl` files.
- Do not scan or open deal-room files.
- Do not overwrite a project with a conflicting identity. Stop and explain the conflict.
- Preserve the portable `deal_room_root` value written by the script; do not replace it with an absolute machine path.
- Treat an unchanged existing project as a successful idempotent result.

## Contract details

Read `../../references/contracts.md` only when project identity, versioning, or extension behavior needs clarification.
