import { type RequestHandler, json } from "@sveltejs/kit";
import { updateDriftProfile } from "$lib/server/card/monitoring/utils";

/** Get a page of recent drift alerts
 */
export const PUT: RequestHandler = async ({ request, fetch }) => {
  const { update_request } = await request.json();
  const response = await updateDriftProfile(fetch, update_request);
  return json(response);
};
