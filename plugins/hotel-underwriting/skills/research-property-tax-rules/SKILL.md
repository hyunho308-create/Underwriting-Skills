---
name: research-property-tax-rules
description: Research official sources for a hotel's local real-property-tax rules, rate history, and major government-imposed transaction taxes. Use for assessment, reassessment, growth limits, transfer taxes, and recordation taxes. Do not use for parcel histories, projections, legal opinions, appeals, ancillary closing costs, or fact reconciliation.
---

# Research Property Tax Rules

Research current jurisdiction rules and major government charges on a property's transfer or financing. Store source-linked `property.tax` evidence only; do not calculate pro forma taxes or write facts.

Before researching, read and follow [online-source-access.md](../../references/online-source-access.md).

## Workflow

1. Confirm the project, hotel name, and full address. Resolve the state, county or equivalent, municipality, and commercial property class.
2. Identify the responsible assessor, collector or treasurer, recorder or clerk, state tax authority, and controlling law. Research the topics below from current official sources; collect five comparable rate years when available.
3. Register each used page or PDF as a versioned `web_page` source with its canonical URL, effective or publication date when known, and access date.
4. Create and apply `.hotel-underwriting/derived/property-tax-rules-evidence-bundle.json` with producer version `0.3.0`, one hotel entity, `property.tax` evidence, and no facts. Write the coverage file and validate the contracts.
5. Report jurisdictions, sources, rate years, gaps, structure-dependent uncertainties, and zero facts written.

## Topics

- Assessment framework and calendar: valuation standard, ratio, class, land and improvement treatment, lien date, cycle, and notice timing.
- Reassessment: sale, deed, entity, control, and partial-interest triggers; improvement, repair, maintenance, threshold, and completion rules.
- Growth limits: caps, recapture, exceptions, reset conditions, and excluded components.
- Recurring taxes: base and local rates, debt levies, material special charges, and five comparable years for the narrowest applicable geography.
- Transaction taxes: material transfer, conveyance, documentary-stamp, recordation, controlling-interest, mortgage-recording, intangible, and related government surcharges. Capture the base, rate or tiers, trigger, statutory taxpayer, timing, exemptions, and effective date.

## Research rules

- Prefer controlling law, then administering agencies and official rate documents. Use secondary sources only to find official authority.
- Keep recurring taxes, reassessment, and transaction taxes separate. Preserve asset, deed, entity, control, partial-interest, and mortgage distinctions.
- Do not decide whether an unknown transaction structure triggers a rule or calculate a transaction amount without the required consideration, debt, and structure.
- Cover material government taxes and surcharges only. Exclude title, escrow, brokerage, legal, survey, lender, diligence, and routine filing costs.
- Preserve official units, years, geography, effective dates, conflicts, and uncertainty. Do not provide legal opinions, forecasts, appeals advice, or reconciled facts.

## Evidence and coverage

Use the hotel as the subject and topic names as `observation_kind`. Use `jurisdiction_rule`, `jurisdiction_rate_history`, or `transaction_tax_rule` as `scope`.

Create `.hotel-underwriting/derived/property-tax-rules-coverage.json` with the address, jurisdictions, authorities, sources, topic status, rate years, material transaction taxes, effective dates, exemptions, uncertainties, and evidence counts.

Stop when controlling sources cover the recurring rules and material state and local transaction charges. Do not chase immaterial filing fees. Require `facts_added: 0`.
