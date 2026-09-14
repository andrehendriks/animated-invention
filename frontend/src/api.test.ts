import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { atlasApi, setApiKey } from "./api";

describe("atlasApi", () => {
  beforeEach(() => {
    setApiKey("");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends an API key only when one has been configured", async () => {
    const fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: "ok", services: [] }),
    });
    vi.stubGlobal("fetch", fetch);

    await atlasApi.health();
    setApiKey("session-key");
    await atlasApi.health();

    expect(fetch.mock.calls[0][1].headers).not.toHaveProperty("X-API-Key");
    expect(fetch.mock.calls[1][1].headers).toHaveProperty("X-API-Key", "session-key");
  });

  it("returns the API error detail when a request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: () => Promise.resolve({ detail: "Docker integration is disabled" }),
    }));

    await expect(atlasApi.containers()).rejects.toThrow("Docker integration is disabled");
  });
});
