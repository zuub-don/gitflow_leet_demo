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
    if not info.name or not info.name.strip():
        raise ValueError("Season name must not be empty.")
    if not info.months:
        raise ValueError(f"Season '{info.name}' must have at least one month.")
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


def remove(name: str) -> bool:
    """Remove a season from the registry. Returns True if removed."""
    key = name.strip().lower()
    if key in _REGISTRY:
        del _REGISTRY[key]
        return True
    return False
