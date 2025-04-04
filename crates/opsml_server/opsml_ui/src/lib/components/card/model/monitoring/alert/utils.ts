import { RoutePaths } from "$lib/components/api/routes";
import type { AlertResponse, DriftAlertRequest, Alert } from "./types";
import { opsmlClient } from "$lib/components/api/client.svelte";
import type { TimeInterval } from "../types";
import { timeIntervalToDateTime } from "../util";
import { sampleAlerts } from "../example";

export async function getDriftAlerts(
  space: string,
  name: string,
  version: string,
  timeInterval: TimeInterval,
  active: boolean
): Promise<Alert[]> {
  let alertRequest: DriftAlertRequest = {
    space: space,
    name: name,
    version: version,
    limit_datetime: timeIntervalToDateTime(timeInterval),
    active: active,
  };

  //const response = await opsmlClient.post(RoutePaths.DRIFT_ALERT, alertRequest);
  //const alertResponse = (await response.json()) as AlertResponse;
  //if (alertResponse.status !== "success") {
  //throw new Error(`Failed to fetch drift alerts: ${alertResponse.status}`);
  //}
  //return alertResponse.data;
  return sampleAlerts;
}
