import { setupRegistryPage } from "$lib/server/card/utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent, params, fetch }) => {
  const space = params.space;
  const name = undefined; // No name parameter in this route
  let { registryType } = await parent();
  let registryPage = await setupRegistryPage(registryType, space, name, fetch);
  return {
    page: registryPage,
    selectedSpace: space,
    selectedName: name,
  };
};
