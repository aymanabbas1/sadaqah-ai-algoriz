# Backend Build Specification

## Runtime

FastAPI reads crisis, NGO, source, and relationship records from Supabase through its Data API. The Supabase secret key remains in `backend/.env`; React never receives it.

## Startup

1. Run `backend/supabase/migrations/001_initial_schema.sql` in the Supabase SQL Editor.
2. Run the ingestion command from `backend`.
3. Start the backend and frontend with `start-dev.ps1`.
4. Open `http://127.0.0.1:5173`.

## Configuration

```env
SUPABASE_URL=https://PROJECT.supabase.co/rest/v1/
SUPABASE_SECRET_KEY=sb_secret_...
DATA_REPOSITORY=supabase
```

The URL normalizer also accepts the project base URL without `/rest/v1`.

## Data Refresh

`python -m app.ingestion` performs the following:

1. Fetch current OCHA response plans for eight crisis contexts.
2. Fetch UNHCR displacement statistics where applicable.
3. Fetch five official NGO pages or annual-report PDFs.
4. Apply source-specific extraction patterns.
5. Upsert profiles and replace current provenance links.
6. Record completed, partial, and failed runs.

The source client limits concurrent connections and retries only transient failures. A blocked source is recorded without replacing its last verified baseline with guessed data.

## Daily Schedule

`.github/workflows/daily-ingestion.yml` runs daily at `02:00 UTC`. Add `SUPABASE_URL` and `SUPABASE_SECRET_KEY` as GitHub repository secrets before enabling the workflow.

## Verification

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m app.ingestion --dry-run

cd ..\frontend
npm.cmd run build
```
