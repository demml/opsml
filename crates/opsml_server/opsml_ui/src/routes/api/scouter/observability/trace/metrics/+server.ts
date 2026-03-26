import { type RequestHandler, json } from "@sveltejs/kit";
import { dev } from "$app/environment";
import type {
  TraceMetricsRequest,
  TraceMetricsResponse,
} from "$lib/components/trace/types";
import { getTraceMetrics } from "$lib/server/trace/utils";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const requestBody: TraceMetricsRequest = await request.json();

  // DEV ONLY: static mock data. This branch is dead in production builds.
  if (dev) {
    const { getMockTraceMetrics } = await import("$lib/server/trace/mockData");
    return json({ response: getMockTraceMetrics(requestBody), error: null });
  }

  try {
    const response: TraceMetricsResponse = await getTraceMetrics(
      fetch,
      requestBody,
    );
    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching trace metrics:", error);
    return json(
      {
        response: null,
        error: error instanceof Error ? error.message : "Failed to fetch trace metrics",
      },
      { status: 500 },
    );
  }
};
