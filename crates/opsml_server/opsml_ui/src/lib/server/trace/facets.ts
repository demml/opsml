import type { TraceFilters, TraceFacetsResponse } from "$lib/components/trace/types";
import { ServerPaths } from "$lib/components/api/routes";

export async function getTraceFacets(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters,
): Promise<TraceFacetsResponse> {
  const { cursor_start_time, cursor_trace_id, direction, ...facetFilters } = filters;
  const response = await fetch(ServerPaths.TRACE_FACETS, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(facetFilters),
  });
  if (!response.ok) {
    throw new Error(`Facets request failed: ${response.status}`);
  }
  const { response: data, error } = await response.json();
  if (error) throw new Error(error);
  return data as TraceFacetsResponse;
}
