export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, readme, registryPath } = await parent();
  console.log(JSON.stringify(metadata));

  return { metadata, registry, readme, registryPath };
};
