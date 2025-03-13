export const prerender = true;
export const ssr = false;
import { opsmlClient } from "$lib/components/api/client.svelte";
import { RegistryType } from "$lib/utils";
import { getCardMetadata, getUID } from "$lib/components/card/utils";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import { getCardReadMe } from "$lib/components/readme/util";

// @ts-ignore
export const load: LayoutServerLoad = async ({ url }) => {
  await opsmlClient.validateAuth(true);

  let registry = RegistryType.Model;
  let uid = await getUID(url, registry);
  let metadata = (await getCardMetadata(uid, registry)) as ModelCard;
  let readme = await getCardReadMe(
    metadata.name,
    metadata.repository,
    registry
  );
  return { metadata, registry, readme };
};
