/**
 * WeatherService — Effect Service for seasonal weather profiles.
 *
 * Demonstrates:
 * - Effect.Service pattern for external data access
 * - Layer composition (WeatherService depends on SeasonRegistry)
 * - Typed errors propagated through the Effect error channel
 * - Test Layer that returns controlled data
 */
import { Effect, Context, Layer } from "effect";
import {
  SeasonRegistryTag,
  SeasonNotFoundError,
} from "./Registry.js";

// ── Weather Types ────────────────────────────────────────────────────

export interface WeatherData {
  readonly season: string;
  readonly avgHighC: number;
  readonly avgLowC: number;
  readonly humidityPct: number;
  readonly conditions: string;
  readonly uvIndex: number;
}

// ── Service Interface ────────────────────────────────────────────────

export interface WeatherService {
  readonly getWeather: (
    seasonName: string
  ) => Effect.Effect<WeatherData, SeasonNotFoundError>;

  readonly formatWeather: (data: WeatherData) => string;
}

// ── Service Tag ──────────────────────────────────────────────────────

export class WeatherServiceTag extends Context.Tag("WeatherService")<
  WeatherServiceTag,
  WeatherService
>() {}

// ── Static Weather Profiles ──────────────────────────────────────────

const WEATHER_PROFILES: Record<string, Omit<WeatherData, "season">> = {
  spring: {
    avgHighC: 18.0,
    avgLowC: 7.0,
    humidityPct: 65.0,
    conditions: "Partly cloudy with occasional showers",
    uvIndex: 5,
  },
  summer: {
    avgHighC: 32.0,
    avgLowC: 20.0,
    humidityPct: 55.0,
    conditions: "Sunny and hot",
    uvIndex: 9,
  },
  autumn: {
    avgHighC: 14.0,
    avgLowC: 5.0,
    humidityPct: 70.0,
    conditions: "Overcast with morning fog",
    uvIndex: 3,
  },
  winter: {
    avgHighC: 2.0,
    avgLowC: -8.0,
    humidityPct: 75.0,
    conditions: "Cold with chance of snow",
    uvIndex: 1,
  },
};

// ── Production Implementation ────────────────────────────────────────

const makeWeatherService = Effect.gen(function* () {
  // Depend on the SeasonRegistry to validate season names
  const registry = yield* SeasonRegistryTag;

  const getWeather: WeatherService["getWeather"] = (seasonName) =>
    Effect.gen(function* () {
      // Validate the season exists in the registry (propagates SeasonNotFoundError)
      const season = yield* registry.get(seasonName);
      const key = season.name.trim().toLowerCase();
      const profile = WEATHER_PROFILES[key];

      if (!profile) {
        return yield* Effect.fail(
          new SeasonNotFoundError(seasonName)
        );
      }

      return {
        season: season.name,
        ...profile,
      } satisfies WeatherData;
    });

  const formatWeather: WeatherService["formatWeather"] = (data) =>
    [
      `Weather for ${data.season}:`,
      `  High/Low  : ${data.avgHighC}°C / ${data.avgLowC}°C`,
      `  Humidity  : ${data.humidityPct}%`,
      `  Conditions: ${data.conditions}`,
      `  UV Index  : ${data.uvIndex}`,
    ].join("\n");

  return { getWeather, formatWeather } satisfies WeatherService;
});

// ── Layers ───────────────────────────────────────────────────────────

/**
 * Live WeatherService layer.
 * Requires SeasonRegistryTag in its dependency graph.
 */
export const WeatherLive = Layer.effect(WeatherServiceTag, makeWeatherService);
