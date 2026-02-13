"""Tests for the summer module."""
from seasons.registry import get, _REGISTRY
from seasons.summer import SUMMER, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_summer_data():
    assert SUMMER.name == "Summer"
    assert SUMMER.months == ("June", "July", "August")
    assert SUMMER.avg_temp_c == 28.0
    assert "Swimming" in SUMMER.activities


def test_summer_init_registers():
    init()
    assert get("summer") is SUMMER
