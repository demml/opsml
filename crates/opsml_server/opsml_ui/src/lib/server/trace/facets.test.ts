import { describe, expect, it, vi } from "vitest";
import type { TraceFilters, TraceFacetsResponse } from "$lib/components/trace/types";
import { getTraceFacets } from "$lib/server/trace/facets";
import { ServerPaths } from "$lib/components/api/routes";

function makeFilters(overrides: Partial<TraceFilters> = {}): TraceFilters {
  return {
    start_time: "2026-01-01T00:00:00Z",
    end_time: "2026-01-01T01:00:00Z",
    service_name: "svc-a",
    cursor_start_time: "2026-01-01T00:30:00Z",
    cursor_trace_id: "abc123",
    direction: "next",
    ...overrides,
  };
}

function makeFacetsResponse(): TraceFacetsResponse {
  return {
    services: [{ value: "svc-a", trace_count: 5 }],
    status_codes: [{ value: "200", trace_count: 4 }],
    total_count: 5,
  };
}

describe("getTraceFacets", () => {
  it("POSTs to ServerPaths.TRACE_FACETS and returns response", async () => {
    const payload = makeFacetsResponse();
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ response: payload, error: null }),
    });

    const result = await getTraceFacets(mockFetch as typeof fetch, makeFilters());

    expect(mockFetch).toHaveBeenCalledOnce();
    const [url, init] = mockFetch.mock.calls[0];
    expect(url).toBe(ServerPaths.TRACE_FACETS);
    expect(init.method).toBe("POST");
    expect(result).toEqual(payload);
  });

  it("strips cursor fields from POST body", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ response: makeFacetsResponse(), error: null }),
    });

    await getTraceFacets(mockFetch as typeof fetch, makeFilters());

    const body = JSON.parse(mockFetch.mock.calls[0][1].body as string);
    expect(body).not.toHaveProperty("cursor_start_time");
    expect(body).not.toHaveProperty("cursor_trace_id");
    expect(body).not.toHaveProperty("direction");
    expect(body).toHaveProperty("service_name", "svc-a");
  });

  it("throws on non-ok response", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({}),
    });

    await expect(getTraceFacets(mockFetch as typeof fetch, makeFilters())).rejects.toThrow(
      "Facets request failed: 503",
    );
  });

  it("throws when response body contains error", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ response: null, error: "upstream failure" }),
    });

    await expect(getTraceFacets(mockFetch as typeof fetch, makeFilters())).rejects.toThrow(
      "upstream failure",
    );
  });
});
