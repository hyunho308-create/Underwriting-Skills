---
name: research-cvent-data
description: Research an exact hotel listing on Cvent Venues and stage an auditable meeting-space inventory, non-overlapping behind-doors meeting area, and guestroom counts. Use when divisible rooms, prefunction areas, outlets, or outdoor venues could inflate reported meeting space. Do not treat search snippets or Cvent's headline total as the calculated behind-doors total.
---

# Research Cvent Data

Preserve every listed space, but count only unique ballroom, meeting-room, and boardroom area as behind-doors meeting space.

Before researching, read and follow [online-source-access.md](../../references/online-source-access.md).

## Workflow

1. Confirm the active project, canonical hotel name, and full address.
2. Find the exact property on [Cvent Venues](https://www.cvent.com/venues) and verify its address. Preserve Cvent's displayed name as source wording; do not use a similarly named listing or search snippet.
3. Inspect meeting-room, guestroom, and capacity sections. When a floorplan or event guide is available, read its text and visually review every relevant page for room boundaries, subdivisions, combinations, indoor/outdoor status, and prefunction areas.
4. Register the canonical venue page and each used floorplan as versioned `web_page` sources with property identity, address, title, publisher, access date, and source role.
5. Read and apply [meeting-space-counting.md](../../references/meeting-space-counting.md). Inventory every listed venue, classify it, build its containment hierarchy, select one non-overlapping basis per hierarchy, and calculate the confirmed behind-doors area.
6. Capture Cvent's source-reported total guestrooms, double-room count, and suite count without deriving missing values.
7. Stage and apply `.hotel-underwriting/derived/cvent-data-evidence-bundle.json` with producer version `0.2.0`, one hotel entity, `property.meeting_space` and `property.rooms` evidence only, and no facts.
8. Write `.hotel-underwriting/derived/cvent-data-coverage.json`, validate contracts, and report sources, spaces inventoried, behind-doors area, room counts, limitations, and zero facts written.

## Room inventory

- `total_guest_rooms`: Cvent's reported guestroom count.
- `double_room_count`: only rooms Cvent labels as doubles, double/doubles, or rooms with two beds; never interpret this as double occupancy or total rooms less suites.
- `suite_count`: Cvent's reported suite count.

Use `property.rooms` with `scope: cvent_room_inventory`. Preserve Cvent's original labels in `source_labels`; mark missing or conflicting fields in coverage rather than inferring them.

## Boundaries

- Use `property.meeting_space` with `scope: cvent_venue_inventory` and follow the shared inventory, reconciliation, and coverage contracts.
- Preserve Cvent's headline meeting-space total only as source-reported reconciliation input. It never overrides the venue hierarchy or calculated total.
- Treat Cvent and floorplans as source claims. Do not estimate missing areas, treat capacities as room counts, force uncertain classifications, or convert calculations into facts.
- Report a partial confirmed total when the inventory is incomplete or ambiguous; a partial result is preferable to an inflated complete total.
