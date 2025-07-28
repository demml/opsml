export const ssr = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ url }) => {
  // get space for url if exists
  const space: string | undefined = url.searchParams.get("space") || undefined;
  const name = url.searchParams.get("name") || undefined;

  await validateUserOrRedirect();
  let registryPage = await setupRegistryPage(RegistryType.Prompt, space, name);
  return { page: registryPage, selectedSpace: space, selectedName: name };
};
