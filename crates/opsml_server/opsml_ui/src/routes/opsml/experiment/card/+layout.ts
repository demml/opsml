export const prerender = true;
export const ssr = false;
import { opsmlClient } from "$lib/components/api/client.svelte";
import { getRegistryTypeLowerCase, RegistryType } from "$lib/utils";
import { getCardMetadata, getUID } from "$lib/components/card/utils";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";
import { getCardReadMe } from "$lib/components/readme/util";
import type { ExperimentCard } from "$lib/components/card/card_interfaces/experimentcard";

// @ts-ignore
export const load: LayoutServerLoad = async ({ url }) => {
  console.log("loading experiment");
  await opsmlClient.validateAuth(true);

  let registry = RegistryType.Experiment;
  let uid = await getUID(url, registry);

  let metadata = (await getCardMetadata(uid, registry)) as ExperimentCard;

  let readme = await getCardReadMe(
    metadata.name,
    metadata.repository,
    registry
  );

  let registryPath = getRegistryTypeLowerCase(registry);

  return { metadata, registry, readme, registryPath };
};
