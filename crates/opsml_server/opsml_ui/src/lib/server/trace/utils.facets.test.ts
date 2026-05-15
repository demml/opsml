import { beforeEach, describe, expect, it, vi } from "vitest";
import { getTraceFacets, TraceServerError } from "./utils";
import { serviceClause } from "$lib/components/trace/clause";
import { RoutePaths } from "$lib/components/api/routes";

const clientState = vi.hoisted(() => ({
  captured: [] as unknown[],
  ok: true,
  status: 200,
  text: "",
}));

vi.mock("../api/opsmlClient", () => ({
  createOpsmlClient: () => ({
    post: vi.fn(async (path, body) => {
      clientState.captured.push({ path, body });
      return {
        ok: clientState.ok,
        status: clientState.status,
        text: async () => clientState.text,
        json: async () => ({ services: [], status_codes: [], total_count: 0 }),
      };
    }),
  }),
}));

describe("getTraceFacets", () => {
  beforeEach(() => {
    clientState.captured.length = 0;
    clientState.ok = true;
    clientState.status = 200;
    clientState.text = "";
  });

  it("posts filters through the shared trace facets route", async () => {
    const filters = { clause: serviceClause("checkout") };
    await getTraceFacets(globalThis.fetch, filters);
    expect(clientState.captured[0]).toEqual({
      path: RoutePaths.TRACE_FACETS,
      body: filters,
    });
  });

  it("raises TraceServerError with the backend status when the proxy fails", async () => {
    clientState.ok = false;
    clientState.status = 503;
    clientState.text = "scouter unavailable";

    await expect(getTraceFacets(globalThis.fetch, {})).rejects.toMatchObject({
      message: "scouter unavailable",
      status: 503,
    } satisfies Partial<TraceServerError>);
  });
});
