import { type RequestHandler, json } from "@sveltejs/kit";
import { getGenAIEvalTask } from "$lib/server/scouter/genai/utils";
import type { GenAIEvalTaskRequest } from "$lib/components/scouter/genai/types";

export const POST: RequestHandler = async ({ request, fetch }) => {
  const task_request: GenAIEvalTaskRequest = await request.json();
  const response = await getGenAIEvalTask(fetch, task_request);
  return json(response);
};
