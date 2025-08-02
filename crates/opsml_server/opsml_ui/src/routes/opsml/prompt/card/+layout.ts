export const prerender = true;
export const ssr = false;
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { getRegistryTypeLowerCase, RegistryType } from "$lib/utils";
import { getCardMetadata, getUID } from "$lib/components/card/utils";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import { getCardReadMe } from "$lib/components/readme/util";

function getLastPartOfPath(path: string): string {
  const parts = path.split("/");
  return parts[parts.length - 1];
}

// @ts-ignore
export const load: LayoutServerLoad = async ({ url }) => {
  await validateUserOrRedirect();

  let registry = RegistryType.Prompt;
  let uid = await getUID(url, registry);

  let metadata = (await getCardMetadata(uid, registry)) as PromptCard;

  let readme = await getCardReadMe(metadata.name, metadata.space, registry);

  let registryPath = getRegistryTypeLowerCase(registry);

  let activeTab = getLastPartOfPath(url.pathname);

  return { metadata, registry, readme, registryPath, activeTab };
};
