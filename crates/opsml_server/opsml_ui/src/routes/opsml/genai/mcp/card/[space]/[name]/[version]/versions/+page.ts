export const ssr = false;

import { getRegistryStats, getVersionPage } from "$lib/components/card/utils";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

// @ts-ignore
export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registryType } = await parent();

  // get metric names, parameters
  let versionPage = await getVersionPage(
    registryType,
    metadata.space,
    metadata.name
  );

  let versionStats = await getRegistryStats(
    registryType,
    metadata.name,
    metadata.space
  );

  return { versionPage, versionStats };
};
