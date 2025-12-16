import { type RequestHandler, json } from "@sveltejs/kit";
import type { LLMDriftRecordPaginationRequest } from "$lib/components/card/monitoring/llm/llm";
import { getLLMDriftRecordPage } from "$lib/server/card/monitoring/utils";

/** Get a page of LLM monitoring records
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const llmRequest: LLMDriftRecordPaginationRequest = await request.json();
  const response = await getLLMDriftRecordPage(fetch, llmRequest);
  return json(response);
};
