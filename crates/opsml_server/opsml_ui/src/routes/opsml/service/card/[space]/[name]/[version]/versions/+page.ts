export const ssr = false;

import { getRegistryStats, getVersionPage } from "$lib/components/card/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
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
