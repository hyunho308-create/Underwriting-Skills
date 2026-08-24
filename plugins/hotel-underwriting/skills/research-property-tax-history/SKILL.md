---
name: research-property-tax-history
description: Research a hotel's parcel identity, assessed and taxable values, official rates and bills, and payment history from official public records. Use for parcel-level tax due diligence and multiple-parcel checks. Require the hotel name and full address. This is not a title report, tax certificate, or legal opinion.
---

# Research Property Tax History

Create source-linked `property.tax` evidence and a cited parcel-level history from official public records.

Read and follow [online-source-access.md](../../references/online-source-access.md). Allow slow parcel, year, bill, and payment views to load fully. Prefer official assessor, collector, treasurer, auditor, recorder, GIS, state, municipal, and officially linked vendor portals; use third-party sites only for discovery.

## Workflow

1. Confirm the project, hotel name, and full address. Use a requested year range or collect up to the latest ten readily available years and state actual coverage.
2. Verify the address, county or equivalent, municipality, special jurisdictions, and assessment and billing authorities.
3. Search the official assessor or GIS by address, then use verified parcel IDs. Match situs, property type, owner, hotel name, legal description, map, or building details. Test explicitly for multiple taxable parcels and report uncertain scope.
4. For each verified parcel and year, collect assessment components, taxable value, official rates, bills, special charges, installments, and displayed payment history. Align assessment, tax, and fiscal years.
5. Register each used page or PDF as a versioned `web_page` source. Create and apply `.hotel-underwriting/derived/property-tax-history-evidence-bundle.json` with producer version `0.2.0`, one hotel entity, `property.tax` evidence only, and no facts.
6. Write `.hotel-underwriting/derived/property-tax-history-coverage.json` with parcels, match evidence, years, authorities, sources, inaccessible records, topic status, and evidence counts. Validate and report zero facts written.

## Evidence rules

- Keep market, appraised, assessed, equalized, capped, and taxable values distinct. Missing fields are `Not published`, not zero.
- Preserve official rate units. Keep ad valorem tax, special assessments, direct charges, bonds, fees, credits, and net bills separate.
- Treat payment status as source-reported. Call a bill unpaid or delinquent only when the official portal says so or shows a positive balance; absent records are unavailable evidence.
- Label calculations and inferences. Never derive a rate from tax containing special charges; keep any calculated effective rate separate from the official rate and show its formula.
- Keep parcels separate. Add a combined hotel total only when the parcel set is verified and label it calculated.
- Stop at inaccessible or unavailable records and preserve the limitation. Write nothing to `facts.jsonl` and require `facts_added: 0`.

Report the property, jurisdiction, verified parcels, coverage years, assessments, rates, bills, payments, sources, calculations, gaps, and access limitations. End with: `Public-record research only; not a title report, tax certificate, or legal opinion.`
