import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceRequest,
  TraceSpansResponse,
} from "$lib/components/trace/types";
import { getTraceSpans } from "$lib/server/trace/utils";

/**
 * POST endpoint for fetching trace spans
 * @param request - SvelteKit request containing TraceRequest in body
 * @param fetch - SvelteKit fetch function for server-side requests
 * @returns JSON response with either span data or error message
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const filters: TraceRequest = await request.json();
    const response: TraceSpansResponse = await getTraceSpans(fetch, filters);

    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching spans:", error);

    return json(
      {
        response: null,
        error: error instanceof Error ? error.message : "Failed to fetch spans",
      },
      { status: 500 }
    );
  }
};
