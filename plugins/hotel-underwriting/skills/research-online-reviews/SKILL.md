---
name: research-online-reviews
description: Research Google, Tripadvisor, Booking.com, Expedia, and similar hotel reviews, then stage source-linked property.reviews observations. Use for physical condition, service, location, guest experience, and renovations, closures, or changes. Do not aggregate themes, score sentiment, draw conclusions, or write facts.
---

# Research Online Reviews

Retain raw guest reports for later analysis; stop before cross-review synthesis.

Before researching, read and follow [online-source-access.md](../../references/online-source-access.md).

## Workflow

1. Confirm the active project, hotel name, and full address.
2. Review Google and Tripadvisor plus one major verified-booking site such as Booking.com or Expedia when accessible. Focus on the latest 24 months and inspect recent low-rated, high-rated, and chronologically latest reviews. Aim for roughly 20 accessible reviews per site without forcing a quota; go older only for renovation, closure, opening, or operating-change signals.
3. Split distinct substantive points into separate observations. Never combine different reviews into one record.
4. Register each retained canonical review page as a versioned `web_page` source with site, hotel identity, address, page title, access date, and review coverage.
5. Stage and apply `.hotel-underwriting/derived/online-review-evidence-bundle.json` with producer version `0.3.0`, one hotel entity, `property.reviews` evidence only, and no facts.
6. Write `.hotel-underwriting/derived/online-review-coverage.json`, validate contracts, and report sources, periods, sampling limitations, observation counts, and zero facts or summaries written.

## Classification

Assign one `attributes.category` to each observation:

- `physical_condition`: rooms, cleanliness, finishes, public areas, building systems, maintenance, and hotel facilities.
- `service`: staff touchpoints, waits, staffing, management response, and service recovery.
- `location`: neighborhood, access, walkability, safety, outside noise, views, parking, and transportation.
- `guest_experience`: satisfaction, value, fees, F&B, amenities, atmosphere, traveler fit, and intent to return.
- `renovations_closures_changes`: construction, disruption, temporary spaces, closures, reopenings, and reported brand, management, service, or amenity changes.

Use `complaint`, `strength`, or `change` in `attributes.observation_type`; split genuinely distinct positive and negative points.

## Evidence rules

- Each record represents one review observation and uses the hotel as `subject`. Include site, review locator and date, stay date, rating and scale, verified-stay flag, traveler type, touchpoint, language, and uncertainty when available.
- Phrase the statement as a guest report, supported by a short excerpt and precise locator. Do not convert vague statements such as “recently renovated” into inferred dates or property facts.
- Preserve conflicting reports separately. Do not calculate frequency, severity, sentiment, rating trends, cross-site agreement, or rankings.
- Do not bypass logins, access controls, anti-bot measures, or unavailable pages; record limitations and continue with accessible sources.
- Do not create conclusions, underwriting implications, diligence recommendations, model changes, summaries, or facts.

Coverage records hotel identity, canonical pages, periods checked, approximate reviews inspected, retained counts by category and type, older periods checked for changes, inaccessible or thin sources, duplicates, language limits, and confirmation that no synthesis or facts were written.
