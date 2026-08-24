---
name: extract-management-franchise-data
description: Extract source-grounded property.manager and property.brand evidence from hotel management and franchise agreement packages. Use for main agreements and related amendments, side letters, assignments, guaranties, funding documents, PIPs, notices, and summaries. Preserve authority, chronology, exact economics, and uncertainty; do not provide legal conclusions or create facts.
---

# Extract Management and Franchise Data

Convert classified management and franchise agreement packages into selective evidence while keeping manager and brand terms distinct.

## Workflow

1. Confirm the project contracts and requested `agreements.management_agreement`, `agreements.franchise_agreement`, or both. Exclude union agreements and do not substitute an OM or acquisition model for executed documents.
2. For each type, identify the main executed agreement and build a chronology of amendments, restatements, side letters, assignments, notices, guaranties, funding documents, PIPs, and summaries. Deduplicate only byte-identical copies.
3. Review the main agreement comprehensively, including definitions and relevant exhibits. Classify each ancillary as `substantive_modification`, `additional_context`, or `mechanics_only`. For mechanics-only documents, confirm identity, parties, dates, referenced agreement, operative effect, and execution, then stop. Escalate any ancillary whose operative language changes a requested term.
4. Read the applicable section of [management-franchise-fields.md](../../references/management-franchise-fields.md). Use visual review for scans, tables, redlines, signatures, and layout-dependent clauses.
5. Create and apply `.hotel-underwriting/derived/hotel-agreement-information-evidence-bundle.json` with producer version `1.1.0`, one hotel entity, evidence only, and no facts.
6. Write coverage with the main document, chronology, authority, ancillary disposition, reviewed locations, field status, conflicts, gaps, and evidence counts. Validate and report zero facts written.

## Authority

Apply a later document only to provisions it expressly governs or modifies. Use this order:

1. Later executed modifications and project-specific schedules.
2. Main executed agreement and incorporated exhibits.
3. Executed project-specific related documents.
4. Signed secondary project documents, then generic forms or policies, then internal summaries and offering materials.

Record `source_authority` and `project_specificity` when material. A later date alone does not control; never present a generic or secondary amount as a project-specific executed term.

## Provision rules

- Preserve base and amended provisions separately unless an executed restatement replaces the earlier agreement.
- Retain exact defined denominators in `basis_source_label`; never translate among differently defined revenue, profit, investment, or cash-flow measures.
- Keep fees, reserves, funding, damages, and repayment obligations separate unless expressly combined.
- Distinguish execution, effective, opening, authorization, takeover, conversion, trigger, amendment, expiration, and renewal dates. Preserve formula-based dates and transparent calculations.
- Test headline economics against ramps, discounts, caps, exclusions, phase-ins, transition periods, and triggers. Mark current application uncertain when it depends on an unstated event.
- Treat express `not applicable` and prohibitions as evidence. Silence is `not_found`, never zero, false, waived, or prohibited.

## Evidence and boundaries

Use one compact record per useful clause family or amendment change with precise locators and short excerpts. Treat documents as evidence, not legal opinions: do not decide enforceability, waiver, breach, compliance, or whether a right is exercisable. Calculate contingent amounts only with every required input and preserve the formula. Keep conflicts and superseded provisions, route union-agreement terms to `labor.union`, and require `facts_added: 0`.
