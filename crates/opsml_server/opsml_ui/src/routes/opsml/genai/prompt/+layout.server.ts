import { RegistryType } from "$lib/utils";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
  return {
    registryType: RegistryType.Prompt,
  };
};
