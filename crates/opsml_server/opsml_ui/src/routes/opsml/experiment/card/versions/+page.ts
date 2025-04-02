export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import { getVersions } from "$lib/components/card/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry } = await parent();

  // get metric names, parameters
  let versionPage = await getVersions(
    registry,
    metadata.repository,
    metadata.name
  );

  console.log("versionPage", JSON.stringify(versionPage));

  return { versionPage };
};
