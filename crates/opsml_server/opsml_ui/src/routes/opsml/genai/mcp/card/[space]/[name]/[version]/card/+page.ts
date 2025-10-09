export const ssr = false;

import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

// @ts-ignore
export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType, readme } = await parent();

  return { metadata, registryType, readme };
};
