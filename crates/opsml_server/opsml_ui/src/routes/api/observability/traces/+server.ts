import { type RequestHandler, json } from "@sveltejs/kit";
import { getLLMRecordPage } from "$lib/server/card/monitoring/utils";
import type { TraceFilters } from "$lib/components/card/trace/types";

/** Get a paginated traces
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { service_info, status, cursor }: TraceFilters = await request.json();
  const response = await getLLMRecordPage(fetch, service_info, status, cursor);
  return json(response);
};
