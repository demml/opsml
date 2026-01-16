import { type RequestHandler, json } from "@sveltejs/kit";
import { getGenAIEvalRecordPage } from "$lib/server/scouter/genai/utils";
import type { GenAIEvalRecordPaginationRequest } from "$lib/components/scouter/genai/types";

/** Get a page of latest metrics for drift profiles
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const page_request: GenAIEvalRecordPaginationRequest = await request.json();
  const response = await getGenAIEvalRecordPage(fetch, page_request);
  return json(response);
};
