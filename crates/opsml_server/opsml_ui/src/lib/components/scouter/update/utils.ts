import { createInternalApiClient } from "$lib/api/internalClient";
import type { UpdateProfileRequest, UpdateResponse } from "../types";
import { ServerPaths } from "$lib/components/api/routes";

export async function updateMonitoringDriftProfile(
  fetch: typeof window.fetch,
  updateRequest: UpdateProfileRequest
): Promise<UpdateResponse> {
  const client = createInternalApiClient(fetch);
  const resp = await client.put(
    ServerPaths.UPDATE_MONITORING_PROFILE,
    updateRequest
  );

  const response = (await resp.json()) as UpdateResponse;
  return response;
}
