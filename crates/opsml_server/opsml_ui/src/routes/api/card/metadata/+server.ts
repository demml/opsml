import type { RequestHandler } from "./$types";
import { json } from "@sveltejs/kit";
import { getCardMetadata } from "$lib/server/card/utils";

/** Get Card Metadata
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { space, name, version, uid, registry_type } = await request.json();

  const response = await getCardMetadata(
    space,
    name,
    version,
    uid,
    registry_type,
    fetch
  );
  return json(response);
};
