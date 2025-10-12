import type { RequestHandler } from "./$types";
import { json } from "@sveltejs/kit";
import { createReadMe } from "$lib/server/card/readme/utils";

/** Get Card Metadata
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { space, name, registry_type, content } = await request.json();
  const response = await createReadMe(
    space,
    name,
    registry_type,
    content,
    fetch
  );
  return json(response);
};
