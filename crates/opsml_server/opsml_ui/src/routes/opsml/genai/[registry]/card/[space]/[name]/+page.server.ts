import { setupRegistryPage } from "$lib/server/card/utils";
import type { PageServerLoad } from "./$types";
import { redirect } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ parent, params, fetch }) => {
  const space = params.space;
  const name = params.name;
  let { registryType } = await parent();

  if (!registryType) {
    throw redirect(307, "/opsml/home");
  }

  let registryPage = await setupRegistryPage(registryType, space, name, fetch);
  return { page: registryPage, selectedSpace: space, selectedName: name };
};
