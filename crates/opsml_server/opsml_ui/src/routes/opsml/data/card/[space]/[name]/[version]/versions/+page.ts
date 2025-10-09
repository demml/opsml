export const ssr = false;

import { getRegistryStats, getVersionPage } from "$lib/components/card/utils";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType } = await parent();

  // get metric names, parameters
  let versionPage = await getVersionPage(
    registryType,
    metadata.space,
    metadata.name
  );

  let space = [metadata.space];
  let versionStats = await getRegistryStats(registryType, metadata.name, space);

  return { versionPage, versionStats };
};
