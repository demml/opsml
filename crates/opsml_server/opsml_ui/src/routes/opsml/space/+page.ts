export const ssr = false;

import { getAllSpaceStats } from "$lib/components/space/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({}) => {
  // get space for url if exists
  let spaces = await getAllSpaceStats();

  return { spaces };
};
