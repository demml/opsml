export const ssr = false;
export const prerender = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ params }) => {
  await validateUserOrRedirect();

  const space = params.space;
  const name = undefined; // No name parameter in this route

  let registryPage = await setupRegistryPage(RegistryType.Data, space, name);
  return { page: registryPage, selectedSpace: space, selectedName: name };
};
