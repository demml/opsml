import type { RequestHandler } from "./$types";
import { getRegistryPage } from "$lib/server/card/utils";
import { json } from "@sveltejs/kit";

/** Get Registry Page Data */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { registry_type, sort_by, spaces, searchTerm, tags, page, cursor } =
    await request.json();

  const response = await getRegistryPage(
    fetch,
    registry_type,
    sort_by,
    spaces,
    searchTerm,
    tags,
    page,
    cursor
  );

  return json(response);
};
