"""Spring season data and utilities."""
from seasons.registry import SeasonInfo, register

SPRING = SeasonInfo(
    name="Spring",
    months=("March", "April", "May"),
    avg_temp_c=15.0,
    description=(
        "Spring marks the transition from winter to summer. "
        "Days grow longer, temperatures rise, and flora begins to bloom."
    ),
    activities=(
        "Hiking",
        "Gardening",
        "Bird watching",
        "Cycling",
        "Picnicking",
    ),
)


def init() -> None:
    """Register spring in the global season registry."""
    register(SPRING)
