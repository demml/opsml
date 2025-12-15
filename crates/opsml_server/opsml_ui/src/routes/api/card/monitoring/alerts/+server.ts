import { type RequestHandler, json } from "@sveltejs/kit";
import { getDriftAlerts } from "$lib/server/card/monitoring/utils";

/** Get a page of recent drift alerts
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { uid, timeRange, active } = await request.json();
  const response = await getDriftAlerts(fetch, uid, timeRange, active);
  return json(response);
};
