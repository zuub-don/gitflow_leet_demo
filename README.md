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

## Release History

| Version | Date       | Highlights                                          |
|---------|------------|-----------------------------------------------------|
| 3.0.0   | 2026-02-13 | Weather, Compare, Impact Analyzer — survived chaos  |
| 2.0.2   | 2026-02-13 | Emergency hotfix: registry input validation         |
| 2.0.0   | 2026-02-13 | All four seasons, summary command                   |
| 1.0.1   | 2026-02-13 | Whitespace-tolerant lookups                         |
| 1.0.0   | 2026-02-13 | Spring & Summer, initial release                    |

## Real-World Chaos Scenarios

This repo's git history demonstrates how Git Flow handles real-world failures.
Run `git log --oneline --graph --all --decorate` to see the full story.

### 1. Buggy Feature → Revert → Proper Fix

`feature/weather-api` was merged to `develop` without CI passing (reviewer on PTO).
The module hit a non-existent API with `timeout=0`. Immediately **reverted** on develop.
Then `feature/weather-api-v2` rewrote it with offline profiles and proper tests.

**Git evidence:** Look for the `Revert "merge: feature/weather-api"` commit on develop.

### 2. Conflicting Features on the Same File

`feature/compare-command` added a new CLI subcommand while `feature/refactor-output`
rewrote the output formatting — both modifying `seasons/cli.py`. Merged sequentially
with conflict resolution required on the second merge.

### 3. Release Candidate Iteration (RC1 → RC2)

`release/3.0.0` started at `3.0.0-rc1`. QA found two bugs:
- `seasons compare spring spring` produced nonsensical output (self-comparison)
- Long activity strings broke the box-drawing layout

Both fixed directly on the release branch, then bumped to `3.0.0-rc2`.

### 4. Emergency Hotfix During Active Release

While `release/3.0.0` was in QA, production broke: the registry accepted
seasons with empty names, crashing the CLI formatter.

- `hotfix/2.0.2` branched from `main`, fixed & tagged `v2.0.2`
- The fix was **cherry-picked** into the active `release/3.0.0` branch
- The hotfix was also **back-merged** into `develop` (with version conflict resolution)

**This is the hardest Git Flow scenario** — three branches receiving the same fix
through different mechanisms (merge, cherry-pick, merge).

### 5. Accidental Commit to Main

Someone pushed `seasons/experimental.py` directly to `main` — no branch, no PR,
no review, and it contained a `42 / 0` division-by-zero bug.
**Immediately reverted** in the next commit.

**Git evidence:** Two consecutive commits on `main` — the accident and its revert.

## Change Impact Analyzer

See [`tools/README.md`](tools/README.md) for the full documentation on the
programmatic change impact scoring system, pre-commit hook, and GitHub Action.
