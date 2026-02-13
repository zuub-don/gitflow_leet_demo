"""Regression tests for registry input validation (hotfix/2.0.2)."""
import pytest
from seasons.registry import SeasonInfo, register, remove, _REGISTRY


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_register_empty_name_raises():
    info = SeasonInfo(name="", months=("Jan",), avg_temp_c=0.0, description="x")
    with pytest.raises(ValueError, match="must not be empty"):
        register(info)


def test_register_whitespace_only_name_raises():
    info = SeasonInfo(name="   ", months=("Jan",), avg_temp_c=0.0, description="x")
    with pytest.raises(ValueError, match="must not be empty"):
        register(info)


def test_register_no_months_raises():
    info = SeasonInfo(name="Bad", months=(), avg_temp_c=0.0, description="x")
    with pytest.raises(ValueError, match="must have at least one month"):
        register(info)


def test_remove_existing():
    info = SeasonInfo(name="Gone", months=("Jan",), avg_temp_c=0.0, description="x")
    register(info)
    assert remove("gone") is True
    assert _REGISTRY.get("gone") is None


def test_remove_nonexistent():
    assert remove("nope") is False
