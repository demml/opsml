import { type RequestHandler, json } from "@sveltejs/kit";
import { getDriftAlerts } from "$lib/server/card/monitoring/utils";

/** Get a page of recent drift alerts
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { space, name, version, timeInterval, active } = await request.json();
  const response = await getDriftAlerts(
    fetch,
    space,
    name,
    version,
    timeInterval,
    active
  );
  return json(response);
};
