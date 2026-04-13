import { type RequestHandler, json } from "@sveltejs/kit";
import { getAgentEvalTask } from "$lib/server/scouter/agent/utils";
import type { AgentEvalTaskRequest } from "$lib/components/scouter/agent/types";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const task_request: AgentEvalTaskRequest = await request.json();
  const response = await getAgentEvalTask(fetch, task_request);
  return json(response);
};
