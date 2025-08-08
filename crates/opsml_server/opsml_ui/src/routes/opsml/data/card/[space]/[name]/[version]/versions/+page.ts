export const ssr = false;

import { getRegistryStats, getVersionPage } from "$lib/components/card/utils";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registry } = await parent();

  // get metric names, parameters
  let versionPage = await getVersionPage(
    registry,
    metadata.space,
    metadata.name
  );

  let versionStats = await getRegistryStats(
    registry,
    metadata.name,
    metadata.space
  );

  return { registry, versionPage, versionStats };
};
