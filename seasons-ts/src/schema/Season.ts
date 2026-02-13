/**
 * Season Schema — @effect/schema domain models.
 *
 * Single source of truth for the Season type: runtime validation,
 * encoding/decoding, and TypeScript type inference all derived from
 * one schema definition. No more dataclass + manual validation drift.
 */
import { Schema } from "@effect/schema";

// ── Branded Types ────────────────────────────────────────────────────

export const SeasonName = Schema.String.pipe(
  Schema.trimmed(),
  Schema.nonEmptyString(),
  Schema.brand("SeasonName")
);
export type SeasonName = typeof SeasonName.Type;

export const Month = Schema.Literal(
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
);
export type Month = typeof Month.Type;

export const Celsius = Schema.Number.pipe(
  Schema.greaterThanOrEqualTo(-90),
  Schema.lessThanOrEqualTo(60),
  Schema.brand("Celsius")
);
export type Celsius = typeof Celsius.Type;

export const UVIndex = Schema.Int.pipe(
  Schema.greaterThanOrEqualTo(0),
  Schema.lessThanOrEqualTo(11),
  Schema.brand("UVIndex")
);
export type UVIndex = typeof UVIndex.Type;

export const Percentage = Schema.Number.pipe(
  Schema.greaterThanOrEqualTo(0),
  Schema.lessThanOrEqualTo(100),
  Schema.brand("Percentage")
);
export type Percentage = typeof Percentage.Type;

// ── Season Schema ────────────────────────────────────────────────────

export class Season extends Schema.Class<Season>("Season")({
  name: SeasonName,
  months: Schema.NonEmptyArray(Month),
  avgTempC: Celsius,
  description: Schema.String,
  activities: Schema.Array(Schema.String).pipe(Schema.withDefault(() => [])),
}) {}

// ── Weather Profile Schema ───────────────────────────────────────────

export class WeatherProfile extends Schema.Class<WeatherProfile>("WeatherProfile")({
  season: SeasonName,
  avgHighC: Celsius,
  avgLowC: Celsius,
  humidityPct: Percentage,
  conditions: Schema.String,
  uvIndex: UVIndex,
}) {}

// ── Typed Errors ─────────────────────────────────────────────────────

export class SeasonNotFoundError extends Schema.TaggedError<SeasonNotFoundError>()(
  "SeasonNotFoundError",
  {
    name: Schema.String,
    message: Schema.String,
  }
) {}

export class SeasonAlreadyExistsError extends Schema.TaggedError<SeasonAlreadyExistsError>()(
  "SeasonAlreadyExistsError",
  {
    name: Schema.String,
    message: Schema.String,
  }
) {}

export class ValidationError extends Schema.TaggedError<ValidationError>()(
  "ValidationError",
  {
    field: Schema.String,
    message: Schema.String,
  }
) {}

// ── Seed Data ────────────────────────────────────────────────────────

export const SEED_SEASONS = [
  {
    name: "Spring",
    months: ["March", "April", "May"],
    avgTempC: 15.0,
    description:
      "Spring marks the transition from winter to summer. " +
      "Days grow longer, temperatures rise, and flora begins to bloom.",
    activities: ["Hiking", "Gardening", "Bird watching", "Cycling", "Picnicking"],
  },
  {
    name: "Summer",
    months: ["June", "July", "August"],
    avgTempC: 28.0,
    description:
      "Summer is the warmest season, characterized by long days, " +
      "high temperatures, and abundant sunshine.",
    activities: ["Swimming", "Surfing", "Camping", "Barbecuing", "Traveling"],
  },
  {
    name: "Autumn",
    months: ["September", "October", "November"],
    avgTempC: 12.0,
    description:
      "Autumn is the transitional season between summer and winter. " +
      "Leaves change color, temperatures cool, and harvests are gathered.",
    activities: ["Leaf peeping", "Apple picking", "Hiking", "Pumpkin carving", "Bonfires"],
  },
  {
    name: "Winter",
    months: ["December", "January", "February"],
    avgTempC: -2.0,
    description:
      "Winter is the coldest season, marked by short days, low temperatures, " +
      "and often snow or ice.",
    activities: ["Skiing", "Snowboarding", "Ice skating", "Sledding"],
  },
] as const;
