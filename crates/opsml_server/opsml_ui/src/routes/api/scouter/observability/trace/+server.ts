import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  TraceFilters,
  TracePaginationResponse,
} from "$lib/components/trace/types";
import { getTracePage } from "$lib/server/trace/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import { validateTraceFilters } from "$lib/components/trace/validation";

/**
 * Proxies trace page requests after validating the shared FilterClause body.
 *
 * Dev mocks and Scouter receive the same clause-shaped request contract so the
 * UI does not keep a legacy scalar-filter translation layer alive.
 */
export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const body = await request.json();
  const validation = validateTraceFilters(body);
  if (!validation.ok) {
    return json({ response: null, error: validation.error }, { status: 400 });
  }
  const filters: TraceFilters = validation.value;

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
