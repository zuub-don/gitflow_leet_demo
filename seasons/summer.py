"""Summer season data and utilities."""
from seasons.registry import SeasonInfo, register

SUMMER = SeasonInfo(
    name="Summer",
    months=("June", "July", "August"),
    avg_temp_c=28.0,
    description=(
        "Summer is the warmest season, characterized by long days, "
        "high temperatures, and abundant sunshine. It is the peak season "
        "for outdoor recreation."
    ),
    activities=(
        "Swimming",
        "Surfing",
        "Camping",
        "Barbecuing",
        "Traveling",
        "Outdoor concerts",
    ),
)


def init() -> None:
    """Register summer in the global season registry."""
    register(SUMMER)
