# Seasons — A Git Flow Showcase

> **This repository exists to demonstrate what a real-world Git Flow history looks like.**
> It contains merges, reverts, cherry-picks, hotfixes during releases, merge conflicts,
> accidental commits, an emergency production fix, a leadership-driven tech stack migration,
> and five tagged releases — all navigable through the git graph.

## See It Visually

**[View the Network Graph →](https://github.com/zuub-don/gitflow_leet_demo/network)**

The GitHub network graph is the best way to explore this repo. You'll see the full branch
topology: feature branches forking from `develop`, release branches bridging to `main`,
hotfixes landing on both, and the messy real-world recovery paths in between.

You can also explore it locally:

```bash
git log --oneline --graph --all --decorate
```

---

## What This Repo Demonstrates

This is a **Seasons CLI** — a small Python application that serves as the vehicle
for a rich, semi-realistic Git Flow history. The code is real and tested (59 passing tests),
but the point is the *git history*, not the application.

### The Timeline

| Tag | What Happened |
|-----|---------------|
| `v1.0.0` | Initial release — Spring & Summer modules, CLI with `info` and `all` commands |
| `v1.0.1` | **Hotfix** — registry lookups crashed on whitespace input |
| `v2.0.0` | All four seasons, `summary` command, full test coverage |
| `v2.0.2` | **Emergency hotfix** — registry accepted empty names, crashed the formatter. Landed *while a release was in progress* |
| `v3.0.0` | Weather profiles, season comparison, change impact analyzer — shipped after surviving 5 chaos incidents |
| `develop` | **Effect-TS migration** in progress — new leadership, new stack, coexisting alongside Python |

---

## Git Flow Model

```
main ─────●─────────────●──────●──────────────●──────────────●───
           \           / \    / \            / \            /
            release/1.0  h/1.0.1 \   h/2.0.2  release/3.0.0
             \        /    \  /   \    \  /     /  /  /   /
develop ──────●──●───●──────●──●───●────●──●───●──●──●───●── → (v4.0.0-dev: Effect-TS)
               \ /              \ / \ /        \ / \ /
           feature/*        feature/* feature/*  effects/*
```

### Branch Rules

| Branch | Purpose | Merges Into |
|--------|---------|-------------|
| `main` | Tagged production releases only | — |
| `develop` | Integration branch; always ahead of `main` | — |
| `feature/*` | One branch per feature or fix | `develop` (via `--no-ff`) |
| `release/*` | Stabilization, RC iteration, version bumps | `main` + `develop` |
| `hotfix/*` | Urgent production fixes from `main` | `main` + `develop` |

Every merge uses `--no-ff` to preserve the branch topology in the graph.

---

## The Chaos Scenarios

These aren't hypothetical. Each one is visible in the git history.

### 1. Buggy Feature → Revert → Proper Fix

`feature/weather-api` merged to `develop` with a broken external API call (`timeout=0`,
non-existent endpoint). Reviewer was on PTO. CI would have caught it.

**Recovery:** `git revert -m 1` on the merge commit, then a new `feature/weather-api-v2`
branch with offline weather profiles and proper tests.

**Find it:** `git log --oneline develop | grep -i revert`

### 2. Conflicting Features on the Same File

Two developers worked on `seasons/cli.py` simultaneously:

- `feature/compare-command` — added a new subcommand
- `feature/refactor-output` — rewrote the output formatting

The second merge required manual conflict resolution.

**Find it:** `git log --oneline --merges develop | grep -i conflict`

### 3. Release Candidate Iteration (RC1 → RC2)

`release/3.0.0` cut at `v3.0.0-rc1`. QA found two bugs:

- Self-comparison (`seasons compare spring spring`) produced nonsensical output
- Long activity strings overflowed the box-drawing layout

Both fixed directly on the release branch. Bumped to `v3.0.0-rc2`.

**Find it:** Look at the commits between `rc1` and `rc2` on the release branch in the network graph.

### 4. Emergency Hotfix During an Active Release

**This is the hardest Git Flow scenario.** While `release/3.0.0` was in QA, production
broke: the registry accepted seasons with empty names, crashing the CLI formatter.

- `hotfix/2.0.2` branched from `main` → fixed → tagged `v2.0.2` → merged back to `main`
- The same fix was **cherry-picked** into the in-flight `release/3.0.0`
- The hotfix was **back-merged** into `develop` (with version conflict resolution)

Three branches received the same fix through three different git mechanisms: merge,
cherry-pick, and merge with conflict resolution.

**Find it:** The `v2.0.2` tag on `main` and the cherry-pick commit on the release branch.

### 5. Accidental Commit Directly to Main

Someone pushed `seasons/experimental.py` (containing `42 / 0`) straight to `main`.
No branch, no PR, no review. **Immediately reverted** in the very next commit.

**Find it:** Two consecutive commits on `main` — the accident and its revert.

---

## The Tech Stack Migration (Effect-TS)

New technical leadership decided to rewrite the application in TypeScript using the
[Effect](https://effect.website/) ecosystem. Rather than a big-bang replacement, the
migration lives **alongside** the Python code in `seasons-ts/`.

This is documented in [ADR-001](docs/adr/001-migrate-to-effect-ts.md) and was introduced
through five sequential feature branches — each merged to `develop` via `--no-ff`:

| Feature Branch | What It Introduced |
|----------------|-------------------|
| `feature/effects-rfc` | Architecture Decision Record |
| `feature/effects-scaffold` | `package.json`, `tsconfig.json`, vitest, tsup |
| `feature/effects-schema` | `@effect/schema` domain models — branded types, typed errors, seed data |
| `feature/effects-services` | Effect Services with Layer DI — Registry (Ref-backed), Weather |
| `feature/effects-cli` | `@effect/cli` commands — `all`, `info`, `summary`, `compare`, `weather` |

### Key Effect Patterns

- **Schema-first** — `SeasonName`, `Month`, `Celsius` as branded types with runtime validation
- **Services + Layers** — composable dependency injection replacing the global `_REGISTRY` dict
- **Typed error channel** — `SeasonNotFoundError | SeasonAlreadyExistsError` in the Effect error type
- **Layer graph** — `SeededRegistry → WeatherLive → AppLayer` composed at the entry point

### Running It

```bash
cd seasons-ts && pnpm install
pnpm test          # vitest
pnpm dev -- all    # run via tsx
```

---

## Running the Python Version

```bash
pip install -e ".[dev]"
seasons --help
seasons info spring
seasons compare spring winter
pytest -v           # 59 tests
```

---

## Change Impact Analyzer

A programmatic scoring system for change risk. See [`tools/README.md`](tools/README.md)
for CLI usage, pre-commit hook integration, and GitHub Action workflow.

---

## Exploring the History

| What to Look At | Command |
|-----------------|---------|
| Full graph | `git log --oneline --graph --all --decorate` |
| Just the merges | `git log --oneline --merges --all` |
| All tags | `git tag -l` |
| Network graph | **[github.com/zuub-don/gitflow_leet_demo/network](https://github.com/zuub-don/gitflow_leet_demo/network)** |
| Hotfix cherry-pick | `git log --oneline --all --grep="cherry-pick"` |
| The revert | `git log --oneline --all --grep="Revert"` |
| Release RC commits | `git log --oneline --all --grep="rc"` |

This project uses [Semantic Versioning](https://semver.org/).
Current version: see `seasons/__version__.py`.
