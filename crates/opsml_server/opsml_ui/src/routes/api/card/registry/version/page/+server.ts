import { getVersionPage } from "$lib/server/card/utils";
import { json, type RequestHandler } from "@sveltejs/kit";

/** Get a page of versions for a registry item using cursor-based pagination */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { registry_type, space, name, cursor, limit } = await request.json();
  const response = await getVersionPage(
    fetch,
    registry_type,
    space,
    name,
    cursor,
    limit,
  );
  return json(response);
};
