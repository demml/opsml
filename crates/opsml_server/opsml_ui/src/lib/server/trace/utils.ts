import type {
  TraceFilters,
  TracePaginationResponse,
} from "$lib/components/card/trace/types";
import { createOpsmlClient } from "../api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";

export async function getTracePage(
  fetch: typeof globalThis.fetch,
  filters: TraceFilters
): Promise<TracePaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.LLM_RECORD_PAGE,
    filters
  );
  return (await response.json()) as TracePaginationResponse;
}
