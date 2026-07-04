import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiFailure, embed } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("api client", () => {
  it("returns parsed JSON on 200", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ params: { method: "dct" } }), { status: 200 })));
    const body = await embed(new FormData());
    expect(body.params.method).toBe("dct");
  });
  it("throws ApiFailure with bilingual detail on error status", async () => {
    const payload = { error: { code: "bad_method", zh: "算法错误", en: "Bad method" } };
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(payload), { status: 400 })));
    await expect(embed(new FormData())).rejects.toSatisfy((e: unknown) => e instanceof ApiFailure && e.detail.code === "bad_method");
  });
});
