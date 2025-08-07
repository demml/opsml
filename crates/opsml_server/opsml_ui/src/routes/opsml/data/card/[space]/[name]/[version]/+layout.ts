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
export const load: LayoutLoad = async ({ url, params }) => {
  const { space, name, version } = params;

  await validateUserOrRedirect();

  let registry = RegistryType.Data;
  let uid = await getUID(space, name, version, registry);

  let metadata = (await getCardMetadata(uid, registry)) as DataCard;

  let readme = await getCardReadMe(metadata.name, metadata.space, registry);

  let registryPath = getRegistryTypeLowerCase(registry);

  let activeTab = getLastPartOfPath(url.pathname);

  return { metadata, registry, readme, registryPath, activeTab };
};
