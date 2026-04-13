import { type RequestHandler, json } from "@sveltejs/kit";
import { getAgentEvalWorkflowPage } from "$lib/server/scouter/agent/utils";
import type { EvalRecordPaginationRequest } from "$lib/components/scouter/agent/types";

/** Get a page of latest metrics for drift profiles
 */
export const POST: RequestHandler = async ({ request, fetch }) => {
  const page_request: EvalRecordPaginationRequest = await request.json();
  const response = await getAgentEvalWorkflowPage(fetch, page_request);
  return json(response);
};
