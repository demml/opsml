import { type RequestHandler, json } from "@sveltejs/kit";
import { RoutePaths } from "$lib/components/api/routes";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const body = await request.json();
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GENAI_MODELS,
    body,
  );
  return json(await response.json());
};
