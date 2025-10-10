import { setupRegistryPage } from "$lib/server/card/utils";
import { logger } from "$lib/server/logger";
import { RegistryType } from "$lib/utils";

export const load: PageServerLoad = async ({ fetch }) => {
  let registryPage = await setupRegistryPage(
    RegistryType.Model,
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
