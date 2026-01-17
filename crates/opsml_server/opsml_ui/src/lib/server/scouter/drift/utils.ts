import { createOpsmlClient } from "$lib/server/api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";
import {
  TimeInterval,
  type UpdateProfileRequest,
  type UpdateResponse,
  DriftType,
  type DriftRequest,
} from "$lib/components/scouter/types";
import { RegistryType } from "$lib/utils";
import type {
  BinnedMetricUnion,
  DriftProfileUri,
} from "$lib/components/scouter/types";
import type {
  DriftProfile,
  DriftProfileResponse,
} from "$lib/components/scouter/utils";
import type {
  UpdateAlertResponse,
  UpdateAlertStatus,
  DriftAlertPaginationRequest,
  DriftAlertPaginationResponse,
} from "$lib/components/scouter/alert/types";
import type { TimeRange } from "$lib/components/trace/types";
import { timeRangeToInterval } from "$lib/components/trace/utils";
import type { BinnedMetrics } from "$lib/components/scouter/custom/types";
import type { BinnedPsiFeatureMetrics } from "$lib/components/scouter/psi/types";
import type { BinnedSpcFeatureMetrics } from "$lib/components/scouter/spc/types";

export async function getDriftProfiles(
  fetch: typeof globalThis.fetch,
  uid: string,
  driftMap: Record<string, DriftProfileUri>,
  registryType: RegistryType
): Promise<DriftProfileResponse> {
  const body = {
    uid: uid,
    drift_profile_uri_map: driftMap,
    registry_type: registryType,
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.DRIFT_PROFILE_UI,
    body
  );
  return (await response.json()) as DriftProfileResponse;
}

export async function updateDriftProfile(
  fetch: typeof globalThis.fetch,
  updateRequest: UpdateProfileRequest
): Promise<UpdateResponse> {
  const response = await createOpsmlClient(fetch).put(
    RoutePaths.DRIFT_PROFILE,
    updateRequest
  );
  return (await response.json()) as UpdateResponse;
}

export async function getDriftAlerts(
  fetch: typeof globalThis.fetch,
  request: DriftAlertPaginationRequest
): Promise<DriftAlertPaginationResponse> {
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.DRIFT_ALERT,
    request
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch drift alerts: ${response.status}`);
  }
  const alertResponse = (await response.json()) as DriftAlertPaginationResponse;

  return alertResponse;
}

//// Acknowledge an alert by its ID
export async function acknowledgeAlert(
  fetch: typeof globalThis.fetch,
  id: number,
  space: string
): Promise<boolean> {
  const request: UpdateAlertStatus = {
    id: id,
    active: false,
    space: space,
  };

  const response = await createOpsmlClient(fetch).put(
    RoutePaths.DRIFT_ALERT,
    request
  );

  if (!response.ok) {
    throw new Error(`Failed to acknowledge alert: ${response.status}`);
  }
  const updateResponse = (await response.json()) as UpdateAlertResponse;

  if (!updateResponse.updated) {
    throw new Error("Failed to acknowledge alert");
  }

  return updateResponse.updated;
}

/** Generic  helper for getting latest metrics for multiple drift types
 * @param fetch - fetch function
 * @param profiles - drift profiles
 * @param time_range - time range for the metrics
 * @param max_data_points - maximum data points to fetch
 * @returns binned drift map
 */
async function getDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  driftType: DriftType,
  time_range: TimeRange,
  max_data_points: number,
  route: RoutePaths
): Promise<BinnedMetricUnion> {
  const time_interval = timeRangeToInterval(time_range);

  const request: DriftRequest = {
    space: space,
    uid: uid,
    time_interval: time_interval,
    max_data_points: max_data_points,
    drift_type: driftType as DriftType,
  };

  // if time_interval is custom, add start and end datetime
  if (time_interval === TimeInterval.Custom) {
    request.start_custom_datetime = time_range.startTime;
    request.end_custom_datetime = time_range.endTime;
  }

  // Make the request and store result in driftMap
  const response = await createOpsmlClient(fetch).get(route, request);
  const data = (await response.json()) as BinnedMetricUnion;

  return data;
}

export async function getCustomDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedMetrics> {
  return (await getDriftMetrics(
    fetch,
    space,
    uid,
    DriftType.Custom,
    time_range,
    max_data_points,
    RoutePaths.CUSTOM_DRIFT
  )) as BinnedMetrics;
}

export async function getPsiDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedPsiFeatureMetrics> {
  return (await getDriftMetrics(
    fetch,
    space,
    uid,
    DriftType.Psi,
    time_range,
    max_data_points,
    RoutePaths.PSI_DRIFT
  )) as BinnedPsiFeatureMetrics;
}

export async function getSpcDriftMetrics<T extends DriftType.Spc>(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedSpcFeatureMetrics> {
  return (await getDriftMetrics(
    fetch,
    space,
    uid,
    DriftType.Spc,
    time_range,
    max_data_points,
    RoutePaths.SPC_DRIFT
  )) as BinnedSpcFeatureMetrics;
}

export async function getGenAIEvalTaskDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedMetrics> {
  return (await getDriftMetrics(
    fetch,
    space,
    uid,
    DriftType.GenAI,
    time_range,
    max_data_points,
    RoutePaths.GENAI_EVAL_TASK_DRIFT
  )) as BinnedMetrics;
}

export async function getGenAIEvalWorkflowDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedMetrics> {
  return (await getDriftMetrics(
    fetch,
    space,
    uid,
    DriftType.GenAI,
    time_range,
    max_data_points,
    RoutePaths.GENAI_EVAL_WORKFLOW_DRIFT
  )) as BinnedMetrics;
}
