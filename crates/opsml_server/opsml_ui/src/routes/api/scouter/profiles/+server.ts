import { type RequestHandler, json } from "@sveltejs/kit";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";

export const GET: RequestHandler = async ({ fetch, url }) => {
  const query = url.searchParams.toString();
  const path = query ? `${RoutePaths.PROFILES_LIST}?${query}` : RoutePaths.PROFILES_LIST;
  const response = await createOpsmlClient(fetch).get(path);
  return json(await response.json());
};
