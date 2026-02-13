"""Command-line interface for Seasons."""
import argparse
import sys

from seasons.__version__ import __version__
from seasons import registry
from seasons import weather


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seasons",
        description="Display information about the four seasons.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("all", help="Show all available seasons")
    info_parser = sub.add_parser("info", help="Show details for a season")
    info_parser.add_argument("name", type=str, help="Season name")
    sub.add_parser("summary", help="Show a compact summary table")
    weather_parser = sub.add_parser("weather", help="Show weather profile for a season")
    weather_parser.add_argument("name", type=str, help="Season name")
    return parser


def _format_season(info: registry.SeasonInfo) -> str:
    lines = [
        f"━━━ {info.name} ━━━",
        f"  Months     : {', '.join(info.months)}",
        f"  Avg Temp   : {info.avg_temp_c}°C",
        f"  Description: {info.description}",
    ]
    if info.activities:
        lines.append(f"  Activities : {', '.join(info.activities)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "all":
        seasons = registry.all_seasons()
        if not seasons:
            print("No seasons registered.")
            return 0
        for s in seasons:
            print(_format_season(s))
            print()
        return 0

    if args.command == "info":
        info = registry.get(args.name)
        if info is None:
            print(f"Unknown season: '{args.name}'", file=sys.stderr)
            return 1
        print(_format_season(info))
        return 0

    if args.command == "summary":
        _print_summary()
        return 0

    if args.command == "weather":
        try:
            profile = weather.get_weather(args.name)
            print(weather.format_weather(profile))
            return 0
        except weather.SeasonNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    return 0


def _print_summary() -> None:
    seasons = registry.all_seasons()
    if not seasons:
        print("No seasons registered.")
        return
    header = f"{'Season':<10} {'Months':<30} {'Avg °C':>6}"
    print(header)
    print("─" * len(header))
    for s in seasons:
        months_str = ", ".join(s.months)
        print(f"{s.name:<10} {months_str:<30} {s.avg_temp_c:>6.1f}")


if __name__ == "__main__":
    sys.exit(main())
