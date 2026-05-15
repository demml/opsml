import { type RequestHandler, json } from "@sveltejs/kit";
import type { TraceFacetsResponse, TraceFilters } from "$lib/components/trace/types";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import { getTraceFacets, TraceServerError } from "$lib/server/trace/utils";
import { validateTraceFilters } from "$lib/components/trace/validation";

/**
 * Returns trace facet counts for the current validated FilterClause body.
 *
 * Unsupported or malformed filter payloads are rejected before the request can
 * hit dev mocks or Scouter, which keeps facet refresh behavior deterministic.
 */
export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const body = await request.json();
  const validation = validateTraceFilters(body);
  if (!validation.ok) {
    return json({ response: null, error: validation.error }, { status: 400 });
  }
  const filters: TraceFilters = validation.value;

  if (isDevMockEnabled(cookies)) {
    const { getMockTraceFacets } = await import("$lib/server/trace/mockData");
    return json({ response: getMockTraceFacets(filters), error: null });
  }

  try {
    const response: TraceFacetsResponse = await getTraceFacets(fetch, filters);
    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching trace facets:", error);
    return json(
      {
        response: null,
        error: error instanceof Error ? error.message : "Failed to fetch trace facets",
      },
      { status: error instanceof TraceServerError ? error.status : 500 },
    );
  }
};
