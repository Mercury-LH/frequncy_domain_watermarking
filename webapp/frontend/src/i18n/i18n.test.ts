import { describe, expect, it } from "vitest";
import { en } from "./en";
import { zh } from "./zh";

function keysOf(obj: Record<string, unknown>, prefix = ""): string[] {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === "object" && v !== null ? keysOf(v as Record<string, unknown>, `${prefix}${k}.`) : [`${prefix}${k}`],
  );
}

describe("i18n dictionaries", () => {
  it("zh and en have identical key sets", () => {
    expect(keysOf(en).sort()).toEqual(keysOf(zh).sort());
  });
  it("no empty strings", () => {
    for (const dict of [zh, en]) {
      const walk = (o: Record<string, unknown>): void =>
        Object.values(o).forEach((v) =>
          typeof v === "object" && v !== null ? walk(v as Record<string, unknown>) : expect(String(v).trim()).not.toBe(""),
        );
      walk(dict);
    }
  });
});
