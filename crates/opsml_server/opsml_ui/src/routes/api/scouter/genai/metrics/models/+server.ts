import { type RequestHandler, json } from "@sveltejs/kit";
import { RoutePaths } from "$lib/components/api/routes";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const body = await request.json();
    const response = await createOpsmlClient(fetch).post(
      RoutePaths.GENAI_MODELS,
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
