import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceMetricsRequest,
  TraceMetricsResponse,
} from "$lib/components/trace/types";
import { getTraceMetrics } from "$lib/server/trace/utils";
import { logger } from "$lib/server/logger";

/**
 * POST endpoint for fetching trace metrics
 * @param request - SvelteKit request containing TraceMetricsRequest in body
 * @param fetch - SvelteKit fetch function for server-side requests
 * @returns JSON response with either metrics data or error message
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const requestBody: TraceMetricsRequest = await request.json();

    logger.info(
      "Received request for trace metrics " + JSON.stringify(requestBody)
    );

    const response: TraceMetricsResponse = await getTraceMetrics(
      fetch,
      requestBody
    );

    logger.debug("Successfully fetched trace metrics");

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
