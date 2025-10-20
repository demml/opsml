import { type RequestHandler, json } from "@sveltejs/kit";
import { getHardwareMetrics } from "$lib/server/experiment/utils";

/** Get the hardware metrics for a set of experiments
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { uid } = await request.json();
  const response = await getHardwareMetrics(fetch, uid);
  return json(response);
};
