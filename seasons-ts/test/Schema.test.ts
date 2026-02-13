/**
 * Tests for Season schema definitions.
 *
 * Validates that @effect/schema enforces all domain invariants:
 * - SeasonName must be non-empty and trimmed
 * - Months must be valid calendar months
 * - Temperature must be within physical bounds
 * - Seed data decodes successfully
 */
import { describe, it, expect } from "vitest";
import { Schema } from "@effect/schema";
import { Effect, Either } from "effect";
import {
  Season,
  SeasonName,
  Month,
  Celsius,
  UVIndex,
  Percentage,
  WeatherProfile,
  SeasonNotFoundError,
  SeasonAlreadyExistsError,
  SEED_SEASONS,
} from "../src/schema/Season.js";

// ── SeasonName ───────────────────────────────────────────────────────

describe("SeasonName", () => {
  const decode = Schema.decodeUnknownEither(SeasonName);

  it("accepts valid names", () => {
    expect(Either.isRight(decode("Spring"))).toBe(true);
    expect(Either.isRight(decode("Autumn"))).toBe(true);
  });

  it("rejects empty string", () => {
    expect(Either.isLeft(decode(""))).toBe(true);
  });

  it("rejects whitespace-only string", () => {
    expect(Either.isLeft(decode("   "))).toBe(true);
  });

  it("trims whitespace", () => {
    const result = decode("  Spring  ");
    expect(Either.isRight(result)).toBe(true);
  });
});

// ── Month ────────────────────────────────────────────────────────────

describe("Month", () => {
  const decode = Schema.decodeUnknownEither(Month);

  it("accepts valid months", () => {
    expect(Either.isRight(decode("January"))).toBe(true);
    expect(Either.isRight(decode("December"))).toBe(true);
  });

  it("rejects invalid months", () => {
    expect(Either.isLeft(decode("Smarch"))).toBe(true);
    expect(Either.isLeft(decode(""))).toBe(true);
  });
});

// ── Celsius ──────────────────────────────────────────────────────────

describe("Celsius", () => {
  const decode = Schema.decodeUnknownEither(Celsius);

  it("accepts valid temperatures", () => {
    expect(Either.isRight(decode(15.0))).toBe(true);
    expect(Either.isRight(decode(-2.0))).toBe(true);
    expect(Either.isRight(decode(0))).toBe(true);
  });

  it("rejects impossible temperatures", () => {
    expect(Either.isLeft(decode(-100))).toBe(true); // below -90
    expect(Either.isLeft(decode(70))).toBe(true);   // above 60
  });
});

// ── UVIndex ──────────────────────────────────────────────────────────

describe("UVIndex", () => {
  const decode = Schema.decodeUnknownEither(UVIndex);

  it("accepts valid UV indices", () => {
    expect(Either.isRight(decode(0))).toBe(true);
    expect(Either.isRight(decode(11))).toBe(true);
    expect(Either.isRight(decode(5))).toBe(true);
  });

  it("rejects out-of-range values", () => {
    expect(Either.isLeft(decode(-1))).toBe(true);
    expect(Either.isLeft(decode(12))).toBe(true);
  });
});

// ── Percentage ───────────────────────────────────────────────────────

describe("Percentage", () => {
  const decode = Schema.decodeUnknownEither(Percentage);

  it("accepts 0-100 range", () => {
    expect(Either.isRight(decode(0))).toBe(true);
    expect(Either.isRight(decode(100))).toBe(true);
    expect(Either.isRight(decode(55.5))).toBe(true);
  });

  it("rejects out-of-range", () => {
    expect(Either.isLeft(decode(-1))).toBe(true);
    expect(Either.isLeft(decode(101))).toBe(true);
  });
});

// ── Season (full schema) ─────────────────────────────────────────────

describe("Season", () => {
  const decode = Schema.decodeUnknownEither(Season);

  it("decodes valid season data", () => {
    const result = decode({
      name: "Spring",
      months: ["March", "April", "May"],
      avgTempC: 15.0,
      description: "A lovely season",
      activities: ["Hiking"],
    });
    expect(Either.isRight(result)).toBe(true);
  });

  it("defaults activities to empty array", () => {
    const result = decode({
      name: "Test",
      months: ["January"],
      avgTempC: 0,
      description: "Minimal season",
    });
    expect(Either.isRight(result)).toBe(true);
    if (Either.isRight(result)) {
      expect(result.right.activities).toEqual([]);
    }
  });

  it("rejects season with empty months", () => {
    const result = decode({
      name: "Bad",
      months: [],
      avgTempC: 0,
      description: "No months",
    });
    expect(Either.isLeft(result)).toBe(true);
  });

  it("rejects season with invalid month name", () => {
    const result = decode({
      name: "Bad",
      months: ["Smarch"],
      avgTempC: 0,
      description: "Invalid month",
    });
    expect(Either.isLeft(result)).toBe(true);
  });
});

// ── WeatherProfile ───────────────────────────────────────────────────

describe("WeatherProfile", () => {
  const decode = Schema.decodeUnknownEither(WeatherProfile);

  it("decodes valid weather profile", () => {
    const result = decode({
      season: "Spring",
      avgHighC: 18.0,
      avgLowC: 7.0,
      humidityPct: 65.0,
      conditions: "Partly cloudy",
      uvIndex: 5,
    });
    expect(Either.isRight(result)).toBe(true);
  });

  it("rejects humidity over 100%", () => {
    const result = decode({
      season: "Summer",
      avgHighC: 32.0,
      avgLowC: 20.0,
      humidityPct: 150.0,
      conditions: "Humid",
      uvIndex: 9,
    });
    expect(Either.isLeft(result)).toBe(true);
  });
});

// ── Typed Errors ─────────────────────────────────────────────────────

describe("Typed Errors", () => {
  it("SeasonNotFoundError has correct tag", () => {
    const err = new SeasonNotFoundError({
      name: "Narnia",
      message: "Season 'Narnia' not found",
    });
    expect(err._tag).toBe("SeasonNotFoundError");
    expect(err.name).toBe("Narnia");
  });

  it("SeasonAlreadyExistsError has correct tag", () => {
    const err = new SeasonAlreadyExistsError({
      name: "Spring",
      message: "Already exists",
    });
    expect(err._tag).toBe("SeasonAlreadyExistsError");
  });
});

// ── Seed Data ────────────────────────────────────────────────────────

describe("SEED_SEASONS", () => {
  const decode = Schema.decodeUnknownEither(Season);

  it("all seed seasons decode successfully", () => {
    for (const raw of SEED_SEASONS) {
      const result = decode(raw);
      expect(Either.isRight(result)).toBe(true);
    }
  });

  it("contains exactly 4 seasons", () => {
    expect(SEED_SEASONS).toHaveLength(4);
  });

  it("each season has at least one activity", () => {
    for (const s of SEED_SEASONS) {
      expect(s.activities.length).toBeGreaterThan(0);
    }
  });
});
