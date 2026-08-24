---
name: research-market-wages
description: Research applicable local minimum wages and current wage-bearing hotel job postings, then stage source-grounded labor.wages evidence. Use for hourly operating roles and comparable-market wage support. Do not extract property payroll, interpret union agreements, create staffing assumptions, or reconcile facts.
---

# Research Market Wages

Retain statutory rates and advertised wages as observations, not market averages or underwriting assumptions.

Before researching, read and follow [online-source-access.md](../../references/online-source-access.md).

## Workflow

1. Confirm the active project, exact hotel address, operating model, and requested roles. Unless directed otherwise, prioritize housekeeping, front office, engineering, bell/door/valet, security, and operating support roles.
2. Establish the current minimum wage at the exact work location from official municipal, county, state, and applicable sector-specific sources.
3. Search live wage-bearing hotel postings in the city first. Expand geography only when coverage is thin and disclose the mismatch. Use aggregators for discovery, but retain the best accessible underlying posting.
4. Retain two or three strong, nonduplicate observations per priority role unless broader coverage is requested.
5. Register retained authorities and postings as versioned `web_page` sources. Stage and apply `.hotel-underwriting/derived/market-wage-evidence-bundle.json` with producer version `0.4.0`, one hotel entity, `labor.wages` evidence only, and no facts.
6. Write `.hotel-underwriting/derived/market-wage-coverage.json`, validate contracts, and report statutory rates, covered and uncovered roles, limitations, evidence counts, and zero facts written.

## Research rules

- Resolve all potentially applicable wage floors and retain each rate separately with its effective date and conditions. Check material location, hotel or employer size, tipped-worker, collective-bargaining, and worker-specific provisions addressed by the authority.
- Identify the highest applicable floor only when applicability is established. Otherwise retain the candidates and unresolved issue. Include the next enacted rate when officially published.
- Prefer direct hotel, operator, brand, or employer postings, followed by hospitality boards and reputable general job boards. Label salary-estimate pages as context only.
- Favor the same city or submarket and comparable service level, operating type, complexity, union status, and management model. Record material matches and mismatches instead of calculating a score.
- Map titles to normalized roles only when duties support the mapping. Do not use similar-titled residential or non-hotel work as hotel comparables.
- Verify that retained postings are active on the access date. Deduplicate syndicated copies while preserving genuinely distinct shifts, seniority, duties, or employment types.

## Evidence rules

- Use `labor.wages` with `scope: jurisdiction_minimum_wage` or `scope: market_comparable_job_posting`. Include source title, role, property or jurisdiction, market, employment type, wage range and unit, relevant qualifications, dates, status, comparability, mismatches, and uncertainty when available.
- Preserve minimum, maximum, currency, unit, and pay qualifiers such as base, tipped, overtime, union scale, shift differential, or bonus eligibility.
- Do not silently convert hourly and annual pay. If conversion is requested, retain the original wage and disclose the hours assumption.
- Do not infer a full range from “starting at” or “up to,” expected hire pay from the top of a range, or union status from wage level.
- Treat a posting as an advertised wage—not actual payroll, incumbent pay, a market average, or a forecast hiring rate. Do not calculate a benchmark or recommended assumption, modify a workbook, or write facts.

Coverage records the address and market, official wage applicability, requested roles, search sites and geography, candidate disposition, retained counts, gaps, mismatches, inaccessible pages, and confirmation that no facts or assumptions were written.
