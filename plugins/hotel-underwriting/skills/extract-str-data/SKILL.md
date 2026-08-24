---
name: extract-str-data
description: Parse standardized STR or STAR Excel reports into source-grounded property.str evidence for every comp set, with the model resolving the canonical subject-hotel name before records are persisted. Use when classified performance.str_report workbooks support hotel underwriting. Do not use for pace reports, forecasts, non-STR operating statements, web research, or fact reconciliation.
---

# Extract STR Data

Convert standardized STR/STAR workbooks into `property.str` evidence with a deterministic parser. The model chooses the canonical hotel name; preserve source-reported names and keep each comp set distinct.

## Workflow

1. Confirm the project contracts and available `performance.str_report` sources.
2. Locate `scripts/contracts_cli.py` relative to this installed skill, use an available Python 3 executable, and run a read-only preview:

```text
<python> <plugin-root>/scripts/contracts_cli.py extract-str-data --deal-room <path> --read-only
```

3. Resolve the canonical hotel name from project identity, deal-room context, and source-reported labels. Do not copy a workbook label mechanically; ask only when the signals plausibly identify different hotels.
4. Re-run with `--entity-name "<canonical name>" --read-only`; confirm the canonical `subject` and preserved `source_reported_subject`. Then run without `--read-only` to persist evidence and coverage.
5. Review `str-information-evidence-coverage.json`, confirm model-supplied name resolution and the six output groups below, then validate:

```text
<python> <plugin-root>/scripts/contracts_cli.py validate --deal-room <path>
```

Report canonical and source-reported names, reports and months used, comp sets, incomplete sections, skipped files, and zero facts written.

## Source handling

- Parse `.xlsx` and `.xlsm` from saved values. Report unreadable legacy `.xls` files unless a current equivalent provides the required views.
- Ignore byte-identical copies but retain useful older snapshots and changed comp-set definitions.
- Preserve comp-set membership versions, report months, STR IDs, room counts, opening months, and precise workbook locators.
- Preserve blanks as unavailable and reported zeros as zero.

## Output

Use only `property.str`. Each comp set should produce up to six evidence primitives:

- `comp_set_membership`: subject and competitive hotel names, STR IDs, rooms, and opening months from Response.
- `monthly_performance`: 18 months of occupancy, ADR, RevPAR, and penetration.
- `ytd_performance`: three YTD years with explicit periods.
- `running_12_performance`: three running-12 years with explicit periods.
- `day_type_running_12`: weekday and weekend performance.
- `segment_running_12`: transient, group, and contract performance.

Use source-reported MPI, ARI, or RGI when available. Any calculated segmentation index must be transparent and null when its denominator is zero or unavailable.

## Interpretation boundaries

- Treat STR as source evidence and keep every comp set distinct.
- Use reported aggregate YTD, running-12, and RevPAR values rather than reconstructing them from monthly data.
- Preserve valid zeros and treat missing sections as incomplete coverage. Reject sections that fail parser sanity checks.
- Do not force day-type results to reconcile with monthly sheets or interpret penetration as investment merit.
- Perform no forecasting or external research and write no facts.

Coverage must report partial or missing groups rather than manufacture values. Re-running must add no duplicate evidence, and both extraction and contract validation must report `facts_added: 0`.
