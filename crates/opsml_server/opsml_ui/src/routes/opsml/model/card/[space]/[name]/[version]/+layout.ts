export const prerender = false;
export const ssr = false;
import { getRegistryTypeLowerCase } from "$lib/utils";
import { getCardMetadata } from "$lib/components/card/utils";

import type { LayoutLoad } from "./$types";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import { getCardReadMe } from "$lib/components/readme/util";

// @ts-ignore
export const load: LayoutLoad = async ({ params, parent }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  let metadata = (await getCardMetadata(
    space,
    name,
    version,
    registryType
  )) as ModelCard;

  let readme = await getCardReadMe(metadata.name, metadata.space, registryType);

  let registryPath = getRegistryTypeLowerCase(registryType);
  let activeTab = "card"; // Default active tab

  return { metadata, registryType, readme, registryPath, activeTab };
};
