# Meeting-space classification and behind-doors counting

Use this policy whenever a skill inventories hotel meeting or event venues and calculates behind-doors meeting space.

## Space types

Assign one `space_type` to every listed venue:

- `ballroom`: an enclosed ballroom or grand ballroom used as true meeting or event space.
- `meeting_room`: an enclosed meeting, conference, salon, breakout, function, or multipurpose room that is not better classified as a ballroom or boardroom.
- `boardroom`: a dedicated enclosed boardroom.
- `prefunction_lobby_terrace`: foyers, prefunction rooms, registration areas, lobbies, entrances, corridors, galleries used mainly for circulation, and terraces.
- `f_and_b_outlet`: restaurants, bars, lounges, cafes, private dining rooms, and other spaces primarily operated as food-and-beverage outlets. A PDR remains an outlet even when marketed for events.
- `outdoor_venue`: lawns, courtyards, gardens, rooftops, pool decks, patios, and other open-air event areas. A terrace remains `prefunction_lobby_terrace` unless the source clearly presents it as a separate outdoor venue.

Only `ballroom`, `meeting_room`, and `boardroom` are behind-doors eligible. Exclude the other types even when enclosed, reservable, or included in a source's total meeting-space figure.

## Inventory fields

For every space retain:

- `name`
- `reported_area_sf`, when stated
- `space_type`
- `configuration_role`: `standalone`, `aggregate_parent`, `subdivision`, or `uncertain`
- `parent_space_name`, when applicable
- `behind_doors_eligible`
- `counting_status`: `included`, `excluded_overlap`, `excluded_non_behind_doors`, or `unresolved`
- `counting_reason`

Preserve useful source-shaped details such as capacities, ceiling height, floor, dimensions, and subdivision names, but do not use them as substitutes for area.

## Prevent double counting

1. Build a containment hierarchy from explicit room labels, combination names, capacity tables, and floorplans. Similar area alone does not prove a parent-child relationship.
2. When an aggregate parent represents the same physical envelope as its subdivisions, count either the parent or a complete mutually exclusive set of children, never both.
3. Prefer the aggregate parent's reported area when it clearly represents the full unique envelope. Example: include a 10,000-square-foot Grand Ballroom once and mark its 5,000-square-foot A and B subdivisions `excluded_overlap`.
4. When the parent has no area but complete mutually exclusive child areas are available, sum the children and leave the parent uncounted.
5. Apply the same rule through multiple levels. Never count a grand ballroom, its salons, and the salons' sections together.
6. Do not add capacities, ceiling heights, dimensions, venue counts, or headline marketing totals to area calculations.
7. Reconcile a source-reported total to the inventory, but do not force agreement. Differences may reflect prefunction, outlets, outdoor space, overlap, estimates, or unidentified space.
8. If hierarchy, eligibility, or area remains ambiguous after reviewing available floorplans, mark the affected spaces `unresolved`. Report only `confirmed_behind_doors_meeting_space_sf`, set `total_status` to `partial`, and do not publish an unsupported complete total.

## Counting reconciliation

Retain:

- every included space or hierarchy basis and its area;
- every excluded or unresolved space and the reason;
- overlap groups and parent-child relationships;
- explicit arithmetic supporting the result;
- `behind_doors_total_meeting_space_sf` with `total_status: complete` only when the unique eligible inventory is complete; otherwise `confirmed_behind_doors_meeting_space_sf` with `total_status: partial`.

The calculation is source-grounded evidence, not a reconciled fact. Do not estimate missing areas.

## Evidence primitive contract

Use `property.meeting_space` with `observation_kind: meeting_space_inventory`. Set `scope` to identify the producer source, such as `cvent_venue_inventory`, `official_hotel_site_meeting_inventory`, or `offering_memorandum_meeting_inventory`.

The compact inventory primitive must retain:

- `source_reported_hotel_name`, when it differs from the canonical subject name;
- `source_reported_total_meeting_space_sf`, when stated, labeled as source-reported only;
- `behind_doors_total_meeting_space_sf` with `total_status: complete`, or `confirmed_behind_doors_meeting_space_sf` with `total_status: partial`;
- `spaces`, using the shared inventory fields;
- `overlap_groups`;
- `counting_reconciliation`, including the included spaces and areas, excluded or unresolved spaces and reasons, and explicit arithmetic.

Use the canonical model-resolved hotel name as `subject`. Preserve the source's property name separately rather than allowing source wording to create a second hotel entity.

Keep short localized excerpts and precise web selectors or PDF page locators. One evidence record must remain localized to one registered source. When a floorplan provides hierarchy evidence separate from a capacity page, create a separate floorplan-supported evidence record rather than implying both came from one source.

A complete total must be supported by a registered source that presents the complete inventory or reconciliation basis. If no single source does, retain source-specific venue evidence and place any unresolved cross-source consolidation in disposable coverage. Do not create a durable complete total that cannot be localized to one source.

## Coverage contract

Record consistently:

- canonical hotel name, source-reported hotel name, address, and exact identity match;
- every venue page, capacity chart, event guide, and floorplan attempted or used;
- field status as `found`, `partial`, `conflicting`, or `not_found`;
- number of spaces by `space_type`, `configuration_role`, and `counting_status`;
- every overlap group and unresolved relationship;
- source-reported total, calculated or confirmed behind-doors total, explicit reconciliation, and difference from the source total;
- whether floorplans were available and visually reviewed;
- inaccessible sections, missing areas, ambiguous venue identities, stale materials, and other limitations;
- confirmation that no meeting-space facts were written.
