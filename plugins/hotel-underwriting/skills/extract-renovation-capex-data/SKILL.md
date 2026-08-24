---
name: extract-renovation-capex-data
description: Convert hotel CapEx ledgers, renovation spend summaries, reserve schedules, and relevant active-project budgets into source-grounded property.renovation_capex evidence focused on major scope, timing, budget, and actual spend. Exclude drawings, physical-condition assessments, long-range replacement forecasts, recommendations, and fact creation.
---

# Extract Renovation and CapEx Data

Retain actual spend history and decision-useful major projects without turning every ledger line into evidence.

## Workflow

1. Confirm the project contracts and `capital.capex_history` or `capital.capex_plan` sources. Include plans only for active or recently completed major projects with relevant scope, timing, budget, or spend.
2. Exclude drawings, renderings, physical-condition reports, and routine long-range replacement plans. Deduplicate identical files and avoid summary/detail double counting.
3. Index workbook sheets and PDF pages. Inspect relevant ranges, displayed values, formulas, hidden state, tables, and descriptions; render scans and layout-dependent pages. Use summaries for totals and detail for scope, timing, and drivers.
4. Identify every amount as actual spend, original or current budget, forecast, estimate, commitment, remaining cost, or another source-defined measure before interpreting it.
5. Create and apply `.hotel-underwriting/derived/renovation-capex-information-evidence-bundle.json` with producer version `0.3.0`, one hotel entity, `property.renovation_capex` evidence only, and no facts. Write coverage with source dispositions, periods, components, scope, timing, amount types, funding, conflicts, gaps, and evidence counts; validate and report zero facts written.

## Select and structure evidence

Use judgment rather than a fixed dollar threshold. Retain a project separately when it is a renovation, redevelopment, expansion, material share of spend, affects a meaningful property area or building system, spans periods or funding sources, causes disruption, or has distinctive scope, timing, budget, spend, or per-key information.

Do not emit one record for every small repair, equipment purchase, vehicle, or routine replacement. Preserve minor items only within compact source totals or category tables unless their pattern is independently material.

Use `renovation_program`, `capex_history`, `capex_project`, or `renovation_impact` in `attributes.observation_kind` when helpful.

Prefer one record per major program, major item, or compact historical table. Require only `type`, `subject`, and `statement`; keep source-shaped detail in `attributes` and use precise workbook or PDF locators.

## Interpretation boundaries

- Preserve source roles, exact amount labels, original descriptions, property areas, and stated funding. Never infer an unlabeled funding source.
- Distinguish spend periods, construction periods, and completion dates; stopping spend does not prove completion.
- Keep hotels, parcels, and components separate. Exclude acquisition, financing, working-capital, and transaction costs unless a renovation subtotal is stated.
- Use summary totals and detail scope without double counting. Preserve conflicts; missing scope, timing, budget, spend, or status is not zero.
- Do not infer condition, deferred maintenance, remaining need, future performance, reserves, adjustments, or investment conclusions from spend alone.

Keep excerpts concise, generate coverage mechanically, and require `facts_added: 0`.
