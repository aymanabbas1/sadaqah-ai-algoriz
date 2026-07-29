# Sadaqah Intelligence Platform

## Product

Sadaqah Intelligence Platform connects humanitarian crisis information, responding organizations, NGO profiles, and official sources.

The primary flow is:

1. Open the crisis globe.
2. Select a crisis profile.
3. Review current humanitarian needs and affected locations.
4. See organizations with documented activity in that context.
5. Compare two or three NGO profiles.
6. Open official reports or ask Mansa Musa about the selected information.

## Frontend

- `/`: one-viewport globe-led landing page.
- `/globe`: interactive crisis globe, crisis profile, sources, and Mansa Musa.
- `/compare`: NGO selection, organization details, evidence profiles, sources, and Mansa Musa.
- `/assistant`: backwards-compatible route to the globe.

Frontend technology: React, TypeScript, Vite, Framer Motion, `react-globe.gl`, and Three.js.

## Backend

FastAPI is the only data boundary used by React. It reads structured profiles from Supabase and supplies them to the interface and Mansa's deterministic tools.

Backend technology: Python 3.12, FastAPI, Pydantic, `httpx`, Beautiful Soup, pypdf, Groq, and Supabase Postgres through the Data API.

## Supabase Tables

- `crises`: display-ready crisis profiles plus numeric OCHA fields.
- `ngos`: organization identity and latest published operating information.
- `ngo_crises`: source-evidenced links between organizations and crises.
- `sources`: URLs, reporting years, retrieval metadata, hashes, excerpts, and fetch errors.
- `ingestion_runs`: status and counts for every refresh.

The migration is `backend/supabase/migrations/001_initial_schema.sql`.

## Official Data Sources

### Humanitarian crises

- UN OCHA Humanitarian Programme Cycle API: current response plans, people in need, plan year, and funding requirement.
- UNHCR Refugee Statistics API: internally displaced or hosted refugee figures where the dataset applies.

The current catalog contains Afghanistan, Central Sahel, Eastern DRC, Gaza, the Rohingya response in Bangladesh, Somalia, Sudan, and Yemen.

### NGOs

- CARE 2025 Annual Report.
- Human Appeal Annual Report 2024.
- Islamic Relief Worldwide Annual Report 2024.
- Mercy Corps 2025 Annual Impact Report.
- Save the Children 2025 Impact page.

NGO parsers update reach, country coverage, activity, and financial fields only when the configured official source explicitly provides them. A missing or blocked field is not estimated.

## Ingestion

```text
Official API, HTML page, or PDF
    |
Fetch with a low-concurrency source client
    |
Extract source-specific fields
    |
Validate and preserve reporting context
    |
Upsert profiles, sources, and NGO-crisis evidence
    |
Record the ingestion run
```

Manual dry run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.ingestion --dry-run
```

Supabase write:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.ingestion
```

The GitHub Actions workflow `.github/workflows/daily-ingestion.yml` runs at `02:00 UTC` every day and can also be started manually.

## Mansa Musa

Mansa receives an explicit screen context with every request. Crisis mode can retrieve the selected crisis, its sources, and documented responders; NGO comparison mode retrieves only the selected NGO profiles and reports. FastAPI selects the context-appropriate deterministic tool, then Groq explains that structured result. If Groq is unavailable, FastAPI returns a deterministic explanation of the same result.

## API

```text
GET  /api/v1/health
POST /api/v1/chat
GET  /api/v1/methodology
GET  /api/v1/globe
GET  /api/v1/crises
GET  /api/v1/crises/{id}
GET  /api/v1/crises/{id}/ngos
GET  /api/v1/ngos
GET  /api/v1/ngos/{id}
POST /api/v1/ngos/compare
```
