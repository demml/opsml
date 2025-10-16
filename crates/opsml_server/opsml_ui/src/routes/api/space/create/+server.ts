import { type RequestHandler, json } from "@sveltejs/kit";
import { createSpace } from "$lib/server/space/utils";

/** Get a page of LLM monitoring records
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { space, description } = await request.json();
  const response = await createSpace(fetch, space, description);
  return json(response);
};
