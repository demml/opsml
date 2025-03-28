import { RoutePaths } from "$lib/components/api/routes";
import type { AlertResponse, DriftAlertRequest } from "./types";
import { opsmlClient } from "$lib/components/api/client.svelte";
import type { TimeInterval } from "../types";
import { timeIntervalToDateTime } from "../util";

export async function getDriftAlerts(
  repository: string,
  name: string,
  version: string,
  timeInterval: TimeInterval,
  active: boolean
): Promise<AlertResponse> {
  let alertRequest: DriftAlertRequest = {
    repository: repository,
    name: name,
    version: version,
    limit_datetime: timeIntervalToDateTime(timeInterval),
    active: active,
  };

  const response = await opsmlClient.get(RoutePaths.DRIFT_ALERT, alertRequest);
  return (await response.json()) as AlertResponse;
}
