/**
 * Tests for the SeasonRegistry Effect Service.
 *
 * Demonstrates testing Effect services by providing Layers
 * and running effects with Effect.runPromise.
 */
import { describe, it, expect } from "vitest";
import { Effect, Layer, Exit } from "effect";
import {
  SeasonRegistryTag,
  RegistryLive,
  makeSeededRegistry,
  SeasonNotFoundError,
  SeasonAlreadyExistsError,
  RegistryValidationError,
} from "../src/services/Registry.js";

const testSeason = {
  name: "Spring",
  months: ["March", "April", "May"] as const,
  avgTempC: 15.0,
  description: "A lovely season",
  activities: ["Hiking", "Gardening"] as const,
};

const allSeasons = [
  testSeason,
  {
    name: "Summer",
    months: ["June", "July", "August"] as const,
    avgTempC: 28.0,
    description: "Hot",
    activities: ["Swimming"] as const,
  },
  {
    name: "Autumn",
    months: ["September", "October", "November"] as const,
    avgTempC: 12.0,
    description: "Cool",
    activities: ["Leaf peeping"] as const,
  },
  {
    name: "Winter",
    months: ["December", "January", "February"] as const,
    avgTempC: -2.0,
    description: "Cold",
    activities: ["Skiing"] as const,
  },
];

// Helper: run an effect against the live (empty) registry
const runWithEmptyRegistry = <A, E>(
  effect: Effect.Effect<A, E, typeof SeasonRegistryTag.Service>
) =>
  Effect.runPromise(
    effect.pipe(Effect.provide(RegistryLive))
  );

// Helper: run against a seeded registry
const runWithSeeded = <A, E>(
  effect: Effect.Effect<A, E, typeof SeasonRegistryTag.Service>
) =>
  Effect.runPromise(
    effect.pipe(Effect.provide(makeSeededRegistry(allSeasons)))
  );

// ── Register ─────────────────────────────────────────────────────────

describe("SeasonRegistry.register", () => {
  it("registers a valid season", async () => {
    await runWithEmptyRegistry(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        yield* registry.register(testSeason);
        const count = yield* registry.count();
        expect(count).toBe(1);
      })
    );
  });

  it("rejects duplicate registration", async () => {
    const exit = await Effect.runPromiseExit(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        yield* registry.register(testSeason);
        yield* registry.register(testSeason); // duplicate
      }).pipe(Effect.provide(RegistryLive))
    );

    expect(Exit.isFailure(exit)).toBe(true);
  });

  it("rejects empty name", async () => {
    const exit = await Effect.runPromiseExit(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        yield* registry.register({ ...testSeason, name: "" });
      }).pipe(Effect.provide(RegistryLive))
    );

    expect(Exit.isFailure(exit)).toBe(true);
  });

  it("rejects empty months", async () => {
    const exit = await Effect.runPromiseExit(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        yield* registry.register({ ...testSeason, months: [] });
      }).pipe(Effect.provide(RegistryLive))
    );

    expect(Exit.isFailure(exit)).toBe(true);
  });
});

// ── Get ──────────────────────────────────────────────────────────────

describe("SeasonRegistry.get", () => {
  it("retrieves a registered season", async () => {
    await runWithSeeded(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        const spring = yield* registry.get("spring");
        expect(spring.name).toBe("Spring");
      })
    );
  });

  it("is case-insensitive", async () => {
    await runWithSeeded(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        const s1 = yield* registry.get("SPRING");
        const s2 = yield* registry.get("spring");
        expect(s1.name).toBe(s2.name);
      })
    );
  });

  it("fails with SeasonNotFoundError for unknown season", async () => {
    const exit = await Effect.runPromiseExit(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        yield* registry.get("narnia");
      }).pipe(Effect.provide(RegistryLive))
    );

    expect(Exit.isFailure(exit)).toBe(true);
  });
});

// ── GetAll ────────────────────────────────────────────────────────────

describe("SeasonRegistry.getAll", () => {
  it("returns all seasons sorted alphabetically", async () => {
    await runWithSeeded(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        const all = yield* registry.getAll();
        const names = all.map((s) => s.name);
        expect(names).toEqual(["Autumn", "Spring", "Summer", "Winter"]);
      })
    );
  });

  it("returns empty array when registry is empty", async () => {
    await runWithEmptyRegistry(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        const all = yield* registry.getAll();
        expect(all).toHaveLength(0);
      })
    );
  });
});

// ── Remove ───────────────────────────────────────────────────────────

describe("SeasonRegistry.remove", () => {
  it("removes an existing season", async () => {
    await runWithSeeded(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        const removed = yield* registry.remove("spring");
        expect(removed).toBe(true);
        const count = yield* registry.count();
        expect(count).toBe(3);
      })
    );
  });

  it("returns false for non-existent season", async () => {
    await runWithEmptyRegistry(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        const removed = yield* registry.remove("narnia");
        expect(removed).toBe(false);
      })
    );
  });
});

// ── Seeded Layer ─────────────────────────────────────────────────────

describe("makeSeededRegistry", () => {
  it("pre-populates with all provided seasons", async () => {
    await runWithSeeded(
      Effect.gen(function* () {
        const registry = yield* SeasonRegistryTag;
        const count = yield* registry.count();
        expect(count).toBe(4);
      })
    );
  });
});
