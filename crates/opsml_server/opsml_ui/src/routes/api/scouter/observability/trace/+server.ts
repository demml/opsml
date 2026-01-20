import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceFilters,
  TracePaginationResponse,
} from "$lib/components/trace/types";
import { getTracePage } from "$lib/server/trace/utils";

/**
 * POST endpoint for fetching paginated traces
 * @param request - SvelteKit request containing TraceFilters in body
 * @param fetch - SvelteKit fetch function for server-side requests
 * @returns JSON response with either trace data or error message
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const filters: TraceFilters = await request.json();
    const response: TracePaginationResponse = await getTracePage(
      fetch,
      filters
    );

    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching traces:", error);

    return json(
      {
        response: null,
        error:
          error instanceof Error ? error.message : "Failed to fetch traces",
      },
      { status: 500 }
    );
  }
};
