import type { AlertCondition } from "../types";
import type { CustomMetricDriftConfig } from "./types";
import type { TimeRange } from "$lib/components/trace/types";
import type { DriftType } from "../types";
import type { DriftProfile } from "../utils";
import type { BinnedMetrics } from "./types";
import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";

export function getCustomAlertCondition(
  config: CustomMetricDriftConfig,
  name: string
): AlertCondition | null {
  if (!config.alert_config.alert_conditions) {
    return null;
  }

  const condition = config.alert_config.alert_conditions[name];
  if (!condition) {
    return null;
  }

  return {
    alert_threshold: condition.alert_threshold,
    baseline_value: condition.baseline_value,
  };
}

/** Helper for retrieving custom drift metrics
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param space - the space of the drift profile
 * @param uid - the uid of the drift profile
 * @param driftType - the type of drift to get metrics for
 * @param time_range - the time range to get metrics for
 * @param max_data_points - the maximum number of data points to retrieve
 * @returns BinnedMetrics - the binned custom feature metrics
 */
export async function getCustomDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedMetrics> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.CUSTOM_DRIFT,
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
