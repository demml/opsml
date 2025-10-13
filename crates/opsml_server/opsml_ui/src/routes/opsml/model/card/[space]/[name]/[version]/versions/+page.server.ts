import { getRegistryStats, getVersionPage } from "$lib/server/card/utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent, fetch }) => {
  const { metadata, registryType } = await parent();

  let [versionPage, versionStats] = await Promise.all([
    getVersionPage(fetch, registryType, metadata.space, metadata.name),
    getRegistryStats(fetch, registryType, metadata.name, [metadata.space]),
  ]);

  return { versionPage, versionStats };
};
