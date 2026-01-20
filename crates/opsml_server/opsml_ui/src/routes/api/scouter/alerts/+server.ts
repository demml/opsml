import { type RequestHandler, json } from "@sveltejs/kit";
import { getDriftAlerts } from "$lib/server/scouter/drift/utils";
import type { DriftAlertPaginationRequest } from "$lib/components/card/monitoring/alert/types";

/** Get a page of recent drift alerts
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const alertRequest: DriftAlertPaginationRequest = await request.json();
  const response = await getDriftAlerts(fetch, alertRequest);
  return json(response);
};
