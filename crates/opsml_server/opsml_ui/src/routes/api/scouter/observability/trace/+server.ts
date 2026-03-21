import { type RequestHandler, json } from "@sveltejs/kit";
import { dev } from "$app/environment";
import type {
  TraceFilters,
  TracePaginationResponse,
} from "$lib/components/trace/types";
import { getTracePage } from "$lib/server/trace/utils";
import { getMockTracePage } from "$lib/server/trace/mockData";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const filters: TraceFilters = await request.json();

  if (dev) {
    return json({ response: getMockTracePage(filters), error: null });
  }

  try {
    const response: TracePaginationResponse = await getTracePage(
      fetch,
      filters,
    );
    return json({ response, error: null });
  } catch (error) {
    console.warn(
      "Scouter backend unavailable, serving mock trace data:",
      error instanceof Error ? error.message : error,
    );
    return json({ response: getMockTracePage(filters), error: null });
  }
};
