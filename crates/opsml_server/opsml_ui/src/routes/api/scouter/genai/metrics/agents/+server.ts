import { type RequestHandler, json } from "@sveltejs/kit";
import { RoutePaths } from "$lib/components/api/routes";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export const POST: RequestHandler = async ({ request, fetch, url }) => {
  try {
    const body = await request.json();
    const query = url.searchParams.toString();
    const path =
      query.length > 0 ? `${RoutePaths.GENAI_AGENTS}?${query}` : RoutePaths.GENAI_AGENTS;
    const response = await createOpsmlClient(fetch).post(path, body);
    if (!response.ok) {
      return new Response(await response.text(), { status: response.status });
    }
    return json(await response.json());
  } catch {
    return new Response("Internal server error", { status: 500 });
  }
};
