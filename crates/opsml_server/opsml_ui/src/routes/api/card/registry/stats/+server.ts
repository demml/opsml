import type { RequestHandler } from "./$types";
import { getRegistryStats } from "$lib/server/card/utils";
import { json } from "@sveltejs/kit";
import { logger } from "$lib/server/logger";

/** Get Registry stats data
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { registry_type, searchTerm, spaces, tags } = await request.json();
  const response = await getRegistryStats(
    fetch,
    registry_type,
    searchTerm,
    spaces,
    tags
  );
  return json(response);
};
