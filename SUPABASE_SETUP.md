# Supabase Setup

## 1. Create The Tables

1. Open your Supabase project.
2. Open **SQL Editor**.
3. Create a new query.
4. Paste the contents of `backend/supabase/migrations/001_initial_schema.sql`.
5. Select **Run**.

For a project that already ran the initial migration, also run `backend/supabase/migrations/002_add_ngo_donation_url.sql` to store the verified official donation links.

The migration is idempotent and enables read-only public policies for profile data. Ingestion history and all writes remain backend-only.

## 2. Load Official Data

From the workspace root:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.ingestion
```

A successful run prints counts for 8 crises, 5 NGOs, attached sources, and NGO-crisis links. `partial` is allowed when an official website blocks automated access; the error is saved in `ingestion_runs`.

## 3. Start The Application

```powershell
cd ..
.\start-dev.ps1
```

Check `http://127.0.0.1:8001/api/v1/health`. Its `repository` field should be `supabase`.

## 4. Enable Daily Refresh

After pushing the project to GitHub:

1. Open **Repository Settings**.
2. Open **Secrets and variables → Actions**.
3. Add `SUPABASE_URL`.
4. Add `SUPABASE_SECRET_KEY`.
5. Open **Actions → Daily official-source refresh**.
6. Run it manually once to verify the secrets.

The workflow then runs daily at `02:00 UTC`.
