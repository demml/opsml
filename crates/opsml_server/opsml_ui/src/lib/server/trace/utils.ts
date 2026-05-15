import type {
  TraceFacetResponse,
  TraceFilters,
  TraceMetricsResponse,
  TracePaginationResponse,
  TraceRequest,
  TraceMetricsRequest,
  TraceSpansResponse,
  TraceFacetsResponse,
} from "$lib/components/trace/types";
import { createOpsmlClient } from "../api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";

/**
 * Error raised by trace server helpers when the backend returns a non-OK
 * response and the SvelteKit route should preserve that HTTP status.
 */
export class TraceServerError extends Error {
  constructor(
    message: string,
    public status = 500,
  ) {
    super(message);
    this.name = "TraceServerError";
  }
}

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
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.TRACE_METRICS,
    metricsRequest
  );
  return (await response.json()) as TraceMetricsResponse;
}

/**
 * Fetch trace facets through the shared OpsML server client.
 *
 * Keeping this transport logic in the server helper layer matches the other
 * trace BFF calls and keeps `+server.ts` focused on request parsing, mock-mode
 * branching, and response enveloping.
 */
export async function getTraceFacets(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters,
): Promise<TraceFacetsResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.TRACE_FACETS,
    filters,
  );
  if (!response.ok) {
    const errorBody = await response.text();
    throw new TraceServerError(
      errorBody || `Facets request failed: ${response.status}`,
      response.status,
    );
  }
  return (await response.json()) as TraceFacetsResponse;
}

export async function getTraceSpansFromFilters(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters,
): Promise<TraceSpansResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.TRACE_SPANS_FILTERS,
    filters,
  );
  return (await response.json()) as TraceSpansResponse;
}

export async function getTraceSpansById(
  fetch: typeof globalThis.fetch,
  traceId: string,
): Promise<TraceSpansResponse> {
  const response = await createOpsmlClient(fetch).get(
    `${RoutePaths.TRACE_SPANS_BY_ID}/${traceId}/spans`,
  );
  return (await response.json()) as TraceSpansResponse;
}

export function deriveTraceFacetsFromSpans(
  spansResponse: TraceSpansResponse,
): TraceFacetResponse {
  const serviceCounts = new Map<string, number>();
  const statusCounts = new Map<string, number>();
  const attributeKeyCounts = new Map<string, number>();

  const spansByTrace = new Map<string, TraceSpansResponse["spans"]>();
  for (const span of spansResponse.spans) {
    const existing = spansByTrace.get(span.trace_id) ?? [];
    existing.push(span);
    spansByTrace.set(span.trace_id, existing);
  }

  for (const traceSpans of spansByTrace.values()) {
    const rootSpan = traceSpans.find((span) => span.parent_span_id === null);
    const representative = rootSpan ?? traceSpans[0];

    if (representative?.service_name) {
      serviceCounts.set(
        representative.service_name,
        (serviceCounts.get(representative.service_name) ?? 0) + 1,
      );
    }

    if (representative) {
      const statusKey = String(representative.status_code);
      statusCounts.set(statusKey, (statusCounts.get(statusKey) ?? 0) + 1);
    }

    const traceAttributeKeys = new Set<string>();
    for (const span of traceSpans) {
      for (const attribute of span.attributes) {
        if (attribute.key) {
          traceAttributeKeys.add(attribute.key);
        }
      }
    }
    for (const key of traceAttributeKeys) {
      attributeKeyCounts.set(key, (attributeKeyCounts.get(key) ?? 0) + 1);
    }
  }

  const toFacetCounts = (countMap: Map<string, number>) =>
    Array.from(countMap.entries())
      .map(([value, count]) => ({ value, count }))
      .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));

  return {
    services: toFacetCounts(serviceCounts),
    status_codes: toFacetCounts(statusCounts),
    attribute_keys: toFacetCounts(attributeKeyCounts),
  };
}
