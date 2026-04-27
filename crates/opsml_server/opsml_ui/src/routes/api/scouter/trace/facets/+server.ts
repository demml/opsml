import { type RequestHandler, json } from "@sveltejs/kit";
import type { TraceFacetsResponse, TraceFilters } from "$lib/components/trace/types";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import { deriveTraceFacetsFromSpans } from "$lib/server/trace/utils";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";

export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const filters: TraceFilters = await request.json();

  if (isDevMockEnabled(cookies)) {
    const { getMockTracePage, getMockTraceSpans } = await import("$lib/server/trace/mockData");
    const page = getMockTracePage({ ...filters, limit: 200 });
    const spans = page.items.flatMap((trace) =>
      getMockTraceSpans({
        trace_id: trace.trace_id,
        service_name: trace.service_name,
        start_time: trace.start_time,
        end_time: trace.end_time ?? undefined,
      }).spans,
    );
    const oldFacets = deriveTraceFacetsFromSpans({ spans });
    const response: TraceFacetsResponse = {
      services: oldFacets.services.map((f) => ({ value: f.value, trace_count: f.count })),
      status_codes: oldFacets.status_codes.map((f) => ({ value: f.value, trace_count: f.count })),
      total_count: oldFacets.services.reduce((sum, f) => sum + f.count, 0),
    };
    return json({ response, error: null });
  }

  try {
    const resp = await createOpsmlClient(fetch).post(RoutePaths.TRACE_FACETS, filters);
    const response = (await resp.json()) as TraceFacetsResponse;
    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching trace facets:", error);
    return json(
      {
        response: null,
        error: error instanceof Error ? error.message : "Failed to fetch trace facets",
      },
      { status: 500 },
    );
  }
};
