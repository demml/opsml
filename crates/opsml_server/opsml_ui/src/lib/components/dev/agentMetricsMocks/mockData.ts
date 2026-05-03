import type { DateTime } from "$lib/types";
import type {
  AgentDashboardResponse,
  AgentMetricBucket,
  GenAiAgentActivity,
  GenAiErrorCount,
  GenAiModelUsage,
  GenAiOperationBreakdown,
  GenAiToolActivity,
  MockMetricsBundle,
  ModelCostBreakdown,
  ToolDashboardResponse,
  ToolTimeBucket,
} from "./types";

// Deterministic PRNG so mockup looks identical across reloads.
function mulberry32(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export interface MockOptions {
  bucketCount?: number;
  bucketIntervalMs?: number;
  endTime?: Date;
  seed?: number;
  trafficScale?: number;
}

export function buildMockBundle(opts: MockOptions = {}): MockMetricsBundle {
  const bucketCount = opts.bucketCount ?? 60;
  const bucketIntervalMs = opts.bucketIntervalMs ?? 60_000;
  const end = opts.endTime ?? new Date();
  const trafficScale = opts.trafficScale ?? 1;
  const rand = mulberry32(opts.seed ?? 42);

  const buckets: AgentMetricBucket[] = [];
  for (let i = bucketCount - 1; i >= 0; i--) {
    const ts = new Date(end.getTime() - i * bucketIntervalMs);
    // Sinusoidal traffic pattern + noise
    const phase = ((bucketCount - i) / bucketCount) * Math.PI * 2;
    const base = 80 + 60 * Math.sin(phase) + rand() * 40;
    const span_count = Math.max(1, Math.round(base * trafficScale));
    const error_rate =
      Math.max(0, 0.005 + Math.sin(phase * 1.7) * 0.01 + (rand() - 0.5) * 0.02);
    const error_count = Math.round(span_count * error_rate);

    const p50 = 280 + Math.sin(phase * 0.8) * 80 + rand() * 40;
    const p95 = p50 * (2.4 + rand() * 0.5);
    const p99 = p50 * (3.6 + rand() * 0.8);
    const avg = p50 * (1.1 + rand() * 0.2);

    const input_t = Math.round(span_count * (350 + rand() * 200));
    const output_t = Math.round(span_count * (140 + rand() * 90));
    const cache_creation = Math.round(input_t * 0.12);
    const cache_read = Math.round(input_t * 0.32);

    const cost = (input_t / 1e6) * 3.0 + (output_t / 1e6) * 15.0;

    buckets.push({
      bucket_start: ts.toISOString() as DateTime,
      span_count,
      error_count,
      error_rate,
      avg_duration_ms: avg,
      p50_duration_ms: p50,
      p95_duration_ms: p95,
      p99_duration_ms: p99,
      total_input_tokens: input_t,
      total_output_tokens: output_t,
      total_cache_creation_tokens: cache_creation,
      total_cache_read_tokens: cache_read,
      total_cost: cost,
    });
  }

  const total_requests = buckets.reduce((a, b) => a + b.span_count, 0);
  const total_errors = buckets.reduce((a, b) => a + b.error_count, 0);
  const total_input_tokens = buckets.reduce(
    (a, b) => a + b.total_input_tokens,
    0,
  );
  const total_output_tokens = buckets.reduce(
    (a, b) => a + b.total_output_tokens,
    0,
  );
  const total_cache_creation_tokens = buckets.reduce(
    (a, b) => a + b.total_cache_creation_tokens,
    0,
  );
  const total_cache_read_tokens = buckets.reduce(
    (a, b) => a + b.total_cache_read_tokens,
    0,
  );

  // Model cost breakdown — distribute totals across 4 models with realistic skew
  const modelMix: { model: string; share: number; mult: number }[] = [
    { model: "gpt-4o", share: 0.52, mult: 1.0 },
    { model: "claude-3-5-sonnet", share: 0.28, mult: 1.4 },
    { model: "gpt-4o-mini", share: 0.14, mult: 0.12 },
    { model: "gemini-1.5-pro", share: 0.06, mult: 0.9 },
  ];
  const cost_by_model: ModelCostBreakdown[] = modelMix.map((m) => {
    const in_t = Math.round(total_input_tokens * m.share);
    const out_t = Math.round(total_output_tokens * m.share);
    const cc = Math.round(total_cache_creation_tokens * m.share);
    const cr = Math.round(total_cache_read_tokens * m.share);
    const cost = ((in_t / 1e6) * 3.0 + (out_t / 1e6) * 15.0) * m.mult;
    return {
      model: m.model,
      total_input_tokens: in_t,
      total_output_tokens: out_t,
      total_cache_creation_tokens: cc,
      total_cache_read_tokens: cr,
      total_cost: cost,
    };
  });

  const summary = {
    total_requests,
    avg_duration_ms:
      buckets.reduce((a, b) => a + b.avg_duration_ms * b.span_count, 0) /
      Math.max(1, total_requests),
    p50_duration_ms: 312,
    p95_duration_ms: 842,
    p99_duration_ms: 1410,
    overall_error_rate: total_errors / Math.max(1, total_requests),
    total_input_tokens,
    total_output_tokens,
    total_cache_creation_tokens,
    total_cache_read_tokens,
    unique_agent_count: 4,
    unique_conversation_count: 287,
    cost_by_model,
  };

  const agent_dashboard: AgentDashboardResponse = { summary, buckets };

  const tool_aggregates: GenAiToolActivity[] = [
    {
      tool_name: "search_documents",
      tool_type: "function",
      call_count: 4210,
      avg_duration_ms: 142,
      error_rate: 0.002,
    },
    {
      tool_name: "vector_lookup",
      tool_type: "function",
      call_count: 2801,
      avg_duration_ms: 38,
      error_rate: 0.011,
    },
    {
      tool_name: "http_get",
      tool_type: "function",
      call_count: 820,
      avg_duration_ms: 612,
      error_rate: 0.038,
    },
    {
      tool_name: "code_interpreter",
      tool_type: "builtin",
      call_count: 318,
      avg_duration_ms: 1820,
      error_rate: 0.027,
    },
    {
      tool_name: "send_email",
      tool_type: "function",
      call_count: 91,
      avg_duration_ms: 240,
      error_rate: 0.054,
    },
  ];

  const tool_time_series: ToolTimeBucket[] = [];
  for (let i = bucketCount - 1; i >= 0; i--) {
    const ts = new Date(end.getTime() - i * bucketIntervalMs);
    for (const t of tool_aggregates) {
      const phase = ((bucketCount - i) / bucketCount) * Math.PI * 2;
      tool_time_series.push({
        bucket_start: ts.toISOString() as DateTime,
        tool_name: t.tool_name,
        tool_type: t.tool_type,
        call_count: Math.max(
          0,
          Math.round((t.call_count / bucketCount) * (1 + Math.sin(phase) * 0.3)),
        ),
        avg_duration_ms: t.avg_duration_ms * (0.85 + rand() * 0.3),
        error_rate: t.error_rate * (0.5 + rand()),
      });
    }
  }

  const tool_dashboard: ToolDashboardResponse = {
    aggregates: tool_aggregates,
    time_series: tool_time_series,
  };

  const model_usage: GenAiModelUsage[] = [
    {
      model: "gpt-4o",
      provider_name: "openai",
      span_count: Math.round(total_requests * 0.52),
      total_input_tokens: cost_by_model[0].total_input_tokens,
      total_output_tokens: cost_by_model[0].total_output_tokens,
      p50_duration_ms: 420,
      p95_duration_ms: 712,
      error_rate: 0.004,
    },
    {
      model: "claude-3-5-sonnet",
      provider_name: "anthropic",
      span_count: Math.round(total_requests * 0.28),
      total_input_tokens: cost_by_model[1].total_input_tokens,
      total_output_tokens: cost_by_model[1].total_output_tokens,
      p50_duration_ms: 680,
      p95_duration_ms: 1100,
      error_rate: 0.021,
    },
    {
      model: "gpt-4o-mini",
      provider_name: "openai",
      span_count: Math.round(total_requests * 0.14),
      total_input_tokens: cost_by_model[2].total_input_tokens,
      total_output_tokens: cost_by_model[2].total_output_tokens,
      p50_duration_ms: 180,
      p95_duration_ms: 340,
      error_rate: 0.001,
    },
    {
      model: "gemini-1.5-pro",
      provider_name: "google",
      span_count: Math.round(total_requests * 0.06),
      total_input_tokens: cost_by_model[3].total_input_tokens,
      total_output_tokens: cost_by_model[3].total_output_tokens,
      p50_duration_ms: 540,
      p95_duration_ms: 920,
      error_rate: 0.012,
    },
  ];

  const operation_breakdown: GenAiOperationBreakdown[] = [
    {
      operation_name: "chat.completions",
      provider_name: "openai",
      span_count: Math.round(total_requests * 0.66),
      avg_duration_ms: 612,
      total_input_tokens: Math.round(total_input_tokens * 0.66),
      total_output_tokens: Math.round(total_output_tokens * 0.66),
      error_rate: 0.006,
    },
    {
      operation_name: "messages",
      provider_name: "anthropic",
      span_count: Math.round(total_requests * 0.28),
      avg_duration_ms: 910,
      total_input_tokens: Math.round(total_input_tokens * 0.28),
      total_output_tokens: Math.round(total_output_tokens * 0.28),
      error_rate: 0.018,
    },
    {
      operation_name: "execute_tool",
      provider_name: null,
      span_count: Math.round(total_requests * 0.42),
      avg_duration_ms: 184,
      total_input_tokens: 0,
      total_output_tokens: 0,
      error_rate: 0.024,
    },
    {
      operation_name: "invoke_agent",
      provider_name: null,
      span_count: Math.round(total_requests * 0.18),
      avg_duration_ms: 2840,
      total_input_tokens: 0,
      total_output_tokens: 0,
      error_rate: 0.011,
    },
    {
      operation_name: "embeddings",
      provider_name: "openai",
      span_count: Math.round(total_requests * 0.12),
      avg_duration_ms: 92,
      total_input_tokens: Math.round(total_input_tokens * 0.06),
      total_output_tokens: 0,
      error_rate: 0.002,
    },
  ];

  const errors: GenAiErrorCount[] = [
    { error_type: "request_timeout", count: 84 },
    { error_type: "rate_limit", count: 42 },
    { error_type: "context_length_exceeded", count: 21 },
    { error_type: "tool_execution_failed", count: 18 },
    { error_type: "invalid_response", count: 9 },
    { error_type: "auth_failed", count: 3 },
  ];

  const agents: GenAiAgentActivity[] = [
    {
      agent_name: "research_agent",
      agent_id: "agent-research-01",
      conversation_id: null,
      span_count: Math.round(total_requests * 0.41),
      total_input_tokens: Math.round(total_input_tokens * 0.41),
      total_output_tokens: Math.round(total_output_tokens * 0.41),
      last_seen: end.toISOString() as DateTime,
    },
    {
      agent_name: "support_agent",
      agent_id: "agent-support-02",
      conversation_id: null,
      span_count: Math.round(total_requests * 0.34),
      total_input_tokens: Math.round(total_input_tokens * 0.34),
      total_output_tokens: Math.round(total_output_tokens * 0.34),
      last_seen: end.toISOString() as DateTime,
    },
    {
      agent_name: "code_agent",
      agent_id: "agent-code-03",
      conversation_id: null,
      span_count: Math.round(total_requests * 0.18),
      total_input_tokens: Math.round(total_input_tokens * 0.18),
      total_output_tokens: Math.round(total_output_tokens * 0.18),
      last_seen: end.toISOString() as DateTime,
    },
    {
      agent_name: "summarizer",
      agent_id: "agent-summary-04",
      conversation_id: null,
      span_count: Math.round(total_requests * 0.07),
      total_input_tokens: Math.round(total_input_tokens * 0.07),
      total_output_tokens: Math.round(total_output_tokens * 0.07),
      last_seen: end.toISOString() as DateTime,
    },
  ];

  return {
    agent_dashboard,
    tool_dashboard,
    model_usage,
    operation_breakdown,
    errors,
    agents,
  };
}
