import { type RequestHandler, json } from "@sveltejs/kit";
import type {
  ScouterEntityIdResponse,
  ScouterEntityIdTagsRequest,
} from "$lib/components/tags/types";
import { getScouterEntityIdFromTags } from "$lib/server/tags/utils";

/**
 * POST endpoint for fetching entity ID from tags
 * @param request - SvelteKit request containing TraceMetricsRequest in body
 * @param fetch - SvelteKit fetch function for server-side requests
 * @returns JSON response with either entity ID data or error message
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const requestBody: ScouterEntityIdTagsRequest = await request.json();

    const response: ScouterEntityIdResponse = await getScouterEntityIdFromTags(
      fetch,
      requestBody
    );

    return json({ response, error: null });
  } catch (error) {
    return json(
      {
        response: null,
        error:
          error instanceof Error
            ? error.message
            : "Failed to fetch entity ID from tags",
      },
      { status: 500 }
    );
  }
};
