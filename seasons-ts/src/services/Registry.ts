/**
 * SeasonRegistry — Effect Service with Layer-based dependency injection.
 *
 * Replaces the Python global `_REGISTRY` dict with a composable,
 * testable Effect Service. The registry is backed by a Ref (mutable
 * reference) managed within the Effect runtime.
 *
 * Key patterns demonstrated:
 * - Effect.Service for interface definition
 * - Layer for production vs test implementations
 * - Ref for managed mutable state
 * - Typed errors in the error channel
 */
import { Effect, Context, Layer, Ref, HashMap, Array as Arr, Option, pipe } from "effect";
import { Schema } from "@effect/schema";

// ── Import domain types (will be available after schema branch merges) ──
// For now we define inline minimal types; these will be replaced by the
// schema imports after integration.

interface SeasonData {
  readonly name: string;
  readonly months: readonly string[];
  readonly avgTempC: number;
  readonly description: string;
  readonly activities: readonly string[];
}

// ── Typed Errors ─────────────────────────────────────────────────────

export class SeasonNotFoundError {
  readonly _tag = "SeasonNotFoundError" as const;
  constructor(readonly name: string) {}
  get message() {
    return `Season '${this.name}' not found in registry.`;
  }
}

export class SeasonAlreadyExistsError {
  readonly _tag = "SeasonAlreadyExistsError" as const;
  constructor(readonly name: string) {}
  get message() {
    return `Season '${this.name}' is already registered.`;
  }
}

export class RegistryValidationError {
  readonly _tag = "RegistryValidationError" as const;
  constructor(
    readonly field: string,
    readonly message: string
  ) {}
}

// ── Service Interface ────────────────────────────────────────────────

export interface SeasonRegistry {
  readonly register: (
    season: SeasonData
  ) => Effect.Effect<void, SeasonAlreadyExistsError | RegistryValidationError>;

  readonly get: (
    name: string
  ) => Effect.Effect<SeasonData, SeasonNotFoundError>;

  readonly getAll: () => Effect.Effect<readonly SeasonData[]>;

  readonly remove: (
    name: string
  ) => Effect.Effect<boolean>;

  readonly count: () => Effect.Effect<number>;
}

// ── Service Tag ──────────────────────────────────────────────────────

export class SeasonRegistryTag extends Context.Tag("SeasonRegistry")<
  SeasonRegistryTag,
  SeasonRegistry
>() {}

// ── Production Implementation (Ref-backed) ───────────────────────────

const normalize = (name: string): string => name.trim().toLowerCase();

const makeRegistryImpl = Effect.gen(function* () {
  const store = yield* Ref.make(HashMap.empty<string, SeasonData>());

  const register: SeasonRegistry["register"] = (season) =>
    Effect.gen(function* () {
      // Validate
      if (!season.name || !season.name.trim()) {
        return yield* Effect.fail(
          new RegistryValidationError("name", "Season name must not be empty.")
        );
      }
      if (!season.months || season.months.length === 0) {
        return yield* Effect.fail(
          new RegistryValidationError("months", `Season '${season.name}' must have at least one month.`)
        );
      }

      const key = normalize(season.name);
      const current = yield* Ref.get(store);

      if (HashMap.has(current, key)) {
        return yield* Effect.fail(new SeasonAlreadyExistsError(season.name));
      }

      yield* Ref.update(store, HashMap.set(key, season));
    });

  const get: SeasonRegistry["get"] = (name) =>
    Effect.gen(function* () {
      const key = normalize(name);
      const current = yield* Ref.get(store);
      const entry = HashMap.get(current, key);

      return yield* Option.match(entry, {
        onNone: () => Effect.fail(new SeasonNotFoundError(name)),
        onSome: (s) => Effect.succeed(s),
      });
    }).pipe(Effect.flatten);

  const getAll: SeasonRegistry["getAll"] = () =>
    Ref.get(store).pipe(
      Effect.map(HashMap.values),
      Effect.map(Arr.fromIterable),
      Effect.map(Arr.sort((a: SeasonData, b: SeasonData) => a.name.localeCompare(b.name)))
    );

  const remove: SeasonRegistry["remove"] = (name) =>
    Effect.gen(function* () {
      const key = normalize(name);
      const current = yield* Ref.get(store);

      if (!HashMap.has(current, key)) {
        return false;
      }

      yield* Ref.update(store, HashMap.remove(key));
      return true;
    });

  const count: SeasonRegistry["count"] = () =>
    Ref.get(store).pipe(Effect.map(HashMap.size));

  return {
    register,
    get,
    getAll,
    remove,
    count,
  } satisfies SeasonRegistry;
});

// ── Layers ───────────────────────────────────────────────────────────

/** Live registry layer — empty on creation, populate with register(). */
export const RegistryLive = Layer.effect(SeasonRegistryTag, makeRegistryImpl);

/** Seeded registry layer — pre-populated with all 4 seasons. */
export const makeSeededRegistry = (seasons: readonly SeasonData[]) =>
  Layer.effect(
    SeasonRegistryTag,
    Effect.gen(function* () {
      const registry = yield* makeRegistryImpl;
      for (const season of seasons) {
        yield* registry.register(season);
      }
      return registry;
    })
  );
