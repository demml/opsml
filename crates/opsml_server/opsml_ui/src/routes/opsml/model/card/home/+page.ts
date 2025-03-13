export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import { getCardReadMe } from "$lib/components/readme/util";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, url }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, readme } = await parent();

  return { metadata, registry, readme };
};
