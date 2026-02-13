"""Tests for the spring module."""
from seasons.registry import get, _REGISTRY
from seasons.spring import SPRING, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_spring_data():
    assert SPRING.name == "Spring"
    assert len(SPRING.months) == 3
    assert SPRING.avg_temp_c == 15.0
    assert len(SPRING.activities) > 0


def test_spring_init_registers():
    init()
    assert get("spring") is SPRING
