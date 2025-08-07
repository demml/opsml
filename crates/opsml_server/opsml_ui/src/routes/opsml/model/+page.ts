export const ssr = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  const { registryType } = await parent();
  await validateUserOrRedirect();

  let registryPage = await setupRegistryPage(
    registryType,
    undefined,
    undefined
  );
  return {
    page: registryPage,
    selectedSpace: undefined,
    selectedName: undefined,
  };
};
