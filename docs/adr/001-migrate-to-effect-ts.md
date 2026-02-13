# ADR-001: Migrate to Effect-TS

**Status:** Accepted
**Date:** 2026-02-13
**Deciders:** New VP Engineering, Staff Engineer, Tech Lead
**Supersedes:** Original Python implementation

## Context

New technical leadership has evaluated the current Python-based Seasons CLI and
determined that the project should migrate to TypeScript using the
[Effect](https://effect.website/) ecosystem. The rationale:

1. **Type-safe error handling** — Effect's typed error channel eliminates the
   class of bugs where errors are silently swallowed or untyped exceptions
   propagate unpredictably (see: the `weather-api` v1 incident).

2. **Schema-first design** — `@effect/schema` provides runtime validation,
   encoding/decoding, and automatic type inference from a single source of
   truth. No more `dataclass` + manual validation divergence (see: the
   `hotfix/2.0.2` registry validation incident).

3. **Structured concurrency** — Effect Fibers provide cancellation, timeouts,
   and resource safety by default. Future API integrations won't repeat the
   `timeout=0` disaster.

4. **Dependency injection via Layers** — Services and Layers replace the global
   `_REGISTRY` dict with a composable, testable dependency graph.

5. **Modern CLI tooling** — `@effect/cli` provides type-safe argument parsing
   with automatic help generation and shell completions.

## Decision

We will introduce a TypeScript/Effect rewrite **alongside** the existing Python
code. This is a coexistence strategy, not a big-bang replacement.

### Architecture

```
seasons-ts/
├── src/
│   ├── schema/          # @effect/schema domain models
│   │   └── Season.ts    # Season schema with encode/decode
│   ├── services/        # Effect Services + Layers
│   │   ├── Registry.ts  # SeasonRegistry service
│   │   └── Weather.ts   # WeatherService (replaces offline profiles)
│   ├── cli/             # @effect/cli commands
│   │   ├── index.ts     # Root command
│   │   ├── info.ts      # seasons info <name>
│   │   ├── compare.ts   # seasons compare <a> <b>
│   │   └── weather.ts   # seasons weather <name>
│   └── main.ts          # Entry point
├── test/
│   ├── Schema.test.ts
│   ├── Registry.test.ts
│   └── Cli.test.ts
├── package.json
├── tsconfig.json
└── vitest.config.ts
```

### Technology Stack

| Concern            | Choice                    | Why                                    |
|--------------------|---------------------------|----------------------------------------|
| Language           | TypeScript 5.x            | Type safety, ecosystem                 |
| Runtime            | Node.js 22+ LTS           | Stable, Effect-optimized               |
| Core framework     | `effect` 3.x              | Typed errors, structured concurrency   |
| Schema/validation  | `@effect/schema`          | Single source of truth for types       |
| CLI framework      | `@effect/cli`             | Type-safe args, auto help/completions  |
| HTTP (future)      | `@effect/platform`        | Unified platform layer                 |
| Test runner        | `vitest`                  | Fast, ESM-native, good DX             |
| Build              | `tsup` or `tsx`           | Fast builds, ESM output                |
| Lint               | `eslint` + `@effect/eslint-plugin` | Effect-aware linting          |
| Package manager    | `pnpm`                    | Fast, strict, workspace-ready          |

### Migration Strategy

1. **Phase 1 (this ADR):** Document the decision. Get buy-in.
2. **Phase 2:** Scaffold the TypeScript project in `seasons-ts/`.
3. **Phase 3:** Rewrite domain models with `@effect/schema`, services with
   Effect Layers. Each in its own feature branch.
4. **Phase 4:** Rewrite CLI with `@effect/cli`.
5. **Phase 5:** Integration tests, CI pipeline for TS, update README.
6. **Phase 6 (future):** Deprecate Python implementation, promote TS as primary.

### Git Flow Plan

Each phase gets its own `feature/*` branch off `develop`:

```
feature/effects-rfc        → ADR (this document)
feature/effects-scaffold   → Project setup
feature/effects-schema     → Domain models
feature/effects-services   → Registry + Weather services
feature/effects-cli        → CLI rewrite
```

All merge to `develop` via `--no-ff`. Release as `4.0.0` (major: new runtime).

## Consequences

### Positive
- Type-safe error handling eliminates entire class of production incidents
- Schema-first design prevents validation drift
- Effect's composability makes testing trivial (swap Layers in tests)
- Modern DX: fast builds, hot reload, shell completions

### Negative
- Team needs to learn Effect (steep learning curve)
- Dual-stack maintenance during transition period
- Node.js runtime dependency added alongside Python
- Risk of "rewrite fatigue" if migration stalls

### Risks
- **Learning curve:** Effect's functional paradigm is unfamiliar to most TS devs.
  Mitigated by pairing sessions and incremental adoption.
- **Scope creep:** "While we're rewriting, let's also..." — strictly scope to
  feature parity with Python version first.
- **Stale Python code:** During coexistence, bugs must be fixed in both stacks.
  Mitigated by keeping Python as primary until TS reaches parity.

## References

- [Effect Documentation](https://effect.website/docs/getting-started)
- [Effect GitHub](https://github.com/Effect-TS/effect)
- [ADR template](https://adr.github.io/)
- Internal incidents: hotfix/2.0.2, weather-api revert
