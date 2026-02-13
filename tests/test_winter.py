"""Tests for the winter module."""
from seasons.registry import get, _REGISTRY
from seasons.winter import WINTER, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_winter_data():
    assert WINTER.name == "Winter"
    assert WINTER.months == ("December", "January", "February")
    assert WINTER.avg_temp_c == -2.0
    assert "Skiing" in WINTER.activities


def test_winter_init_registers():
    init()
    assert get("winter") is WINTER
