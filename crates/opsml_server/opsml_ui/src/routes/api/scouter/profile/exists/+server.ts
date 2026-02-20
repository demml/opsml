import { type RequestHandler, json } from "@sveltejs/kit";
import { getDriftProfileExists } from "$lib/components/scouter/utils";
import type { GetProfileExistsRequest } from "$lib/components/scouter/types";

/**
 * POST endpoint for checking if a drift profile exists
 * @param request - SvelteKit request containing GetProfileExistsRequest in body
 * @param fetch - SvelteKit fetch function for server-side requests
 * @returns JSON response with either boolean result or error message
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const filters: GetProfileExistsRequest = await request.json();
    const response: boolean = await getDriftProfileExists(fetch, filters);

    return json({ response, error: null });
  } catch (error) {
    console.error("Error checking drift profile existence:", error);

    return json(
      {
        response: null,
        error:
          error instanceof Error
            ? error.message
            : "Failed to check drift profile existence",
      },
      { status: 500 },
    );
  }
};
