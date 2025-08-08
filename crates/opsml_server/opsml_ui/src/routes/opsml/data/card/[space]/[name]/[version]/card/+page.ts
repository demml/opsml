export const ssr = false;

import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registry, readme, registryPath } = await parent();

  return { metadata, registry, readme, registryPath };
};
