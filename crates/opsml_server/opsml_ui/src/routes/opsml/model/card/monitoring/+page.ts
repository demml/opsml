export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";
import { getDriftProfiles } from "$lib/components/monitoring/util";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, registryPath } = await parent();

  let profiles = await getDriftProfiles(metadata);

  console.log(profiles);

  return { profiles };
};
