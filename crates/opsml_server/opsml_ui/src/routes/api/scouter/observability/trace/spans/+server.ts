import { type RequestHandler, json } from "@sveltejs/kit";
import { dev } from "$app/environment";
import type {
  TraceRequest,
  TraceSpansResponse,
} from "$lib/components/trace/types";
import { getTraceSpans } from "$lib/server/trace/utils";
import { getMockTraceSpans } from "$lib/server/trace/mockData";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const filters: TraceRequest = await request.json();

  if (dev) {
    return json({ response: getMockTraceSpans(filters), error: null });
  }

  try {
    const response: TraceSpansResponse = await getTraceSpans(fetch, filters);
    return json({ response, error: null });
  } catch (error) {
    console.warn(
      "Scouter backend unavailable, serving mock span data:",
      error instanceof Error ? error.message : error,
    );
    return json({ response: getMockTraceSpans(filters), error: null });
  }
};
