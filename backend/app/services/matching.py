from app.schemas import NgoProfile, RegionStat


def find_crisis(query: str, crises: list[RegionStat]) -> RegionStat | None:
    normalized = query.lower()
    return next(
        (
            crisis
            for crisis in crises
            if crisis.id.lower() in normalized
            or crisis.name.lower() in normalized
            or crisis.country.lower() in normalized
        ),
        None,
    )


def ngos_for_crisis(ngos: list[NgoProfile], crisis_id: str) -> list[NgoProfile]:
    return sorted(
        [ngo for ngo in ngos if crisis_id in ngo.crisisIds or "global" in ngo.crisisIds],
        key=lambda ngo: ngo.name,
    )


def select_ngos(ngos: list[NgoProfile], ids: list[str]) -> list[NgoProfile]:
    by_id = {ngo.id: ngo for ngo in ngos}
    return [by_id[ngo_id] for ngo_id in ids if ngo_id in by_id]
