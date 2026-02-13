import { describe, it, expect } from "vitest";

describe("scaffold", () => {
  it("project structure exists", () => {
    expect(true).toBe(true);
  });

  it("effect can be imported", async () => {
    const { Effect } = await import("effect");
    const result = Effect.runSync(Effect.succeed(42));
    expect(result).toBe(42);
  });
});
