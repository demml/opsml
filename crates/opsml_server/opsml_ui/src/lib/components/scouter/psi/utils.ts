import type { PsiThreshold } from "./types";
import type { TimeRange } from "$lib/components/trace/types";
import type { DriftType } from "../types";
import type { DriftProfile } from "../utils";
import type { BinnedPsiFeatureMetrics } from "./types";
import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";

export function getPsiThresholdKeyValue(threshold: PsiThreshold): {
  type: string;
  value: number;
} {
  if (threshold.Normal) {
    return { type: "Normal", value: threshold.Normal.alpha };
  } else if (threshold.ChiSquare) {
    return { type: "ChiSquare", value: threshold.ChiSquare.alpha };
  } else if (threshold.Fixed) {
    return { type: "Fixed", value: threshold.Fixed.threshold };
  }
  throw new Error("Invalid PsiThreshold configuration");
}

export function updatePsiThreshold(type: string, value: number): PsiThreshold {
  const numericValue = Number(value);

  if (isNaN(numericValue)) {
    throw new Error(`Invalid numeric value: ${value}`);
  }

  switch (type) {
    case "Normal":
      return { Normal: { alpha: numericValue } };
    case "ChiSquare":
      return { ChiSquare: { alpha: numericValue } };
    case "Fixed":
      return { Fixed: { threshold: numericValue } };
    default:
      throw new Error(`Unknown threshold type: ${type}`);
  }
}

/** Helper for retrieving psi drift metrics
 * This routes the request to the internal API client
 * which then send the request to opsml and then scouter to retrieve the data
 * **CLIENT SIDE ONLY FUNCTION**
 * @param fetch - the fetch function
 * @param space - the space of the drift profile
 * @param uid - the uid of the drift profile
 * @param driftType - the type of drift to get metrics for
 * @param time_range - the time range to get metrics for
 * @param max_data_points - the maximum number of data points to retrieve
 * @returns BinnedPsiFeatureMetrics - the binned psi feature metrics
 */
export async function getPsiDriftMetrics(
  fetch: typeof globalThis.fetch,
  space: string,
  uid: string,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedPsiFeatureMetrics> {
  let resp = await createInternalApiClient(fetch).post(ServerPaths.PSI_DRIFT, {
    space,
    uid,
    time_range,
    max_data_points,
  });

  let response = (await resp.json()) as BinnedPsiFeatureMetrics;

  return response;
}
