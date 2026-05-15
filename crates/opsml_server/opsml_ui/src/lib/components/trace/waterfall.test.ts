import { describe, expect, it } from "vitest";
import { prepareWaterfallSpans } from "./waterfall";
import type { TraceSpan } from "./types";

function span(overrides: Partial<TraceSpan> & Pick<TraceSpan, "span_id" | "span_name">): TraceSpan {
  return {
    trace_id: "trace-1",
    parent_span_id: null,
    span_kind: "INTERNAL",
    start_time: "2026-05-11T14:12:53.973265Z",
    end_time: "2026-05-11T14:12:53.973265Z",
    duration_ms: 0,
    status_code: 0,
    status_message: null,
    attributes: [],
    events: [],
    links: [],
    depth: 0,
    path: [],
    root_span_id: "root",
    span_order: 0,
    input: null,
    output: null,
    service_name: "svc",
    ...overrides,
  };
}

describe("prepareWaterfallSpans", () => {
  it("uses spans with missing parents as visual roots", () => {
    const root = span({
      span_id: "root",
      span_name: "agent.request",
      parent_span_id: "remote-parent",
      duration_ms: 4400,
      span_order: 0,
    });
    const child = span({
      span_id: "child",
      span_name: "invocation",
      parent_span_id: "root",
      duration_ms: 1000,
      span_order: 1,
    });

    const result = prepareWaterfallSpans([root, child]);

    expect(result.map((item) => item.span_id)).toEqual(["root", "child"]);
    expect(result.map((item) => item.depth)).toEqual([0, 1]);
  });

  it("derives nested depth and path from parent_span_id when backend depth is flat", () => {
    const root = span({ span_id: "root", span_name: "agent.request", depth: 0, span_order: 0 });
    const child = span({
      span_id: "child",
      span_name: "call_llm",
      parent_span_id: "root",
      depth: 0,
      span_order: 1,
    });
    const grandchild = span({
      span_id: "grandchild",
      span_name: "generate_content",
      parent_span_id: "child",
      depth: 0,
      span_order: 2,
    });

    const result = prepareWaterfallSpans([grandchild, child, root]);

    expect(result.map((item) => [item.span_id, item.depth, item.path])).toEqual([
      ["root", 0, []],
      ["child", 1, ["root"]],
      ["grandchild", 2, ["root", "child"]],
    ]);
  });
});
