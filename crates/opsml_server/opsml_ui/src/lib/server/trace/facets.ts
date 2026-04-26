import type { TraceFilters, TraceFacetResponse } from "$lib/components/trace/types";
import {
  deriveTraceFacetsFromSpans,
  getTraceSpansFromFilters,
} from "$lib/server/trace/utils";

const FACET_SPAN_LIMIT = 500;

export async function getTraceFacets(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters,
): Promise<TraceFacetResponse> {
  const limit = Math.min(filters.limit ?? FACET_SPAN_LIMIT, FACET_SPAN_LIMIT);
  const spans = await getTraceSpansFromFilters(fetch, {
    ...filters,
    limit,
    cursor_start_time: undefined,
    cursor_trace_id: undefined,
    direction: undefined,
  });
  return deriveTraceFacetsFromSpans(spans);
}
