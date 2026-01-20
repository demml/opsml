import { type RequestHandler, json } from "@sveltejs/kit";
import { getDriftProfiles } from "$lib/server/scouter/drift/utils";

/** Get a page of latest metrics for drift profiles
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { uid, driftMap, registryType } = await request.json();
  const response = await getDriftProfiles(fetch, uid, driftMap, registryType);
  return json(response);
};
