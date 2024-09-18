import {
  type DriftProfileResponse,
  CommonPaths,
  type SuccessResponse,
  type FeatureDriftValuesResponse,
  type FeatureDriftValues,
} from "$lib/scripts/types";
import { apiHandler } from "$lib/scripts/apiHandler";

/// Get drift profile
/// @param name - name of the model
/// @param repository - repository of the model
/// @param version - version of the model
export async function getDriftProfile(
  repository: string,
  name: string,
  version: string
): Promise<DriftProfileResponse> {
  const profile_response = await apiHandler.get(
    `${CommonPaths.DRIFT_PROFILE}?${new URLSearchParams({
      repository: repository,
      name: name,
      version: version,
    }).toString()}`
  );

  const response = (await profile_response.json()) as DriftProfileResponse;
  return response;
}

/// Update drift profile
/// @param profile - drift profile
export async function updateDriftProfile(
  repository: string,
  version: string,
  name: string,
  profile: string
): Promise<SuccessResponse> {
  let body = {
    name: name,
    repository: repository,
    version: version,
    profile: profile,
  };

  const update_response = await apiHandler.put(CommonPaths.DRIFT_PROFILE, body);

  const response = (await update_response.json()) as SuccessResponse;
  return response;
}

/// get feature drift values
/// @param repository - repository of the model
/// @param name - name of the model
/// @param version - version of the model
/// @param time_window - time window for drift values
/// @param feature - optional feature to filter for drift values
export async function getFeatureDriftValues(
  repository: string,
  name: string,
  version: string,
  time_window: string,
  max_data_points: number,
  feature?: string
): Promise<FeatureDriftValues> {
  let params = {
    repository: repository,
    name: name,
    version: version,
    time_window: time_window,
    max_data_points: max_data_points.toString(),
  };

  if (feature) {
    params["feature"] = feature;
  }

  const values_response = await apiHandler.get(
    `${CommonPaths.DRIFT_VALUES}?${new URLSearchParams(params).toString()}`
  );

  const response = (await values_response.json()) as FeatureDriftValuesResponse;
  return response.data;
}
