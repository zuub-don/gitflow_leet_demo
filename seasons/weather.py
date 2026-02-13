"""Weather integration — provides seasonal weather data.

v2: Rewritten after the original weather API integration was reverted.
    - Removed dependency on external API
    - Uses offline seasonal weather profiles
    - Properly testable with no network calls
"""
from __future__ import annotations

from dataclasses import dataclass

from seasons.registry import get


@dataclass(frozen=True)
class WeatherProfile:
    """Typical weather profile for a season."""
    season: str
    avg_high_c: float
    avg_low_c: float
    humidity_pct: float
    conditions: str
    uv_index: int


# Offline weather profiles — no flaky API calls
_PROFILES: dict[str, WeatherProfile] = {
    "spring": WeatherProfile(
        season="Spring", avg_high_c=18.0, avg_low_c=7.0,
        humidity_pct=65.0, conditions="Partly cloudy with occasional showers",
        uv_index=5,
    ),
    "summer": WeatherProfile(
        season="Summer", avg_high_c=32.0, avg_low_c=20.0,
        humidity_pct=55.0, conditions="Sunny and hot",
        uv_index=9,
    ),
    "autumn": WeatherProfile(
        season="Autumn", avg_high_c=14.0, avg_low_c=5.0,
        humidity_pct=70.0, conditions="Overcast with morning fog",
        uv_index=3,
    ),
    "winter": WeatherProfile(
        season="Winter", avg_high_c=2.0, avg_low_c=-8.0,
        humidity_pct=75.0, conditions="Cold with chance of snow",
        uv_index=1,
    ),
}


class SeasonNotFoundError(Exception):
    """Raised when a season is not in the registry or weather profiles."""


def get_weather(season_name: str) -> WeatherProfile:
    """Get the weather profile for a season.

    Raises:
        SeasonNotFoundError: If the season is not recognized.
    """
    key = season_name.strip().lower()

    # Validate against the registry first
    if get(key) is None:
        raise SeasonNotFoundError(f"Unknown season: '{season_name}'")

    profile = _PROFILES.get(key)
    if profile is None:
        raise SeasonNotFoundError(
            f"No weather profile available for '{season_name}'"
        )
    return profile


def format_weather(profile: WeatherProfile) -> str:
    """Format a weather profile for display."""
    return (
        f"Weather for {profile.season}:\n"
        f"  High/Low  : {profile.avg_high_c}°C / {profile.avg_low_c}°C\n"
        f"  Humidity  : {profile.humidity_pct}%\n"
        f"  Conditions: {profile.conditions}\n"
        f"  UV Index  : {profile.uv_index}"
    )
