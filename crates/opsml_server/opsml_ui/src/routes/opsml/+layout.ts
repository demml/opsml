import type { LayoutLoad } from "./$types";
import { createInternalApiClient } from "$lib/api/internalClient";
import { ServerPaths } from "$lib/components/api/routes";
import type { UserResponse } from "$lib/components/user/types";
import { userStore } from "$lib/components/user/user.svelte";

export const load: LayoutLoad = async ({ fetch }) => {
  const resp = await createInternalApiClient(fetch).get(ServerPaths.USER);
  const user = (await resp.json()) as {
    success: boolean;
    user: UserResponse | null;
  };

  if (user.success) {
    let userResponse = user.user as UserResponse;
    userStore.fromUserResponse(userResponse);
  }

  return { user };
};
