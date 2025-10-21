import { type RequestHandler, json } from "@sveltejs/kit";
import { getCardMetricNames } from "$lib/server/experiment/utils";

/** Get the metric names for a given experiment
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { uid } = await request.json();
  const response = await getCardMetricNames(fetch, uid);
  return json(response);
};
