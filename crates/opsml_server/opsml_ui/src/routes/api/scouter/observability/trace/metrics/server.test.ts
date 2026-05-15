import { beforeEach, describe, expect, it, vi } from "vitest";
import { andClause, serviceClause, statusCodeClause } from "$lib/components/trace/clause";

const state = vi.hoisted(() => ({
  captured: [] as unknown[],
  mockEnabled: false,
  mockMetricsCalls: 0,
}));

vi.mock("$lib/server/trace/utils", () => ({
  getTraceMetrics: vi.fn(async (_fetch, body) => {
    state.captured.push(body);
    return { metrics: [] };
  }),
}));

vi.mock("$lib/server/mock/mode", () => ({
  isDevMockEnabled: () => state.mockEnabled,
}));

vi.mock("$lib/server/trace/mockData", () => ({
  getMockTraceMetrics: vi.fn((body) => {
    state.mockMetricsCalls += 1;
    state.captured.push(body);
    return { metrics: [] };
  }),
}));

import { POST } from "./+server";

async function postJson(body: unknown) {
  const request = new Request("http://localhost/api/scouter/observability/trace/metrics", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return POST({ request, fetch: globalThis.fetch, cookies: {} } as never);
}

describe("POST /api/scouter/observability/trace/metrics", () => {
  beforeEach(() => {
    state.captured.length = 0;
    state.mockEnabled = false;
    state.mockMetricsCalls = 0;
  });

  it("forwards a clause-shaped body with default bucket interval", async () => {
    const input = {
      clause: andClause(serviceClause("checkout"), statusCodeClause(500)),
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
      entity_uid: "card-1",
    };
    await postJson(input);
    expect(state.captured[0]).toEqual({ bucket_interval: "1 hours", ...input });
  });

  it("returns 400 when start_time is missing", async () => {
    const response = await postJson({ end_time: "2026-01-02T00:00:00Z" });
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({
      response: null,
      error: "start_time and end_time are required",
    });
    expect(state.captured).toHaveLength(0);
  });

  it("returns 400 when end_time is missing", async () => {
    const response = await postJson({ start_time: "2026-01-01T00:00:00Z" });
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({
      response: null,
      error: "start_time and end_time are required",
    });
    expect(state.captured).toHaveLength(0);
  });

  it("returns 400 for malformed clauses", async () => {
    const response = await postJson({
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
      clause: { op: "service", value: 42 },
    });
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({
      response: null,
      error: "service.value must be a string",
    });
    expect(state.captured).toHaveLength(0);
  });

  it("short-circuits to mock metrics when mock mode is enabled", async () => {
    state.mockEnabled = true;
    const input = {
      start_time: "2026-01-01T00:00:00Z",
      end_time: "2026-01-02T00:00:00Z",
    };
    await postJson(input);
    expect(state.mockMetricsCalls).toBe(1);
    expect(state.captured[0]).toEqual(input);
  });
});
