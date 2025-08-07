export const ssr = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ url }) => {
  await validateUserOrRedirect();

  let registryPage = await setupRegistryPage(
    RegistryType.Data,
    undefined,
    undefined
  );
  return {
    page: registryPage,
    selectedSpace: undefined,
    selectedName: undefined,
  };
};
