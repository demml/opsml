import type { RequestHandler } from "./$types";
import { getRegistryPage } from "$lib/server/card/utils";
import { json } from "@sveltejs/kit";
import { logger } from "$lib/server/logger";

/** Get Registry Page Data
 */
export const POST: RequestHandler = async ({ request, cookies, fetch }) => {
  const { registry_type, sort_by, spaces, searchTerm, tags, page } =
    await request.json();
  const jwt_token = cookies.get("jwt_token");
  const response = await getRegistryPage(
    fetch,
    registry_type,
    sort_by,
    spaces,
    searchTerm,
    tags,
    page
  );
  return json(response);
};
