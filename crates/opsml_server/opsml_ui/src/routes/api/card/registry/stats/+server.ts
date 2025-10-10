import type { RequestHandler } from "./$types";
import { getRegistryStats } from "$lib/server/card/utils";
import { json } from "@sveltejs/kit";
import { logger } from "$lib/server/logger";

/** Get Registry stats data
 */
export const POST: RequestHandler = async ({ request, cookies, fetch }) => {
  logger.debug(`Handling user registration request...`);
  const { registry_type, searchTerm, spaces, tags } = await request.json();
  const jwt_token = cookies.get("jwt_token");
  const response = await getRegistryStats(
    fetch,
    jwt_token,
    registry_type,
    searchTerm,
    spaces,
    tags
  );
  return json(response);
};
