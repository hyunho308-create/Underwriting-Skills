---
name: research-official-site-data
description: Research an exact hotel's official website for room types and sizes, F&B venues, meeting space, amenities, parking, and mandatory guest fees, then stage source-linked property evidence. Do not rely on third-party listings, snippets, or headline meeting-space totals.
---

# Research Official Site Data

Convert official property pages and linked documents into current evidence without treating site silence as absence.

Before researching, read and follow [online-source-access.md](../../references/online-source-access.md).

## Workflow

1. Confirm the active project, canonical hotel name, and full address.
2. Use only the property website, its brand or operator property page, and official documents linked from them. Review relevant rooms, accommodations, suites, dining, meetings, capacity, amenities, FAQ, parking, policy, and mandatory-fee pages.
3. Read linked event guides or floorplan PDFs and visually inspect relevant pages for room boundaries, subdivisions, combinations, indoor/outdoor status, and prefunction areas.
4. Register each used page or PDF separately with hotel identity, address, title, publisher, access date, and source role.
5. Stage and apply `.hotel-underwriting/derived/official-site-data-evidence-bundle.json` with producer version `0.4.0`, one hotel entity, evidence only, and no facts.
6. Write `.hotel-underwriting/derived/official-site-data-coverage.json`, validate contracts, and report findings, gaps, limitations, uncertainty, and zero facts written.

## Evidence profile

- **Room types:** Use `property.rooms` with `scope: official_hotel_site_room_inventory`. Retain each named room or suite category and its source-reported square footage or range, plus available bed type, view, location, occupancy, suite status, and accessibility qualifications. Preserve approximate, “from,” and range wording; do not infer room size, category counts, or total inventory from missing fields. Keep alternate marketing names separate unless the source clearly establishes they are the same category.
- **F&B venues:** Use `property.outlets`, normally one record per current named venue. Retain its name, supported type, concept, and available hours, meal periods, location, operating status, and uncertainty. Do not create outlets from generic “onsite dining” language or merge separately named venues.
- **Meeting space:** Read and apply [meeting-space-counting.md](../../references/meeting-space-counting.md) with `scope: official_hotel_site_meeting_inventory`. Inventory every listed venue; use headline totals only for reconciliation and calculate a defensible non-overlapping behind-doors total.
- **Amenities:** Use `property.amenities_ood` for source-labeled hotel amenities. Exclude outlets, ordinary room features, meeting rooms, nearby third parties, and generic service claims. Preserve seasonal, offsite, partner-operated, fee-based, or on-request qualifications.
- **Parking and mandatory fees:** Use separate `property.guest_fees` records for valet, self-parking, and each resort, destination, amenity, or facility fee. Retain the official name, amount or percentage, currency, charging basis, taxes, inclusions, exemptions, timing, and limitations when stated.

Event-marketed private dining rooms remain F&B outlets for meeting-space classification. Preserve “from,” “up to,” optional, package-dependent, parking-only, and tax-exclusive wording; do not convert daily fees to per-stay amounts.

## Boundaries

- Require `type`, `subject`, and `statement`; retain source-shaped details in `attributes` with short excerpts and precise page, selector, or PDF locators.
- Treat the official site as a source claim. Preserve conflicts and stale-date concerns, and record silence or missing information in coverage rather than inferring absence.
- Do not supplement from Cvent, OTAs, review sites, Google listings, or other third parties. Draw no market conclusions, modify no workbook, and write no facts.

Coverage identifies official domains and identity match, every page or PDF attempted, room types and size availability, field status for each evidence group, meeting-space reconciliation, gaps, conflicts, stale or inaccessible content, and confirmation that no facts were written.
