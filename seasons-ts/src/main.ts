/**
 * Entry point for the Seasons CLI — Effect-TS rewrite.
 *
 * This file will be expanded when @effect/cli commands are wired in.
 * For now it serves as the scaffold entry point.
 */
import { Effect, Console } from "effect";

const program = Effect.gen(function* () {
  yield* Console.log("🌱 Seasons CLI (Effect-TS) — scaffold ready");
  yield* Console.log("Run `pnpm test` to verify the setup.");
});

Effect.runPromise(program).catch(console.error);
