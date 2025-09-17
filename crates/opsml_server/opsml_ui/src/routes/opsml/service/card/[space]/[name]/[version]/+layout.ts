export const prerender = false;
export const ssr = false;
import { getRegistryPath, getRegistryTypeLowerCase } from "$lib/utils";
import { getCardMetadata } from "$lib/components/card/utils";

import type { LayoutLoad } from "./$types";
import { getCardReadMe } from "$lib/components/readme/util";
import type { ServiceCard } from "$lib/components/card/card_interfaces/servicecard";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

// @ts-ignore
export const load: LayoutLoad = async ({ params, parent }) => {
  await validateUserOrRedirect();
  const { registryType } = await parent();
  const { space, name, version } = params;

  let metadata = (await getCardMetadata(
    space,
    name,
    version,
    undefined,
    registryType
  )) as ServiceCard;

  let readme = await getCardReadMe(metadata.name, metadata.space, registryType);

  let activeTab = "card"; // Default active tab

  return { metadata, registryType, readme, activeTab };
};
