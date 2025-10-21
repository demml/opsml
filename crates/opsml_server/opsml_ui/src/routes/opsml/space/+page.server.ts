export const ssr = false;

import { getAllSpaceStats } from "$lib/server/space/utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
  // get space for url if exists
  let spaces = await getAllSpaceStats(fetch);

  return { spaces };
};
