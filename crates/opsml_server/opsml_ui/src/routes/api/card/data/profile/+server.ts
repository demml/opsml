import { type RequestHandler, json } from "@sveltejs/kit";
import { getDataProfile } from "$lib/server/data/utils";

/** Get a page of LLM monitoring records
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { card } = await request.json();
  const response = await getDataProfile(fetch, card);
  return json(response);
};
