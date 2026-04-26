import { type RequestHandler, json } from "@sveltejs/kit";
import { RoutePaths } from "$lib/components/api/routes";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export const GET: RequestHandler = async ({ fetch, params, url }) => {
  const query = url.searchParams.toString();
  const path = `${RoutePaths.GENAI_CONVERSATION}/${encodeURIComponent(params.id)}`;
  const response = await createOpsmlClient(fetch).get(
    query.length > 0 ? `${path}?${query}` : path,
  );
  return json(await response.json());
};
