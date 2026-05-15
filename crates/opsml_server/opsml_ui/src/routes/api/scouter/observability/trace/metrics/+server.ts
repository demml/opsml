import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceMetricsRequest,
  TraceMetricsResponse,
} from "$lib/components/trace/types";
import { getTraceMetrics } from "$lib/server/trace/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import { validateTraceMetricsRequest } from "$lib/components/trace/validation";

/**
 * Proxies trace metrics requests after validating time bounds and FilterClause.
 *
 * Metrics require explicit `start_time` and `end_time` because both Scouter and
 * the mock evaluator aggregate over a bounded interval.
 */
export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const input = await request.json();
  const validation = validateTraceMetricsRequest(input);

  if (!validation.ok) {
    return json(
      { response: null, error: validation.error },
      { status: 400 },
    );
  }
  const body: TraceMetricsRequest = validation.value;

  if (isDevMockEnabled(cookies)) {
    const { getMockTraceMetrics } = await import("$lib/server/trace/mockData");
    return json({ response: getMockTraceMetrics(body), error: null });
  }

  try {
    const response: TraceMetricsResponse = await getTraceMetrics(
      fetch,
      { bucket_interval: "1 hours", ...body },
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
