from typing import Protocol

from app.data.seed import NGOS, REGIONS
from app.schemas import NgoProfile, RegionStat


class Repository(Protocol):
    mode: str

    async def list_crises(self) -> list[RegionStat]: ...

    async def get_crisis(self, crisis_id: str) -> RegionStat | None: ...

    async def list_ngos(self) -> list[NgoProfile]: ...

    async def get_ngo(self, ngo_id: str) -> NgoProfile | None: ...


class InMemoryRepository:
    mode = "local"

    async def list_crises(self) -> list[RegionStat]:
        return [item.model_copy(deep=True) for item in REGIONS]

    async def get_crisis(self, crisis_id: str) -> RegionStat | None:
        return next((item.model_copy(deep=True) for item in REGIONS if item.id == crisis_id), None)

    async def list_ngos(self) -> list[NgoProfile]:
        return [item.model_copy(deep=True) for item in NGOS]

    async def get_ngo(self, ngo_id: str) -> NgoProfile | None:
        return next((item.model_copy(deep=True) for item in NGOS if item.id == ngo_id), None)
