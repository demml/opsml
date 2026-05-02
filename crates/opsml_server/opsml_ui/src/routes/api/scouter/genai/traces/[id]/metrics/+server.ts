import { type RequestHandler, json } from "@sveltejs/kit";
import { RoutePaths } from "$lib/components/api/routes";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export const POST: RequestHandler = async ({ request, fetch, params }) => {
  if (!params.id) {
    return new Response("Missing trace id", { status: 400 });
  }

  try {
    const body = await request.json();
    const response = await createOpsmlClient(fetch).post(
      `${RoutePaths.GENAI_TRACE_METRICS}/${encodeURIComponent(params.id)}/metrics`,
      body,
    );
    if (!response.ok) {
      return new Response(await response.text(), { status: response.status });
    }
    return json(await response.json());
  } catch {
    return new Response("Internal server error", { status: 500 });
  }
};
