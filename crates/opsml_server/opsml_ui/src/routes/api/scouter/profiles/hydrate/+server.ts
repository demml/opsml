import { type RequestHandler, json } from "@sveltejs/kit";
import { getDriftProfiles } from "$lib/server/scouter/drift/utils";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const { uid, driftMap, registryType } = await request.json();
  const response = await getDriftProfiles(fetch, uid, driftMap, registryType);
  return json(response);
};
