import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";
import type {
  AgentEvalProfile,
  EvalRecordPaginationRequest,
  EvalRecordPaginationResponse,
  AgentEvalTaskRequest,
  AgentEvalTaskResponse,
  AgentEvalWorkflowPaginationResponse,
} from "$lib/components/scouter/agent/types";
import type { TimeRange } from "$lib/components/trace/types";
import type { DriftType } from "../types";
import type { DriftProfile } from "../utils";
import type { BinnedMetrics } from "../custom/types";
import type {
  AgentAssertionTask,
  AssertionTask,
  LLMJudgeTask,
  TraceAssertionTask,
} from "./task";

export async function getServerEvalRecordPage(
  fetch: typeof globalThis.fetch,
  request: EvalRecordPaginationRequest,
): Promise<EvalRecordPaginationResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.AGENT_EVAL_RECORD_PAGE,
    request,
  );

  let response = (await resp.json()) as EvalRecordPaginationResponse;

  return response;
}

/** Helper for retrieving an agent eval workflow page
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param request - the agent eval workflow pagination request
 * @returns AgentEvalWorkflowPaginationResponse - the agent eval workflow pagination response
 */
export async function getServerAgentEvalWorkflowPage(
  fetch: typeof globalThis.fetch,
  request: EvalRecordPaginationRequest,
): Promise<AgentEvalWorkflowPaginationResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.AGENT_EVAL_WORKFLOW_PAGE,
    request,
  );

  let response = (await resp.json()) as AgentEvalWorkflowPaginationResponse;
  return response;
}

/** Helper for retrieving an agent eval task by id
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param request - the agent eval task request
 * @returns AgentEvalTaskResponse - the agent eval task response
 */
export async function getServerAgentEvalTask(
  fetch: typeof globalThis.fetch,
  request: AgentEvalTaskRequest,
): Promise<AgentEvalTaskResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.AGENT_EVAL_TASK,
    request,
  );

  let response = (await resp.json()) as AgentEvalTaskResponse;
  return response;
}

/** Helper for retrieving agent task drift metrics
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param space - the space of the drift profile
 * @param uid - the uid of the drift profile
 * @param driftType - the type of drift to get metrics for
 * @param time_range - the time range to get metrics for
 * @param max_data_points - the maximum number of data points to retrieve
 * @returns BinnedMetrics - the binned agent task feature metrics
 */
export async function getAgentEvalTaskDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number,
): Promise<BinnedMetrics> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.AGENT_TASK_DRIFT,
    {
      space,
      uid,
      time_range,
      max_data_points,
    },
  );

  let response = (await resp.json()) as BinnedMetrics;

  return response;
}

/** Helper for retrieving agent workflow drift metrics
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param space - the space of the drift profile
 * @param uid - the uid of the drift profile
 * @param driftType - the type of drift to get metrics for
 * @param time_range - the time range to get metrics for
 * @param max_data_points - the maximum number of data points to retrieve
 * @returns BinnedMetrics - the binned agent workflow feature metrics
 */
export async function getAgentEvalWorkflowDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number,
): Promise<BinnedMetrics> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.AGENT_WORKFLOW_DRIFT,
    {
      space,
      uid,
      time_range,
      max_data_points,
    },
  );

  let response = (await resp.json()) as BinnedMetrics;

  return response;
}

export class AgentEvalProfileHelper {
  /**
   * Get LLMJudgeTask by task ID from the profile.
   */
  static getLLMJudgeById(
    profile: AgentEvalProfile,
    id: string,
  ): LLMJudgeTask | null {
    return profile.tasks.judge.find((task) => task.id === id) ?? null;
  }

  /**
   * Get AssertionTask by task ID from the profile.
   */
  static getAssertionById(
    profile: AgentEvalProfile,
    id: string,
  ): AssertionTask | null {
    return profile.tasks.assertion.find((task) => task.id === id) ?? null;
  }

  /**
   * Get TraceAssertionTask by task ID from the profile.
   */
  static getTraceAssertionById(
    profile: AgentEvalProfile,
    id: string,
  ): TraceAssertionTask | null {
    return profile.tasks.trace.find((task) => task.id === id) ?? null;
  }

  /**
   * Get AgentAssertionTask by task ID from the profile.
   */
  static getAgentAssertionById(
    profile: AgentEvalProfile,
    id: string,
  ): AgentAssertionTask | null {
    return profile.tasks.agent.find((task) => task.id === id) ?? null;
  }
}
