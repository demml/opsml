import { setupRegistryPage } from "$lib/server/card/utils";
import type { PageServerLoad } from "./$types";
import { RegistryType } from "$lib/utils";

export const load: PageServerLoad = async ({ params, fetch }) => {
  const space = params.space;
  const name = params.name;
  let registryPage = await setupRegistryPage(
    RegistryType.Mcp,
    space,
    name,
    fetch
  );
  return { page: registryPage, selectedSpace: space, selectedName: name };
};
