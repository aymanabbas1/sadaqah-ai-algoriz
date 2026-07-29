from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class CrisisConfig:
    id: str
    name: str
    country: str
    iso3: str
    lat: float
    lng: float
    crisis_type: str
    focus_areas: list[str]
    affected_locations: list[str]
    summary: str
    plan_page_url: str
    displacement_page_url: str | None = None
    displacement_mode: Literal["coo", "coa", "none"] = "coo"


@dataclass(frozen=True)
class NgoSourceConfig:
    title: str
    source_type: str
    url: str
    reporting_year: int
    parser: str
    display_url: str | None = None


@dataclass(frozen=True)
class NgoConfig:
    id: str
    initials: str
    short_name: str
    name: str
    descriptor: str
    founded_year: int
    accent: str
    accepted_giving_types: list[str]
    focus_areas: list[str]
    donation_url: str
    baseline: dict[str, Any]
    source: NgoSourceConfig


@dataclass
class FetchResult:
    url: str
    status: int
    content: bytes = b""
    text: str = ""
    content_hash: str | None = None
    etag: str | None = None
    last_modified: str | None = None
    error: str | None = None


@dataclass
class IngestionBundle:
    crises: list[dict[str, Any]] = field(default_factory=list)
    ngos: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    ngo_crises: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    checked: int = 0
    updated: int = 0
