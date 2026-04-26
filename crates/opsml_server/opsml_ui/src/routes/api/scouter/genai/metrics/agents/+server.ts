import { type RequestHandler, json } from "@sveltejs/kit";
import { RoutePaths } from "$lib/components/api/routes";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export const POST: RequestHandler = async ({ request, fetch, url }) => {
  const body = await request.json();
  const query = url.searchParams.toString();
  const path =
    query.length > 0 ? `${RoutePaths.GENAI_AGENTS}?${query}` : RoutePaths.GENAI_AGENTS;

  const response = await createOpsmlClient(fetch).post(path, body);
  return json(await response.json());
};
