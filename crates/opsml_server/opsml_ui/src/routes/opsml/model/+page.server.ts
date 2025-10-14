import { setupRegistryPage } from "$lib/server/card/utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent, fetch }) => {
  let { registryType } = await parent();
  let registryPage = await setupRegistryPage(
    registryType,
    undefined,
    undefined,
    fetch
  );

  return {
    page: registryPage,
    selectedSpace: undefined,
    selectedName: undefined,
  };
};
