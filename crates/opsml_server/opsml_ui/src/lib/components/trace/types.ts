import type { DateTime } from "$lib/types";

export interface TraceListItem {
  trace_id: string;
  service_name: string;
  scope: string;
  root_operation: string;
  start_time: DateTime;
  end_time: DateTime | null;
  duration_ms: number | null;
  status_code: number;
  status_message: string | null;
  span_count: number;
  has_errors: boolean;
  error_count: number;
  created_at: DateTime;
  resource_attributes: Attribute[];
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
  service_name?: string;
  has_errors?: boolean;
  status_code?: number;
  start_time?: DateTime;
  end_time?: DateTime;
  limit?: number;
  cursor_start_time?: DateTime;
  cursor_trace_id?: string;
  direction?: "next" | "previous";
  attribute_filters?: string[];
  tace_ids?: string[];
}

export interface TraceCursor {
  start_time: DateTime;
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

function getAttributeValueType(
  value: any
): "null" | "boolean" | "number" | "string" | "array" | "object" {
  if (value === null) return "null";
  if (typeof value === "boolean") return "boolean";
  if (typeof value === "number") return "number";
  if (typeof value === "string") return "string";
  if (Array.isArray(value)) return "array";
  if (typeof value === "object") return "object";
  return "null";
}

/**
 * Format an attribute value for display based on its type
 */
export function formatAttributeValue(value: any): string {
  const type = getAttributeValueType(value);

  switch (type) {
    case "null":
      return "null";
    case "boolean":
      return value.toString();
    case "number":
      return value.toString();
    case "string":
      return value;
    case "array":
    case "object":
      return JSON.stringify(value, null, 2);
    default:
      return String(value);
  }
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
  service_name: string;
}

export interface TraceSpansResponse {
  spans: TraceSpan[];
}

export interface TraceRequest {
  trace_id: string;
  service_name?: string;
}

export interface TraceMetricsRequest {
  service_name?: string;
  start_time?: DateTime;
  end_time?: DateTime;
  bucket_interval?: string;
  attribute_filters?: string[];
}

export interface TraceMetricsResponse {
  metrics: TraceMetricBucket[];
}

export interface TimeRange {
  label: string;
  value: string;
  startTime: DateTime;
  endTime: DateTime;
  bucketInterval: string;
}

/**
 * Filters for trace data queries
 */
export interface TracePageFilter {
  filters: TraceFilters;
  bucket_interval: string;
  selected_range: string;
}

export const SPAN_ERROR = "span.error";
export const EXCEPTION_TRACEBACK = "exception.traceback";
