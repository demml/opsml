import type { LayoutServerLoad } from "./$types";
import { getRegistryFromString } from "$lib/utils";

export const load: LayoutServerLoad = async ({ params }) => {
  let registryType = getRegistryFromString(params.registry);
  return {
    registryType,
  };
};
