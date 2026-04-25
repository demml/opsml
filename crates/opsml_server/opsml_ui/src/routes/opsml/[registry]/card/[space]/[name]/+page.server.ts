import { setupRegistryPage } from "$lib/server/card/utils";
import {
  buildMockRegistryPageData,
  isRegistryPageEmpty,
} from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type { PageServerLoad } from "./$types";
import { redirect } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ parent, params, fetch, cookies }) => {
  const space = params.space;
  const name = params.name;
  let { registryType } = await parent();
  const useMockFallback = isDevMockEnabled(cookies);

  if (!registryType) {
    throw redirect(307, "/opsml/home");
  }

  try {
    let registryPage = await setupRegistryPage(registryType, space, name, fetch);

    if (useMockFallback && isRegistryPageEmpty(registryPage)) {
      return {
        page: buildMockRegistryPageData(registryType, space, name),
        selectedSpace: space,
        selectedName: name,
        mockMode: true,
      };
    }

    return {
      page: registryPage,
      selectedSpace: space,
      selectedName: name,
      mockMode: false,
    };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return {
      page: buildMockRegistryPageData(registryType, space, name),
      selectedSpace: space,
      selectedName: name,
      mockMode: true,
    };
  }
};
