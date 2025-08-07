export const prerender = false;
export const ssr = false;
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { getRegistryTypeLowerCase, RegistryType } from "$lib/utils";
import { getCardMetadata, getUID } from "$lib/components/card/utils";

import type { LayoutLoad } from "./$types";
import type { DataCard } from "$lib/components/card/card_interfaces/datacard";
import { getCardReadMe } from "$lib/components/readme/util";

function getLastPartOfPath(path: string): string {
  const parts = path.split("/");
  return parts[parts.length - 1];
}

// @ts-ignore
export const load: LayoutLoad = async ({ params }) => {
  const { space, name, version } = params;

  await validateUserOrRedirect();

  console.log("Loading Data Card Layout");

  let registry = RegistryType.Data;
  //let uid = await getUID(space, name, version, registry);

  let metadata = (await getCardMetadata(
    space,
    name,
    version,
    registry
  )) as DataCard;

  let readme = await getCardReadMe(metadata.name, metadata.space, registry);

  let registryPath = getRegistryTypeLowerCase(registry);
  let activeTab = "card"; // Default active tab

  return { metadata, registry, readme, registryPath, activeTab };
};
