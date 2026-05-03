// Mock-only subset of scouter genai contracts. Mirrors
// crates/scouter_types/src/trace/genai.rs response shapes used by the
// agent metrics dashboard mockups. Will be replaced by the production
// types module once the dashboard design is locked.

import type { DateTime } from "$lib/types";

export interface GenAiTokenBucket {
  bucket_start: DateTime;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cache_creation_tokens: number;
  total_cache_read_tokens: number;
  span_count: number;
  error_rate: number;
}

export interface AgentMetricBucket {
  bucket_start: DateTime;
  span_count: number;
  error_count: number;
  error_rate: number;
  avg_duration_ms: number;
  p50_duration_ms: number | null;
  p95_duration_ms: number | null;
  p99_duration_ms: number | null;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cache_creation_tokens: number;
  total_cache_read_tokens: number;
  total_cost: number | null;
}

export interface ModelCostBreakdown {
  model: string;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cache_creation_tokens: number;
  total_cache_read_tokens: number;
  total_cost: number | null;
}

export interface AgentDashboardSummary {
  total_requests: number;
  avg_duration_ms: number;
  p50_duration_ms: number | null;
  p95_duration_ms: number | null;
  p99_duration_ms: number | null;
  overall_error_rate: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cache_creation_tokens: number;
  total_cache_read_tokens: number;
  unique_agent_count: number;
  unique_conversation_count: number;
  cost_by_model: ModelCostBreakdown[];
}

export interface AgentDashboardResponse {
  summary: AgentDashboardSummary;
  buckets: AgentMetricBucket[];
}

export interface GenAiModelUsage {
  model: string;
  provider_name: string | null;
  span_count: number;
  total_input_tokens: number;
  total_output_tokens: number;
  p50_duration_ms: number | null;
  p95_duration_ms: number | null;
  error_rate: number;
}

export interface GenAiOperationBreakdown {
  operation_name: string;
  provider_name: string | null;
  span_count: number;
  avg_duration_ms: number;
  total_input_tokens: number;
  total_output_tokens: number;
  error_rate: number;
}

export interface GenAiToolActivity {
  tool_name: string | null;
  tool_type: string | null;
  call_count: number;
  avg_duration_ms: number;
  error_rate: number;
}

export interface ToolTimeBucket {
  bucket_start: DateTime;
  tool_name: string | null;
  tool_type: string | null;
  call_count: number;
  avg_duration_ms: number;
  error_rate: number;
}

export interface ToolDashboardResponse {
  aggregates: GenAiToolActivity[];
  time_series: ToolTimeBucket[];
}

export interface GenAiErrorCount {
  error_type: string;
  count: number;
}

export interface GenAiAgentActivity {
  agent_name: string | null;
  agent_id: string | null;
  conversation_id: string | null;
  span_count: number;
  total_input_tokens: number;
  total_output_tokens: number;
  last_seen: DateTime | null;
}

export interface MockMetricsBundle {
  agent_dashboard: AgentDashboardResponse;
  tool_dashboard: ToolDashboardResponse;
  model_usage: GenAiModelUsage[];
  operation_breakdown: GenAiOperationBreakdown[];
  errors: GenAiErrorCount[];
  agents: GenAiAgentActivity[];
}

// ── Trace-scoped span detail (mirrors scouter_types::GenAiSpanRecord) ────────

export interface GenAiEvalResult {
  name: string;
  score_label: string | null;
  score_value: number | null;
  explanation: string | null;
  response_id: string | null;
}

export interface GenAiSpanRecord {
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  service_name: string;
  start_time: DateTime;
  end_time: DateTime | null;
  duration_ms: number;
  status_code: number;
  operation_name: string | null;
  provider_name: string | null;
  request_model: string | null;
  response_model: string | null;
  response_id: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  cache_creation_input_tokens: number | null;
  cache_read_input_tokens: number | null;
  finish_reasons: string[];
  output_type: string | null;
  conversation_id: string | null;
  agent_name: string | null;
  agent_id: string | null;
  agent_description: string | null;
  agent_version: string | null;
  data_source_id: string | null;
  tool_name: string | null;
  tool_type: string | null;
  tool_call_id: string | null;
  request_temperature: number | null;
  request_max_tokens: number | null;
  request_top_p: number | null;
  request_choice_count: number | null;
  request_seed: number | null;
  request_frequency_penalty: number | null;
  request_presence_penalty: number | null;
  request_stop_sequences: string[];
  server_address: string | null;
  server_port: number | null;
  error_type: string | null;
  openai_api_type: string | null;
  openai_service_tier: string | null;
  label: string | null;
  input_messages: string | null;
  output_messages: string | null;
  system_instructions: string | null;
  tool_definitions: string | null;
  eval_results: GenAiEvalResult[];
}

export interface GenAiTraceMetricsResponse {
  trace_id: string;
  has_genai_spans: boolean;
  spans: GenAiSpanRecord[];
  span_limit: number;
  spans_truncated: boolean;
  sensitive_content_redacted: boolean;
  token_metrics: { buckets: GenAiTokenBucket[] };
  operation_breakdown: { operations: GenAiOperationBreakdown[] };
  model_usage: { models: GenAiModelUsage[] };
  agent_activity: { agents: GenAiAgentActivity[] };
  agent_dashboard: AgentDashboardResponse;
  tool_dashboard: ToolDashboardResponse;
  error_breakdown: { errors: GenAiErrorCount[] };
}
