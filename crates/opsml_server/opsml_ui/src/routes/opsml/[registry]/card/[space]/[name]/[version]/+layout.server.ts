import type { LayoutServerLoad } from "./$types";
import { loadCardLayout } from "$lib/server/card/layout";
import type { RegistryType } from "$lib/utils";

// @ts-ignore
export const load: LayoutServerLoad = async ({ params, parent, fetch }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  return await loadCardLayout(
    registryType as RegistryType,
    space,
    name,
    version,
    fetch,
  );
};
