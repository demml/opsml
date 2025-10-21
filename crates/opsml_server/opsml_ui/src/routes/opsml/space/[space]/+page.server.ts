import { getSpace } from "$lib/server/space/utils";
import type { PageServerLoad } from "./$types";
import { getRecentCards } from "$lib/components/home/utils.server";

export const load: PageServerLoad = async ({ params, fetch }) => {
  // get space for url if exists
  let spaceRecord = await getSpace(fetch, params.space);
  let recentCards = await getRecentCards(fetch, params.space);

  return { spaceRecord, recentCards };
};
