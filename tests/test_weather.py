"""Tests for the weather API integration — THESE WILL FAIL."""
import pytest
from seasons.weather import fetch_weather, get_weather_summary


def test_fetch_weather_spring():
    """This test hits a non-existent API and will always fail."""
    forecast = fetch_weather("spring")
    assert forecast.season == "Spring"
    assert forecast.temperature_c > -50


def test_fetch_weather_unknown_season():
    with pytest.raises(ValueError, match="Unknown season"):
        fetch_weather("narnia")


def test_weather_summary():
    """This test also hits the broken API."""
    summary = get_weather_summary("summer")
    assert "Summer" in summary
