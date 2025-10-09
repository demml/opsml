export const ssr = false;
export const prerender = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ params, parent }) => {
  const { registryType } = await parent();

  const space = params.space;
  const name = params.name;

  let registryPage = await setupRegistryPage(registryType, space, name);
  return { page: registryPage, selectedSpace: space, selectedName: name };
};
