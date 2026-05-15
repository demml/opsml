import { beforeEach, describe, expect, it, vi } from "vitest";
import { andClause, serviceClause, statusCodeClause } from "$lib/components/trace/clause";

const state = vi.hoisted(() => ({
  captured: [] as unknown[],
  mockEnabled: false,
  helperStatus: 200,
  helperError: "",
  mockFacetCalls: 0,
}));

vi.mock("$lib/server/trace/utils", () => {
  class TraceServerError extends Error {
    constructor(message: string, public status = 500) {
      super(message);
    }
  }

  return {
    TraceServerError,
    getTraceFacets: vi.fn(async (_fetch, body) => {
      state.captured.push({ helper: true, body });
      if (state.helperError) {
        throw new TraceServerError(state.helperError, state.helperStatus);
      }
      return {
        services: [{ value: "checkout", trace_count: 4 }],
        status_codes: [{ value: "500", trace_count: 2 }],
        total_count: 4,
      };
    }),
  };
});

vi.mock("$lib/server/mock/mode", () => ({
  isDevMockEnabled: () => state.mockEnabled,
}));

vi.mock("$lib/server/trace/mockData", () => ({
  getMockTraceFacets: vi.fn((body) => {
    state.mockFacetCalls += 1;
    state.captured.push({ mock: true, body });
    return { services: [], status_codes: [], total_count: 0 };
  }),
}));

import { POST } from "./+server";

async function postJson(body: unknown) {
  const request = new Request("http://localhost/api/scouter/trace/facets", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return POST({ request, fetch: globalThis.fetch, cookies: {} } as never);
}

describe("POST /api/scouter/trace/facets", () => {
  beforeEach(() => {
    state.captured.length = 0;
    state.mockEnabled = false;
    state.helperStatus = 200;
    state.helperError = "";
    state.mockFacetCalls = 0;
  });

  it("forwards clause-shaped body verbatim", async () => {
    const input = {
      clause: andClause(serviceClause("checkout"), statusCodeClause(500)),
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
    };
    await postJson(input);
    expect(state.captured[0]).toEqual({ helper: true, body: input });
  });

  it("propagates backend non-ok status and body", async () => {
    state.helperStatus = 503;
    state.helperError = "scouter unavailable";
    const response = await postJson({ start_time: "2026-01-01T00:00:00Z" });
    expect(response.status).toBe(503);
    await expect(response.json()).resolves.toEqual({
      response: null,
      error: "scouter unavailable",
    });
  });

  it("returns 400 for invalid trace filters before mock or helper work", async () => {
    state.mockEnabled = true;
    const response = await postJson({ clause: { op: "status_code", value: "500" } });
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({
      response: null,
      error: "status_code.value must be an integer",
    });
    expect(state.captured).toHaveLength(0);
    expect(state.mockFacetCalls).toBe(0);
  });

  it("short-circuits to mock facets when mock mode is enabled", async () => {
    state.mockEnabled = true;
    const input = { start_time: "2026-01-01T00:00:00Z" };
    await postJson(input);
    expect(state.mockFacetCalls).toBe(1);
    expect(state.captured[0]).toEqual({ mock: true, body: input });
  });
});
