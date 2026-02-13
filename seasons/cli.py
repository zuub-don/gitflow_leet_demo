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
    cmp_parser = sub.add_parser("compare", help="Compare two seasons side by side")
    cmp_parser.add_argument("first", type=str, help="First season")
    cmp_parser.add_argument("second", type=str, help="Second season")
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

    if args.command == "compare":
        a = registry.get(args.first)
        b = registry.get(args.second)
        if a is None:
            print(f"Unknown season: '{args.first}'", file=sys.stderr)
            return 1
        if b is None:
            print(f"Unknown season: '{args.second}'", file=sys.stderr)
            return 1
        print(_format_comparison(a, b))
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


def _format_comparison(a: registry.SeasonInfo, b: registry.SeasonInfo) -> str:
    """Format a side-by-side comparison of two seasons."""
    lines = [
        f"{'':15} {'┃ ' + a.name:<20} {'┃ ' + b.name:<20}",
        "─" * 55,
        f"{'Months':15} ┃ {', '.join(a.months):<18} ┃ {', '.join(b.months):<18}",
        f"{'Avg Temp':15} ┃ {a.avg_temp_c:<18.1f} ┃ {b.avg_temp_c:<18.1f}",
    ]
    diff = a.avg_temp_c - b.avg_temp_c
    if diff > 0:
        lines.append(f"  → {a.name} is {diff:.1f}°C warmer than {b.name}")
    elif diff < 0:
        lines.append(f"  → {b.name} is {abs(diff):.1f}°C warmer than {a.name}")
    else:
        lines.append(f"  → Both seasons have the same average temperature")
    return "\n".join(lines)


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
