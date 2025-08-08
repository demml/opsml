export const ssr = false;

import type { PageLoad } from "./$types";
import { getCardParameters } from "$lib/components/card/experiment/util";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType, readme, registryPath } = await parent();

  let parameters = await getCardParameters(metadata.uid);

  return { metadata, registryType, readme, registryPath, parameters };
};
