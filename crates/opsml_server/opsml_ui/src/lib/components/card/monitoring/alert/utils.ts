import { RoutePaths } from "$lib/components/api/routes";
import type {
  AlertResponse,
  DriftAlertRequest,
  Alert,
  UpdateAlertResponse,
  UpdateAlertStatus,
} from "./types";
import { opsmlClient } from "$lib/components/api/client.svelte";
import type { TimeInterval } from "../types";
import { timeIntervalToDateTime } from "../util";
import { sampleAlerts } from "../example";
import { userStore } from "$lib/components/user/user.svelte";

export async function getDriftAlerts(
  space: string,
  name: string,
  version: string,
  timeInterval: TimeInterval,
  active: boolean
): Promise<Alert[]> {
  // For testing purposes, return sample alerts
  let alertRequest: DriftAlertRequest = {
    space: space,
    name: name,
    version: version,
    limit_datetime: timeIntervalToDateTime(timeInterval),
    active: active,
  };

  const response = await opsmlClient.get(
    RoutePaths.DRIFT_ALERT,
    alertRequest,
    userStore.jwt_token
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch drift alerts: ${response.status}`);
  }
  const alertResponse = (await response.json()) as AlertResponse;

  return alertResponse.alerts;
}

//// Acknowledge an alert by its ID
export async function acknowledgeAlert(
  id: number,
  space: string
): Promise<boolean> {
  const request: UpdateAlertStatus = {
    id: id,
    active: false,
    space: space,
  };

  const response = await opsmlClient.put(
    RoutePaths.DRIFT_ALERT,
    request,
    userStore.jwt_token
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
