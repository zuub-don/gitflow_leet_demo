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

| Version | Date       | Highlights                        |
|---------|------------|-----------------------------------|
| 2.0.0   | 2026-02-13 | All four seasons, summary command |
| 1.0.1   | 2026-02-13 | Whitespace-tolerant lookups       |
| 1.0.0   | 2026-02-13 | Spring & Summer, initial release  |
