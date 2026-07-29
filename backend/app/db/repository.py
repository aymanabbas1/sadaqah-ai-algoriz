from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.db.client import SupabaseDataClient
from app.data.ngo_links import NGO_DONATION_URLS
from app.schemas import NgoProfile, RegionStat, SourceRecord


class SupabaseRepository:
    mode = "supabase"

    def __init__(self, client: SupabaseDataClient) -> None:
        self.client = client

    async def close(self) -> None:
        await self.client.close()

    async def list_crises(self) -> list[RegionStat]:
        rows, source_rows = await asyncio.gather(
            self.client.select("crises", {"select": "*", "order": "name.asc"}),
            self.client.select("sources", {"select": "*", "entity_type": "eq.crisis", "order": "title.asc"}),
        )
        sources = self._group_sources(source_rows)
        return [self._crisis(row, sources.get(row["id"], [])) for row in rows]

    async def get_crisis(self, crisis_id: str) -> RegionStat | None:
        rows, source_rows = await asyncio.gather(
            self.client.select("crises", {"select": "*", "id": f"eq.{crisis_id}", "limit": 1}),
            self.client.select("sources", {"select": "*", "entity_type": "eq.crisis", "entity_id": f"eq.{crisis_id}", "order": "title.asc"}),
        )
        return self._crisis(rows[0], self._sources(source_rows)) if rows else None

    async def list_ngos(self) -> list[NgoProfile]:
        rows, source_rows, links = await asyncio.gather(
            self.client.select("ngos", {"select": "*", "order": "name.asc"}),
            self.client.select("sources", {"select": "*", "entity_type": "eq.ngo", "order": "title.asc"}),
            self.client.select("ngo_crises", {"select": "ngo_id,crisis_id"}),
        )
        sources = self._group_sources(source_rows)
        crisis_ids = self._group_links(links)
        return [self._ngo(row, sources.get(row["id"], []), crisis_ids.get(row["id"], [])) for row in rows]

    async def get_ngo(self, ngo_id: str) -> NgoProfile | None:
        rows, source_rows, links = await asyncio.gather(
            self.client.select("ngos", {"select": "*", "id": f"eq.{ngo_id}", "limit": 1}),
            self.client.select("sources", {"select": "*", "entity_type": "eq.ngo", "entity_id": f"eq.{ngo_id}", "order": "title.asc"}),
            self.client.select("ngo_crises", {"select": "ngo_id,crisis_id", "ngo_id": f"eq.{ngo_id}"}),
        )
        return self._ngo(rows[0], self._sources(source_rows), [item["crisis_id"] for item in links]) if rows else None

    @staticmethod
    def _crisis(row: dict[str, Any], sources: list[SourceRecord]) -> RegionStat:
        return RegionStat(
            id=row["id"],
            name=row["name"],
            country=row["country"],
            lat=float(row["lat"]),
            lng=float(row["lng"]),
            crisisType=row["crisis_type"],
            peopleInNeed=row["people_in_need"],
            displacedPeople=row["displaced_people"],
            fundingStatus=row["funding_status"],
            focusAreas=row.get("focus_areas") or [],
            affectedLocations=row.get("affected_locations") or [],
            summary=row["summary"],
            sources=sources,
            asOf=row.get("data_as_of") or row.get("updated_at") or datetime.now(timezone.utc),
        )

    @staticmethod
    def _ngo(row: dict[str, Any], sources: list[SourceRecord], crisis_ids: list[str]) -> NgoProfile:
        year = datetime.now(timezone.utc).year
        return NgoProfile(
            id=row["id"],
            initials=row["initials"],
            shortName=row["short_name"],
            name=row["name"],
            descriptor=row["descriptor"],
            coverage=row["coverage"],
            foundedYear=row["founded_year"],
            yearsActive=max(0, year - row["founded_year"]),
            reportingYear=row["reporting_year"],
            annualIncome=row.get("annual_income"),
            annualExpenditure=row.get("annual_expenditure"),
            reportedReach=row["reported_reach"],
            countriesActive=row["countries_active"],
            reportedActivity=row.get("reported_activity"),
            donationUrl=row.get("donation_url") or NGO_DONATION_URLS[row["id"]],
            accent=row["accent"],
            acceptedGivingTypes=row.get("accepted_giving_types") or [],
            focusAreas=row.get("focus_areas") or [],
            crisisIds=crisis_ids,
            sources=sources,
            asOf=row.get("data_as_of") or row.get("updated_at") or datetime.now(timezone.utc),
        )

    @staticmethod
    def _sources(rows: list[dict[str, Any]]) -> list[SourceRecord]:
        return [
            SourceRecord(
                title=row["title"],
                organization=row["organization"],
                sourceType=row["source_type"],
                url=row["url"],
                reportingYear=row.get("reporting_year"),
            )
            for row in rows
        ]

    @classmethod
    def _group_sources(cls, rows: list[dict[str, Any]]) -> dict[str, list[SourceRecord]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(row["entity_id"], []).append(row)
        return {key: cls._sources(items) for key, items in grouped.items()}

    @staticmethod
    def _group_links(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}
        for row in rows:
            grouped.setdefault(row["ngo_id"], []).append(row["crisis_id"])
        return grouped
