import { describe, expect, it } from "vitest";
import type { TraceSpansResponse } from "$lib/components/trace/types";
import { deriveTraceFacetsFromSpans } from "$lib/server/trace/utils";

function makeSpansResponse(): TraceSpansResponse {
  return {
    spans: [
      {
        trace_id: "trace-1",
        span_id: "root-1",
        parent_span_id: null,
        span_name: "root",
        span_kind: "SERVER",
        start_time: "2026-01-01T00:00:00Z",
        end_time: "2026-01-01T00:00:01Z",
        duration_ms: 1000,
        status_code: 1,
        status_message: null,
        attributes: [
          { key: "http.method", value: "GET" },
          { key: "dup.key", value: "a" },
        ],
        events: [],
        links: [],
        depth: 0,
        path: [],
        root_span_id: "root-1",
        span_order: 0,
        input: null,
        output: null,
        service_name: "svc-a",
      },
      {
        trace_id: "trace-1",
        span_id: "child-1",
        parent_span_id: "root-1",
        span_name: "child",
        span_kind: "INTERNAL",
        start_time: "2026-01-01T00:00:00Z",
        end_time: "2026-01-01T00:00:00.5Z",
        duration_ms: 500,
        status_code: 1,
        status_message: null,
        attributes: [
          { key: "dup.key", value: "b" },
          { key: "db.system", value: "sqlite" },
        ],
        events: [],
        links: [],
        depth: 1,
        path: [],
        root_span_id: "root-1",
        span_order: 1,
        input: null,
        output: null,
        service_name: "svc-a",
      },
      {
        trace_id: "trace-2",
        span_id: "no-root-1",
        parent_span_id: "missing-root",
        span_name: "child",
        span_kind: "SERVER",
        start_time: "2026-01-01T00:00:00Z",
        end_time: "2026-01-01T00:00:00.2Z",
        duration_ms: 200,
        status_code: 2,
        status_message: null,
        attributes: [{ key: "custom.key", value: true }],
        events: [],
        links: [],
        depth: 0,
        path: [],
        root_span_id: "missing-root",
        span_order: 0,
        input: null,
        output: null,
        service_name: "svc-b",
      },
      {
        trace_id: "trace-2",
        span_id: "no-root-2",
        parent_span_id: "missing-root",
        span_name: "child-2",
        span_kind: "INTERNAL",
        start_time: "2026-01-01T00:00:00Z",
        end_time: "2026-01-01T00:00:00.1Z",
        duration_ms: 100,
        status_code: 2,
        status_message: null,
        attributes: [{ key: "custom.key", value: false }],
        events: [],
        links: [],
        depth: 1,
        path: [],
        root_span_id: "missing-root",
        span_order: 1,
        input: null,
        output: null,
        service_name: "svc-b",
      },
    ],
  };
}

describe("deriveTraceFacetsFromSpans", () => {
  it("derives service and status facets from root or first span per trace", () => {
    const facets = deriveTraceFacetsFromSpans(makeSpansResponse());
    expect(facets.services).toEqual([
      { value: "svc-a", count: 1 },
      { value: "svc-b", count: 1 },
    ]);
    expect(facets.status_codes).toEqual([
      { value: "1", count: 1 },
      { value: "2", count: 1 },
    ]);
  });

  it("counts attribute keys once per trace even when duplicate keys appear across spans", () => {
    const facets = deriveTraceFacetsFromSpans(makeSpansResponse());
    expect(facets.attribute_keys).toEqual([
      { value: "custom.key", count: 1 },
      { value: "db.system", count: 1 },
      { value: "dup.key", count: 1 },
      { value: "http.method", count: 1 },
    ]);
  });
});
