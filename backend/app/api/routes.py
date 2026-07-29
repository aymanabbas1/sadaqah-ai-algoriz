from fastapi import APIRouter, HTTPException, Request, status

from app.core.config import Settings
from app.repository import Repository
from app.schemas import (
    ChatRequest,
    ChatResponse,
    CompareRequest,
    CompareResponse,
    GlobeResponse,
    GlobeSummary,
    HealthResponse,
    MethodologyResponse,
    NgoProfile,
    RegionStat,
)
from app.services.chat import ChatService
from app.services.matching import ngos_for_crisis, select_ngos
from app.services.tools import METHODOLOGY


router = APIRouter(prefix="/api/v1")


def repository_from(request: Request) -> Repository:
    return request.app.state.repository


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings: Settings = request.app.state.settings
    return HealthResponse(
        repository=request.app.state.repository.mode,
        llmProvider=settings.llm_provider,
        llmConfigured=request.app.state.llm.configured,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    service: ChatService = request.app.state.chat_service
    return await service.respond(payload)


@router.get("/methodology", response_model=MethodologyResponse)
async def methodology() -> MethodologyResponse:
    return METHODOLOGY


@router.get("/crises", response_model=list[RegionStat])
async def list_crises(request: Request) -> list[RegionStat]:
    crises = await repository_from(request).list_crises()
    return sorted(crises, key=lambda crisis: crisis.name)


@router.get("/crises/{crisis_id}", response_model=RegionStat)
async def get_crisis(crisis_id: str, request: Request) -> RegionStat:
    crisis = await repository_from(request).get_crisis(crisis_id)
    if not crisis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crisis not found")
    return crisis


@router.get("/crises/{crisis_id}/ngos", response_model=list[NgoProfile])
async def crisis_ngos(crisis_id: str, request: Request) -> list[NgoProfile]:
    repository = repository_from(request)
    if not await repository.get_crisis(crisis_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crisis not found")
    return ngos_for_crisis(await repository.list_ngos(), crisis_id)


@router.get("/globe", response_model=GlobeResponse)
async def globe(request: Request) -> GlobeResponse:
    crises = sorted(await repository_from(request).list_crises(), key=lambda crisis: crisis.name)
    return GlobeResponse(
        regions=crises,
        summary=GlobeSummary(
            crisisProfiles=len(crises),
            countriesCovered=len({crisis.country for crisis in crises}),
            sourceRecords=sum(len(crisis.sources) for crisis in crises),
        ),
    )


@router.get("/ngos", response_model=list[NgoProfile])
async def list_ngos(request: Request) -> list[NgoProfile]:
    ngos = await repository_from(request).list_ngos()
    return sorted(ngos, key=lambda ngo: ngo.name)


@router.get("/ngos/{ngo_id}", response_model=NgoProfile)
async def get_ngo(ngo_id: str, request: Request) -> NgoProfile:
    ngo = await repository_from(request).get_ngo(ngo_id)
    if not ngo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found")
    return ngo


@router.post("/ngos/compare", response_model=CompareResponse)
async def compare(payload: CompareRequest, request: Request) -> CompareResponse:
    repository = repository_from(request)
    crisis = await repository.get_crisis(payload.crisisId)
    if not crisis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crisis not found")
    responders = ngos_for_crisis(await repository.list_ngos(), payload.crisisId)
    selected = select_ngos(responders, payload.ids)
    if len(selected) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Select at least two organizations documented in this crisis",
        )
    return CompareResponse(
        organizations=selected,
        rationale=f"Latest published details for organizations documented in {crisis.name}.",
    )
