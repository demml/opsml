import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/svelte";

vi.mock(
  "$lib/components/card/agent/observability/GenAiChartCard.svelte",
  () => ({ default: vi.fn() }),
);

import TraceGenAiPanel from "../TraceGenAiPanel.svelte";
import type {
  GenAiTraceMetricsResponse,
  AgentDashboardSummary,
  AgentMetricBucket,
} from "$lib/components/scouter/genai/types";

function summary(): AgentDashboardSummary {
  return {
    total_requests: 10,
    avg_duration_ms: 200,
    p50_duration_ms: 150,
    p95_duration_ms: 400,
    p99_duration_ms: 500,
    overall_error_rate: 0.1,
    total_input_tokens: 1000,
    total_output_tokens: 500,
    total_cache_creation_tokens: 0,
    total_cache_read_tokens: 0,
    unique_agent_count: 2,
    unique_conversation_count: 1,
    cost_by_model: [
      {
        model: "claude-3-5-sonnet",
        total_input_tokens: 1000,
        total_output_tokens: 500,
        total_cache_creation_tokens: 0,
        total_cache_read_tokens: 0,
        total_cost: 1.25,
      },
    ],
  };
}

function bucket(start: string): AgentMetricBucket {
  return {
    bucket_start: start,
    span_count: 5,
    error_count: 1,
    error_rate: 0.2,
    avg_duration_ms: 200,
    p50_duration_ms: 150,
    p95_duration_ms: 400,
    p99_duration_ms: 500,
    total_input_tokens: 500,
    total_output_tokens: 250,
    total_cache_creation_tokens: 0,
    total_cache_read_tokens: 0,
    total_cost: 0.5,
  };
}

function makeGenai(
  overrides: Partial<GenAiTraceMetricsResponse> = {},
): GenAiTraceMetricsResponse {
  return {
    trace_id: "trace-1",
    has_genai_spans: true,
    spans: [],
    span_limit: 500,
    spans_truncated: false,
    sensitive_content_redacted: false,
    token_metrics: { buckets: [] },
    operation_breakdown: { operations: [] },
    model_usage: {
      models: [
        {
          model: "claude-3-5-sonnet",
          provider_name: "anthropic",
          span_count: 10,
          total_input_tokens: 1000,
          total_output_tokens: 500,
          p50_duration_ms: 150,
          p95_duration_ms: 400,
          error_rate: 0.1,
        },
      ],
    },
    agent_activity: {
      agents: [
        {
          agent_name: "planner",
          agent_id: null,
          conversation_id: null,
          span_count: 5,
          total_input_tokens: 500,
          total_output_tokens: 250,
          last_seen: null,
        },
      ],
    },
    agent_dashboard: {
      summary: summary(),
      buckets: [bucket("2026-01-01T00:00:00Z"), bucket("2026-01-01T00:01:00Z")],
    },
    tool_dashboard: {
      aggregates: [
        {
          tool_name: "search",
          tool_type: "function",
          call_count: 3,
          avg_duration_ms: 80,
          error_rate: 0,
        },
      ],
      time_series: [],
    },
    error_breakdown: { errors: [] },
    ...overrides,
  };
}

describe("TraceGenAiPanel", () => {
  it("renders KPI rail with required labels", () => {
    const { container } = render(TraceGenAiPanel, {
      props: { genai: makeGenai() },
    });
    const text = container.textContent ?? "";
    expect(text).toContain("GenAI Spans");
    expect(text).toContain("p50");
    expect(text).toContain("p95");
    expect(text).toContain("Spend");
    expect(text).toContain("Errors");
    expect(text).toContain("Evals");
  });

  it("renders models, tools, agents tables", () => {
    const { container } = render(TraceGenAiPanel, {
      props: { genai: makeGenai() },
    });
    const text = container.textContent ?? "";
    expect(text).toContain("claude-3-5-sonnet");
    expect(text).toContain("search");
    expect(text).toContain("planner");
  });

  it("shows empty-state row when no tools", () => {
    const genai = makeGenai({ tool_dashboard: { aggregates: [], time_series: [] } });
    const { container } = render(TraceGenAiPanel, { props: { genai } });
    expect(container.textContent).toContain("no tool calls");
  });

  it("renders error breakdown rows", () => {
    const genai = makeGenai({
      error_breakdown: { errors: [{ error_type: "TimeoutError", count: 3 }] },
    });
    const { container } = render(TraceGenAiPanel, { props: { genai } });
    expect(container.textContent).toContain("TimeoutError");
  });

  it("hides Agent Activity table when no agents", () => {
    const genai = makeGenai({ agent_activity: { agents: [] } });
    render(TraceGenAiPanel, { props: { genai } });
    expect(screen.queryByText("Agent Activity")).toBeNull();
  });

  it("does not introduce internal overflow-y-auto", () => {
    const { container } = render(TraceGenAiPanel, {
      props: { genai: makeGenai() },
    });
    expect(container.querySelector(".overflow-y-auto")).toBeNull();
  });

  it("does not include any dark: classes", () => {
    const { container } = render(TraceGenAiPanel, {
      props: { genai: makeGenai() },
    });
    expect(container.innerHTML).not.toContain("dark:");
  });

  it("does not include text-gray-* classes", () => {
    const { container } = render(TraceGenAiPanel, {
      props: { genai: makeGenai() },
    });
    expect(container.innerHTML).not.toMatch(/text-gray-\d+/);
  });
});
