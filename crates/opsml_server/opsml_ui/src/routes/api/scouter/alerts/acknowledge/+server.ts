import { type RequestHandler, json } from "@sveltejs/kit";
import { acknowledgeAlert } from "$lib/server/scouter/drift/utils";

/** Get a page of recent drift alerts
 */
export const PUT: RequestHandler = async ({ request, fetch }) => {
  const { id, space } = await request.json();
  const response = await acknowledgeAlert(fetch, id, space);
  return json(response);
};
