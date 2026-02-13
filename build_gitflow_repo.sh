#!/usr/bin/env bash
set -euo pipefail

#
# build_gitflow_repo.sh
# =====================
# Builds an expert-level Git Flow demonstration repository from scratch.
# Demonstrates: main, develop, feature/*, release/*, hotfix/* branches
# with realistic Python code, tests, versioning, and merge strategies.
#
# Usage: bash build_gitflow_repo.sh
#

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

# ── Safety: refuse to run if .git already exists ──
if [ -d ".git" ]; then
  echo "ERROR: .git already exists in $REPO_DIR. Aborting to avoid data loss."
  exit 1
fi

# ── Helper ──
commit() {
  git add -A
  git commit -m "$1"
}

# ═══════════════════════════════════════════════════════════════════════
# PHASE 0 — Repository Initialization (main branch)
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 0: Initialize repository on main"

git init -b main

# --- .gitignore ---
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
.eggs/
*.egg-info/
dist/
build/
.venv/
.env
.pytest_cache/
.coverage
htmlcov/
EOF

# --- README.md ---
cat > README.md << 'READMEEOF'
# Seasons — Expert Git Flow Demo

A Python CLI application that provides information about the four seasons.
This repository demonstrates an **expert-level Git Flow** branching model.

## Git Flow Branching Model

```
main ─────●────────────────●──────────●────────────────●───
           \              / \        / \              /
            \   release/1.0.0  hotfix/1.0.1  release/2.0.0
             \          /       \  /           \    /
develop ──────●────●───●─────────●──────●───●───●──
               \  /                      \  /
          feature/*                 feature/*
```

### Branch Types

| Branch        | Purpose                                | Merges Into        |
|---------------|----------------------------------------|--------------------|
| `main`        | Production-ready releases (tagged)     | —                  |
| `develop`     | Integration branch for next release    | —                  |
| `feature/*`   | New features                           | `develop`          |
| `release/*`   | Release stabilization & version bumps  | `main` + `develop` |
| `hotfix/*`    | Urgent production fixes                | `main` + `develop` |

### Merge Strategy

- **feature → develop**: `--no-ff` (preserve feature history)
- **release → main**: `--no-ff` (explicit merge commit)
- **release → develop**: `--no-ff`
- **hotfix → main**: `--no-ff`
- **hotfix → develop**: `--no-ff`

## Quick Start

```bash
pip install -e .
seasons --help
seasons info spring
seasons all
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
```

## Versioning

This project uses [Semantic Versioning](https://semver.org/).
See `seasons/__version__.py` for the current version.
READMEEOF

# --- Project skeleton ---
mkdir -p seasons tests

cat > seasons/__init__.py << 'EOF'
"""Seasons — a CLI tool for seasonal information."""
from seasons.__version__ import __version__

__all__ = ["__version__"]
EOF

cat > seasons/__version__.py << 'EOF'
__version__ = "0.1.0-dev"
EOF

cat > seasons/cli.py << 'EOF'
"""Command-line interface for Seasons."""
import argparse
import sys

from seasons.__version__ import __version__


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "all":
        print("Available seasons: (none registered yet)")
        return 0

    if args.command == "info":
        print(f"No data available for '{args.name}'.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF

cat > seasons/registry.py << 'EOF'
"""Central registry for season data."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SeasonInfo:
    name: str
    months: tuple[str, ...]
    avg_temp_c: float
    description: str
    activities: tuple[str, ...] = field(default_factory=tuple)


_REGISTRY: dict[str, SeasonInfo] = {}


def register(info: SeasonInfo) -> None:
    """Register a season in the global registry."""
    key = info.name.lower()
    if key in _REGISTRY:
        raise ValueError(f"Season '{key}' is already registered.")
    _REGISTRY[key] = info


def get(name: str) -> SeasonInfo | None:
    """Retrieve season info by name (case-insensitive)."""
    return _REGISTRY.get(name.lower())


def all_seasons() -> list[SeasonInfo]:
    """Return all registered seasons, sorted alphabetically."""
    return sorted(_REGISTRY.values(), key=lambda s: s.name)
EOF

# --- Tests ---
cat > tests/__init__.py << 'EOF'
EOF

cat > tests/test_registry.py << 'EOF'
"""Tests for the season registry."""
import pytest
from seasons.registry import SeasonInfo, register, get, all_seasons, _REGISTRY


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure each test starts with a clean registry."""
    _REGISTRY.clear()
    yield
    _REGISTRY.clear()


def test_register_and_get():
    info = SeasonInfo(
        name="Test",
        months=("Jan",),
        avg_temp_c=0.0,
        description="A test season.",
    )
    register(info)
    assert get("test") is info
    assert get("TEST") is info


def test_duplicate_register_raises():
    info = SeasonInfo(name="Dup", months=(), avg_temp_c=0.0, description="x")
    register(info)
    with pytest.raises(ValueError, match="already registered"):
        register(info)


def test_get_missing_returns_none():
    assert get("nonexistent") is None


def test_all_seasons_sorted():
    for name in ("Zeta", "Alpha", "Mid"):
        register(SeasonInfo(name=name, months=(), avg_temp_c=0.0, description="x"))
    names = [s.name for s in all_seasons()]
    assert names == ["Alpha", "Mid", "Zeta"]
EOF

cat > tests/test_cli.py << 'EOF'
"""Tests for the CLI module."""
from seasons.cli import main


def test_main_no_args(capsys):
    ret = main([])
    assert ret == 0


def test_main_all(capsys):
    ret = main(["all"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "seasons" in captured.out.lower()


def test_main_info_missing(capsys):
    ret = main(["info", "spring"])
    assert ret == 1
EOF

# --- pyproject.toml ---
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "seasons"
dynamic = ["version"]
description = "CLI tool for seasonal information — Git Flow demo"
requires-python = ">=3.11"
license = {text = "MIT"}
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=7.4", "pytest-cov>=4.1"]

[project.scripts]
seasons = "seasons.cli:main"

[tool.setuptools.dynamic]
version = {attr = "seasons.__version__.__version__"}

[tool.pytest.ini_options]
testpaths = ["tests"]
EOF

# --- LICENSE ---
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Seasons Demo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

commit "chore: initial project scaffold with CLI, registry, and tests"

# ═══════════════════════════════════════════════════════════════════════
# PHASE 1 — Create develop branch
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 1: Create develop branch"
git checkout -b develop

# ═══════════════════════════════════════════════════════════════════════
# PHASE 2 — Feature: Spring Module
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 2a: feature/spring-module"
git checkout -b feature/spring-module develop

cat > seasons/spring.py << 'EOF'
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
EOF

cat > tests/test_spring.py << 'EOF'
"""Tests for the spring module."""
from seasons.registry import get, _REGISTRY
from seasons.spring import SPRING, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_spring_data():
    assert SPRING.name == "Spring"
    assert len(SPRING.months) == 3
    assert SPRING.avg_temp_c == 15.0
    assert len(SPRING.activities) > 0


def test_spring_init_registers():
    init()
    assert get("spring") is SPRING
EOF

commit "feat(spring): add spring season module with data and tests"

# Second commit on spring feature: wire into CLI
cat > seasons/__init__.py << 'EOF'
"""Seasons — a CLI tool for seasonal information."""
from seasons.__version__ import __version__
from seasons import spring

spring.init()

__all__ = ["__version__"]
EOF

# Update CLI to use registry
cat > seasons/cli.py << 'EOF'
"""Command-line interface for Seasons."""
import argparse
import sys

from seasons.__version__ import __version__
from seasons import registry


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
        return 0

    if args.command == "info":
        info = registry.get(args.name)
        if info is None:
            print(f"Unknown season: '{args.name}'", file=sys.stderr)
            return 1
        print(_format_season(info))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF

# Update CLI tests
cat > tests/test_cli.py << 'EOF'
"""Tests for the CLI module."""
from seasons.cli import main


def test_main_no_args(capsys):
    ret = main([])
    assert ret == 0


def test_main_all(capsys):
    ret = main(["all"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "Spring" in captured.out


def test_main_info_spring(capsys):
    ret = main(["info", "spring"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "Spring" in captured.out
    assert "March" in captured.out


def test_main_info_unknown(capsys):
    ret = main(["info", "nonexistent"])
    assert ret == 1
EOF

commit "feat(spring): wire spring module into CLI and registry"

# ═══════════════════════════════════════════════════════════════════════
# PHASE 2b — Feature: Summer Module (created in parallel from develop)
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 2b: feature/summer-module"
git checkout -b feature/summer-module develop

cat > seasons/summer.py << 'EOF'
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
EOF

cat > tests/test_summer.py << 'EOF'
"""Tests for the summer module."""
from seasons.registry import get, _REGISTRY
from seasons.summer import SUMMER, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_summer_data():
    assert SUMMER.name == "Summer"
    assert SUMMER.months == ("June", "July", "August")
    assert SUMMER.avg_temp_c == 28.0
    assert "Swimming" in SUMMER.activities


def test_summer_init_registers():
    init()
    assert get("summer") is SUMMER
EOF

commit "feat(summer): add summer season module with data and tests"

# ═══════════════════════════════════════════════════════════════════════
# PHASE 2c — Merge features into develop (--no-ff)
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 2c: Merge features into develop"
git checkout develop

# Merge spring first
git merge --no-ff feature/spring-module -m "merge: feature/spring-module into develop"

# Merge summer (will need integration)
git merge --no-ff feature/summer-module -m "merge: feature/summer-module into develop"

# Integration commit: wire summer into __init__
cat > seasons/__init__.py << 'EOF'
"""Seasons — a CLI tool for seasonal information."""
from seasons.__version__ import __version__
from seasons import spring, summer

spring.init()
summer.init()

__all__ = ["__version__"]
EOF

commit "chore: integrate summer module into package init"

# Clean up feature branches
git branch -d feature/spring-module
git branch -d feature/summer-module

# ═══════════════════════════════════════════════════════════════════════
# PHASE 3 — Release 1.0.0
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 3: release/1.0.0"
git checkout -b release/1.0.0 develop

# Bump version
cat > seasons/__version__.py << 'EOF'
__version__ = "1.0.0"
EOF

commit "chore(release): bump version to 1.0.0"

# Add CHANGELOG
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] — 2026-02-13

### Added
- Spring season module with month, temperature, and activity data.
- Summer season module with month, temperature, and activity data.
- Central season registry with register/get/all_seasons API.
- CLI with `seasons all` and `seasons info <name>` commands.
- Full test suite for registry, CLI, spring, and summer modules.
EOF

commit "docs(release): add CHANGELOG for v1.0.0"

# Merge release into main
git checkout main
git merge --no-ff release/1.0.0 -m "release: merge release/1.0.0 into main"
git tag -a v1.0.0 -m "Release v1.0.0 — Spring & Summer seasons"

# Back-merge into develop
git checkout develop
git merge --no-ff release/1.0.0 -m "release: back-merge release/1.0.0 into develop"

# Bump develop to next dev version
cat > seasons/__version__.py << 'EOF'
__version__ = "1.1.0-dev"
EOF

commit "chore: bump develop to 1.1.0-dev"

git branch -d release/1.0.0

# ═══════════════════════════════════════════════════════════════════════
# PHASE 4 — Hotfix 1.0.1 (fix a bug in registry)
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 4: hotfix/1.0.1"
git checkout -b hotfix/1.0.1 main

# Fix: registry.get() should strip whitespace (simulated production bug)
cat > seasons/registry.py << 'EOF'
"""Central registry for season data."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SeasonInfo:
    name: str
    months: tuple[str, ...]
    avg_temp_c: float
    description: str
    activities: tuple[str, ...] = field(default_factory=tuple)


_REGISTRY: dict[str, SeasonInfo] = {}


def register(info: SeasonInfo) -> None:
    """Register a season in the global registry."""
    key = info.name.strip().lower()
    if key in _REGISTRY:
        raise ValueError(f"Season '{key}' is already registered.")
    _REGISTRY[key] = info


def get(name: str) -> SeasonInfo | None:
    """Retrieve season info by name (case-insensitive, whitespace-tolerant)."""
    return _REGISTRY.get(name.strip().lower())


def all_seasons() -> list[SeasonInfo]:
    """Return all registered seasons, sorted alphabetically."""
    return sorted(_REGISTRY.values(), key=lambda s: s.name)
EOF

# Add regression test
cat > tests/test_hotfix_whitespace.py << 'EOF'
"""Regression test for whitespace-tolerant season lookup (hotfix/1.0.1)."""
from seasons.registry import SeasonInfo, register, get, _REGISTRY


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_get_strips_whitespace():
    info = SeasonInfo(name="Spring", months=(), avg_temp_c=0.0, description="x")
    register(info)
    assert get("  spring  ") is info
    assert get("Spring ") is info
    assert get(" SPRING") is info


def test_register_strips_whitespace():
    info = SeasonInfo(name=" Padded ", months=(), avg_temp_c=0.0, description="x")
    register(info)
    assert get("padded") is info
EOF

commit "fix(registry): strip whitespace in register() and get() lookups"

# Bump patch version
cat > seasons/__version__.py << 'EOF'
__version__ = "1.0.1"
EOF

commit "chore(hotfix): bump version to 1.0.1"

# Merge hotfix into main
git checkout main
git merge --no-ff hotfix/1.0.1 -m "hotfix: merge hotfix/1.0.1 into main"
git tag -a v1.0.1 -m "Hotfix v1.0.1 — whitespace-tolerant season lookup"

# Merge hotfix into develop
git checkout develop
git merge --no-ff hotfix/1.0.1 -m "hotfix: back-merge hotfix/1.0.1 into develop"

# Resolve version on develop (keep dev version)
cat > seasons/__version__.py << 'EOF'
__version__ = "1.1.0-dev"
EOF

commit "chore: restore develop version after hotfix merge"

git branch -d hotfix/1.0.1

# ═══════════════════════════════════════════════════════════════════════
# PHASE 5 — Feature: Autumn Module
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 5a: feature/autumn-module"
git checkout -b feature/autumn-module develop

cat > seasons/autumn.py << 'EOF'
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
EOF

cat > tests/test_autumn.py << 'EOF'
"""Tests for the autumn module."""
from seasons.registry import get, _REGISTRY
from seasons.autumn import AUTUMN, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_autumn_data():
    assert AUTUMN.name == "Autumn"
    assert AUTUMN.months == ("September", "October", "November")
    assert AUTUMN.avg_temp_c == 12.0
    assert "Leaf peeping" in AUTUMN.activities


def test_autumn_init_registers():
    init()
    assert get("autumn") is AUTUMN
EOF

commit "feat(autumn): add autumn season module with data and tests"

# ═══════════════════════════════════════════════════════════════════════
# PHASE 5b — Feature: Winter Module
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 5b: feature/winter-module"
git checkout -b feature/winter-module develop

cat > seasons/winter.py << 'EOF'
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
EOF

cat > tests/test_winter.py << 'EOF'
"""Tests for the winter module."""
from seasons.registry import get, _REGISTRY
from seasons.winter import WINTER, init


def setup_function():
    _REGISTRY.clear()


def teardown_function():
    _REGISTRY.clear()


def test_winter_data():
    assert WINTER.name == "Winter"
    assert WINTER.months == ("December", "January", "February")
    assert WINTER.avg_temp_c == -2.0
    assert "Skiing" in WINTER.activities


def test_winter_init_registers():
    init()
    assert get("winter") is WINTER
EOF

commit "feat(winter): add winter season module with data and tests"

# ═══════════════════════════════════════════════════════════════════════
# PHASE 5c — Merge autumn & winter into develop
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 5c: Merge autumn and winter into develop"
git checkout develop

git merge --no-ff feature/autumn-module -m "merge: feature/autumn-module into develop"
git merge --no-ff feature/winter-module -m "merge: feature/winter-module into develop"

# Integration: wire all four seasons
cat > seasons/__init__.py << 'EOF'
"""Seasons — a CLI tool for seasonal information."""
from seasons.__version__ import __version__
from seasons import spring, summer, autumn, winter

spring.init()
summer.init()
autumn.init()
winter.init()

__all__ = ["__version__"]
EOF

# Add a summary command to the CLI
cat > seasons/cli.py << 'EOF'
"""Command-line interface for Seasons."""
import argparse
import sys

from seasons.__version__ import __version__
from seasons import registry


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

    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF

# Update CLI tests for all four seasons + summary
cat > tests/test_cli.py << 'EOF'
"""Tests for the CLI module."""
from seasons.cli import main


def test_main_no_args(capsys):
    ret = main([])
    assert ret == 0


def test_main_all(capsys):
    ret = main(["all"])
    captured = capsys.readouterr()
    assert ret == 0
    for name in ("Spring", "Summer", "Autumn", "Winter"):
        assert name in captured.out


def test_main_info_each_season(capsys):
    for name in ("spring", "summer", "autumn", "winter"):
        ret = main(["info", name])
        assert ret == 0


def test_main_info_unknown(capsys):
    ret = main(["info", "nonexistent"])
    assert ret == 1


def test_main_summary(capsys):
    ret = main(["summary"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "Season" in captured.out
    assert "Spring" in captured.out
EOF

commit "chore: integrate all four seasons and add summary CLI command"

git branch -d feature/autumn-module
git branch -d feature/winter-module

# ═══════════════════════════════════════════════════════════════════════
# PHASE 6 — Release 2.0.0
# ═══════════════════════════════════════════════════════════════════════
echo "▸ Phase 6: release/2.0.0"
git checkout -b release/2.0.0 develop

cat > seasons/__version__.py << 'EOF'
__version__ = "2.0.0"
EOF

commit "chore(release): bump version to 2.0.0"

# Update CHANGELOG
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] — 2026-02-13

### Added
- Autumn season module with month, temperature, and activity data.
- Winter season module with month, temperature, and activity data.
- `seasons summary` command for compact tabular output.

### Changed
- CLI `seasons all` now prints a blank line between seasons for readability.

## [1.0.1] — 2026-02-13

### Fixed
- Registry `get()` and `register()` now strip leading/trailing whitespace.

## [1.0.0] — 2026-02-13

### Added
- Spring season module with month, temperature, and activity data.
- Summer season module with month, temperature, and activity data.
- Central season registry with register/get/all_seasons API.
- CLI with `seasons all` and `seasons info <name>` commands.
- Full test suite for registry, CLI, spring, and summer modules.
EOF

commit "docs(release): update CHANGELOG for v2.0.0"

# Update README for v2
cat >> README.md << 'EOF'

## Release History

| Version | Date       | Highlights                        |
|---------|------------|-----------------------------------|
| 2.0.0   | 2026-02-13 | All four seasons, summary command |
| 1.0.1   | 2026-02-13 | Whitespace-tolerant lookups       |
| 1.0.0   | 2026-02-13 | Spring & Summer, initial release  |
EOF

commit "docs(release): update README with release history table"

# Merge release into main
git checkout main
git merge --no-ff release/2.0.0 -m "release: merge release/2.0.0 into main"
git tag -a v2.0.0 -m "Release v2.0.0 — All four seasons complete"

# Back-merge into develop
git checkout develop
git merge --no-ff release/2.0.0 -m "release: back-merge release/2.0.0 into develop"

cat > seasons/__version__.py << 'EOF'
__version__ = "2.1.0-dev"
EOF

commit "chore: bump develop to 2.1.0-dev"

git branch -d release/2.0.0

# ═══════════════════════════════════════════════════════════════════════
# Done — switch to develop as the default working branch
# ═══════════════════════════════════════════════════════════════════════
git checkout develop

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Git Flow demo repo built successfully!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Branches:"
git branch -a
echo ""
echo "Tags:"
git tag -l
echo ""
echo "Log (graph):"
git log --oneline --graph --all --decorate -25
echo ""
echo "Done."
