import { type RequestHandler, json } from "@sveltejs/kit";
import { getLLMRecordPage } from "$lib/server/card/monitoring/utils";

/** Get a page of LLM monitoring records
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const { service_info, status, cursor } = await request.json();
  const response = await getLLMRecordPage(fetch, service_info, status, cursor);
  return json(response);
};
