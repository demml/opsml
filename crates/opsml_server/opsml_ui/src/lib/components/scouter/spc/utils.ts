import type { TimeRange } from "$lib/components/trace/types";
import { DriftType } from "../types";
import type { DriftProfile } from "../utils";
import type { BinnedSpcFeatureMetrics } from "./types";
import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";

/** Helper for retrieving spc drift metrics
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param space - the space of the drift profile
 * @param uid - the uid of the drift profile
 * @param driftType - the type of drift to get metrics for
 * @param time_range - the time range to get metrics for
 * @param max_data_points - the maximum number of data points to retrieve
 * @returns BinnedSpcFeatureMetrics - the binned spc feature metrics
 */
export async function getSpcDriftMetrics<T extends DriftType.Spc>(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedSpcFeatureMetrics> {
  let resp = await createInternalApiClient(fetch).post(ServerPaths.SPC_DRIFT, {
    space,
    uid,
    time_range,
    max_data_points,
  });

  let response = (await resp.json()) as BinnedSpcFeatureMetrics;

  return response;
}
