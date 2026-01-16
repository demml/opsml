import { RoutePaths } from "$lib/components/api/routes";
import type {
  GenAIEvalRecordPaginationRequest,
  GenAIEvalRecordPaginationResponse,
  GenAIEvalTaskRequest,
  GenAIEvalTaskResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "$lib/components/scouter/genai/types";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export async function getGenAIEvalRecordPage(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalRecordPaginationRequest
): Promise<GenAIEvalRecordPaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GENAI_EVAL_RECORD_PAGE,
    request
  );
  return (await response.json()) as GenAIEvalRecordPaginationResponse;
}

export async function getGenAIEvalWorkflowPage(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalRecordPaginationRequest
): Promise<GenAIEvalWorkflowPaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.GENAI_EVAL_WORKFLOW_PAGE,
    request
  );
  return (await response.json()) as GenAIEvalWorkflowPaginationResponse;
}

export async function getGenAIEvalTask(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalTaskRequest
): Promise<GenAIEvalTaskResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.GENAI_EVAL_TASK_RECORD,
    request
  );
  return (await response.json()) as GenAIEvalTaskResponse;
}
