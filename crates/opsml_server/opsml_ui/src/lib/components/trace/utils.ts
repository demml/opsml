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
  TimeRange,
} from "./types";
import {
  MODEL_KEY_ATTR,
  DATA_KEY_ATTR,
  AGENT_KEY_ATTR,
  MCP_KEY_ATTR,
  EXPERIMENT_KEY_ATTR,
  PROMPT_KEY_ATTR,
  SERVICE_KEY_ATTR,
} from "./types";
import { createInternalApiClient } from "$lib/api/internalClient";
import { RegistryType } from "$lib/utils";
import { TimeInterval } from "$lib/components/scouter/types";
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
    start_time: lastTrace.start_time,
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
 * Parse JSON input/output safely
 */
export function parseSpanJson(jsonString: string | null | object): any {
  if (!jsonString) return null;

  if (typeof jsonString === "object") {
    return jsonString;
  }

  if (typeof jsonString === "string") {
    try {
      return JSON.parse(jsonString);
    } catch (error) {
      return jsonString;
    }
  }

  return null;
}

/**
 * Formats attribute values for UI display, truncating long strings
 * to maintain layout integrity in Neo-Brutalist components.
 */
export function formatAttributeValue(value: any): string {
  if (value === null || value === undefined) return "null";

  let result: string;

  if (typeof value === "object") {
    result = JSON.stringify(value);
  } else {
    result = String(value);
  }

  // Truncate to first 32 elements/characters
  return result.length > 32 ? result.substring(0, 32) + "..." : result;
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
    case "15min-live":
      startTime = new Date(now.getTime() - 15 * 60 * 1000);
      bucketInterval = "1 minutes";
      break;
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

/**
 * Get the key attribute name for a given registry type
 * @param registryType - The type of registry
 * @returns The key attribute string for the registry type
 */
export function getCardKeyAttribute(registryType: RegistryType): string {
  switch (registryType) {
    case RegistryType.Model:
      return MODEL_KEY_ATTR;
    case RegistryType.Experiment:
      return EXPERIMENT_KEY_ATTR;
    case RegistryType.Data:
      return DATA_KEY_ATTR;
    case RegistryType.Prompt:
      return PROMPT_KEY_ATTR;
    case RegistryType.Service:
      return SERVICE_KEY_ATTR;
    case RegistryType.Mcp:
      return MCP_KEY_ATTR;
    case RegistryType.Agent:
      return AGENT_KEY_ATTR;
    default:
      // Exhaustiveness check - TypeScript will error if a case is missing
      const _exhaustive: never = registryType;
      throw new Error(`Unhandled registry type: ${_exhaustive}`);
  }
}

/**
 * Convert a TimeRange to a TimeInterval enum value based on the range label.
 * Maps the predefined labels from TimeRangeFilter to TimeInterval enum values.
 */
export function timeRangeToInterval(range: TimeRange): TimeInterval {
  switch (range.label) {
    case "Live (15min)":
    case "Past 15 Minutes":
      return TimeInterval.FifteenMinutes;
    case "Past 30 Minutes":
      return TimeInterval.ThirtyMinutes;
    case "Past 1 Hour":
      return TimeInterval.OneHour;
    case "Past 4 Hours":
      return TimeInterval.FourHours;
    case "Past 12 Hours":
      return TimeInterval.TwelveHours;
    case "Past 24 Hours":
      return TimeInterval.TwentyFourHours;
    case "Past 7 Days":
      return TimeInterval.SevenDays;
    case "Past 30 Days":
      return TimeInterval.ThirtyDays;
    case "Custom Range":
    default:
      return TimeInterval.Custom;
  }
}
