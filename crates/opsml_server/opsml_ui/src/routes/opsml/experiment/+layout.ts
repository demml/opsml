export const prerender = false;
export const ssr = false;
import { RegistryType } from "$lib/utils";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({}) => {
  return {
    registryType: RegistryType.Experiment,
  };
};
