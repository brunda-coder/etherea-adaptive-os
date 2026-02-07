import { describe, expect, it } from "vitest";
import { computeStressFocus, InMemoryStorage, loadJson, runAgentAction, saveJson } from "../src";

describe("agent registry", () => {
  it("returns structured output for each action", () => {
    const ppt = runAgentAction("create_ppt", "Etherea demo");
    expect(ppt.output).toHaveProperty("outline");
    const summary = runAgentAction("summarize_pdf", "whitepaper.pdf");
    expect(summary.output).toHaveProperty("summary");
    const notes = runAgentAction("generate_notes", "Aurora UX");
    expect(notes.output).toHaveProperty("sections");
  });
});

describe("storage", () => {
  it("saves and loads json payload", async () => {
    const storage = new InMemoryStorage();
    await saveJson(storage, "doc", { hello: "world" });
    const loaded = await loadJson<{ hello: string }>(storage, "doc");
    expect(loaded?.hello).toBe("world");
  });
});

describe("stress/focus", () => {
  it("returns bounded values", () => {
    const score = computeStressFocus({ typingPerMinute: 500, mouseMovesPerMinute: 500 });
    expect(score.stress).toBeGreaterThanOrEqual(0);
    expect(score.stress).toBeLessThanOrEqual(100);
    expect(score.focus).toBeGreaterThanOrEqual(0);
    expect(score.focus).toBeLessThanOrEqual(100);
  });
});
