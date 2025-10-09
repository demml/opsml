export const prerender = false;

import { getSpace } from "$lib/components/space/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";
import { getRecentCards } from "$lib/components/home/utils.server";

export const load: PageLoad = async ({ params }) => {
  // get space for url if exists
  let spaceRecord = await getSpace(params.space);
  let recentCards = await getRecentCards(params.space);

  return { spaceRecord, recentCards };
};
