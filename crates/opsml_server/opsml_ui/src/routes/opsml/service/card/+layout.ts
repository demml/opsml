export const prerender = true;
export const ssr = false;
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { getRegistryTypeLowerCase, RegistryType } from "$lib/utils";
import { getCardMetadata, getUID } from "$lib/components/card/utils";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";
import type { ServiceCard } from "$lib/components/card/card_interfaces/servicecard";
import { getCardReadMe } from "$lib/components/readme/util";

// @ts-ignore
export const load: LayoutServerLoad = async ({ url }) => {
  await validateUserOrRedirect();

  let registry = RegistryType.Deck;
  let uid = await getUID(url, registry);

  let metadata = (await getCardMetadata(uid, registry)) as ServiceCard;

  let registryPath = getRegistryTypeLowerCase(registry);

  console.log(JSON.stringify(metadata, null, 2));

  return { metadata, registry, registryPath };
};
