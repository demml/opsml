import {
  type DriftProfileResponse,
  CommonPaths,
  type SuccessResponse,
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
