---
name: extract-property-tax-data
description: Extract source-grounded property.tax evidence from local hotel tax bills, assessments, returns, and schedules. Use for values, reported rates, liabilities, adjustments, installments, and named charges. Exclude online research, payment verification, forecasts, appeals analysis, and fact reconciliation.
---

# Extract Property Tax Evidence from a Data Room

Extract material tax-document claims without forecasting or treating liabilities as payment history.

## Workflow

1. Confirm the project contracts and classified `tax.property_tax` sources. Deduplicate byte-identical copies while preserving versions, parcels, accounts, periods, and bill types. Exclude online sources, projections, and receipt-only payment evidence; record each disposition.
2. Index every PDF page and workbook sheet. Review every data-bearing or unresolved location and the boilerplate needed to interpret rates, units, periods, or adjustments. Render scans and layout-dependent tables, checkboxes, and footnotes.
3. Retain one compact record per bill, account-period table, or independently useful claim. A multi-account table may remain intact when clearer than repetitive records.
4. Create and apply `.hotel-underwriting/derived/property-tax-information-evidence-bundle.json` with producer version `0.4.0`, one hotel entity, `property.tax` evidence only, and no facts.
5. Write `property-tax-information-evidence-coverage.json` with sources used or skipped, page and sheet coverage, periods, accounts, parcels, category status, conflicts, and evidence counts. Validate and report gaps and zero facts written.

A source is complete only when every page or sheet is indexed, every relevant or unresolved location is reviewed, and layout-dependent ambiguity is visually resolved.

## What to retain

- Assessed, taxable, and other source-labeled value components.
- Explicit tax rates, millage, levies, or multipliers.
- Real-estate and personal-property liabilities, installments, and due dates.
- Exemptions, abatements, TIFs, rebates, credits, discounts, and other adjustments.
- Named special charges and the parcel, account, address, jurisdiction, bill type, and period needed to interpret them.

Require only `type`, `subject`, and `statement`; put source-shaped fields inside `attributes`. Preserve source labels when normalization could change meaning.

## Interpretation boundaries

- Preserve source distinctions among assessed, taxable, market, appraised, acquisition, book, and cost values. Never relabel one as another.
- Record `reported_tax_rate` only when stated; do not calculate an effective rate.
- Keep bill types, parcels, accounts, interests, and personal property separate unless the source supplies a total.
- Preserve material formulas, source authority, and conflicts. Missing information is `partial` or `not_found`, never zero.
- A bill supports liability and due dates, not payment status. Exclude projected reassessments, forecasts, appeals, recommendations, and unrelated taxes.

Use precise locators and short excerpts. Keep structured tables in attributes, generate coverage mechanically, write nothing to `facts.jsonl`, and require `facts_added: 0`.
