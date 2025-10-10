import { setupRegistryPage } from "$lib/server/card/utils";
import { RegistryType } from "$lib/utils";

export const load: PageServerLoad = async ({ fetch }) => {
  let registryPage = await setupRegistryPage(
    RegistryType.Service,
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
