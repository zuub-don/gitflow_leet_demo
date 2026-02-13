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


def _format_season(info: registry.SeasonInfo, *, verbose: bool = True) -> str:
    """Format season info with box-drawing characters."""
    width = 56
    name_display = f" {info.name} "
    top = f"┌{'─' * width}┐"
    bot = f"└{'─' * width}┘"
    title = f"│{name_display:─^{width}}│"
    lines = [top, title, f"│{'─' * width}│"]
    lines.append(f"│  {'Months':<12}: {', '.join(info.months):<{width - 17}}│")
    lines.append(f"│  {'Avg Temp':<12}: {info.avg_temp_c}°C{'':<{width - 22 - len(str(info.avg_temp_c))}}│")
    if verbose and info.description:
        desc = info.description[:width - 17]
        lines.append(f"│  {'Description':<12}: {desc:<{width - 17}}│")
    if info.activities:
        act_str = ', '.join(info.activities[:3])
        if len(info.activities) > 3:
            act_str += f' (+{len(info.activities) - 3} more)'
        lines.append(f"│  {'Activities':<12}: {act_str:<{width - 17}}│")
    lines.append(bot)
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
    """Print a compact summary table with box-drawing borders."""
    seasons = registry.all_seasons()
    if not seasons:
        print("No seasons registered.")
        return
    print("┌──────────┬────────────────────────────────┬────────┐")
    print("│ Season   │ Months                         │ Avg °C │")
    print("├──────────┼────────────────────────────────┼────────┤")
    for s in seasons:
        months_str = ", ".join(s.months)
        print(f"│ {s.name:<8} │ {months_str:<30} │ {s.avg_temp_c:>6.1f} │")
    print("└──────────┴────────────────────────────────┴────────┘")


if __name__ == "__main__":
    sys.exit(main())
