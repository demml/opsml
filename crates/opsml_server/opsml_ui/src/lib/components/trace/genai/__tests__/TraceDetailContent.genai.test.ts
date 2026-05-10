import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";

vi.mock("../../TraceWaterfall.svelte", () => ({ default: vi.fn() }));
vi.mock("../../SpanDetailView.svelte", () => ({ default: vi.fn() }));
vi.mock("../../graph/SpanGraph.svelte", () => ({ default: vi.fn() }));
vi.mock("$lib/components/card/agent/observability/VolumeChart.svelte", () => ({ default: vi.fn() }));
vi.mock("$lib/components/card/agent/observability/LatencyChart.svelte", () => ({ default: vi.fn() }));
vi.mock("$lib/components/card/agent/observability/TokenChart.svelte", () => ({ default: vi.fn() }));
vi.mock("$lib/components/card/agent/observability/ErrorRateChart.svelte", () => ({ default: vi.fn() }));
vi.mock("../TraceGenAiPanel.svelte", () => ({ default: vi.fn() }));

import TraceDetailContent from "../../TraceDetailContent.svelte";
import type { TraceListItem, TraceSpan } from "../../types";
import type {
  GenAiTraceMetricsResponse,
  AgentDashboardSummary,
  GenAiSpanRecord,
} from "$lib/components/scouter/genai/types";

function trace(): TraceListItem {
  return {
    trace_id: "trace-1",
    service_name: "svc",
    scope: "INTERNAL",
    root_operation: "POST /predict",
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
  };
}

function span(): TraceSpan {
  return {
    trace_id: "trace-1",
    span_id: "span-1",
    parent_span_id: null,
    span_name: "root",
    span_kind: "INTERNAL",
    start_time: "2026-01-01T00:00:00Z",
    end_time: "2026-01-01T00:00:01Z",
    duration_ms: 1000,
    status_code: 1,
    status_message: null,
    attributes: [],
    events: [],
    links: [],
    depth: 0,
    path: [],
    root_span_id: "span-1",
    span_order: 0,
    input: null,
    output: null,
    service_name: "svc",
  };
}

function summary(): AgentDashboardSummary {
  return {
    total_requests: 1,
    avg_duration_ms: 1000,
    p50_duration_ms: 1000,
    p95_duration_ms: 1000,
    p99_duration_ms: 1000,
    overall_error_rate: 0,
    total_input_tokens: 0,
    total_output_tokens: 0,
    total_cache_creation_tokens: 0,
    total_cache_read_tokens: 0,
    unique_agent_count: 0,
    unique_conversation_count: 0,
    cost_by_model: [],
  };
}

function genai(
  has_genai_spans: boolean,
  spans: GenAiSpanRecord[] = [],
): GenAiTraceMetricsResponse {
  return {
    trace_id: "trace-1",
    has_genai_spans,
    spans,
    span_limit: 500,
    spans_truncated: false,
    sensitive_content_redacted: false,
    token_metrics: { buckets: [] },
    operation_breakdown: { operations: [] },
    model_usage: { models: [] },
    agent_activity: { agents: [] },
    agent_dashboard: { summary: summary(), buckets: [] },
    tool_dashboard: { aggregates: [], time_series: [] },
    error_breakdown: { errors: [] },
  };
}

describe("TraceDetailContent — GenAI tab", () => {
  it("does not show GenAI tab when genai is null", () => {
    render(TraceDetailContent, {
      props: {
        trace: trace(),
        traceSpans: { spans: [span()] },
        genai: null,
      },
    });
    expect(screen.queryByRole("button", { name: /GenAI/i })).toBeNull();
  });

  it("does not show GenAI tab when has_genai_spans is false", () => {
    render(TraceDetailContent, {
      props: {
        trace: trace(),
        traceSpans: { spans: [span()] },
        genai: genai(false),
      },
    });
    expect(screen.queryByRole("button", { name: /GenAI/i })).toBeNull();
  });

  it("shows GenAI tab when has_genai_spans is true", () => {
    render(TraceDetailContent, {
      props: {
        trace: trace(),
        traceSpans: { spans: [span()] },
        genai: genai(true),
      },
    });
    expect(screen.getByRole("button", { name: /GenAI/i })).toBeInTheDocument();
  });

  it("clicking GenAI tab hides waterfall and shows genai body container", async () => {
    const s = span();
    const genaiSpanRecord: GenAiSpanRecord = {
      trace_id: "trace-1",
      span_id: s.span_id,
      service_name: "svc",
      start_time: s.start_time,
      end_time: s.end_time,
      duration_ms: 1000,
      status_code: 200,
      operation_name: "chat",
      provider_name: "anthropic",
      request_model: "claude-3-5-sonnet",
      response_model: "claude-3-5-sonnet",
      response_id: null,
      input_tokens: 10,
      output_tokens: 5,
      cache_creation_input_tokens: null,
      cache_read_input_tokens: null,
      finish_reasons: ["end_turn"],
      output_type: null,
      conversation_id: null,
      agent_name: null,
      agent_id: null,
      agent_description: null,
      agent_version: null,
      data_source_id: null,
      tool_name: null,
      tool_type: null,
      tool_call_id: null,
      request_temperature: null,
      request_max_tokens: null,
      request_top_p: null,
      request_choice_count: null,
      request_seed: null,
      request_frequency_penalty: null,
      request_presence_penalty: null,
      request_stop_sequences: [],
      server_address: null,
      server_port: null,
      error_type: null,
      openai_api_type: null,
      openai_service_tier: null,
      label: null,
      entity_id: null,
      input_messages: null,
      output_messages: null,
      system_instructions: null,
      tool_definitions: null,
      eval_results: [],
    };
    const genAiResp = genai(true, [genaiSpanRecord]);
    const genAiBySpanId: Record<string, GenAiSpanRecord> = {
      [s.span_id]: genaiSpanRecord,
    };
    const { container } = render(TraceDetailContent, {
      props: {
        trace: trace(),
        traceSpans: { spans: [s] },
        genai: genAiResp,
        genAiBySpanId,
      },
    });
    const genAiBtn = screen.getByRole("button", { name: /GenAI/i });
    await fireEvent.click(genAiBtn);
    // GenAI scroll container should now be present; resizable split should not
    expect(container.querySelector(".overscroll-contain")).not.toBeNull();
    expect(container.querySelector("[style*='height']")).toBeNull();
  });
});
