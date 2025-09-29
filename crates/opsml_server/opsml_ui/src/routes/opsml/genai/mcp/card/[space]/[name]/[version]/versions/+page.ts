export const ssr = false;

import { getRegistryStats, getVersionPage } from "$lib/components/card/utils";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

// @ts-ignore
export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registryType } = await parent();

  let [versionPage, versionStats] = await Promise.all([
    getVersionPage(registryType, metadata.space, metadata.name),
    getRegistryStats(registryType, metadata.name, [metadata.space]),
  ]);

  return { versionPage, versionStats };
};
