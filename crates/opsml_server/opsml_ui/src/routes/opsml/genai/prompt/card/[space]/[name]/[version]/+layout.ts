export const prerender = false;
export const ssr = false;
import { getCardMetadata } from "$lib/components/card/utils";

import type { LayoutLoad } from "./$types";
import { getCardReadMe } from "$lib/components/readme/util";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

// @ts-ignore
export const load: LayoutLoad = async ({ params, parent }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  let metadata = (await getCardMetadata(
    space,
    name,
    version,
    undefined,
    registryType
  )) as PromptCard;

  console.log("Prompt Card Metadata:", metadata);

  let readme = await getCardReadMe(metadata.name, metadata.space, registryType);

  let activeTab = "card"; // Default active tab

  return { metadata, registryType, readme, activeTab };
};
