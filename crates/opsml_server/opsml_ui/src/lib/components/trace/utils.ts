import { ServerPaths } from "../api/routes";
import type {
  TraceListItem,
  TraceCursor,
  TraceSpan,
  Attribute,
  TraceMetricsRequest,
  TraceMetricsResponse,
  TraceSpansResponse,
  TraceRequest,
  TraceFilters,
  TracePaginationResponse,
} from "./types";
import { createInternalApiClient } from "$lib/api/internalClient";

/**
 * Extract the next pagination cursor from a list of traces.
 * Returns undefined if there are no traces or we've reached the end.
 */
export function getNextCursor(
  traces: TraceListItem[],
  requestedLimit: number
): TraceCursor | undefined {
  if (traces.length === 0 || traces.length < requestedLimit) {
    return undefined;
  }

  const lastTrace = traces[traces.length - 1];
  return {
    created_at: lastTrace.created_at,
    trace_id: lastTrace.trace_id,
  };
}

/**
 * Format duration in milliseconds to human-readable string.
 */
export function formatDuration(ms: number | null): string {
  if (ms === null) return "N/A";

  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
  return `${(ms / 60000).toFixed(2)}m`;
}

/**
 * Format error rate as percentage.
 */
export function formatErrorRate(rate: number): string {
  return `${(rate * 100).toFixed(2)}%`;
}

/**
 * Get status badge variant based on trace status.
 */
export function getStatusVariant(
  statusCode: number,
  hasErrors: boolean
): "success" | "warning" | "error" {
  if (hasErrors || statusCode >= 400) return "error";
  if (statusCode >= 300) return "warning";
  return "success";
}

/**
 * Get unique services from trace list.
 */
export function getUniqueServices(traces: TraceListItem[]): string[] {
  const services = new Set<string>();
  traces.forEach((trace) => {
    if (trace.service_name) services.add(trace.service_name);
  });
  return Array.from(services).sort();
}

/**
 * Get unique operations from trace list.
 */
export function getUniqueOperations(traces: TraceListItem[]): string[] {
  const operations = new Set<string>();
  traces.forEach((trace) => {
    if (trace.root_operation) operations.add(trace.root_operation);
  });
  return Array.from(operations).sort();
}

/**
 * Calculate aggregate metrics from trace list.
 */
export function calculateAggregateMetrics(traces: TraceListItem[]) {
  const total = traces.length;
  const errors = traces.filter((t) => t.has_errors).length;
  const durations = traces
    .map((t) => t.duration_ms)
    .filter((d): d is number => d !== null)
    .sort((a, b) => a - b);

  return {
    totalTraces: total,
    errorCount: errors,
    errorRate: total > 0 ? errors / total : 0,
    avgDuration:
      durations.length > 0
        ? durations.reduce((sum, d) => sum + d, 0) / durations.length
        : 0,
    p50Duration:
      durations.length > 0
        ? durations[Math.floor(durations.length * 0.5)]
        : null,
    p95Duration:
      durations.length > 0
        ? durations[Math.floor(durations.length * 0.95)]
        : null,
    p99Duration:
      durations.length > 0
        ? durations[Math.floor(durations.length * 0.99)]
        : null,
  };
}

/**
 * Format timestamp to locale string.
 */
export function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

/**
 * Format timestamp for chart axis.
 */
export function formatChartTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Get attribute value by key from span attributes
 */
export function getAttributeValue(attributes: Attribute[], key: string): any {
  const attr = attributes.find((a) => a.key === key);
  return attr?.value;
}

/**
 * Get service name from span attributes
 */
export function getServiceName(span: TraceSpan): string {
  return getAttributeValue(span.attributes, "service.name") || "unknown";
}

/**
 * Parse JSON input/output safely
 */
export function parseSpanJson(jsonString: string | null): any {
  if (!jsonString) return null;
  try {
    return JSON.parse(jsonString);
  } catch {
    return null;
  }
}

/**
 * Format attribute value for display
 */
export function formatAttributeValue(value: any): string {
  if (value === null || value === undefined) return "null";
  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

export function getSpanKindIcon(kind: string | null): string {
  if (!kind) return "●";

  const icons: Record<string, string> = {
    SERVER: "🌐",
    CLIENT: "📡",
    PRODUCER: "📤",
    CONSUMER: "📥",
    INTERNAL: "⚙️",
  };

  return icons[kind] || "●";
}

/**
 * Check if span has errors based on status code
 */
export function hasSpanError(span: TraceSpan): boolean {
  // OpenTelemetry status codes: 0 = UNSET, 1 = OK, 2 = ERROR
  return span.status_code === 2;
}

export function getHttpStatusCode(span: TraceSpan): number | null {
  const statusCode = getAttributeValue(span.attributes, "http.status_code");
  return typeof statusCode === "number" ? statusCode : null;
}

export async function getServerTraceMetrics(
  fetch: typeof globalThis.fetch,
  metricsRequest: TraceMetricsRequest
): Promise<TraceMetricsResponse> {
  console.log("Fetching TraceMetrics with request:", metricsRequest);

  const resp = await createInternalApiClient(fetch).post(
    ServerPaths.TRACE_METRICS,
    metricsRequest
  );

  const { response, error } = await resp.json();

  if (error) {
    throw new Error(error);
  }

  return response as TraceMetricsResponse;
}

export async function getServerTraceSpans(
  fetch: typeof globalThis.fetch,
  traceRequest: TraceRequest
): Promise<TraceSpansResponse> {
  const resp = await createInternalApiClient(fetch).post(
    ServerPaths.TRACE_SPANS,
    traceRequest
  );

  const { response, error } = await resp.json();

  if (error) {
    throw new Error(error);
  }

  return response as TraceSpansResponse;
}

export async function getServerTracePage(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters
): Promise<TracePaginationResponse> {
  const resp = await createInternalApiClient(fetch).post(
    ServerPaths.TRACE_PAGE,
    filters
  );

  const { response, error } = await resp.json();

  if (error) {
    throw new Error(error);
  }

  return response as TracePaginationResponse;
}

export function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    const encodedValue = parts.pop()?.split(";").shift();
    // Always decode to handle browser encoding
    return encodedValue ? decodeURIComponent(encodedValue) : null;
  }
  return null;
}

export function setCookie(name: string, value: string): void {
  const maxAge = 60 * 60; // 1 hour
  // Don't manually encode - browser handles it
  document.cookie = `${name}=${value}; path=/; max-age=${maxAge}; samesite=lax`;
}

/**
 * Calculate dynamic time range based on relative interval
 */
export function calculateTimeRange(range: string): {
  startTime: string;
  endTime: string;
  bucketInterval: string;
} {
  const now = new Date();
  let startTime: Date;
  let bucketInterval: string;

  switch (range) {
    case "15min":
      startTime = new Date(now.getTime() - 15 * 60 * 1000);
      bucketInterval = "1 minutes";
      break;
    case "30min":
      startTime = new Date(now.getTime() - 30 * 60 * 1000);
      bucketInterval = "1 minutes";
      break;
    case "1hour":
      startTime = new Date(now.getTime() - 60 * 60 * 1000);
      bucketInterval = "2 minutes";
      break;
    case "4hours":
      startTime = new Date(now.getTime() - 4 * 60 * 60 * 1000);
      bucketInterval = "10 minutes";
      break;
    case "12hours":
      startTime = new Date(now.getTime() - 12 * 60 * 60 * 1000);
      bucketInterval = "30 minutes";
      break;
    case "24hours":
      startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      bucketInterval = "1 hours";
      break;
    case "7days":
      startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      bucketInterval = "6 hours";
      break;
    case "30days":
      startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      bucketInterval = "1 days";
      break;
    default:
      startTime = new Date(now.getTime() - 15 * 60 * 1000);
      bucketInterval = "1 minutes";
  }

  return {
    startTime: startTime.toISOString(),
    endTime: now.toISOString(),
    bucketInterval,
  };
}
