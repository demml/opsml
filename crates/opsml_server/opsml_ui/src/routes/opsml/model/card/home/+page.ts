export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, url }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry } = await parent();

  return { metadata, registry, content: "" };
};
