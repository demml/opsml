export const ssr = false;

import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  console.log("Loading card page...");
  const { metadata, registryType, readme, registryPath } = await parent();

  return { metadata, registryType, readme, registryPath };
};
