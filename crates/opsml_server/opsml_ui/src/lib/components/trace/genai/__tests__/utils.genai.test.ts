import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("$lib/api/internalClient", () => ({
  createInternalApiClient: vi.fn(),
}));

import { createInternalApiClient } from "$lib/api/internalClient";
import {
  getServerGenAiTraceMetrics,
  buildGenAiBySpanId,
} from "../../utils";
import type { GenAiTraceMetricsResponse } from "$lib/components/scouter/genai/types";

function makeGenAiResponse(traceId = "t1"): GenAiTraceMetricsResponse {
  return {
    trace_id: traceId,
    has_genai_spans: true,
    spans: [],
    span_limit: 500,
    spans_truncated: false,
    sensitive_content_redacted: false,
    token_metrics: { buckets: [] },
    operation_breakdown: { operations: [] },
    model_usage: { models: [] },
    agent_activity: { agents: [] },
    agent_dashboard: {
      summary: {
        total_requests: 0,
        avg_duration_ms: 0,
        p50_duration_ms: 0,
        p95_duration_ms: 0,
        p99_duration_ms: 0,
        overall_error_rate: 0,
        total_input_tokens: 0,
        total_output_tokens: 0,
        total_cache_creation_tokens: 0,
        total_cache_read_tokens: 0,
        unique_agent_count: 0,
        unique_conversation_count: 0,
        cost_by_model: [],
      },
      buckets: [],
    },
    tool_dashboard: { aggregates: [], time_series: [] },
    error_breakdown: { errors: [] },
  };
}

const mockPost = vi.fn();

beforeEach(() => {
  vi.mocked(createInternalApiClient).mockReturnValue({ post: mockPost } as unknown as ReturnType<typeof createInternalApiClient>);
  mockPost.mockReset();
});

describe("getServerGenAiTraceMetrics", () => {
  it("returns parsed body on ok response", async () => {
    const body = makeGenAiResponse();
    mockPost.mockResolvedValue({ ok: true, json: async () => body });
    const result = await getServerGenAiTraceMetrics(fetch, "t1");
    expect(result).toEqual(body);
  });

  it("throws on non-ok response", async () => {
    mockPost.mockResolvedValue({ ok: false, status: 404 });
    await expect(getServerGenAiTraceMetrics(fetch, "t1")).rejects.toThrow("404");
  });

  it("propagates thrown fetch errors", async () => {
    mockPost.mockRejectedValue(new Error("network error"));
    await expect(getServerGenAiTraceMetrics(fetch, "t1")).rejects.toThrow("network error");
  });

  it("encodes special characters in traceId in the URL", async () => {
    const body = makeGenAiResponse();
    mockPost.mockResolvedValue({ ok: true, json: async () => body });
    await getServerGenAiTraceMetrics(fetch, "trace/with space");
    const url: string = mockPost.mock.calls[0][0];
    expect(url).toContain("trace%2Fwith%20space");
  });

  it("sends correct default body shape", async () => {
    const body = makeGenAiResponse();
    mockPost.mockResolvedValue({ ok: true, json: async () => body });
    await getServerGenAiTraceMetrics(fetch, "t1");
    const requestBody = mockPost.mock.calls[0][1];
    expect(requestBody.bucket_interval).toBe("hour");
    expect(requestBody.span_limit).toBe(500);
    expect(requestBody.include_sensitive_content).toBe(true);
  });
});

describe("buildGenAiBySpanId", () => {
  it("returns empty map for null input", () => {
    expect(buildGenAiBySpanId(null)).toEqual({});
  });

  it("returns empty map when has_genai_spans is false", () => {
    const resp = { ...makeGenAiResponse(), has_genai_spans: false };
    expect(buildGenAiBySpanId(resp)).toEqual({});
  });

  it("keys spans by span_id when has_genai_spans is true", () => {
    const spans = [
      { span_id: "a", trace_id: "t1" },
      { span_id: "b", trace_id: "t1" },
    ] as GenAiTraceMetricsResponse["spans"];
    const resp = { ...makeGenAiResponse(), has_genai_spans: true, spans };
    const map = buildGenAiBySpanId(resp);
    expect(Object.keys(map)).toHaveLength(2);
    expect(map["a"].span_id).toBe("a");
    expect(map["b"].span_id).toBe("b");
  });
});
