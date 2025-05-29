import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { CreateSpaceResponse } from "./types";
import { userStore } from "../user/user.svelte";

export async function createSpace(space: string): Promise<CreateSpaceResponse> {
  let params = { space: space };
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
