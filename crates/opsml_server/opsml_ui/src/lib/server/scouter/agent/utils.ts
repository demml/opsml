import { RoutePaths } from "$lib/components/api/routes";
import type {
  EvalRecordPaginationRequest,
  EvalRecordPaginationResponse,
  AgentEvalTaskRequest,
  AgentEvalTaskResponse,
  AgentEvalWorkflowPaginationResponse,
} from "$lib/components/scouter/agent/types";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export async function getEvalRecordPage(
  fetch: typeof globalThis.fetch,
  request: EvalRecordPaginationRequest,
): Promise<EvalRecordPaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.AGENT_EVAL_RECORD_PAGE,
    request,
  );
  return (await response.json()) as EvalRecordPaginationResponse;
}

export async function getAgentEvalWorkflowPage(
  fetch: typeof globalThis.fetch,
  request: EvalRecordPaginationRequest,
): Promise<AgentEvalWorkflowPaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.AGENT_EVAL_WORKFLOW_PAGE,
    request,
  );
  return (await response.json()) as AgentEvalWorkflowPaginationResponse;
}

export async function getAgentEvalTask(
  fetch: typeof globalThis.fetch,
  request: AgentEvalTaskRequest,
): Promise<AgentEvalTaskResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.AGENT_EVAL_TASK_RECORD,
    request,
  );
  return (await response.json()) as AgentEvalTaskResponse;
}
