export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import { getDataProfile } from "$lib/components/card/data/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, readme, registryPath } = await parent();

  let dataProfile = metadata.metadata.interface_metadata.save_metadata
    ?.data_profile_uri
    ? await getDataProfile(metadata)
    : undefined;

  console.log("dataProfile", JSON.stringify(dataProfile));

  return { dataProfile };
};
