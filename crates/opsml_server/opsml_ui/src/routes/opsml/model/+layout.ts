import { RegistryType } from "$lib/utils";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({}) => {
  return {
    registryType: RegistryType.Model,
  };
};
