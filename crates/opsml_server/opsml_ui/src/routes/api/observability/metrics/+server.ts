import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceRequest,
  TraceSpansResponse,
  TraceMetricsRequest,
  TraceMetricsResponse,
} from "$lib/components/card/trace/types";
import { getTraceMetrics } from "$lib/server/trace/utils";

/**
 * POST endpoint for fetching trace metrics
 * @param request - SvelteKit request containing TraceMetricsRequest in body
 * @param fetch - SvelteKit fetch function for server-side requests
 * @returns JSON response with either metrics data or error message
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const filters: TraceMetricsRequest = await request.json();
    const response: TraceMetricsResponse = await getTraceMetrics(
      fetch,
      filters
    );

    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching metrics:", error);

    return json(
      {
        response: null,
        error:
          error instanceof Error ? error.message : "Failed to fetch metrics",
      },
      { status: 500 }
    );
  }
};
