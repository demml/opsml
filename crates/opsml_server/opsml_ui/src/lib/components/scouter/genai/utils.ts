import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";
import type {
  GenAIEvalRecordPaginationRequest,
  GenAIEvalRecordPaginationResponse,
  GenAIEvalTaskRequest,
  GenAIEvalTaskResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "$lib/components/scouter/genai/types";

export async function getServerGenAIEvalRecordPage(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalRecordPaginationRequest
): Promise<GenAIEvalRecordPaginationResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.GENAI_EVAL_RECORD_PAGE,
    request
  );

  let response = (await resp.json()) as GenAIEvalRecordPaginationResponse;
  return response;
}

export async function getServerGenAIEvalWorkflowPage(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalRecordPaginationRequest
): Promise<GenAIEvalWorkflowPaginationResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.GENAI_EVAL_WORKFLOW_PAGE,
    request
  );

  let response = (await resp.json()) as GenAIEvalWorkflowPaginationResponse;
  return response;
}

export async function getServerGenAIEvalTask(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalTaskRequest
): Promise<GenAIEvalTaskResponse> {
  let resp = await createInternalApiClient(fetch).get(
    ServerPaths.GENAI_EVAL_TASK,
    request
  );

  let response = (await resp.json()) as GenAIEvalTaskResponse;
  return response;
}
