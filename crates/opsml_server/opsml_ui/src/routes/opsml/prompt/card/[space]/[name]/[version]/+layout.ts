export const prerender = false;
export const ssr = false;
import { getRegistryTypeLowerCase } from "$lib/utils";
import { getCardMetadata } from "$lib/components/card/utils";

import type { LayoutLoad } from "./$types";
import { getCardReadMe } from "$lib/components/readme/util";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";

// @ts-ignore
export const load: LayoutLoad = async ({ params, parent }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  let metadata = (await getCardMetadata(
    space,
    name,
    version,
    registryType
  )) as PromptCard;

  let readme = await getCardReadMe(metadata.name, metadata.space, registryType);

  let registryPath = getRegistryTypeLowerCase(registryType);
  let activeTab = "card"; // Default active tab

  return { metadata, registryType, readme, registryPath, activeTab };
};
