export const ssr = false;

import type { PageLoad } from "./$types";
import { getCardParameters } from "$lib/components/card/experiment/util";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registryType, readme, registryPath } = await parent();

  let parameters = await getCardParameters(metadata.uid);

  return { metadata, registryType, readme, registryPath, parameters };
};
