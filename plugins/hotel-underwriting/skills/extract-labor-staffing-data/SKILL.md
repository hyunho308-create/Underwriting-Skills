---
name: extract-labor-staffing-data
description: Extract source-grounded labor.staffing evidence from hotel staffing, FTE, payroll, wage, organization, contract-labor, and detailed financial materials. Use source budgets and forecasts only when clearly labeled. Exclude union agreements, PTEB, online wage research, employee PII, acquisition-model assumptions, newly created forecasts, and fact reconciliation.
---

# Extract Labor Staffing Data

Retain the smallest source-supported FTE and salaries-and-wages detail while protecting employee privacy.

## Workflow

1. Confirm the project contracts and classified sources. Select `labor.staffing` files, deduplicate byte-identical copies, and preserve distinct periods, versions, entities, and scenarios.
2. Exclude union agreements. When dedicated staffing files are absent or less granular, inspect labor schedules and exact S&W account lines in operating statements, budgets, forecasts, and supporting financials. Use service contracts only for identified contract or temporary labor.
3. Exclude the destination acquisition model. Use seller or operator staffing models only when source role and assumptions are explicit and labeled as modeled rather than actual.
4. Index workbook sheets and PDF pages, inspect credible ranges, values, formulas, and periods, render layout-dependent content, and remove employee PII. Review every relevant table to the smallest useful position, classification, subdepartment, department, or account-line level.
5. Create and apply `.hotel-underwriting/derived/labor-staffing-information-evidence-bundle.json` with producer version `0.3.0`, one hotel entity, `labor.staffing` evidence only, and no facts. Write coverage with source dispositions, periods, departments, positions, granularity, actuality, conflicts, gaps, and evidence counts; validate and report zero facts written.

## What to retain

Use source-shaped `attributes` for position staffing, rosters, FTE summaries, wages or salaries, S&W, payroll, hours, bonus, contract labor, productivity, and organization structure. Retain period, source role, actuality, department, position or account, FTEs, headcount, shifts, hours, wage or salary, base S&W, overtime, bonus, total S&W, and productivity when available.

Record employment basis as employee, contract, outsourced, mixed, or not stated. Retain vendor rates, markups, hours, costs, or FTEs when stated, but do not decompose vendor rates into benefits. Union codes may remain context on a staffing row; do not interpret agreement terms or infer union coverage.

Prefer one compact record per useful table, schedule, or exact account line. Keep multi-position tables intact when clearer than repetitive records.

## Interpretation boundaries

- Distinguish actual, budget, forecast, contractual, and scenario values. Do not create new assumptions or forecasts.
- Prefer stated FTE. Calculate from hours only when the source defines the basis; label wage averages and retain formulas and inputs.
- Keep blanks distinct from intentional zeros and keep employee, contract, outsourced, hourly, salary, vendor-rate, FTE, headcount, shift, hour, base, overtime, bonus, and total measures distinct.
- Aggregate employee-level data before persistence. Never retain names, IDs, contacts, addresses, birth dates, or quasi-identifying detail.
- Preserve conflicts and treat missing information as unavailable, not zero. Exclude PTEB, payroll taxes, benefits, pension, insurance, workers compensation, union-agreement terms, online research, and facts.

Use precise locators and short excerpts, generate coverage mechanically, and require `facts_added: 0`.
