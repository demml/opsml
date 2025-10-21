import { type RequestHandler, json } from "@sveltejs/kit";
import { getRecentExperiments } from "$lib/server/experiment/utils";

/** Get recent experiments for a space and name
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { space, name, version } = await request.json();
  const response = await getRecentExperiments(fetch, space, name, version);
  return json(response);
};
