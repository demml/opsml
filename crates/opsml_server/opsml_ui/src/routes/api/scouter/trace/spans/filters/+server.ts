import { type RequestHandler, json } from "@sveltejs/kit";
import type { TraceFacetResponse, TraceFilters } from "$lib/components/trace/types";
import { getTraceFacets } from "$lib/server/trace/facets";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import { deriveTraceFacetsFromSpans } from "$lib/server/trace/utils";

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
    const response = deriveTraceFacetsFromSpans({ spans });
    return json({ response, error: null });
  }

  try {
    const response: TraceFacetResponse = await getTraceFacets(fetch, filters);
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
