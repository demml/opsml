import { beforeEach, describe, expect, it, vi } from "vitest";
import { RegistryType } from "$lib/utils";
import { load } from "../+page";

const traceCalls = vi.hoisted(() => ({
  metrics: [] as unknown[],
  page: [] as unknown[],
  facets: [] as unknown[],
}));

vi.mock("$lib/components/trace/utils", async () => {
  const actual = await vi.importActual<typeof import("$lib/components/trace/utils")>(
    "$lib/components/trace/utils",
  );
  return {
    ...actual,
    getCookie: vi.fn(() => "15min"),
    calculateTimeRange: vi.fn(() => ({
      startTime: "2026-01-01T00:00:00Z",
      endTime: "2026-01-02T00:00:00Z",
      bucketInterval: "1 hours",
    })),
    getServerTraceMetrics: vi.fn(async (_fetch, body) => {
      traceCalls.metrics.push(body);
      return { metrics: [] };
    }),
    getServerTracePage: vi.fn(async (_fetch, body) => {
      traceCalls.page.push(body);
      return {
        items: [
          {
            trace_id: "trace-1",
            service_name: "support-agent",
            scope: "SERVER",
            root_operation: "agent.request",
            start_time: "2026-01-01T00:00:00Z",
            end_time: "2026-01-01T00:00:01Z",
            duration_ms: 1000,
            status_code: 1,
            status_message: null,
            span_count: 1,
            has_errors: false,
            error_count: 0,
            created_at: "2026-01-01T00:00:00Z",
            resource_attributes: [],
          },
        ],
        has_next: false,
        has_previous: false,
      };
    }),
    getServerTraceFacets: vi.fn(async (_fetch, body) => {
      traceCalls.facets.push(body);
      return { services: [], status_codes: [], total_count: 0 };
    }),
  };
});

/** Builds the minimal SvelteKit load event used by route-scope tests. */
function makeLoadCtx(metadata: Record<string, unknown>) {
  return {
    fetch: vi.fn(),
    depends: vi.fn(),
    parent: vi.fn().mockResolvedValue({
      metadata,
      devMockEnabled: false,
    }),
    url: new URL("http://localhost/opsml/agent/agent/card/default/support-agent/1.0.0/observability"),
  } as unknown as Parameters<typeof load>[0];
}

describe("agent observability page load", () => {
  beforeEach(() => {
    traceCalls.metrics.length = 0;
    traceCalls.page.length = 0;
    traceCalls.facets.length = 0;
  });

  it("scopes agent cards with service identity clauses", async () => {
    await load(makeLoadCtx({
      registry_type: RegistryType.Agent,
      name: "support-agent",
      space: "prod",
      version: "1.2.3",
    }));

    const expectedClause = {
      op: "and",
      value: [
        { op: "service", value: "support-agent" },
        { op: "service_namespace", value: "prod" },
        { op: "service_version", value: "1.2.3" },
      ],
    };
    expect(traceCalls.metrics[0]).toMatchObject({ clause: expectedClause });
    expect(traceCalls.page[0]).toMatchObject({ clause: expectedClause });
    expect(traceCalls.facets[0]).toMatchObject({ clause: expectedClause });
    expect(traceCalls.metrics[0]).not.toHaveProperty("entity_uid");
  });

  it("scopes prompt cards with entity_uid and omits clause", async () => {
    await load(makeLoadCtx({
      registry_type: RegistryType.Prompt,
      name: "triage-prompt",
      space: "prod",
      version: "1.2.3",
      eval_profile: { config: { uid: "eval-profile-1" } },
    }));

    expect(traceCalls.metrics[0]).toMatchObject({ entity_uid: "eval-profile-1" });
    expect(traceCalls.page[0]).toMatchObject({ entity_uid: "eval-profile-1" });
    expect(traceCalls.facets[0]).toMatchObject({ entity_uid: "eval-profile-1" });
    expect(traceCalls.metrics[0]).not.toHaveProperty("clause");
  });
});
