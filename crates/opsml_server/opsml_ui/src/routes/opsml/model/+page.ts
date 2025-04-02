export const ssr = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { opsmlClient } from "$lib/components/api/client.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ url }) => {
  // get space for url if exists
  const space = url.searchParams.get("space") || undefined;
  const name = url.searchParams.get("name") || undefined;

  await opsmlClient.validateAuth(true);
  let registryPage = await setupRegistryPage(RegistryType.Model);
  return { page: registryPage, selectedSpace: space, selectedName: name };
};
