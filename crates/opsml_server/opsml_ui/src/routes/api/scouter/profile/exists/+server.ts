import { type RequestHandler, json } from "@sveltejs/kit";
import type { GetProfileExistsRequest } from "$lib/components/scouter/types";
import { getProfileExists } from "$lib/server/scouter/drift/utils";

/**
 * POST endpoint for checking if a drift profile exists
 * @param request - SvelteKit request containing GetProfileExistsRequest in body
 * @param fetch - SvelteKit fetch function for server-side requests
 * @returns JSON response with either boolean result or error message
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  try {
    const filters: GetProfileExistsRequest = await request.json();
    const response: boolean = await getProfileExists(fetch, filters);

    return json(response);
  } catch (error) {
    console.error("Error checking drift profile existence:", error);

    return json(false);
  }
};
