import { type RequestHandler, json } from "@sveltejs/kit";
import { getGroupedMetrics } from "$lib/server/experiment/utils";

/** Get a page of LLM monitoring records
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { experiments, selectedMetrics } = await request.json();
  const response = await getGroupedMetrics(fetch, experiments, selectedMetrics);
  return json(response);
};
