import { setupRegistryPage } from "$lib/server/card/utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({
  params,
  parent,
  cookies,
  fetch,
}) => {
  const { registryType } = await parent();

  const space = params.space;
  const name = undefined; // No name parameter in this route

  let registryPage = await setupRegistryPage(
    registryType,
    space,
    name,
    fetch,
    cookies.get("jwt_token")
  );
  return {
    page: registryPage,
    selectedSpace: space,
    selectedName: name,
    fetch,
  };
};
