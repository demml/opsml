import { RoutePaths } from "$lib/components/api/routes";
import type {
  EvalRecordPaginationRequest,
  EvalRecordPaginationResponse,
  GenAIEvalTaskRequest,
  GenAIEvalTaskResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "$lib/components/scouter/genai/types";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export async function getEvalRecordPage(
  fetch: typeof globalThis.fetch,
  request: EvalRecordPaginationRequest,
): Promise<EvalRecordPaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GENAI_EVAL_RECORD_PAGE,
    request,
  );
  return (await response.json()) as EvalRecordPaginationResponse;
}

export async function getGenAIEvalWorkflowPage(
  fetch: typeof globalThis.fetch,
  request: EvalRecordPaginationRequest,
): Promise<GenAIEvalWorkflowPaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GENAI_EVAL_WORKFLOW_PAGE,
    request,
  );
  return (await response.json()) as GenAIEvalWorkflowPaginationResponse;
}

export async function getGenAIEvalTask(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalTaskRequest,
): Promise<GenAIEvalTaskResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.GENAI_EVAL_TASK_RECORD,
    request,
  );
  return (await response.json()) as GenAIEvalTaskResponse;
}
