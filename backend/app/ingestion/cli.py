from __future__ import annotations

import argparse
import asyncio
import json

from app.core.config import get_settings
from app.db.client import SupabaseDataClient
from app.ingestion.service import IngestionService


async def run(dry_run: bool, trigger: str) -> None:
    settings = get_settings()
    database = None
    if not dry_run:
        if not settings.supabase_configured:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY are required")
        database = SupabaseDataClient(settings.supabase_data_api_url, settings.supabase_secret_key)
    service = IngestionService(database)
    try:
        summary = await service.run(trigger=trigger, dry_run=dry_run)
        print(json.dumps(summary, indent=2))
    finally:
        await service.close()
        if database:
            await database.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Sadaqah Intelligence from official sources")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and parse sources without writing to Supabase")
    parser.add_argument("--trigger", default="manual", choices=["manual", "github-cron"])
    args = parser.parse_args()
    asyncio.run(run(args.dry_run, args.trigger))


if __name__ == "__main__":
    main()
