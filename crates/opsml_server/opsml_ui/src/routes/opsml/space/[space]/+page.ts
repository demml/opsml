export const prerender = false;

import { getSpace } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ params }) => {
  await validateUserOrRedirect();

  // get space for url if exists
  let spaceRecord = await getSpace(params.space);

  console.log("Space loaded:", spaceRecord);

  return { spaceRecord };
};
