"""Regression test for whitespace-tolerant season lookup (hotfix/1.0.1)."""
from seasons.registry import SeasonInfo, register, get, _REGISTRY


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_get_strips_whitespace():
    info = SeasonInfo(name="Spring", months=("Mar",), avg_temp_c=0.0, description="x")
    register(info)
    assert get("  spring  ") is info
    assert get("Spring ") is info
    assert get(" SPRING") is info


def test_register_strips_whitespace():
    info = SeasonInfo(name=" Padded ", months=("Jan",), avg_temp_c=0.0, description="x")
    register(info)
    assert get("padded") is info
