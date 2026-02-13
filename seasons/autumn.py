"""Autumn season data and utilities."""
from seasons.registry import SeasonInfo, register

AUTUMN = SeasonInfo(
    name="Autumn",
    months=("September", "October", "November"),
    avg_temp_c=12.0,
    description=(
        "Autumn is the transitional season between summer and winter. "
        "Leaves change color, temperatures cool, and harvests are gathered. "
        "It is often considered the most visually stunning season."
    ),
    activities=(
        "Leaf peeping",
        "Apple picking",
        "Hiking",
        "Pumpkin carving",
        "Bonfires",
    ),
)


def init() -> None:
    """Register autumn in the global season registry."""
    register(AUTUMN)
