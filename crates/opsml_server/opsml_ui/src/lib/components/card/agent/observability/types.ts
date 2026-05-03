import type { DateTime } from "$lib/types";

export interface ModelPricing {
  input_per_million: number;
  output_per_million: number;
  cache_creation_per_million: number;
  cache_read_per_million: number;
}

// ── Composite GenAI dashboard request ────────────────────────────────────────

/**
 * Request body for `POST /opsml/api/scouter/genai/dashboard`.
 *
 * Scope by setting EITHER `service_name` (service-wide view, e.g. an AgentCard)
 * OR `entity_id` (a single Scouter entity such as an `AgentEvalProfile`).
 * Sending both is allowed but unusual; the backend treats them as AND.
 */
export interface GenAiDashboardRequest {
  service_name: string | null;
  entity_id: string | null;
  start_time: DateTime;
  end_time: DateTime;
  bucket_interval: string;
  agent_name: string | null;
  provider_name: string | null;
  operation_name: string | null;
  model: string | null;
  model_pricing: Record<string, ModelPricing>;
}

// ── Existing per-panel types (still used inside the composite response) ──────

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

export interface GenAiTokenBucket {
  bucket_start: DateTime;
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

// ── Composite response types ─────────────────────────────────────────────────

/**
 * Echoes the filters the server actually applied. Mirrors the request body so
 * the UI can confirm scope without tracking request state.
 */
export interface AppliedFilters {
  service_name: string | null;
  entity_id: string | null;
  agent_name: string | null;
  provider_name: string | null;
  operation_name: string | null;
  model: string | null;
  start_time: DateTime;
  end_time: DateTime;
  bucket_interval: string;
}

/**
 * Distinct filter values present in the query window. Always service-scoped
 * (NOT narrowed by `agent_name`) so dropdowns stay populated during drilldown.
 */
export interface AvailableFilters {
  agents: GenAiAgentActivity[];
  providers: string[];
  models: string[];
  operations: string[];
}

export interface DashboardMetadata {
  generated_at: DateTime;
  schema_version: number;
  total_spans: number;
}

/**
 * Composite dashboard response from `POST /opsml/api/scouter/genai/dashboard`.
 * Single round-trip — populates every dashboard panel.
 */
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

/**
 * Lightweight descriptor of an `AgentEvalProfile` used to populate the
 * Profile dropdown in the dashboard FilterBar. Sourced from prompt cards
 * associated with the surrounding agent service.
 */
export interface EvalProfileOption {
  uid: string;
  alias: string | null;
  name: string;
}

/**
 * Bundle handed to `AgentGenAiDashboard.svelte`. Wraps the composite dashboard
 * response together with the time range that was queried so the UI can
 * recompute relative ranges on refresh.
 */
export interface AgentGenAiBundle {
  dashboard: GenAiDashboardResponse;
  range: {
    start_time: string;
    end_time: string;
    bucket_interval: string;
    selected_range: string;
  };
  /**
   * Eval profiles available for entity_id scoping. Empty for prompt-card
   * scope (entity_id is locked to that prompt's profile) and for agents
   * with no associated prompt cards that carry an eval profile.
   */
  eval_profiles: EvalProfileOption[];
}
