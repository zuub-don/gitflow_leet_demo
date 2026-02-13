/**
 * CLI Commands — @effect/cli rewrite of the Seasons CLI.
 *
 * Demonstrates:
 * - Type-safe argument parsing with @effect/cli
 * - Structured error handling through the Effect error channel
 * - Layer-based dependency injection for testability
 * - Composable command definitions
 */
import { Command, Options, Args } from "@effect/cli";
import { Effect, Console } from "effect";
import {
  SeasonRegistryTag,
  SeasonNotFoundError,
} from "../services/Registry.js";
import { WeatherServiceTag } from "../services/Weather.js";

// ── Formatters ───────────────────────────────────────────────────────

interface SeasonLike {
  readonly name: string;
  readonly months: readonly string[];
  readonly avgTempC: number;
  readonly description: string;
  readonly activities: readonly string[];
}

const formatSeason = (s: SeasonLike): string => {
  const width = 56;
  const top = `┌${"─".repeat(width)}┐`;
  const bot = `└${"─".repeat(width)}┘`;
  const title = `│${` ${s.name} `.padStart((width + s.name.length + 2) / 2, "─").padEnd(width, "─")}│`;
  const lines = [top, title, `│${"─".repeat(width)}│`];

  const field = (label: string, value: string) => {
    const content = `  ${label.padEnd(12)}: ${value}`;
    return `│${content.padEnd(width)}│`;
  };

  lines.push(field("Months", s.months.join(", ")));
  lines.push(field("Avg Temp", `${s.avgTempC}°C`));
  lines.push(field("Description", s.description.slice(0, width - 17)));

  if (s.activities.length > 0) {
    let actStr = s.activities.slice(0, 3).join(", ");
    if (s.activities.length > 3) {
      actStr += ` (+${s.activities.length - 3} more)`;
    }
    if (actStr.length > width - 17) {
      actStr = actStr.slice(0, width - 20) + "...";
    }
    lines.push(field("Activities", actStr));
  }

  lines.push(bot);
  return lines.join("\n");
};

const formatComparison = (a: SeasonLike, b: SeasonLike): string => {
  const lines = [
    `${"".padEnd(15)} ┃ ${a.name.padEnd(18)} ┃ ${b.name.padEnd(18)}`,
    "─".repeat(55),
    `${"Months".padEnd(15)} ┃ ${a.months.join(", ").padEnd(18)} ┃ ${b.months.join(", ").padEnd(18)}`,
    `${"Avg Temp".padEnd(15)} ┃ ${String(a.avgTempC).padEnd(18)} ┃ ${String(b.avgTempC).padEnd(18)}`,
  ];
  const diff = a.avgTempC - b.avgTempC;
  if (diff > 0) {
    lines.push(`  → ${a.name} is ${diff.toFixed(1)}°C warmer than ${b.name}`);
  } else if (diff < 0) {
    lines.push(`  → ${b.name} is ${Math.abs(diff).toFixed(1)}°C warmer than ${a.name}`);
  } else {
    lines.push("  → Both seasons have the same average temperature");
  }
  return lines.join("\n");
};

// ── Args & Options ───────────────────────────────────────────────────

const seasonNameArg = Args.text({ name: "season" }).pipe(
  Args.withDescription("Name of a season (spring, summer, autumn, winter)")
);

const firstSeasonArg = Args.text({ name: "first" }).pipe(
  Args.withDescription("First season to compare")
);

const secondSeasonArg = Args.text({ name: "second" }).pipe(
  Args.withDescription("Second season to compare")
);

const verboseOption = Options.boolean("verbose").pipe(
  Options.withAlias("v"),
  Options.withDefault(false),
  Options.withDescription("Show verbose output")
);

// ── Commands ─────────────────────────────────────────────────────────

export const allCommand = Command.make("all", { verbose: verboseOption }, ({ verbose }) =>
  Effect.gen(function* () {
    const registry = yield* SeasonRegistryTag;
    const seasons = yield* registry.getAll();

    if (seasons.length === 0) {
      yield* Console.log("No seasons registered.");
      return;
    }

    for (const s of seasons) {
      yield* Console.log(formatSeason(s));
      yield* Console.log("");
    }
  })
).pipe(Command.withDescription("Show all available seasons"));

export const infoCommand = Command.make("info", { name: seasonNameArg }, ({ name }) =>
  Effect.gen(function* () {
    const registry = yield* SeasonRegistryTag;
    const season = yield* registry.get(name).pipe(
      Effect.catchTag("SeasonNotFoundError", (err) =>
        Effect.gen(function* () {
          yield* Console.error(`Error: Season '${err.name}' not found.`);
          return yield* Effect.fail(err);
        })
      )
    );
    yield* Console.log(formatSeason(season));
  })
).pipe(Command.withDescription("Show details for a season"));

export const summaryCommand = Command.make("summary", {}, () =>
  Effect.gen(function* () {
    const registry = yield* SeasonRegistryTag;
    const seasons = yield* registry.getAll();

    if (seasons.length === 0) {
      yield* Console.log("No seasons registered.");
      return;
    }

    yield* Console.log("┌──────────┬────────────────────────────────┬────────┐");
    yield* Console.log("│ Season   │ Months                         │ Avg °C │");
    yield* Console.log("├──────────┼────────────────────────────────┼────────┤");
    for (const s of seasons) {
      const months = s.months.join(", ");
      yield* Console.log(
        `│ ${s.name.padEnd(8)} │ ${months.padEnd(30)} │ ${s.avgTempC.toFixed(1).padStart(6)} │`
      );
    }
    yield* Console.log("└──────────┴────────────────────────────────┴────────┘");
  })
).pipe(Command.withDescription("Show a compact summary table"));

export const compareCommand = Command.make(
  "compare",
  { first: firstSeasonArg, second: secondSeasonArg },
  ({ first, second }) =>
    Effect.gen(function* () {
      if (first.trim().toLowerCase() === second.trim().toLowerCase()) {
        yield* Console.error("Cannot compare a season with itself.");
        return;
      }

      const registry = yield* SeasonRegistryTag;
      const a = yield* registry.get(first);
      const b = yield* registry.get(second);
      yield* Console.log(formatComparison(a, b));
    })
).pipe(Command.withDescription("Compare two seasons side by side"));

export const weatherCommand = Command.make(
  "weather",
  { name: seasonNameArg },
  ({ name }) =>
    Effect.gen(function* () {
      const weatherService = yield* WeatherServiceTag;
      const data = yield* weatherService.getWeather(name);
      yield* Console.log(weatherService.formatWeather(data));
    })
).pipe(Command.withDescription("Show weather profile for a season"));
