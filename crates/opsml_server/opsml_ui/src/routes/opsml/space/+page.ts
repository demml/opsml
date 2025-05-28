export const ssr = false;

import { getAllSpaces, setupRegistryPage } from "$lib/components/card/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({}) => {
  await validateUserOrRedirect();

  // get space for url if exists
  let spaces = await getAllSpaces();

  console.log("Spaces loaded:", spaces);

  return { spaces };
};
