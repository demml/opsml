import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceFilters,
  TracePaginationResponse,
} from "$lib/components/trace/types";
import { getTracePage } from "$lib/server/trace/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";

export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const filters: TraceFilters = await request.json();

  if (isDevMockEnabled(cookies)) {
    const { getMockTracePage } = await import("$lib/server/trace/mockData");
    return json({ response: getMockTracePage(filters), error: null });
  }

  try {
    const response: TracePaginationResponse = await getTracePage(
      fetch,
      filters,
    );
    return json({ response, error: null });
  } catch (error) {
    console.error("Error fetching traces:", error);
    return json(
      {
        response: null,
        error: error instanceof Error ? error.message : "Failed to fetch traces",
      },
      { status: 500 },
    );
  }
};
