import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";
import type {
  GenAIEvalRecordPaginationRequest,
  GenAIEvalRecordPaginationResponse,
  GenAIEvalTaskRequest,
  GenAIEvalTaskResponse,
  GenAIEvalWorkflowPaginationResponse,
} from "$lib/components/scouter/genai/types";
import type { TimeRange } from "$lib/components/trace/types";
import type { DriftType } from "../types";
import type { DriftProfile } from "../utils";
import type { BinnedMetrics } from "../custom/types";

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

/** Helper for retrieving a genai eval workflow page
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param request - the genai eval workflow pagination request
 * @returns GenAIEvalWorkflowPaginationResponse - the genai eval workflow pagination response
 */
export async function getServerGenAIEvalWorkflowPage(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalRecordPaginationRequest
): Promise<GenAIEvalWorkflowPaginationResponse> {
  console.log(JSON.stringify(request));
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.GENAI_EVAL_WORKFLOW_PAGE,
    request
  );

  let response = (await resp.json()) as GenAIEvalWorkflowPaginationResponse;
  return response;
}

/** Helper for retrieving a genai eval task by id
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param request - the genai eval task request
 * @returns GenAIEvalTaskResponse - the genai eval task response
 */
export async function getServerGenAIEvalTask(
  fetch: typeof globalThis.fetch,
  request: GenAIEvalTaskRequest
): Promise<GenAIEvalTaskResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.GENAI_EVAL_TASK,
    request
  );

  let response = (await resp.json()) as GenAIEvalTaskResponse;
  return response;
}

/** Helper for retrieving genai task drift metrics
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param space - the space of the drift profile
 * @param uid - the uid of the drift profile
 * @param driftType - the type of drift to get metrics for
 * @param time_range - the time range to get metrics for
 * @param max_data_points - the maximum number of data points to retrieve
 * @returns BinnedMetrics - the binned genai task feature metrics
 */
export async function getGenAIEvalTaskDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedMetrics> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.GENAI_TASK_DRIFT,
    {
      space,
      uid,
      time_range,
      max_data_points,
    }
  );

  let response = (await resp.json()) as BinnedMetrics;

  return response;
}

/** Helper for retrieving genai workflow drift metrics
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param space - the space of the drift profile
 * @param uid - the uid of the drift profile
 * @param driftType - the type of drift to get metrics for
 * @param time_range - the time range to get metrics for
 * @param max_data_points - the maximum number of data points to retrieve
 * @returns BinnedMetrics - the binned genai workflow feature metrics
 */
export async function getGenAIEvalWorkflowDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedMetrics> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.GENAI_WORKFLOW_DRIFT,
    {
      space,
      uid,
      time_range,
      max_data_points,
    }
  );

  let response = (await resp.json()) as BinnedMetrics;

  return response;
}
