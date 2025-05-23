export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import { getRegistryStats, getVersionPage } from "$lib/components/card/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth();

  const { metadata, registry } = await parent();

  // get metric names, parameters
  let versionPage = await getVersionPage(
    registry,
    metadata.space,
    metadata.name
  );

  console.log("versionPage", JSON.stringify(versionPage));

  let versionStats = await getRegistryStats(
    registry,
    metadata.name,
    metadata.space
  );

  return { registry, versionPage, versionStats };
};
