import { setupRegistryPage } from "$lib/server/card/utils";

export const load: PageServerLoad = async ({ parent, cookies, fetch }) => {
  const { registryType } = await parent();

  let registryPage = await setupRegistryPage(
    registryType,
    undefined,
    undefined,
    fetch,
    cookies.get("jwt_token")
  );

  return {
    page: registryPage,
    selectedSpace: undefined,
    selectedName: undefined,
  };
};
