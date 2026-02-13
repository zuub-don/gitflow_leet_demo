"""Central registry for season data."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SeasonInfo:
    name: str
    months: tuple[str, ...]
    avg_temp_c: float
    description: str
    activities: tuple[str, ...] = field(default_factory=tuple)


_REGISTRY: dict[str, SeasonInfo] = {}


def register(info: SeasonInfo) -> None:
    """Register a season in the global registry."""
    key = info.name.strip().lower()
    if key in _REGISTRY:
        raise ValueError(f"Season '{key}' is already registered.")
    _REGISTRY[key] = info


def get(name: str) -> SeasonInfo | None:
    """Retrieve season info by name (case-insensitive, whitespace-tolerant)."""
    return _REGISTRY.get(name.strip().lower())


def all_seasons() -> list[SeasonInfo]:
    """Return all registered seasons, sorted alphabetically."""
    return sorted(_REGISTRY.values(), key=lambda s: s.name)
