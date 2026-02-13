"""Tests for the autumn module."""
from seasons.registry import get, _REGISTRY
from seasons.autumn import AUTUMN, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_autumn_data():
    assert AUTUMN.name == "Autumn"
    assert AUTUMN.months == ("September", "October", "November")
    assert AUTUMN.avg_temp_c == 12.0
    assert "Leaf peeping" in AUTUMN.activities


def test_autumn_init_registers():
    init()
    assert get("autumn") is AUTUMN
