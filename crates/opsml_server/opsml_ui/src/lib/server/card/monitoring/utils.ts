import { createOpsmlClient } from "$lib/server/api/opsmlClient";
import { RoutePaths } from "$lib/components/api/routes";
import {
  TimeInterval,
  type UpdateProfileRequest,
  type UpdateResponse,
  type LLMPageRequest,
  type LLMPageResponse,
  type PaginationCursor,
  type ServiceInfo,
  type LLMPaginationRequest,
  Status,
  DriftType,
  type DriftRequest,
  type BinnedDriftMap,
} from "$lib/components/card/monitoring/types";
import { RegistryType } from "$lib/utils";
import type { DriftProfileUri } from "$lib/components/card/monitoring/types";
import type { DriftProfileResponse } from "$lib/components/card/monitoring/utils";
import type {
  AlertResponse,
  DriftAlertRequest,
  Alert,
  UpdateAlertResponse,
  UpdateAlertStatus,
} from "$lib/components/card/monitoring/alert/types";
import { getProfileConfig } from "$lib/components/card/monitoring/utils";
import type { TimeRange } from "$lib/components/trace/types";
import { timeRangeToInterval } from "$lib/components/trace/utils";

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

export async function getLLMRecordPage(
  fetch: typeof globalThis.fetch,
  service_info: ServiceInfo,
  status?: Status,
  cursor?: PaginationCursor
): Promise<LLMPageResponse> {
  let pagination: LLMPaginationRequest = {
    cursor,
    limit: 20,
  };

  const request: LLMPageRequest = {
    service_info,
    status,
    pagination,
  };

  const response = await createOpsmlClient(fetch).post(
    RoutePaths.LLM_RECORD_PAGE,
    request
  );
  return (await response.json()) as LLMPageResponse;
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
  uid: string,
  timeRange: TimeRange,
  active: boolean
): Promise<Alert[]> {
  // For testing purposes, return sample alerts
  let alertRequest: DriftAlertRequest = {
    uid: uid,
    limit_datetime: timeRange.startTime,
    active: active,
  };

  const response = await createOpsmlClient(fetch).get(
    RoutePaths.DRIFT_ALERT,
    alertRequest
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch drift alerts: ${response.status}`);
  }
  const alertResponse = (await response.json()) as AlertResponse;

  return alertResponse.alerts;
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

export async function getLatestMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedDriftMap> {
  const driftMap: BinnedDriftMap = {};

  // Create an array of promises
  const requests = Object.entries(profiles).map(
    async ([driftType, profile]) => {
      const config = getProfileConfig(driftType as DriftType, profile.profile);
      const time_interval = timeRangeToInterval(time_range);

      const request: DriftRequest = {
        space: config.space,
        uid: config.uid,
        time_interval: time_interval,
        max_data_points: max_data_points,
        drift_type: driftType as DriftType,
      };

      // if time_interval is custom, add begin and end datetime
      if (time_interval === TimeInterval.Custom) {
        request.begin_custom_datetime = time_range.startTime;
        request.end_custom_datetime = time_range.endTime;
      }

      // Determine route based on drift type
      const route = (() => {
        switch (driftType) {
          case DriftType.Custom:
            return RoutePaths.CUSTOM_DRIFT;
          case DriftType.Psi:
            return RoutePaths.PSI_DRIFT;
          case DriftType.Spc:
            return RoutePaths.SPC_DRIFT;
          case DriftType.LLM:
            return RoutePaths.LLM_DRIFT;
          default:
            throw new Error(`Unsupported drift type: ${driftType}`);
        }
      })();

      // Make the request and store result in driftMap
      const response = await createOpsmlClient(fetch).get(route, request);
      const data = await response.json();
      driftMap[driftType as DriftType] = data;
    }
  );

  // Wait for all requests to complete
  await Promise.all(requests);

  return driftMap;
}
