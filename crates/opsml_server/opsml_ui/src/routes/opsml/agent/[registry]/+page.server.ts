import { setupRegistryPage } from "$lib/server/card/utils";
import { getRegistryFromString, RegistryType } from "$lib/utils";
import {
  buildMockRegistryPageData,
  isRegistryPageEmpty,
} from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad, EntryGenerator } from "./$types";

export const entries: EntryGenerator = () => {
  return [
    { registry: "model" },
    { registry: "data" },
    { registry: "experiment" },
    { registry: "service" },
  ];
};

export const load: PageServerLoad = async ({ parent, fetch, cookies }) => {
  let { registryType } = await parent();
  const useMockFallback = isDevMockEnabled(cookies);

  if (!registryType) {
    throw redirect(307, "/opsml/home");
  }

  try {
    let registryPage = await setupRegistryPage(
      registryType,
      undefined,
      undefined,
      fetch
    );

    if (useMockFallback && isRegistryPageEmpty(registryPage)) {
      return {
        page: buildMockRegistryPageData(registryType),
        selectedSpace: undefined,
        selectedName: undefined,
        mockMode: true,
      };
    }

    return {
      page: registryPage,
      selectedSpace: undefined,
      selectedName: undefined,
      mockMode: false,
    };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return {
      page: buildMockRegistryPageData(registryType),
      selectedSpace: undefined,
      selectedName: undefined,
      mockMode: true,
    };
  }
};
