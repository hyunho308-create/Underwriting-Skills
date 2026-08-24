---
name: extract-om-data
description: Extract compact, page-traceable hotel underwriting evidence from one investment-sale offering memorandum, covering the property, market, competitors, and source-supported SWOT candidates. Review every page. Do not use other sources, reconcile facts, or normalize financials.
---

# Extract Hotel Information Evidence from an OM

Read one classified OM completely and retain only material source-grounded observations. Record gaps in coverage without creating empty evidence.

## Workflow

1. Confirm the project contracts and one source classified as `marketing.offering_materials`. If multiple distinct OMs remain and the user did not select one, ask which to use.
2. Open only that OM. Review every page in order with one-based page boundaries. Render sparse, scanned, table-, diagram-, or layout-dependent pages; keyword search may cross-check but never replace page review.
3. Consolidate material observations after completing the review. Preserve contradictions, distinguish history from current status, and avoid duplicating broker claims.
4. Create `.hotel-underwriting/derived/om-information-evidence-bundle.json` with producer version `0.9.0`, one hotel entity, evidence only, and no `facts` array. Apply it with `contracts_cli.py apply-findings`.
5. Write `om-information-evidence-coverage.json` with page-review counts, visual-review pages, basket status (`found`, `partial`, `conflicting`, or `not_found`), and evidence counts. Validate and report the source, evidence, conflicts, gaps, and zero facts written.

## Evidence routing

Use only these primitive groups and put reusable detail in `attributes`.

| Group | Primitive types |
| --- | --- |
| Property | `property.rooms`, `property.meeting_space`, `property.outlets`, `property.amenities_ood`, `property.physical`, `property.renovation_capex`, `property.operations`, `property.location`, `property.changes` |
| Affiliations | `property.manager`, `property.brand` |
| Labor | `labor.staffing`, `labor.union` |
| Market | `property.supply`, `property.demand`, `market.stats`, `market.changes` |
| Competitors | `comp_set.hotel_profile`; use each competitor as the subject and retain only source-reported attributes |
| SWOT | `swot.strength`, `swot.weakness`, `swot.opportunity`, `swot.threat`; treat these as candidates, not conclusions |

## Meeting space and outlets

When the OM contains event information, read [meeting-space-counting.md](../../references/meeting-space-counting.md) and use `scope: offering_memorandum_meeting_inventory`.

- Inventory every listed venue and classify non-meeting areas; do not double count divisible spaces.
- Keep headline totals source-reported. Calculate behind-doors area only from a defensible non-overlapping reconciliation; otherwise use `partial` or `not_calculated` without estimating missing areas.
- Record the shared meeting-space coverage fields as well as basket coverage.

For each named outlet, retain explicitly reported area and seat counts with their source labels. Do not infer seats from event capacity, estimate area from plans, or add components unless the source establishes they are mutually exclusive.

## Evidence boundaries

- Keep one material claim or compact source table per evidence record, with a short excerpt and precise `pdf_page` locator. Put fields beyond `type`, `subject`, and `statement` in `attributes`.
- Treat the OM as claims, not unquestioned truth. Preserve reported values, transparent calculations, uncertainty, contradictions, and historical context.
- Do not infer dates, agreement coverage, operating status, or absence from silence. Exclude generic enthusiasm and unsupported superlatives.
- Do not open other files, research online, reconcile facts, or write to `facts.jsonl`; require `facts_added: 0`.
