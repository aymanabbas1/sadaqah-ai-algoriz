from __future__ import annotations

import re
from typing import Any, Callable


def parse_ngo_facts(parser: str, text: str, baseline: dict[str, Any]) -> dict[str, Any]:
    facts = dict(baseline)
    if not text:
        return facts
    parser_fn = PARSERS[parser]
    facts.update({key: value for key, value in parser_fn(text).items() if value is not None})
    return facts


def _care(text: str) -> dict[str, Any]:
    reach = _match(text, r"CARE reached\s+([\d.]+)\s+million people\s+across\s+(\d+)\s+countries")
    projects = _match(text, r"([\d,]+)\s+projects")
    return {
        "reported_reach": f"{reach[0]}M people" if reach else None,
        "countries_active": int(reach[1]) if reach else None,
        "reported_activity": f"{projects[0]} projects" if projects else None,
    }


def _human_appeal(text: str) -> dict[str, Any]:
    impact = _match(text, r"helped\s+([\d,]+)\s+people across\s+(\d+)\s+countries")
    income = _match(text, r"annual income of\s+[^\d]{0,4}([\d.]+)\s+million")
    expenditure = _match(text, r"Total expenditure\s+[\d,]+\s+[\d,]+\s+([\d,]+)")
    reach = int(impact[0].replace(",", "")) if impact else None
    spend = int(expenditure[0].replace(",", "")) if expenditure else None
    return {
        "reported_reach": _compact(reach, "people") if reach else None,
        "countries_active": int(impact[1]) if impact else None,
        "annual_income": f"GBP {income[0]}M" if income else None,
        "annual_expenditure": f"GBP {spend / 1_000_000:.1f}M" if spend else None,
    }


def _islamic_relief(text: str) -> dict[str, Any]:
    reach = _match(text, r"supported\s+([\d.]+)\s+million people") or _match(text, r"help an incredible\s+([\d.]+)\s+million people")
    income = _match(text, r"OUR TOTAL INCOME:\s+[^\d]{0,4}([\d.]+)\s+MILLION")
    expenditure = _match(text, r"OUR TOTAL EXPENDITURE:\s+[^\d]{0,4}([\d.]+)\s+MILLION")
    emergencies = _match(text, r"ran\s+(\d+)\s+emergency (?:projects|responses) in\s+(\d+)\s+countries")
    return {
        "reported_reach": f"{reach[0]}M people" if reach else None,
        "annual_income": f"GBP {income[0]}M" if income else None,
        "annual_expenditure": f"GBP {expenditure[0]}M" if expenditure else None,
        "reported_activity": f"{emergencies[0]} emergency projects in {emergencies[1]} countries" if emergencies else None,
    }


def _mercy_corps(text: str) -> dict[str, Any]:
    impact = _match(text, r"in\s+2025\s+Mercy Corps reached\s+([\d.]+)\s+million people across\s+(\d+)\s+countries")
    return {
        "reported_reach": f"{impact[0]}M people" if impact else None,
        "countries_active": int(impact[1]) if impact else None,
    }


def _save_the_children(text: str) -> dict[str, Any]:
    impact = _match(
        text,
        r"OUR IMPACT FOR CHILDREN IN\s+2025\s+([\d.]+)\s+million children reached\s+(\d+)\s+countries where we worked\s+(\d+)\s+emergencies responded to",
    )
    return {
        "reported_reach": f"{impact[0]}M children" if impact else None,
        "countries_active": int(impact[1]) if impact else None,
        "reported_activity": f"{impact[2]} emergencies responded to" if impact else None,
    }


def _match(text: str, pattern: str) -> tuple[str, ...] | None:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.groups() if match else None


def _compact(value: int, unit: str) -> str:
    if value >= 1_000_000:
        number = f"{value / 1_000_000:.2f}".rstrip("0").rstrip(".")
        return f"{number}M {unit}"
    if value >= 1_000:
        number = f"{value / 1_000:.1f}".rstrip("0").rstrip(".")
        return f"{number}K {unit}"
    return f"{value:,} {unit}"


PARSERS: dict[str, Callable[[str], dict[str, Any]]] = {
    "care": _care,
    "human_appeal": _human_appeal,
    "islamic_relief": _islamic_relief,
    "mercy_corps": _mercy_corps,
    "save_the_children": _save_the_children,
}
