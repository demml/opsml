import { type RequestHandler, json } from "@sveltejs/kit";
import { dev } from "$app/environment";
import type {
  TraceRequest,
  TraceSpansResponse,
} from "$lib/components/trace/types";
import { getTraceSpans } from "$lib/server/trace/utils";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const filters: TraceRequest = await request.json();

  // DEV ONLY: static mock data. This branch is dead in production builds.
  if (dev) {
    const { getMockTraceSpans } = await import("$lib/server/trace/mockData");
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
    const { getMockTraceSpans } = await import("$lib/server/trace/mockData");
    return json({ response: getMockTraceSpans(filters), error: null });
  }
};
