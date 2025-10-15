import { type RequestHandler, json } from "@sveltejs/kit";
import { getGroupedMetrics } from "$lib/server/experiment/utils";

/** Get the grouped metrics for a set of experiments
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { experiments, selectedMetrics } = await request.json();
  const response = await getGroupedMetrics(fetch, experiments, selectedMetrics);
  return json(response);
};
