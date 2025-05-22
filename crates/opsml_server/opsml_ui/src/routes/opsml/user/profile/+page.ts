import { userStore } from "$lib/components/user/user.svelte";
import { getUser } from "$lib/components/user/utils";
import { opsmlClient } from "$lib/components/api/client.svelte";

import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
  await opsmlClient.validateAuth(true);
  let userInfo = await getUser(userStore.username);

  return { userInfo };
};
