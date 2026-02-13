"""Tests for the season registry."""
import pytest
from seasons.registry import SeasonInfo, register, get, all_seasons, _REGISTRY


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure each test starts with a clean registry."""
    _REGISTRY.clear()
    yield
    _REGISTRY.clear()


def test_register_and_get():
    info = SeasonInfo(
        name="Test",
        months=("Jan",),
        avg_temp_c=0.0,
        description="A test season.",
    )
    register(info)
    assert get("test") is info
    assert get("TEST") is info


def test_duplicate_register_raises():
    info = SeasonInfo(name="Dup", months=("Jan",), avg_temp_c=0.0, description="x")
    register(info)
    with pytest.raises(ValueError, match="already registered"):
        register(info)


def test_get_missing_returns_none():
    assert get("nonexistent") is None


def test_all_seasons_sorted():
    for name in ("Zeta", "Alpha", "Mid"):
        register(SeasonInfo(name=name, months=("Jan",), avg_temp_c=0.0, description="x"))
    names = [s.name for s in all_seasons()]
    assert names == ["Alpha", "Mid", "Zeta"]
