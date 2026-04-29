import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceRequest,
  TraceSpansResponse,
} from "$lib/components/trace/types";
import { getTraceSpans } from "$lib/server/trace/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";

export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const filters: TraceRequest = await request.json();

  if (isDevMockEnabled(cookies)) {
    const { getMockTraceSpans } = await import("$lib/server/trace/mockData");
    return json({ response: getMockTraceSpans(filters), error: null });
  }

  try {
    const response: TraceSpansResponse = await getTraceSpans(fetch, filters);
    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching trace spans:", error);
    return json(
      {
        response: null,
        error: error instanceof Error ? error.message : "Failed to fetch trace spans",
      },
      { status: 500 },
    );
  }
};
