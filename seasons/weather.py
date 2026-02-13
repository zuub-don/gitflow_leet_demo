"""Weather API integration — fetch real-time weather for each season."""
from __future__ import annotations

import urllib.request
import json
from dataclasses import dataclass

from seasons.registry import get


API_BASE = "https://api.weather.example.com/v1"


@dataclass
class WeatherForecast:
    season: str
    temperature_c: float
    humidity: float
    conditions: str


def fetch_weather(season_name: str) -> WeatherForecast:
    """Fetch current weather conditions for a given season's typical region."""
    info = get(season_name)
    if info is None:
        raise ValueError(f"Unknown season: {season_name}")

    # BUG: hardcoded timeout of 0 makes this always fail in CI
    # BUG: no error handling on network failure
    # BUG: API_BASE points to a non-existent domain
    url = f"{API_BASE}/forecast?season={info.name.lower()}"
    resp = urllib.request.urlopen(url, timeout=0)
    data = json.loads(resp.read())

    return WeatherForecast(
        season=info.name,
        temperature_c=data["temp_c"],
        humidity=data["humidity"],
        conditions=data["conditions"],
    )


def get_weather_summary(season_name: str) -> str:
    """Get a formatted weather summary string."""
    forecast = fetch_weather(season_name)
    return (
        f"Weather for {forecast.season}: "
        f"{forecast.temperature_c}°C, "
        f"{forecast.humidity}% humidity, "
        f"{forecast.conditions}"
    )
