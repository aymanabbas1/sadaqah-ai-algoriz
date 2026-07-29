# NGO Metrics Research

## Decision

Sadaqah Intelligence does not assign NGO ratings such as transparency, regional strength, reporting quality, response speed, trustworthiness, or effectiveness. It also does not calculate recommendation fit.

The comparison displays facts published by each organization. No aggregate score is calculated, the selected profiles are not sorted, and the platform does not choose a winner.

## Official Sources Reviewed

- [Islamic Relief Worldwide history](https://islamic-relief.org/about-us/our-history/)
- [Islamic Relief Worldwide 2024 results](https://islamic-relief.org/news/2024-islamic-relief-spent-more-than-ever-before-to-support-the-worlds-most-vulnerable/)
- [Human Appeal annual reports](https://humanappeal.org.uk/about-us/annual-reports)
- [CARE 2025 annual report](https://www.care.org/resources/care-2025-annual-report/)
- [Mercy Corps 2025 annual impact report](https://www.mercycorps.org/annual-reports/2025)
- [Save the Children 2025 impact](https://www.savethechildren.net/)

## Extraction Contract For A Later Pipeline

Each extracted value should include:

- `value`: the raw value as published.
- `unit`: people, children, households, countries, projects, currency, or year.
- `reporting_year`: the period the value describes.
- `source_url`: the exact official page or report.
- `source_type`: history page, annual report, financial statement, impact report, programme page, or giving-policy page.
- `retrieved_at`: when the pipeline collected it.
- `raw_label`: the organization's original wording.
- `review_status`: whether a human has checked the extraction.

## Common Objective Fields

| Field | Preferred source | UI purpose |
| --- | --- | --- |
| Founded year | Official history/about page | Show operating history |
| Latest report year | Annual-report index | Make recency visible |
| Annual income | Audited financial statements | Show reported financial scale |
| Annual expenditure | Audited financial statements | Show reported expenditure |
| Reported reach | Annual or impact report | Show the organization's published reach |
| Countries active | Annual report or where-we-work page | Show geographic scale |
| Reported activity | Annual or impact report | Show programmes, projects, or emergencies when available |
| Crisis presence | Country or emergency-response page | Identify documented responders for a selected crisis |
| Focus areas | Programme or impact page | Describe published areas of work |
| Giving types | Official donation or policy page | Display published giving options |

## Comparability Rules

- Keep the reporting year visible beside every annual value.
- Preserve original wording for reach figures, including whether it means people, children, households, direct reach, or indirect reach.
- Do not imply that more income, countries, or beneficiaries means better effectiveness.
- Do not compare converted currencies until the original value, exchange rate, and conversion date are retained.
- Treat project counts as optional because organizations define projects, programmes, initiatives, and emergency responses differently.
- Store cause-specific outputs such as food packs, wells, shelters, or cash grants separately. Do not add unlike outputs into one total.
- Treat official website values as organizational claims unless independently verified by an audited statement or regulator.
- Display missing data as unavailable rather than estimating it.

## Current Dataset

The ingestion pipeline writes these fields and their provenance to Supabase. Source-specific parsers refresh values from official HTML pages and annual-report PDFs; failed checks are recorded without estimating replacement values. The figures remain each organization's published claims unless an attached source is an audited statement or regulator filing.
