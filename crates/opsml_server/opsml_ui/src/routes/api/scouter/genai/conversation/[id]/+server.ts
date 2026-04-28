import { type RequestHandler, json } from "@sveltejs/kit";
import { RoutePaths } from "$lib/components/api/routes";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export const GET: RequestHandler = async ({ fetch, params, url }) => {
  if (!params.id) {
    return new Response("Missing conversation id", { status: 400 });
  }
  try {
    const query = url.searchParams.toString();
    const path = `${RoutePaths.GENAI_CONVERSATION}/${encodeURIComponent(params.id)}`;
    const response = await createOpsmlClient(fetch).get(
      query.length > 0 ? `${path}?${query}` : path,
    );
    if (!response.ok) {
      return new Response(await response.text(), { status: response.status });
    }
    return json(await response.json());
  } catch {
    return new Response("Internal server error", { status: 500 });
  }
};
