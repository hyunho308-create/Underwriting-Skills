---
name: research-union-status
description: Screen one or more hotels against FairHotel.org and classify each as listed, listed with a labor dispute or boycott warning, not listed on a verified destination list, or unverified. Use for quick hotel union-status research based on FairHotel. Require hotel name and city; use addresses to disambiguate. Do not use for broader labor-law research or definitive legal verification.
---

# Research Union Status

Use FairHotel.org as a directory screening source.

Before researching, read and follow [online-source-access.md](../../references/online-source-access.md).

## Workflow

1. Require each hotel's name and city. Use state, country, address, and ZIP when supplied; ask for an address only when plausible matches remain. Group batch requests by city.
2. Search FairHotel directly for the exact hotel and city, adding the address when available. Open official results; snippets are discovery only. Match name and location while allowing harmless punctuation, abbreviation, or brand-suffix differences, never a different property from the same chain.
3. Inspect every match for a **Labor Dispute/Boycott** marker. When no reliable match appears, verify the complete destination result list through direct retrieval or the built-in browser before classifying the hotel as not listed. Never rely on a failed exact-name search or a still-loading page.
4. Return one classification below. Reuse a verified complete city list for every hotel in that city.
5. When a result belongs to an active underwriting project, register the exact FairHotel page or complete destination result as a versioned `web_page` source. Create and apply `.hotel-underwriting/derived/union-status-evidence-bundle.json` with producer version `0.2.0`, one hotel entity, `labor.union` evidence only, and no facts. Write coverage with destination completeness, match evidence, warning status, access limitations, and evidence counts; validate and report zero facts written.

For ad hoc batch screening without a hotel project, return the report only. Do not invent project records; persist each result only to its corresponding project.

## Classification

Return exactly one primary classification:

- `likely_union_fairhotel_listed`: reliable hotel-and-location match without a dispute or boycott marker.
- `listed_labor_dispute_or_boycott`: reliable match with the warning; do not present it as an ordinary union-friendly listing.
- `not_listed_screen_as_nonunion`: verified complete destination list with no reliable match; absence is not proof of nonunion status.
- `unverified`: destination failed, remained incomplete, or the match stayed ambiguous.

Never infer status from a name-only match when the address conflicts.

## Report

Report the hotel, destination, classification, matched name and address or `No reliable match`, warning status, source URL, and check date. End with: `FairHotel directory screening only.`
