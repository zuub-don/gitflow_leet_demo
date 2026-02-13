/**
 * Entry point for the Seasons CLI — Effect-TS rewrite.
 *
 * Composes the CLI command tree with the service Layer graph
 * and runs it via @effect/platform's NodeRuntime.
 */
import { Effect, Layer } from "effect";
import { NodeContext, NodeRuntime } from "@effect/platform-node";
import { CliApp } from "@effect/cli";
import { rootCommand } from "./cli/index.js";
import { makeSeededRegistry } from "./services/Registry.js";
import { WeatherLive } from "./services/Weather.js";
import { SEED_SEASONS } from "./schema/Season.js";

// ── Layer Graph ──────────────────────────────────────────────────────
//
// WeatherLive depends on SeasonRegistryTag, so we compose:
//   SeededRegistry -> WeatherLive -> merged into AppLayer
//
const SeededRegistry = makeSeededRegistry(SEED_SEASONS as any);
const AppLayer = Layer.mergeAll(
  SeededRegistry,
  WeatherLive.pipe(Layer.provide(SeededRegistry))
);

// ── Run ──────────────────────────────────────────────────────────────

const cli = CliApp.make({
  name: "seasons",
  version: "4.0.0-dev",
  command: rootCommand,
});

const program = Effect.gen(function* () {
  const args = process.argv.slice(2);
  yield* CliApp.run(cli, args, rootCommand);
}).pipe(
  Effect.provide(AppLayer),
  Effect.provide(NodeContext.layer)
);

NodeRuntime.runMain(program);
