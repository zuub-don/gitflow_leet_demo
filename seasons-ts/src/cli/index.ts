/**
 * Root CLI command — composes all subcommands into a single CLI app.
 *
 * Uses @effect/cli for type-safe argument parsing with automatic
 * help generation and shell completions.
 */
import { Command } from "@effect/cli";
import {
  allCommand,
  infoCommand,
  summaryCommand,
  compareCommand,
  weatherCommand,
} from "./commands.js";

export const rootCommand = Command.make("seasons").pipe(
  Command.withDescription("Display information about the four seasons. (Effect-TS)"),
  Command.withSubcommands([
    allCommand,
    infoCommand,
    summaryCommand,
    compareCommand,
    weatherCommand,
  ])
);
