import { setupRegistryPage } from "$lib/server/card/utils";
import type { PageServerLoad } from "./$types";
import { RegistryType } from "$lib/utils";

export const load: PageServerLoad = async ({ params, fetch }) => {
  const space = params.space;
  const name = undefined; // No name parameter in this route

  let registryPage = await setupRegistryPage(
    RegistryType.Data,
    space,
    name,
    fetch
  );
  return {
    page: registryPage,
    selectedSpace: space,
    selectedName: name,
  };
};
