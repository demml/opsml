import type { LayoutServerLoad } from "./$types";
import { getRegistryFromString } from "$lib/utils";

export const load: LayoutServerLoad = async ({ params }) => {
  console.log("Params received in layout server load:", params);
  let registryType = getRegistryFromString(params.registry);
  return {
    registryType,
  };
};
