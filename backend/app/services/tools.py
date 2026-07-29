from __future__ import annotations

from typing import Any

from app.repository import Repository
from app.schemas import Artifact, MethodologyResponse, NgoMetricDefinition, ToolDefinition, ToolResult
from app.services.matching import ngos_for_crisis, select_ngos


METHODOLOGY = MethodologyResponse(
    ngoMetrics=[
        NgoMetricDefinition(id="founded_year", label="Founded year", definition="The year the organization states it began operating.", sourceType="Official history or about page", comparisonNote="Used to derive years operating."),
        NgoMetricDefinition(id="annual_income", label="Annual income", definition="Total income in the latest published financial period when available.", sourceType="Audited annual report", comparisonNote="Shown in the organization's reported currency; scale is not effectiveness."),
        NgoMetricDefinition(id="annual_expenditure", label="Annual expenditure", definition="Latest published expenditure when available.", sourceType="Audited annual report", comparisonNote="Accounting definitions differ across organizations."),
        NgoMetricDefinition(id="reported_reach", label="Reported reach", definition="The organization's own latest published reach figure and population label.", sourceType="Annual or impact report", comparisonNote="Children, people, households, direct reach, and indirect reach are not interchangeable."),
        NgoMetricDefinition(id="countries_active", label="Countries active", definition="Number of countries where the organization reports active work.", sourceType="Annual report or where-we-work page", comparisonNote="A scale measure, not a quality rating."),
        NgoMetricDefinition(id="reported_activity", label="Reported activity", definition="Projects, programmes, initiatives, or emergencies stated in the report.", sourceType="Annual or impact report", comparisonNote="Displayed as published and not combined across definitions."),
        NgoMetricDefinition(id="reporting_year", label="Latest report year", definition="The reporting period attached to the displayed figures.", sourceType="Annual-report index", comparisonNote="Always shown beside annual values."),
    ],
    tools=[
        ToolDefinition(name="search_crises", purpose="Find crisis profiles without ranking them.", usedWhen="The user asks about a location, crisis, or humanitarian situation."),
        ToolDefinition(name="get_crisis_profile", purpose="Return one crisis profile and its official sources.", usedWhen="A crisis is selected or identified."),
        ToolDefinition(name="list_ngos_for_crisis", purpose="List NGOs with documented activity in a crisis.", usedWhen="The user asks which organizations are active in the selected crisis."),
        ToolDefinition(name="search_ngos", purpose="Find NGO profiles by name or focus area.", usedWhen="The user asks about organizations generally."),
        ToolDefinition(name="get_ngo_profile", purpose="Return one NGO's reported operating facts and official sources.", usedWhen="A specific NGO is identified."),
        ToolDefinition(name="compare_ngo_facts", purpose="Place selected NGO facts side by side without choosing a winner.", usedWhen="The user asks to compare selected organizations."),
        ToolDefinition(name="get_sources", purpose="Return official source links for a crisis or NGO.", usedWhen="The user asks where information came from."),
    ],
    principles=[
        "Crisis profiles are never ranked or assigned a platform priority score.",
        "NGOs are never labelled best, trusted, or most effective.",
        "Comparison shows reported facts with their reporting periods and official source links.",
        "Mansa Musa retrieves and explains information but does not make donation decisions.",
    ],
)


class ToolEngine:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    async def search_crises(self, query: str = "") -> ToolResult:
        crises = await self.repository.list_crises()
        tokens = {token.strip("?.,!") for token in query.lower().split() if len(token.strip("?.,!")) > 3}
        if tokens:
            matches = [
                crisis for crisis in crises
                if any(
                    token in f"{crisis.id} {crisis.name} {crisis.country} {crisis.crisisType} {' '.join(crisis.focusAreas)}".lower()
                    for token in tokens
                )
            ]
            if matches:
                crises = matches
        crises.sort(key=lambda crisis: crisis.name)
        data = [crisis.model_dump(mode="json") for crisis in crises]
        sources = [item for crisis in crises for item in crisis.sources]
        return ToolResult(intent="crisis_lookup", data=data, sources=sources, artifacts=[Artifact(type="globe_regions", data=data)])

    async def get_crisis_profile(self, crisis_id: str) -> ToolResult:
        crisis = await self.repository.get_crisis(crisis_id)
        if not crisis:
            return await self.search_crises(crisis_id)
        data = crisis.model_dump(mode="json")
        return ToolResult(intent="crisis_lookup", data=data, sources=crisis.sources, artifacts=[Artifact(type="crisis_profile", data=data)])

    async def list_ngos_for_crisis(self, crisis_id: str) -> ToolResult:
        crisis = await self.repository.get_crisis(crisis_id)
        all_ngos = await self.repository.list_ngos()
        organizations = ngos_for_crisis(all_ngos, crisis_id)
        data = {
            "crisis": crisis.model_dump(mode="json") if crisis else None,
            "organizations": [ngo.model_dump(mode="json") for ngo in organizations],
        }
        sources = [item for ngo in organizations for item in ngo.sources]
        return ToolResult(intent="ngo_lookup", data=data, sources=sources, artifacts=[Artifact(type="ngo_profile", data=data)])

    async def search_ngos(self, query: str = "") -> ToolResult:
        ngos = await self.repository.list_ngos()
        tokens = {token.strip("?.,!") for token in query.lower().split() if len(token.strip("?.,!")) > 3}
        if tokens:
            matches = [
                ngo for ngo in ngos
                if any(token in f"{ngo.name} {ngo.shortName} {ngo.coverage} {' '.join(ngo.focusAreas)}".lower() for token in tokens)
            ]
            if matches:
                ngos = matches
        ngos.sort(key=lambda ngo: ngo.name)
        data = [ngo.model_dump(mode="json") for ngo in ngos]
        sources = [item for ngo in ngos for item in ngo.sources]
        return ToolResult(intent="ngo_lookup", data=data, sources=sources, artifacts=[Artifact(type="ngo_profile", data=data)])

    async def get_ngo_profile(self, ngo_id: str) -> ToolResult:
        ngo = await self.repository.get_ngo(ngo_id)
        if not ngo:
            return await self.search_ngos(ngo_id)
        data = ngo.model_dump(mode="json")
        return ToolResult(intent="ngo_lookup", data=data, sources=ngo.sources, artifacts=[Artifact(type="ngo_profile", data=data)])

    async def compare_ngo_facts(self, ids: list[str]) -> ToolResult:
        all_ngos = await self.repository.list_ngos()
        organizations = select_ngos(all_ngos, ids)
        payload = {"organizations": [ngo.model_dump(mode="json") for ngo in organizations]}
        sources = [item for ngo in organizations for item in ngo.sources]
        return ToolResult(intent="compare_ngos", data=payload, sources=sources, artifacts=[Artifact(type="ngo_comparison", data=payload)])

    async def get_sources(self, entity_type: str, entity_id: str) -> ToolResult:
        if entity_type == "ngo":
            entity = await self.repository.get_ngo(entity_id)
        else:
            entity = await self.repository.get_crisis(entity_id)
        sources = entity.sources if entity else []
        data = [item.model_dump(mode="json") for item in sources]
        return ToolResult(intent="sources", data=data, sources=sources, artifacts=[Artifact(type="sources", data=data)])

    async def execute(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        handlers = {
            "search_crises": self.search_crises,
            "get_crisis_profile": self.get_crisis_profile,
            "list_ngos_for_crisis": self.list_ngos_for_crisis,
            "search_ngos": self.search_ngos,
            "get_ngo_profile": self.get_ngo_profile,
            "compare_ngo_facts": self.compare_ngo_facts,
            "get_sources": self.get_sources,
        }
        handler = handlers.get(name)
        if handler is None:
            raise ValueError(f"Tool is not allowlisted: {name}")
        return await handler(**arguments)


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {"type": "function", "function": {"name": "search_crises", "description": "Find crisis profiles alphabetically without ranking urgency.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_crisis_profile", "description": "Get one selected crisis profile and official sources.", "parameters": {"type": "object", "properties": {"crisis_id": {"type": "string"}}, "required": ["crisis_id"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "list_ngos_for_crisis", "description": "List organizations with documented activity in the selected crisis. Do not rank them.", "parameters": {"type": "object", "properties": {"crisis_id": {"type": "string"}}, "required": ["crisis_id"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "search_ngos", "description": "Find NGO profiles by name or focus. Do not recommend or rank them.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_ngo_profile", "description": "Get one NGO's reported facts and official source links.", "parameters": {"type": "object", "properties": {"ngo_id": {"type": "string"}}, "required": ["ngo_id"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "compare_ngo_facts", "description": "Compare two or three selected NGOs side by side without ordering or choosing a winner.", "parameters": {"type": "object", "properties": {"ids": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}}, "required": ["ids"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_sources", "description": "Return official source links for one crisis or NGO.", "parameters": {"type": "object", "properties": {"entity_type": {"type": "string", "enum": ["crisis", "ngo"]}, "entity_id": {"type": "string"}}, "required": ["entity_type", "entity_id"], "additionalProperties": False}}},
]
