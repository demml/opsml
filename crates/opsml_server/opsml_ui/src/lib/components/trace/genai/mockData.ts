import type {
  AgentDashboardResponse,
  AgentMetricBucket,
  GenAiAgentActivity,
  GenAiErrorCount,
  GenAiEvalResult,
  GenAiModelUsage,
  GenAiOperationBreakdown,
  GenAiSpanRecord,
  GenAiTokenBucket,
  GenAiToolActivity,
  GenAiTraceMetricsResponse,
  ModelCostBreakdown,
  ToolTimeBucket,
} from "$lib/components/scouter/genai/types";

interface SpanSpec {
  start_offset_ms: number;
  duration_ms: number;
  operation_name: string;
  provider_name?: string;
  request_model?: string;
  response_model?: string;
  input_tokens?: number;
  output_tokens?: number;
  cache_creation?: number;
  cache_read?: number;
  finish_reasons?: string[];
  tool_name?: string;
  tool_type?: string;
  tool_call_id?: string;
  error_type?: string;
  status_code?: number;
  label?: string;
  agent_name?: string;
  input_messages?: string;
  output_messages?: string;
  system_instructions?: string;
  tool_definitions?: string;
  request_temperature?: number;
  request_max_tokens?: number;
  request_top_p?: number;
  eval_results?: GenAiEvalResult[];
}

const SAMPLE_SYSTEM = "You are a research assistant. Cite sources. Be concise.";
const SAMPLE_USER_INPUT =
  "Compare mixture-of-experts vs dense transformer efficiency at >100B params.";

const SPECS: SpanSpec[] = [
  {
    start_offset_ms: 0,
    duration_ms: 8420,
    operation_name: "invoke_agent",
    label: "research_agent.run",
    agent_name: "research_agent",
  },
  {
    start_offset_ms: 12,
    duration_ms: 1840,
    operation_name: "chat.completions",
    provider_name: "openai",
    request_model: "gpt-4o",
    response_model: "gpt-4o-2024-08-06",
    input_tokens: 412,
    output_tokens: 188,
    cache_creation: 96,
    cache_read: 0,
    finish_reasons: ["tool_calls"],
    request_temperature: 0.2,
    request_max_tokens: 2048,
    request_top_p: 1.0,
    agent_name: "research_agent",
    system_instructions: JSON.stringify(SAMPLE_SYSTEM),
    input_messages: JSON.stringify([
      { role: "system", content: SAMPLE_SYSTEM },
      { role: "user", content: SAMPLE_USER_INPUT },
    ]),
    output_messages: JSON.stringify([
      {
        role: "assistant",
        content: "I'll search for recent benchmarks before answering.",
      },
    ]),
    tool_definitions: JSON.stringify([
      { name: "search_documents", description: "Vector search over arxiv corpus" },
      { name: "http_get", description: "Fetch a URL and return cleaned text" },
    ]),
  },
  {
    start_offset_ms: 1880,
    duration_ms: 142,
    operation_name: "execute_tool",
    tool_name: "search_documents",
    tool_type: "function",
    tool_call_id: "call_a1b2",
    label: "search_documents",
    agent_name: "research_agent",
  },
  {
    start_offset_ms: 2050,
    duration_ms: 2210,
    operation_name: "messages",
    provider_name: "anthropic",
    request_model: "claude-3-5-sonnet-20241022",
    response_model: "claude-3-5-sonnet-20241022",
    input_tokens: 3120,
    output_tokens: 642,
    cache_creation: 1880,
    cache_read: 1240,
    finish_reasons: ["end_turn"],
    request_temperature: 0.3,
    request_max_tokens: 4096,
    request_top_p: 0.95,
    agent_name: "research_agent",
    input_messages: JSON.stringify([
      {
        role: "user",
        content: [
          { type: "text", text: "Synthesize findings from these 12 retrieved chunks." },
        ],
      },
    ]),
    output_messages: JSON.stringify([
      {
        role: "assistant",
        content: [
          {
            type: "text",
            text: "MoE architectures achieve ~2.4× tokens/joule at 175B vs dense baselines.",
          },
        ],
      },
    ]),
    eval_results: [
      {
        name: "Relevance",
        score_label: "relevant",
        score_value: 4.0,
        explanation: "Directly addresses comparison criteria.",
        response_id: "msg_01abc",
      },
      {
        name: "Faithfulness",
        score_label: "faithful",
        score_value: 0.92,
        explanation: "All claims attributable to retrieved sources.",
        response_id: "msg_01abc",
      },
    ],
  },
  {
    start_offset_ms: 4280,
    duration_ms: 612,
    operation_name: "execute_tool",
    tool_name: "http_get",
    tool_type: "function",
    tool_call_id: "call_c3d4",
    error_type: "request_timeout",
    status_code: 1,
    label: "http_get arxiv.org",
    agent_name: "research_agent",
  },
  {
    start_offset_ms: 4910,
    duration_ms: 612,
    operation_name: "execute_tool",
    tool_name: "http_get",
    tool_type: "function",
    tool_call_id: "call_c3d4_retry",
    label: "http_get arxiv.org (retry)",
    agent_name: "research_agent",
  },
  {
    start_offset_ms: 5540,
    duration_ms: 92,
    operation_name: "embeddings",
    provider_name: "openai",
    request_model: "text-embedding-3-large",
    response_model: "text-embedding-3-large",
    input_tokens: 1840,
    output_tokens: 0,
    agent_name: "research_agent",
  },
  {
    start_offset_ms: 7480,
    duration_ms: 920,
    operation_name: "chat.completions",
    provider_name: "openai",
    request_model: "gpt-4o-mini",
    response_model: "gpt-4o-mini-2024-07-18",
    input_tokens: 980,
    output_tokens: 240,
    cache_creation: 0,
    cache_read: 720,
    finish_reasons: ["stop"],
    request_temperature: 0.0,
    request_max_tokens: 512,
    label: "summarize_for_user",
    agent_name: "research_agent",
    input_messages: JSON.stringify([
      { role: "system", content: "Summarize findings in 5 bullets." },
    ]),
    output_messages: JSON.stringify([
      {
        role: "assistant",
        content:
          "• MoE models 2.4× tokens/joule vs dense\n• Routing overhead amortized at batch >32\n• Memory bandwidth bottleneck above 8 experts",
      },
    ]),
    eval_results: [
      {
        name: "Conciseness",
        score_label: "concise",
        score_value: 5.0,
        explanation: "5 bullets, all on topic.",
        response_id: "chatcmpl-summary-001",
      },
    ],
  },
];

const CONVERSATION_ID = "conv-mock-research-44";
const SERVICE_NAME = "research-agent-mock";

function buildSpan(
  trace_id: string,
  span_id: string,
  spec: SpanSpec,
  traceStart: Date,
): GenAiSpanRecord {
  const start = new Date(traceStart.getTime() + spec.start_offset_ms);
  const end = new Date(start.getTime() + spec.duration_ms);
  return {
    trace_id,
    span_id,
    service_name: SERVICE_NAME,
    start_time: start.toISOString(),
    end_time: end.toISOString(),
    duration_ms: spec.duration_ms,
    status_code: spec.status_code ?? 0,
    operation_name: spec.operation_name,
    provider_name: spec.provider_name ?? null,
    request_model: spec.request_model ?? null,
    response_model: spec.response_model ?? null,
    response_id: spec.request_model ? `resp_${span_id.slice(0, 6)}` : null,
    input_tokens: spec.input_tokens ?? null,
    output_tokens: spec.output_tokens ?? null,
    cache_creation_input_tokens: spec.cache_creation ?? null,
    cache_read_input_tokens: spec.cache_read ?? null,
    finish_reasons: spec.finish_reasons ?? [],
    output_type: spec.finish_reasons?.length ? "text" : null,
    conversation_id: CONVERSATION_ID,
    agent_name: spec.agent_name ?? null,
    agent_id: spec.agent_name ? `agent-${spec.agent_name}` : null,
    agent_description: null,
    agent_version: "0.1.0",
    data_source_id: null,
    tool_name: spec.tool_name ?? null,
    tool_type: spec.tool_type ?? null,
    tool_call_id: spec.tool_call_id ?? null,
    request_temperature: spec.request_temperature ?? null,
    request_max_tokens: spec.request_max_tokens ?? null,
    request_top_p: spec.request_top_p ?? null,
    request_choice_count: null,
    request_seed: null,
    request_frequency_penalty: null,
    request_presence_penalty: null,
    request_stop_sequences: [],
    server_address:
      spec.provider_name === "openai"
        ? "api.openai.com"
        : spec.provider_name === "anthropic"
          ? "api.anthropic.com"
          : null,
    server_port: spec.provider_name ? 443 : null,
    error_type: spec.error_type ?? null,
    openai_api_type: spec.provider_name === "openai" ? "responses" : null,
    openai_service_tier: spec.provider_name === "openai" ? "default" : null,
    label: spec.label ?? null,
    entity_id: null,
    input_messages: spec.input_messages ?? null,
    output_messages: spec.output_messages ?? null,
    system_instructions: spec.system_instructions ?? null,
    tool_definitions: spec.tool_definitions ?? null,
    eval_results: spec.eval_results ?? [],
  };
}

export function getMockGenAiTraceMetrics(
  traceId: string,
  spanIds: string[],
): GenAiTraceMetricsResponse {
  const traceStart = new Date(Date.now() - 60_000);
  const usableSpecs = SPECS.slice(0, spanIds.length);
  const spans = usableSpecs.map((spec, i) =>
    buildSpan(traceId, spanIds[i], spec, traceStart),
  );

  if (spans.length === 0) {
    return emptyResponse(traceId);
  }

  const totalIn = spans.reduce((a, s) => a + (s.input_tokens ?? 0), 0);
  const totalOut = spans.reduce((a, s) => a + (s.output_tokens ?? 0), 0);
  const totalCacheCreate = spans.reduce(
    (a, s) => a + (s.cache_creation_input_tokens ?? 0),
    0,
  );
  const totalCacheRead = spans.reduce(
    (a, s) => a + (s.cache_read_input_tokens ?? 0),
    0,
  );
  const errorCount = spans.filter((s) => s.error_type).length;

  const tokenBuckets: GenAiTokenBucket[] = [
    {
      bucket_start: traceStart.toISOString(),
      total_input_tokens: totalIn,
      total_output_tokens: totalOut,
      total_cache_creation_tokens: totalCacheCreate,
      total_cache_read_tokens: totalCacheRead,
      span_count: spans.length,
      error_rate: errorCount / spans.length,
    },
  ];

  const opMap = new Map<string, GenAiOperationBreakdown>();
  for (const s of spans) {
    if (!s.operation_name) continue;
    const existing = opMap.get(s.operation_name) ?? {
      operation_name: s.operation_name,
      provider_name: s.provider_name,
      span_count: 0,
      avg_duration_ms: 0,
      total_input_tokens: 0,
      total_output_tokens: 0,
      error_rate: 0,
    };
    existing.span_count += 1;
    existing.avg_duration_ms += s.duration_ms;
    existing.total_input_tokens += s.input_tokens ?? 0;
    existing.total_output_tokens += s.output_tokens ?? 0;
    if (s.error_type) existing.error_rate += 1;
    opMap.set(s.operation_name, existing);
  }
  const operations = Array.from(opMap.values()).map((o) => ({
    ...o,
    avg_duration_ms: o.avg_duration_ms / o.span_count,
    error_rate: o.error_rate / o.span_count,
  }));

  const modelMap = new Map<string, GenAiModelUsage>();
  for (const s of spans) {
    const key = s.response_model ?? s.request_model;
    if (!key) continue;
    const existing = modelMap.get(key) ?? {
      model: key,
      provider_name: s.provider_name,
      span_count: 0,
      total_input_tokens: 0,
      total_output_tokens: 0,
      p50_duration_ms: s.duration_ms,
      p95_duration_ms: s.duration_ms,
      error_rate: 0,
    };
    existing.span_count += 1;
    existing.total_input_tokens += s.input_tokens ?? 0;
    existing.total_output_tokens += s.output_tokens ?? 0;
    modelMap.set(key, existing);
  }
  const models = Array.from(modelMap.values());

  const toolMap = new Map<string, GenAiToolActivity>();
  const toolTimeSeries: ToolTimeBucket[] = [];
  for (const s of spans) {
    if (!s.tool_name) continue;
    const existing = toolMap.get(s.tool_name) ?? {
      tool_name: s.tool_name,
      tool_type: s.tool_type,
      call_count: 0,
      avg_duration_ms: 0,
      error_rate: 0,
    };
    existing.call_count += 1;
    existing.avg_duration_ms += s.duration_ms;
    if (s.error_type) existing.error_rate += 1;
    toolMap.set(s.tool_name, existing);
    toolTimeSeries.push({
      bucket_start: s.start_time,
      tool_name: s.tool_name,
      tool_type: s.tool_type,
      call_count: 1,
      avg_duration_ms: s.duration_ms,
      error_rate: s.error_type ? 1 : 0,
    });
  }
  const toolAggregates = Array.from(toolMap.values()).map((t) => ({
    ...t,
    avg_duration_ms: t.avg_duration_ms / t.call_count,
    error_rate: t.error_rate / t.call_count,
  }));

  const errorMap = new Map<string, number>();
  for (const s of spans) {
    if (s.error_type) errorMap.set(s.error_type, (errorMap.get(s.error_type) ?? 0) + 1);
  }
  const errors: GenAiErrorCount[] = Array.from(errorMap.entries()).map(([k, v]) => ({
    error_type: k,
    count: v,
  }));

  const agents: GenAiAgentActivity[] = [
    {
      agent_name: "research_agent",
      agent_id: "agent-research_agent",
      conversation_id: CONVERSATION_ID,
      span_count: spans.length,
      total_input_tokens: totalIn,
      total_output_tokens: totalOut,
      last_seen: spans[spans.length - 1].end_time,
    },
  ];

  const totalCost =
    (totalIn / 1e6) * 3.0 +
    (totalOut / 1e6) * 15.0 +
    (totalCacheCreate / 1e6) * 3.75 +
    (totalCacheRead / 1e6) * 0.3;

  const costByModel: ModelCostBreakdown[] = models.map((m) => ({
    model: m.model,
    total_input_tokens: m.total_input_tokens,
    total_output_tokens: m.total_output_tokens,
    total_cache_creation_tokens: 0,
    total_cache_read_tokens: 0,
    total_cost: (m.total_input_tokens / 1e6) * 3.0 + (m.total_output_tokens / 1e6) * 15.0,
  }));

  const dashboardBuckets: AgentMetricBucket[] = [
    {
      bucket_start: traceStart.toISOString(),
      span_count: spans.length,
      error_count: errorCount,
      error_rate: errorCount / spans.length,
      avg_duration_ms:
        spans.reduce((a, s) => a + s.duration_ms, 0) / spans.length,
      p50_duration_ms: 612,
      p95_duration_ms: 2210,
      p99_duration_ms: spans[0]?.duration_ms ?? 0,
      total_input_tokens: totalIn,
      total_output_tokens: totalOut,
      total_cache_creation_tokens: totalCacheCreate,
      total_cache_read_tokens: totalCacheRead,
      total_cost: totalCost,
    },
  ];

  const agent_dashboard: AgentDashboardResponse = {
    summary: {
      total_requests: spans.length,
      avg_duration_ms:
        spans.reduce((a, s) => a + s.duration_ms, 0) / spans.length,
      p50_duration_ms: 612,
      p95_duration_ms: 2210,
      p99_duration_ms: spans[0]?.duration_ms ?? 0,
      overall_error_rate: errorCount / spans.length,
      total_input_tokens: totalIn,
      total_output_tokens: totalOut,
      total_cache_creation_tokens: totalCacheCreate,
      total_cache_read_tokens: totalCacheRead,
      unique_agent_count: 1,
      unique_conversation_count: 1,
      cost_by_model: costByModel,
    },
    buckets: dashboardBuckets,
  };

  return {
    trace_id: traceId,
    has_genai_spans: true,
    spans,
    span_limit: 500,
    spans_truncated: false,
    sensitive_content_redacted: false,
    token_metrics: { buckets: tokenBuckets },
    operation_breakdown: { operations },
    model_usage: { models },
    agent_activity: { agents },
    agent_dashboard,
    tool_dashboard: {
      aggregates: toolAggregates,
      time_series: toolTimeSeries,
    },
    error_breakdown: { errors },
  };
}

function emptyResponse(trace_id: string): GenAiTraceMetricsResponse {
  return {
    trace_id,
    has_genai_spans: false,
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
        p50_duration_ms: null,
        p95_duration_ms: null,
        p99_duration_ms: null,
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
