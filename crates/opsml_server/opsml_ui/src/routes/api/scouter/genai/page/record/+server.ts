import { type RequestHandler, json } from "@sveltejs/kit";
import { getEvalRecordPage } from "$lib/server/scouter/genai/utils";
import type { EvalRecordPaginationRequest } from "$lib/components/scouter/genai/types";

/** Get a page of latest metrics for drift profiles
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const page_request: EvalRecordPaginationRequest = await request.json();
  const response = await getEvalRecordPage(fetch, page_request);
  return json(response);
};
