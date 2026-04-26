import type { TraceFilters, TraceFacetResponse } from "$lib/components/trace/types";
import {
  deriveTraceFacetsFromSpans,
  getTraceSpansFromFilters,
} from "$lib/server/trace/utils";

/**
 * /opsml/api/scouter/trace/spans/filters currently returns TraceSpansResponse (raw spans),
 * not pre-aggregated facets. This helper derives service/status/attribute-key facet counts
 * from that spans payload for the observability filter sidebar.
 */
export async function getTraceFacets(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters,
): Promise<TraceFacetResponse> {
  const spans = await getTraceSpansFromFilters(fetch, filters);
  return deriveTraceFacetsFromSpans(spans);
}
