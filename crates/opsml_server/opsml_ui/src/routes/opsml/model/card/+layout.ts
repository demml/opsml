export const prerender = true;
export const ssr = false;
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { getRegistryTypeLowerCase, RegistryType } from "$lib/utils";
import { getCardMetadata, getUID } from "$lib/components/card/utils";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import { getCardReadMe } from "$lib/components/readme/util";
import { uiSettingsStore } from "$lib/components/settings/settings.svelte";

// @ts-ignore
export const load: LayoutServerLoad = async ({ url }) => {
  await validateUserOrRedirect();
  await uiSettingsStore.getSettings();

  let registry = RegistryType.Model;
  let uid = await getUID(url, registry);

  let metadata = (await getCardMetadata(uid, registry)) as ModelCard;

  let readme = await getCardReadMe(metadata.name, metadata.space, registry);

  let registryPath = getRegistryTypeLowerCase(registry);

  return { metadata, registry, readme, registryPath };
};
