export const ssr = false;

import { setupRegistryPage } from "$lib/server/card/utils";

export const load: PageServerLoad = async ({ parent }) => {
  const { registryType } = await parent();

  let registryPage = await setupRegistryPage(
    registryType,
    undefined,
    undefined
  );

  return {
    page: registryPage,
    selectedSpace: undefined,
    selectedName: undefined,
  };
};
