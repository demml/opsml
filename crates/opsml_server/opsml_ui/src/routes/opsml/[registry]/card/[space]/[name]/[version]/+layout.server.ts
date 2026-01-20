import type { LayoutServerLoad } from "./$types";
import { loadCardLayout, loadServiceCardLayout } from "$lib/server/card/layout";
import { RegistryType } from "$lib/utils";
import { logger } from "$lib/server/logger";

export const load: LayoutServerLoad = async ({ params, parent, fetch }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  if (registryType === RegistryType.Service) {
    return await loadServiceCardLayout(registryType, space, name, fetch);
  }

  return await loadCardLayout(
    registryType as RegistryType,
    space,
    name,
    version,
    fetch,
  );
};
