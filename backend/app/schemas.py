from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


Confidence = Literal["high", "medium", "low"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SourceRecord(BaseModel):
    title: str
    organization: str
    sourceType: str
    url: str
    reportingYear: int | None = None


class RegionStat(BaseModel):
    id: str
    name: str
    country: str
    lat: float
    lng: float
    crisisType: str
    peopleInNeed: str
    displacedPeople: str
    fundingStatus: str
    focusAreas: list[str]
    affectedLocations: list[str]
    summary: str
    sources: list[SourceRecord]
    asOf: datetime = Field(default_factory=utc_now)


class NgoProfile(BaseModel):
    id: str
    initials: str
    shortName: str
    name: str
    descriptor: str
    coverage: str
    foundedYear: int
    yearsActive: int = Field(ge=0)
    reportingYear: int
    annualIncome: str | None = None
    annualExpenditure: str | None = None
    reportedReach: str
    countriesActive: int = Field(ge=0)
    reportedActivity: str | None = None
    donationUrl: str
    accent: str
    acceptedGivingTypes: list[str]
    focusAreas: list[str]
    crisisIds: list[str]
    sources: list[SourceRecord]
    asOf: datetime = Field(default_factory=utc_now)


class GlobeSummary(BaseModel):
    crisisProfiles: int
    countriesCovered: int
    sourceRecords: int


class GlobeResponse(BaseModel):
    regions: list[RegionStat]
    summary: GlobeSummary
    asOf: datetime = Field(default_factory=utc_now)


class CompareRequest(BaseModel):
    ids: list[str] = Field(min_length=2, max_length=3)
    crisisId: str


class CompareResponse(BaseModel):
    organizations: list[NgoProfile]
    rationale: str
    asOf: datetime = Field(default_factory=utc_now)


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    contextType: Literal["crisis", "ngo_comparison"]
    crisisId: str | None = None
    ngoIds: list[str] = Field(default_factory=list, max_length=3)
    conversation: list[ConversationMessage] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def validate_screen_context(self) -> "ChatRequest":
        if not self.crisisId:
            raise ValueError("A selected crisis is required")
        if self.contextType == "ngo_comparison" and len(self.ngoIds) < 2:
            raise ValueError("NGO comparison requires at least two selected organizations")
        return self


class Artifact(BaseModel):
    type: Literal["globe_regions", "ngo_comparison", "ngo_profile", "crisis_profile", "sources", "methodology"]
    data: Any


class ChatResponse(BaseModel):
    message: str
    intent: Literal["smalltalk", "crisis_lookup", "ngo_lookup", "compare_ngos", "sources", "methodology", "out_of_scope"]
    artifacts: list[Artifact] = Field(default_factory=list)
    sources: list[SourceRecord] = Field(default_factory=list)
    asOf: datetime = Field(default_factory=utc_now)
    confidence: Confidence = "high"
    mode: Literal["groq", "deterministic"] = "deterministic"


class ToolResult(BaseModel):
    intent: str
    data: Any
    artifacts: list[Artifact] = Field(default_factory=list)
    sources: list[SourceRecord] = Field(default_factory=list)
    asOf: datetime = Field(default_factory=utc_now)
    confidence: Confidence = "high"


class ToolDefinition(BaseModel):
    name: str
    purpose: str
    usedWhen: str


class NgoMetricDefinition(BaseModel):
    id: str
    label: str
    definition: str
    sourceType: str
    comparisonNote: str


class MethodologyResponse(BaseModel):
    ngoMetrics: list[NgoMetricDefinition]
    tools: list[ToolDefinition]
    principles: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    repository: Literal["local", "supabase"] = "local"
    llmProvider: str
    llmConfigured: bool
    timestamp: datetime = Field(default_factory=utc_now)
