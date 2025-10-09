import { userStore } from "$lib/components/user/user.svelte";
import { getUser } from "$lib/components/user/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await parent();

  let userInfo = await getUser(userStore.username);

  return { userInfo };
};
