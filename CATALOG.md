# Hotel Underwriting Catalog

Last updated: 2026-08-23

This is the compact human-readable inventory of the hotel-underwriting plugin. The authoritative definitions remain in [document-types.json](./plugins/hotel-underwriting/references/document-types.json) and each skill's `SKILL.md` under the [skills folder](./plugins/hotel-underwriting/skills/).

Maintenance rule: update this file in the same change whenever a file type, skill, or information-primitive bucket is added, renamed, or removed.

## File types

| File type | Purpose |
| --- | --- |
| `marketing.offering_materials` | Investment-sale OMs, teasers, and sale brochures. |
| `financials.operating_statement` | Historical or current P&L and income statements. |
| `financials.balance_sheet` | Assets, liabilities, and equity statements. |
| `financials.budget` | Management operating budgets. |
| `financials.forecast` | Forecasts, reforecasts, and actual-plus-forecast views. |
| `financials.rent_roll` | Tenant, lease-income, and rent schedules. |
| `financials.other` | General ledgers, trial balances, account detail, and other supporting financial records. |
| `performance.str_report` | STR or STAR hotel and comp-set performance reports. |
| `performance.market_reports` | General lodging-market or submarket reports and data, excluding STR. |
| `performance.pace_report` | Group, catering, banquet, transient, corporate, or all-rooms pace reports. |
| `performance.operating_metrics` | Other hotel ADR, occupancy, segmentation, account-production, or revenue metrics. |
| `performance.ood` | Operating or financial performance for golf, spa, club, marina, and other operated departments. |
| `property.room_inventory` | Room matrices, room types, and key-count schedules. |
| `property.plan_or_layout` | Floor plans, property maps, meeting diagrams, and capacity layouts. |
| `property.survey` | Land, boundary, site, and related surveys. |
| `property.third_party_reports` | PCRs, PCAs, environmental assessments, engineering reports, and similar third-party diligence. |
| `property.photo` | Property photographs and images. |
| `property.property_information` | General property data that does not fit a more specific property type. |
| `capital.capex_history` | Historical CapEx, completed renovation spend, and prior capital investment. |
| `capital.capex_plan` | Forward capital plans, renovation budgets, PIPs, and value-add plans. |
| `agreements.management_agreement` | Hotel management agreements and related amendments or term sheets. |
| `agreements.franchise_agreement` | Franchise, license, and brand agreements. |
| `agreements.rental_management_agreement` | Rental-program agreements for individually owned hotel units. |
| `agreements.condo` | Condominium declarations, CC&Rs, bylaws, HOA documents, rules, and amendments. |
| `agreements.union_agreement` | CBAs, MOAs, MOUs, settlements, and related union agreements. |
| `agreements.lease` | Tenant, restaurant, ground, equipment, and similar leases. |
| `agreements.service_contract` | Third-party hotel service and operating contracts. |
| `agreements.other` | Other identifiable agreements that do not fit a more specific agreement category. |
| `tax.property_tax` | Property-tax bills, assessments, returns, histories, calculations, and supporting schedules. |
| `labor.staffing` | Staffing, FTE, employee census, payroll, wage, contract-labor, union-hours, detailed S&W, and organization information. |
| `financing.debt_terms` | Financing terms, lender summaries, and debt guidance. |
| `transaction.deal_process` | NDAs, process letters, LOIs, purchase documents, checklists, and diligence requests. |
| `analysis.underwriting_model` | Buyer, seller, broker, or lender underwriting and valuation models. |
| `analysis.internal_analysis` | Internal SWOTs, business plans, IC materials, and analytical memos. |
| `unknown` | Files that cannot yet be classified defensibly or fall outside the current catalog. |

## Skills

### Organizational skills

| Skill | Purpose |
| --- | --- |
| `create-underwriting-folder` | Initialize the lightweight project-local contract layer. |
| `inventory-deal-room-files` | Inventory local files and track hashes, duplicates, changes, and versions. |
| `categorize-deal-room-files` | Categorize inventoried files into the controlled file-type catalog. |

### File extraction skills

| Skill | Purpose |
| --- | --- |
| `extract-om-data` | Convert an OM into property, market, comp-set, and SWOT evidence primitives. |
| `extract-property-tax-data` | Extract source-grounded property-tax evidence from local tax documents. |
| `extract-booking-pace-data` | Convert operator pace reports into forward-booking evidence and observations. |
| `extract-str-data` | Extract every STR comp set into hotel membership and subject-versus-comp performance evidence. |
| `extract-renovation-capex-data` | Extract major renovation scope, timing, budget, and historical actual spend. |
| `extract-labor-staffing-data` | Extract position-level FTE, wage, salary, contract-labor, S&W, and staffing-productivity evidence from local sources. |
| `extract-management-franchise-data` | Extract management and franchise agreement parties, term, economics, funding, rights, obligations, and material constraints. |

### Online research skills

| Skill | Purpose |
| --- | --- |
| `research-property-tax-rules` | Research official local assessment rules, reassessment triggers, limits, rates, and major transaction taxes. |
| `research-property-tax-history` | Research parcel-level assessments, bills, rates, and payment history from official portals. |
| `research-union-status` | Screen hotels against FairHotel for listing and labor-dispute status. |
| `research-market-wages` | Find applicable minimum wages and current comparable-hotel wage postings as labor evidence. |
| `research-online-reviews` | Collect raw, source-linked guest-review observations without summarizing or analyzing them. |
| `research-cvent-data` | Research Cvent meeting-space and room inventory with a non-overlapping behind-doors meeting-area calculation. |
| `research-official-site-data` | Research official-site room types and sizes, F&B venues, meeting space, amenities, parking, and mandatory guest-fee evidence. |

## Information-primitive buckets

All buckets use the same flexible evidence wrapper: required `type`, `subject`, and `statement`, with source-shaped detail in optional `attributes`.

The producer column is a lightweight lazy-routing index, not exclusive ownership. A later skill may also add well-supported evidence to an existing basket and should then be added here.

| Bucket | Information retained | Current producer skills |
| --- | --- | --- |
| `property.rooms` | Keys, suites, double-room count, room-type matrix, and room sizes. | `extract-om-data`; `research-cvent-data`; `research-official-site-data` |
| `property.meeting_space` | Meeting area, venues, capacities, breakouts, space classifications, overlap hierarchies, and non-overlapping behind-doors area. | `extract-om-data`; `research-cvent-data`; `research-official-site-data` |
| `property.outlets` | Named F&B, retail, and other customer-facing outlets, including source-reported area and seating when available. | `extract-om-data`; `research-official-site-data` |
| `property.amenities_ood` | Amenities, facilities, and non-outlet operated departments. | `extract-om-data`; `research-official-site-data` |
| `property.guest_fees` | Parking charges and mandatory resort, destination, amenity, facility, and similar guest fees with inclusions and conditions. | `research-official-site-data` |
| `property.physical` | GBA, acreage, year built, stories, and other physical characteristics. | `extract-om-data` |
| `property.renovation_capex` | Renovation history, scope, timing, budget, actual spend, affected areas, and impacts. | `extract-om-data`; `extract-renovation-capex-data` |
| `property.operations` | Ownership, leases, non-labor outsourcing, closures, conversions, and operating changes. | `extract-om-data` |
| `property.manager` | Current and prior managers, changes, dates, agreement economics, rights, and material constraints. | `extract-om-data`; `extract-management-franchise-data` |
| `property.brand` | Current and prior brands, franchise relationships, agreement economics, rights, obligations, and changes. | `extract-om-data`; `extract-management-franchise-data` |
| `property.location` | Access, adjacency, visibility, neighborhood, and positioning. | `extract-om-data` |
| `property.supply` | Existing, planned, opened, closed, and converted hotel supply. | `extract-om-data` |
| `property.demand` | Demand generators, segments, compression periods, and demand patterns. | `extract-om-data` |
| `property.changes` | Other completed, underway, or proposed property catalysts. | `extract-om-data` |
| `property.pace` | OTB positions, comparison baselines, booking pace, pickup, pipeline, and significant observations. | `extract-booking-pace-data` |
| `property.str` | STR comp-set membership plus monthly, YTD, running-12, weekday/weekend, segmentation, and penetration performance. | `extract-str-data` |
| `property.reviews` | Raw guest-review observations about physical condition, service, location, guest experience, renovations, closures, changes, complaints, and strengths. | `research-online-reviews` |
| `property.tax` | Property-specific tax evidence plus jurisdictional assessment rules, parcel history, and rate history. | `extract-property-tax-data`; `research-property-tax-rules`; `research-property-tax-history` |
| `labor.wages` | Statutory and comparable-market wage observations, with source scope retained. | `research-market-wages` |
| `labor.staffing` | Position rosters, FTEs, wage or salary rates, S&W, payroll hours, contract labor, and staffing productivity. | `extract-labor-staffing-data` |
| `labor.union` | Union status and history, named unions or locals, represented groups, disputes, and union-related operating constraints. | `research-union-status` |
| `market.stats` | Demographics, GDP, visitation, traveler, airlift, and convention statistics. | `extract-om-data` |
| `market.changes` | Infrastructure, flight, convention, development, policy, and demand-generator changes. | `extract-om-data` |
| `comp_set.hotel_profile` | Source-reported property profiles for identified competitive hotels. | `extract-om-data` |
| `swot.strength` | Source-grounded candidate strengths. | `extract-om-data` |
| `swot.weakness` | Source-grounded candidate weaknesses. | `extract-om-data` |
| `swot.opportunity` | Source-grounded candidate opportunities. | `extract-om-data` |
| `swot.threat` | Source-grounded candidate threats. | `extract-om-data` |
