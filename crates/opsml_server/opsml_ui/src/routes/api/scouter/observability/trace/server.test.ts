import { describe, expect, it, vi, beforeEach } from "vitest";
import { andClause, serviceClause, statusCodeClause } from "$lib/components/trace/clause";

const state = vi.hoisted(() => ({
  captured: [] as unknown[],
  mockEnabled: false,
  throwError: false,
  mockTracePageCalls: 0,
}));

vi.mock("$lib/server/trace/utils", () => ({
  getTracePage: vi.fn(async (_fetch, body) => {
    state.captured.push(body);
    if (state.throwError) throw new Error("downstream failed");
    return { items: [], has_next: false, has_previous: false };
  }),
}));

vi.mock("$lib/server/mock/mode", () => ({
  isDevMockEnabled: () => state.mockEnabled,
}));

vi.mock("$lib/server/trace/mockData", () => ({
  getMockTracePage: vi.fn((body) => {
    state.mockTracePageCalls += 1;
    state.captured.push(body);
    return { items: [], has_next: false, has_previous: false };
  }),
}));

import { POST } from "./+server";

async function postJson(body: unknown) {
  const request = new Request("http://localhost/api/scouter/observability/trace", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return POST({ request, fetch: globalThis.fetch, cookies: {} } as never);
}

describe("POST /api/scouter/observability/trace", () => {
  beforeEach(() => {
    state.captured.length = 0;
    state.mockEnabled = false;
    state.throwError = false;
    state.mockTracePageCalls = 0;
  });

  it("forwards clause-shaped body verbatim", async () => {
    const input = {
      clause: andClause(serviceClause("checkout"), statusCodeClause(500)),
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
      entity_uid: "card-1",
    };
    await postJson(input);
    expect(state.captured[0]).toEqual(input);
  });

  it("preserves omitted clause", async () => {
    const input = {
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
    };
    await postJson(input);
    expect(state.captured[0]).toEqual(input);
    expect(state.captured[0]).not.toHaveProperty("clause");
  });

  it("short-circuits to mock data when mock mode is enabled", async () => {
    state.mockEnabled = true;
    await postJson({ start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-02T00:00:00Z" });
    expect(state.mockTracePageCalls).toBe(1);
  });

  it("returns 400 for invalid trace filters before mock or proxy work", async () => {
    state.mockEnabled = true;
    const response = await postJson({ service_name: "checkout" });
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({
      response: null,
      error: "unknown field: service_name",
    });
    expect(state.captured).toHaveLength(0);
    expect(state.mockTracePageCalls).toBe(0);
  });

  it("returns 500 when downstream throws", async () => {
    state.throwError = true;
    const response = await postJson({ start_time: "2026-01-01T00:00:00Z", end_time: "2026-01-02T00:00:00Z" });
    expect(response.status).toBe(500);
    await expect(response.json()).resolves.toMatchObject({ error: "downstream failed" });
  });
});
