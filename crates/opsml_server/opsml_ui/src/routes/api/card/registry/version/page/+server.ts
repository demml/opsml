import type { RequestHandler } from "../$types";
import { getVersionPage } from "$lib/server/card/utils";
import { json } from "@sveltejs/kit";

/** Get a page of versions for a registry item
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { registry_type, space, name, page } = await request.json();
  const response = await getVersionPage(
    fetch,
    registry_type,
    space,
    name,
    page
  );
  return json(response);
};
