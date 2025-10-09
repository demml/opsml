export const ssr = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";

// @ts-ignore
export const load: PageLoad = async ({ parent }) => {
  const { registryType } = await parent();

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
