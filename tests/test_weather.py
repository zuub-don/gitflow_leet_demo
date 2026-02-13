"""Tests for the weather module (v2 — no network calls)."""
import pytest
from seasons.registry import _REGISTRY
from seasons import spring, summer, autumn, winter
from seasons.weather import (
    get_weather,
    format_weather,
    SeasonNotFoundError,
    WeatherProfile,
)


@pytest.fixture(autouse=True)
def _ensure_registry():
    _REGISTRY.clear()
    spring.init()
    summer.init()
    autumn.init()
    winter.init()
    yield
    _REGISTRY.clear()


class TestGetWeather:
    def test_all_seasons_have_profiles(self):
        for name in ("spring", "summer", "autumn", "winter"):
            profile = get_weather(name)
            assert isinstance(profile, WeatherProfile)
            assert profile.season.lower() == name

    def test_case_insensitive(self):
        assert get_weather("SPRING").season == "Spring"
        assert get_weather("Summer").season == "Summer"

    def test_whitespace_tolerant(self):
        assert get_weather("  autumn  ").season == "Autumn"

    def test_unknown_season_raises(self):
        with pytest.raises(SeasonNotFoundError, match="Unknown season"):
            get_weather("monsoon")

    def test_temperature_sanity(self):
        for name in ("spring", "summer", "autumn", "winter"):
            p = get_weather(name)
            assert p.avg_high_c > p.avg_low_c, f"{name}: high should exceed low"
            assert 0 <= p.humidity_pct <= 100

    def test_uv_index_range(self):
        for name in ("spring", "summer", "autumn", "winter"):
            p = get_weather(name)
            assert 1 <= p.uv_index <= 11


class TestFormatWeather:
    def test_format_contains_key_fields(self):
        profile = get_weather("winter")
        output = format_weather(profile)
        assert "Winter" in output
        assert "High/Low" in output
        assert "Humidity" in output
        assert "UV Index" in output

    def test_format_returns_string(self):
        profile = get_weather("spring")
        assert isinstance(format_weather(profile), str)
