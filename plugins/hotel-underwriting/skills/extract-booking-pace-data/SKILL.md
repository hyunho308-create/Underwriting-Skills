---
name: extract-booking-pace-data
description: Extract source-grounded property.pace positions and significant observations from hotel group, banquet, catering, transient, corporate, or all-rooms pace reports. Use for OTB, comparable snapshots, target gaps, tentative pipeline, and pickup. Exclude web research, historical P&Ls, unsupported forecasts, conclusions, and facts.
---

# Extract Booking Pace Data

Interpret operator-specific reports without assuming that every forward table is a true pace comparison.

## Workflow

1. Confirm the project contracts and `performance.pace_report` sources. If none exist, write coverage with `status: not_available` and stop.
2. Preserve distinct report families, segments, stay periods, snapshot dates, and business statuses. Deduplicate only byte-identical copies; use earlier comparable snapshots for pickup or deterioration.
3. Index PDF pages and workbook sheets, review complete relevant tables, and render layout-dependent pages. Inspect headers, units, values, formulas, and print areas; reuse confirmed layout interpretation but extract each source independently.
4. Establish the comparison basis below before describing a variance as ahead, behind, favorable, or unfavorable.
5. Create and apply `.hotel-underwriting/derived/pace-information-evidence-bundle.json` with producer version `0.3.0`, one hotel entity, `property.pace` evidence only, and no facts. Write coverage with report families, snapshots, periods, segments, metrics, statuses, comparison bases, conflicts, gaps, and evidence counts; validate and report zero facts written.

## Comparison semantics

Identify the snapshot, stay or event period, segment, metric, units, business status, current value, exact comparison label, and whether each value is OTB, final actual, budget, forecast, pipeline, remaining-to-book, or calculated variance.

Use only supported normalized labels: `same_time_last_year`, `same_time_two_years_ago`, `prior_snapshot`, `last_year_final`, `budget`, `forecast`, `position_only`, or `ambiguous`. Final actuals and targets are not true pace comparisons.

Never relabel `Last Year` as STLY unless the report establishes equivalent OTB snapshots. Preserve the operator's original label and units, including whether revenue is reported in whole dollars or thousands.

## Evidence and observations

Use compact `pace_position` tables and selective `pace_observation` records. Retain the snapshot, stay period, segment, metric, status, units, OTB, baseline, calculation, and limitations in `attributes`.

- Separate completed YTD months from future OTB; do not call a mixed full-year table entirely OTB.
- Start with totals, balance-of-year, quarters, and segments; use months only to explain material concentration or reversals.
- Evaluate absolute and percentage variance together. Separate room nights, ADR, and revenue; do not average ADR without valid weighting.
- Separate group rooms from banquet/catering and definite business from tentative, prospect, or hold pipeline.
- Treat budgets, forecasts, and left-to-book positions as targets. When comparable snapshots exist, retain material pickup, loss, slippage, or deterioration with both source references.
- Prefer a small set of decision-useful observations over row-by-row commentary.

## Boundaries

Treat reports as source claims. Do not assume similarly named fields match across operators. Verify arithmetic, preserve sign conventions, and distinguish blank, unavailable, not applicable, and zero.

Do not infer final performance, compare non-equivalent periods or units, or convert forecasts and final actuals into OTB baselines. Treat far-future and tentative business as less mature, preserve conflicts, perform no external research, and require `facts_added: 0`.
