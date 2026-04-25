import type { LayoutServerLoad } from "./$types";
import { loadCardLayout } from "$lib/server/card/layout";
import type { RegistryType } from "$lib/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";

// @ts-ignore
export const load: LayoutServerLoad = async ({ params, parent, fetch, cookies }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  return await loadCardLayout(
    registryType as RegistryType,
    space,
    name,
    version,
    fetch,
    isDevMockEnabled(cookies),
  );
};
