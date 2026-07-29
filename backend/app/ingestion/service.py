from __future__ import annotations

import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from app.db.client import SupabaseDataClient
from app.ingestion.catalog import CARE_CRISIS_EVIDENCE, CRISES, CRISIS_ALIASES, NGOS
from app.ingestion.extractors import parse_ngo_facts
from app.ingestion.fetcher import OfficialSourceClient
from app.ingestion.models import CrisisConfig, FetchResult, IngestionBundle, NgoConfig


OCHA_PLANS_URL = "https://api.hpc.tools/v2/public/plan"
UNHCR_POPULATION_URL = "https://api.unhcr.org/population/v1/population/"


class IngestionService:
    def __init__(self, database: SupabaseDataClient | None = None) -> None:
        self.database = database
        self.sources = OfficialSourceClient()

    async def close(self) -> None:
        await self.sources.close()

    async def run(self, trigger: str = "manual", dry_run: bool = False) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        started_at = _now()
        if self.database and not dry_run:
            await self.database.insert("ingestion_runs", [{
                "id": run_id,
                "status": "running",
                "trigger": trigger,
                "started_at": started_at,
            }])

        try:
            bundle = await self.collect()
            if self.database and not dry_run:
                await self._persist(bundle)
            status = "partial" if bundle.errors else "completed"
        except Exception as exc:
            if self.database and not dry_run:
                await self.database.update("ingestion_runs", {
                    "status": "failed",
                    "completed_at": _now(),
                    "errors": [{"source": "pipeline", "error": f"{type(exc).__name__}: {exc}"}],
                }, {"id": f"eq.{run_id}"})
            raise

        summary = {
            "run_id": run_id,
            "status": status,
            "dry_run": dry_run,
            "crises": len(bundle.crises),
            "ngos": len(bundle.ngos),
            "sources_checked": bundle.checked,
            "sources_updated": bundle.updated,
            "ngo_crisis_links": len(bundle.ngo_crises),
            "errors": bundle.errors,
        }
        if self.database and not dry_run:
            await self.database.update("ingestion_runs", {
                "status": status,
                "completed_at": _now(),
                "sources_checked": bundle.checked,
                "sources_updated": bundle.updated,
                "crises_updated": len(bundle.crises),
                "ngos_updated": len(bundle.ngos),
                "errors": bundle.errors,
            }, {"id": f"eq.{run_id}"})
        return summary

    async def collect(self) -> IngestionBundle:
        bundle = IngestionBundle()
        crisis_results = await asyncio.gather(*(self._collect_crisis(config) for config in CRISES))
        ngo_results = await asyncio.gather(*(self._collect_ngo(config) for config in NGOS))

        for crisis, sources, errors, checked, updated in crisis_results:
            bundle.crises.append(crisis)
            bundle.sources.extend(sources)
            bundle.errors.extend(errors)
            bundle.checked += checked
            bundle.updated += updated
        for ngo, source, links, errors in ngo_results:
            bundle.ngos.append(ngo)
            bundle.sources.append(source)
            bundle.ngo_crises.extend(links)
            bundle.errors.extend(errors)
            bundle.checked += 1
            bundle.updated += int(source["http_status"] == 200)
        return bundle

    async def _collect_crisis(
        self,
        config: CrisisConfig,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]], int, int]:
        errors: list[dict[str, str]] = []
        source_rows: list[dict[str, Any]] = []
        checked = 0
        updated = 0
        plan_id: int | None = None
        plan_year: int | None = None
        people_in_need: int | None = None
        funding_requirement: int | None = None
        plan_updated_at = _now()
        plan_title = f"{config.name} humanitarian response plan"

        plan_list_url = f"{OCHA_PLANS_URL}?countryISO3={config.iso3}"
        plan_list = await self.sources.fetch(plan_list_url)
        checked += 1
        if plan_list.status == 200:
            try:
                plans = json.loads(plan_list.content).get("data", [])
                latest = max(plans, key=lambda item: (item.get("planVersion") or {}).get("startDate") or "")
                plan_id = latest["id"]
                version = latest.get("planVersion") or {}
                plan_title = version.get("name") or plan_title
                plan_year = int((version.get("startDate") or "0000")[:4])
                funding_requirement = latest.get("revisedRequirements") or latest.get("origRequirements")
                detail_url = f"{OCHA_PLANS_URL}/{plan_id}?content=measurements"
                detail = await self.sources.fetch(detail_url)
                checked += 1
                if detail.status == 200:
                    payload = json.loads(detail.content).get("data", {})
                    people_in_need = _plan_metric(payload, "inNeed")
                    funding_requirement = payload.get("revisedRequirements") or payload.get("origRequirements") or funding_requirement
                    plan_updated_at = payload.get("updatedAt") or plan_updated_at
                    updated += 1
                    source_rows.append(_source_row(
                        entity_type="crisis",
                        entity_id=config.id,
                        title=plan_title,
                        organization="UN OCHA Humanitarian Programme Cycle",
                        source_type="Official humanitarian updates",
                        display_url=config.plan_page_url,
                        reporting_year=plan_year,
                        result=detail,
                        excerpt=f"People in need: {people_in_need}; funding requirement: {funding_requirement}",
                    ))
                else:
                    errors.append(_error(detail_url, detail))
            except (KeyError, TypeError, ValueError) as exc:
                errors.append({"source": plan_list_url, "error": f"Invalid OCHA response: {exc}"})
        else:
            errors.append(_error(plan_list_url, plan_list))

        displaced_value: int | None = None
        displaced_text = "See current displacement updates"
        if config.displacement_mode != "none":
            year = datetime.now(timezone.utc).year
            params = {
                "limit": 20,
                "yearFrom": year - 2,
                "yearTo": year,
                config.displacement_mode: config.iso3,
                "cf_type": "ISO",
            }
            unhcr_url = f"{UNHCR_POPULATION_URL}?" + "&".join(f"{key}={value}" for key, value in params.items())
            displacement = await self.sources.fetch(unhcr_url)
            checked += 1
            if displacement.status == 200:
                try:
                    items = json.loads(displacement.content).get("items", [])
                    latest = max(items, key=lambda item: int(item.get("year") or 0))
                    data_year = int(latest["year"])
                    field = "refugees" if config.displacement_mode == "coa" else "idps"
                    displaced_value = _integer(latest.get(field))
                    if displaced_value:
                        label = "refugees hosted" if field == "refugees" else "internally displaced people"
                        displaced_text = f"{_compact(displaced_value)} {label} ({data_year})"
                    updated += 1
                    source_rows.append(_source_row(
                        entity_type="crisis",
                        entity_id=config.id,
                        title=f"UNHCR displacement statistics for {config.country}",
                        organization="UNHCR",
                        source_type="Official displacement information",
                        display_url=config.displacement_page_url,
                        reporting_year=data_year,
                        result=displacement,
                        excerpt=f"{field}: {displaced_value}",
                    ))
                except (KeyError, TypeError, ValueError) as exc:
                    errors.append({"source": unhcr_url, "error": f"Invalid UNHCR response: {exc}"})
            else:
                errors.append(_error(unhcr_url, displacement))

        crisis = {
            "id": config.id,
            "name": config.name,
            "country": config.country,
            "iso3": config.iso3,
            "lat": config.lat,
            "lng": config.lng,
            "crisis_type": config.crisis_type,
            "people_in_need": f"{_compact(people_in_need)} people" if people_in_need else "See current response plan",
            "people_in_need_value": people_in_need,
            "displaced_people": displaced_text,
            "displaced_people_value": displaced_value,
            "funding_status": f"US${_compact_currency(funding_requirement)} requested for {plan_year}" if funding_requirement else "See current response plan",
            "funding_requirement_usd": funding_requirement,
            "response_plan_id": plan_id,
            "response_plan_year": plan_year,
            "focus_areas": config.focus_areas,
            "affected_locations": config.affected_locations,
            "summary": config.summary,
            "data_as_of": plan_updated_at,
        }
        return crisis, source_rows, errors, checked, updated

    async def _collect_ngo(
        self,
        config: NgoConfig,
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
        fetched = await self.sources.fetch(config.source.url)
        errors: list[dict[str, str]] = []
        if fetched.status != 200:
            errors.append(_error(config.source.url, fetched))
        facts = parse_ngo_facts(config.source.parser, fetched.text, config.baseline)
        year = int(facts["reporting_year"])
        ngo = {
            "id": config.id,
            "initials": config.initials,
            "short_name": config.short_name,
            "name": config.name,
            "descriptor": config.descriptor,
            "coverage": f"{facts['countries_active']} countries reported in {year}",
            "founded_year": config.founded_year,
            "reporting_year": year,
            "annual_income": facts.get("annual_income"),
            "annual_expenditure": facts.get("annual_expenditure"),
            "reported_reach": facts["reported_reach"],
            "countries_active": facts["countries_active"],
            "reported_activity": facts.get("reported_activity"),
            "donation_url": config.donation_url,
            "accent": config.accent,
            "accepted_giving_types": config.accepted_giving_types,
            "focus_areas": config.focus_areas,
            "data_as_of": f"{year}-12-31T00:00:00Z",
        }
        source = _source_row(
            entity_type="ngo",
            entity_id=config.id,
            title=config.source.title,
            organization=config.name,
            source_type=config.source.source_type,
            display_url=config.source.display_url or config.source.url,
            reporting_year=config.source.reporting_year,
            result=fetched,
            excerpt=_excerpt(fetched.text),
        )

        verified_at = _now()
        links: list[dict[str, Any]] = []
        if config.id == "care":
            links = [
                {"ngo_id": config.id, "crisis_id": crisis_id, "evidence_url": url, "verified_at": verified_at}
                for crisis_id, url in CARE_CRISIS_EVIDENCE.items()
            ]
        elif fetched.text:
            for crisis_id, patterns in CRISIS_ALIASES.items():
                if any(re.search(pattern, fetched.text, re.IGNORECASE) for pattern in patterns):
                    links.append({
                        "ngo_id": config.id,
                        "crisis_id": crisis_id,
                        "evidence_url": config.source.url,
                        "verified_at": verified_at,
                    })
        return ngo, source, links, errors

    async def _persist(self, bundle: IngestionBundle) -> None:
        if not self.database:
            return
        await self.database.upsert("crises", bundle.crises, "id")
        await self.database.upsert("ngos", bundle.ngos, "id")

        for entity_type, entity_id in {(item["entity_type"], item["entity_id"]) for item in bundle.sources}:
            await self.database.delete("sources", {"entity_type": f"eq.{entity_type}", "entity_id": f"eq.{entity_id}"})
        await self.database.insert("sources", bundle.sources)

        for ngo in bundle.ngos:
            await self.database.delete("ngo_crises", {"ngo_id": f"eq.{ngo['id']}"})
        await self.database.upsert("ngo_crises", bundle.ngo_crises, "ngo_id,crisis_id")


def _plan_metric(payload: dict[str, Any], metric_type: str) -> int | None:
    for attachment in payload.get("attachments", []):
        value = ((attachment.get("attachmentVersion") or {}).get("value") or {})
        totals = ((value.get("metrics") or {}).get("values") or {}).get("totals", [])
        for metric in totals:
            if metric.get("type") == metric_type and metric.get("value") is not None:
                return _integer(metric["value"])
    return None


def _source_row(
    *,
    entity_type: str,
    entity_id: str,
    title: str,
    organization: str,
    source_type: str,
    display_url: str | None,
    reporting_year: int | None,
    result: FetchResult,
    excerpt: str,
) -> dict[str, Any]:
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "title": title,
        "organization": organization,
        "source_type": source_type,
        "url": display_url,
        "reporting_year": reporting_year,
        "retrieved_at": _now(),
        "http_status": result.status,
        "content_hash": result.content_hash,
        "etag": result.etag,
        "last_modified": result.last_modified,
        "raw_excerpt": excerpt[:1200],
        "last_error": result.error,
    }


def _error(url: str, result: FetchResult) -> dict[str, str]:
    return {"source": url, "error": result.error or f"HTTP {result.status}"}


def _excerpt(text: str) -> str:
    if not text:
        return ""
    markers = ("million people", "children reached", "annual income", "people across")
    lower = text.lower()
    positions = [lower.find(marker) for marker in markers if lower.find(marker) >= 0]
    start = max(0, min(positions) - 250) if positions else 0
    return text[start:start + 1200]


def _integer(value: Any) -> int | None:
    if value in (None, "", "-"):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _compact(value: int | None) -> str:
    if value is None:
        return "Unavailable"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "K"
    return f"{value:,}"


def _compact_currency(value: int | None) -> str:
    if value is None:
        return "Unavailable"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}".rstrip("0").rstrip(".") + "B"
    return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "M"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
