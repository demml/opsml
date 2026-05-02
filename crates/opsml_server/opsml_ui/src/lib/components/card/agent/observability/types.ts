import type { DateTime } from "$lib/types";

export interface ModelPricing {
  input_per_million: number;
  output_per_million: number;
  cache_creation_per_million: number;
  cache_read_per_million: number;
}

export interface AgentDashboardRequest {
  service_name: string | null;
  start_time: DateTime;
  end_time: DateTime;
  bucket_interval: string;
  agent_name: string | null;
  provider_name: string | null;
  model_pricing: Record<string, ModelPricing>;
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

export interface ToolDashboardRequest {
  service_name: string | null;
  start_time: DateTime;
  end_time: DateTime;
  bucket_interval: string;
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

export interface GenAiMetricsRequest {
  service_name: string | null;
  start_time: DateTime;
  end_time: DateTime;
  bucket_interval: string;
  operation_name: string | null;
  provider_name: string | null;
  model: string | null;
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

export interface GenAiModelUsageResponse {
  models: GenAiModelUsage[];
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

export interface GenAiOperationBreakdownResponse {
  operations: GenAiOperationBreakdown[];
}

export interface GenAiErrorCount {
  error_type: string;
  count: number;
}

export interface GenAiErrorBreakdownResponse {
  errors: GenAiErrorCount[];
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

export interface GenAiAgentActivityResponse {
  agents: GenAiAgentActivity[];
}

export interface AgentGenAiBundle {
  agent_dashboard: AgentDashboardResponse;
  tool_dashboard: ToolDashboardResponse;
  model_usage: GenAiModelUsage[];
  operation_breakdown: GenAiOperationBreakdown[];
  errors: GenAiErrorCount[];
  agents: GenAiAgentActivity[];
  range: {
    start_time: string;
    end_time: string;
    bucket_interval: string;
    selected_range: string;
  };
}
