import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceMetricsRequest,
  TraceMetricsResponse,
} from "$lib/components/trace/types";
import { getTraceMetrics } from "$lib/server/trace/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";

export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const requestBody: TraceMetricsRequest = await request.json();

  if (isDevMockEnabled(cookies)) {
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
