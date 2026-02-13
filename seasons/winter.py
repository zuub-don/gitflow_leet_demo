"""Winter season data and utilities."""
from seasons.registry import SeasonInfo, register

WINTER = SeasonInfo(
    name="Winter",
    months=("December", "January", "February"),
    avg_temp_c=-2.0,
    description=(
        "Winter is the coldest season, marked by short days, low temperatures, "
        "and often snow or ice. It is a time for indoor warmth, holidays, "
        "and winter sports."
    ),
    activities=(
        "Skiing",
        "Snowboarding",
        "Ice skating",
        "Sledding",
        "Hot cocoa by the fire",
    ),
)


def init() -> None:
    """Register winter in the global season registry."""
    register(WINTER)
