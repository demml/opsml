import type {
  TraceFilters,
  TraceMetricsResponse,
  TracePaginationResponse,
  TraceRequest,
  TraceMetricsRequest,
  TraceSpansResponse,
} from "$lib/components/trace/types";
import { createOpsmlClient } from "../api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";

export async function getTracePage(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters
): Promise<TracePaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.TRACE_PAGE,
    filters
  );
  return (await response.json()) as TracePaginationResponse;
}

export async function getTraceSpans(
  fetch: typeof globalThis.fetch,
  traceRequest: TraceRequest
): Promise<TraceSpansResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.TRACE_SPANS,
    traceRequest
  );
  return (await response.json()) as TraceSpansResponse;
}

export async function getTraceMetrics(
  fetch: typeof globalThis.fetch,
  metricsRequest: TraceMetricsRequest
): Promise<TraceMetricsResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.TRACE_METRICS,
    metricsRequest
  );
  return (await response.json()) as TraceMetricsResponse;
}
