from __future__ import annotations

from app.repository import Repository
from app.schemas import Artifact, ChatRequest, ChatResponse, SourceRecord, ToolResult
from app.services.llm import LlmOrchestrator
from app.services.tools import ToolEngine


GREETING_WORDS = {"hi", "hello", "hey", "salam", "salaam", "assalamu alaikum", "as-salamu alaykum"}
RANKING_WORDS = ("best", "most urgent", "rank", "recommend", "where should i donate", "where should i give")


class ChatService:
    def __init__(self, repository: Repository, tools: ToolEngine, llm: LlmOrchestrator) -> None:
        self.repository = repository
        self.tools = tools
        self.llm = llm

    async def respond(self, request: ChatRequest) -> ChatResponse:
        if self._is_ranking_request(request.message):
            result = await self._route_locally(request)
            subject = "organizations" if request.ngoIds or "ngo" in request.message.lower() else "humanitarian crises"
            message = (
                f"I do not rank {subject} or choose a winner. "
                "I can show sourced profiles, documented activity, and side-by-side reported facts so you can make the decision."
            )
            return self._build_response(message, [result], mode="deterministic")

        if self._is_greeting(request.message):
            if self.llm.configured:
                try:
                    return ChatResponse(message=await self.llm.greet(request), intent="smalltalk", mode="groq")
                except Exception:
                    pass
            return ChatResponse(
                message="Wa alaikum assalam. I am Mansa Musa. Select a crisis or NGO comparison and I can explain the sourced information.",
                intent="smalltalk",
            )

        result = await self._route_locally(request)
        if self.llm.configured:
            try:
                message = await self.llm.explain(request, result)
                return self._build_response(message, [result], mode="groq")
            except Exception:
                pass
        return self._build_response(self._explain(result), [result], mode="deterministic")

    async def _route_locally(self, request: ChatRequest) -> ToolResult:
        normalized = request.message.lower()
        if request.contextType == "ngo_comparison":
            return await self.tools.compare_ngo_facts(request.ngoIds)

        if "source" in normalized or "link" in normalized or "where did" in normalized:
            return await self.tools.get_sources("crisis", request.crisisId)
        if any(word in normalized for word in ("ngo", "organization", "respond", "who")):
            return await self.tools.list_ngos_for_crisis(request.crisisId)
        return await self.tools.get_crisis_profile(request.crisisId)

    @staticmethod
    def _build_response(message: str, results: list[ToolResult], mode: str) -> ChatResponse:
        primary = results[-1]
        artifacts: list[Artifact] = []
        sources_by_url: dict[str, SourceRecord] = {}
        for result in results:
            artifacts.extend(result.artifacts)
            for source in result.sources:
                sources_by_url[source.url] = source
        return ChatResponse(
            message=message,
            intent=primary.intent,
            artifacts=artifacts,
            sources=list(sources_by_url.values()),
            asOf=primary.asOf,
            confidence=primary.confidence,
            mode=mode,
        )

    @staticmethod
    def _is_greeting(message: str) -> bool:
        return message.lower().strip().rstrip("!.,?") in GREETING_WORDS

    @staticmethod
    def _is_ranking_request(message: str) -> bool:
        normalized = message.lower()
        return any(phrase in normalized for phrase in RANKING_WORDS)

    @staticmethod
    def _explain(result: ToolResult) -> str:
        if result.intent == "compare_ngos":
            names = [item["name"] for item in result.data.get("organizations", [])]
            return f"This comparison places {', '.join(names)} side by side using their reported operating facts. It does not rank them or choose a winner."
        if result.intent == "crisis_lookup":
            records = result.data if isinstance(result.data, list) else [result.data]
            top = records[0]
            return f"{top['name']} is documented as a {top['crisisType'].lower()} crisis. The profile includes reported need, displacement, focus areas, affected locations, and official source links."
        if result.intent == "ngo_lookup":
            records = result.data.get("organizations", []) if isinstance(result.data, dict) and "organizations" in result.data else result.data
            records = records if isinstance(records, list) else [records]
            return f"I found {len(records)} organization profile{'s' if len(records) != 1 else ''} with reported operating facts and official source links."
        if result.intent == "sources":
            return f"I found {len(result.sources)} official source link{'s' if len(result.sources) != 1 else ''} for the selected profile."
        return "I can retrieve crisis profiles, documented NGO activity, factual comparisons, and official source links without ranking them."
