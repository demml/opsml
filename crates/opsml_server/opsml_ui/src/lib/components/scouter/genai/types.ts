export type BucketInterval =
  | "second"
  | "minute"
  | "hour"
  | "day"
  | "week"
  | "month"
  | "year";

export interface ModelPricing {
  input_per_million: number;
  output_per_million: number;
  cache_creation_per_million: number;
  cache_read_per_million: number;
}

export interface GenAiMetricsRequest {
  service_name: string | null;
  start_time: string;
  end_time: string;
  bucket_interval: BucketInterval;
  operation_name: string | null;
  provider_name: string | null;
  model: string | null;
  agent_name: string | null;
}

export interface GenAiSpanFilters {
  service_name: string | null;
  start_time: string | null;
  end_time: string | null;
  operation_name: string | null;
  provider_name: string | null;
  model: string | null;
  conversation_id: string | null;
  agent_name: string | null;
  tool_name: string | null;
  error_type: string | null;
  limit: number | null;
}

export interface GenAiTraceMetricsRequest {
  start_time: string | null;
  end_time: string | null;
  bucket_interval: BucketInterval;
  model_pricing: Record<string, ModelPricing>;
  span_limit: number;
  include_sensitive_content: boolean;
}

export interface AgentDashboardRequest {
  service_name: string | null;
  entity_id: string | null;
  start_time: string;
  end_time: string;
  bucket_interval: BucketInterval;
  agent_name: string | null;
  provider_name: string | null;
  model_pricing: Record<string, ModelPricing>;
}

export interface ToolDashboardRequest {
  service_name: string | null;
  start_time: string;
  end_time: string;
  bucket_interval: BucketInterval;
  agent_name: string | null;
  provider_name: string | null;
  model: string | null;
}

export interface GenAiDashboardRequest {
  service_name: string | null;
  entity_id: string | null;
  start_time: string;
  end_time: string;
  bucket_interval: BucketInterval;
  agent_name: string | null;
  provider_name: string | null;
  operation_name: string | null;
  model: string | null;
  model_pricing: Record<string, ModelPricing>;
}

export interface AgentActivityQuery {
  agent_name: string | null;
}

export interface ConversationQuery {
  start_time: string | null;
  end_time: string | null;
}

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
  service_name: string;
  start_time: string;
  end_time: string | null;
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
  entity_id: string | null;
  input_messages: string | null;
  output_messages: string | null;
  system_instructions: string | null;
  tool_definitions: string | null;
  eval_results: GenAiEvalResult[];
}

export interface GenAiSpansResponse {
  spans: GenAiSpanRecord[];
}

export interface GenAiTokenBucket {
  bucket_start: string;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cache_creation_tokens: number;
  total_cache_read_tokens: number;
  span_count: number;
  error_rate: number;
}

export interface GenAiTokenMetricsResponse {
  buckets: GenAiTokenBucket[];
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

export interface GenAiAgentActivity {
  agent_name: string | null;
  agent_id: string | null;
  conversation_id: string | null;
  span_count: number;
  total_input_tokens: number;
  total_output_tokens: number;
  last_seen: string | null;
}

export interface GenAiAgentActivityResponse {
  agents: GenAiAgentActivity[];
}

export interface GenAiToolActivity {
  tool_name: string | null;
  tool_type: string | null;
  call_count: number;
  avg_duration_ms: number;
  error_rate: number;
}

export interface GenAiToolActivityResponse {
  tools: GenAiToolActivity[];
}

export interface GenAiErrorCount {
  error_type: string;
  count: number;
}

export interface GenAiErrorBreakdownResponse {
  errors: GenAiErrorCount[];
}

export interface AgentMetricBucket {
  bucket_start: string;
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
  total_cost: null;
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

export interface ToolTimeBucket {
  bucket_start: string;
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

export interface AppliedFilters {
  service_name: string | null;
  entity_id: string | null;
  agent_name: string | null;
  provider_name: string | null;
  operation_name: string | null;
  model: string | null;
  start_time: string;
  end_time: string;
  bucket_interval: BucketInterval;
}

export interface AvailableFilters {
  agents: GenAiAgentActivity[];
  providers: string[];
  models: string[];
  operations: string[];
}

export interface DashboardMetadata {
  generated_at: string;
  schema_version: number;
  total_spans: number;
}

export interface GenAiDashboardResponse {
  applied_filters: AppliedFilters;
  available_filters: AvailableFilters;
  metadata: DashboardMetadata;
  token_metrics: GenAiTokenMetricsResponse;
  operation_breakdown: GenAiOperationBreakdownResponse;
  model_usage: GenAiModelUsageResponse;
  agent_dashboard: AgentDashboardResponse;
  tool_dashboard: ToolDashboardResponse;
  error_breakdown: GenAiErrorBreakdownResponse;
  buckets_truncated: boolean;
}

export interface GenAiTraceMetricsResponse {
  trace_id: string;
  has_genai_spans: boolean;
  spans: GenAiSpanRecord[];
  span_limit: number;
  spans_truncated: boolean;
  sensitive_content_redacted: boolean;
  token_metrics: GenAiTokenMetricsResponse;
  operation_breakdown: GenAiOperationBreakdownResponse;
  model_usage: GenAiModelUsageResponse;
  agent_activity: GenAiAgentActivityResponse;
  agent_dashboard: AgentDashboardResponse;
  tool_dashboard: ToolDashboardResponse;
  error_breakdown: GenAiErrorBreakdownResponse;
}
