import type { DateTime } from "$lib/types";

export interface TraceListItem {
  trace_id: string;
  space: string;
  name: string;
  version: string;
  scope: string;
  service_name: string | null;
  root_operation: string | null;
  start_time: DateTime;
  end_time: DateTime | null;
  duration_ms: number | null;
  status_code: number;
  status_message: string | null;
  span_count: number | null;
  has_errors: boolean;
  error_count: number;
  created_at: DateTime;
}

export interface TraceMetricBucket {
  bucket_start: DateTime;
  trace_count: number;
  avg_duration_ms: number;
  p50_duration_ms: number | null;
  p95_duration_ms: number | null;
  p99_duration_ms: number | null;
  error_rate: number;
}

export interface TraceFilters {
  space?: string;
  name?: string;
  version?: string;
  service_name?: string;
  has_errors?: boolean;
  status_code?: number;
  start_time?: DateTime;
  end_time?: DateTime;
  limit?: number;
  cursor_created_at?: DateTime;
  cursor_trace_id?: string;
  direction?: "next" | "previous";
}

export interface TraceCursor {
  created_at: DateTime;
  trace_id: string;
}

export type MetricType =
  | "trace_count"
  | "avg_duration_ms"
  | "p95_duration_ms"
  | "error_rate";

export interface MetricConfig {
  label: string;
  color: string;
  formatter: (val: number) => string;
}

export interface TracePaginationResponse {
  items: TraceListItem[];
  has_next: boolean;
  next_cursor?: TraceCursor;
  has_previous: boolean;
  previous_cursor?: TraceCursor;
}

export interface Attribute {
  key: string;
  value: any; // JSON value from serde_json::Value
}

export interface SpanEvent {
  timestamp: DateTime;
  name: string;
  attributes: Attribute[];
  dropped_attributes_count: number;
}

export interface SpanLink {
  trace_id: string;
  span_id: string;
  trace_state: string;
  attributes: Attribute[];
  dropped_attributes_count: number;
}

export interface TraceSpan {
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  span_name: string;
  span_kind: string | null;
  start_time: DateTime;
  end_time: DateTime | null;
  duration_ms: number | null;
  status_code: number;
  status_message: string | null;
  attributes: Attribute[];
  events: SpanEvent[];
  links: SpanLink[];
  depth: number;
  path: string[];
  root_span_id: string;
  span_order: number;
  input: string | null;
  output: string | null;
}

export interface TraceDetail {
  trace_id: string;
  spans: TraceSpan[];
  root_span: TraceSpan;
  total_duration_ms: number;
  service_count: number;
  span_count: number;
  error_count: number;
  critical_path_duration_ms: number;
}
