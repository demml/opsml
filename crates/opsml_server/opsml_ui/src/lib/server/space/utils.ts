import { RoutePaths } from "$lib/components/api/routes";
import type {
  CreateSpaceResponse,
  SpaceStatsResponse,
  SpaceRecordResponse,
  SpaceRecord,
} from "$lib/components/space/types";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

export async function createSpace(
  fetch: typeof globalThis.fetch,
  space: string,
  description: string
): Promise<CreateSpaceResponse> {
  let params = { space: space, description: description };
  const response = await createOpsmlClient(fetch).post(
    RoutePaths.CREATE_SPACE,
    params
  );
  return await response.json();
}

export async function deleteSpace(
  fetch: typeof globalThis.fetch,
  space: string
): Promise<CreateSpaceResponse> {
  let params = { space: space };
  const response = await createOpsmlClient(fetch).delete(
    RoutePaths.DELETE_SPACE,
    params
  );
  return await response.json();
}

export async function getAllSpaceStats(
  fetch: typeof globalThis.fetch
): Promise<SpaceStatsResponse> {
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.ALL_SPACES,
    undefined
  );
  return await response.json();
}

export async function getSpace(
  fetch: typeof globalThis.fetch,
  space: string
): Promise<SpaceRecord> {
  let params = { space: space };
  const response = await createOpsmlClient(fetch).get(
    RoutePaths.SPACES,
    params
  );
  let recordResponse = (await response.json()) as SpaceRecordResponse;
  // if no items found, return empty record
  if (recordResponse.spaces.length === 0) {
    return {
      space: space,
      description: "",
    };
  }
  return recordResponse.spaces[0];
}
