import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type {
  CreateSpaceResponse,
  SpaceStatsResponse,
  SpaceRecordResponse,
  SpaceRecord,
} from "./types";
import { userStore } from "../user/user.svelte";

export async function createSpace(
  space: string,
  description: string
): Promise<CreateSpaceResponse> {
  let params = { space: space, description: description };
  const response = await opsmlClient.post(
    RoutePaths.CREATE_SPACE,
    params,
    userStore.jwt_token
  );
  return await response.json();
}

export async function deleteSpace(space: string): Promise<CreateSpaceResponse> {
  let params = { space: space };
  const response = await opsmlClient.delete(
    RoutePaths.DELETE_SPACE,
    params,
    userStore.jwt_token
  );
  return await response.json();
}

export async function getAllSpaceStats(): Promise<SpaceStatsResponse> {
  const response = await opsmlClient.get(
    RoutePaths.ALL_SPACES,
    undefined,
    userStore.jwt_token
  );
  return await response.json();
}

export async function getSpace(space: string): Promise<SpaceRecord> {
  let params = { space: space };
  const response = await opsmlClient.get(
    RoutePaths.SPACES,
    params,
    userStore.jwt_token
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
