import { getRegistryStats, getVersionPage } from "$lib/server/card/utils";
import {
  buildMockVersionPage,
  buildMockVersionStats,
} from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent, fetch, cookies }) => {
  const { metadata, registryType } = await parent();
  const useMockFallback = isDevMockEnabled(cookies);

  try {
    let [versionPage, versionStats] = await Promise.all([
      getVersionPage(fetch, registryType, metadata.space, metadata.name),
      getRegistryStats(fetch, registryType, metadata.name, [metadata.space]),
    ]);

    return { versionPage, versionStats, mockMode: false };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return {
      versionPage: buildMockVersionPage(metadata.space, metadata.name),
      versionStats: buildMockVersionStats(),
      mockMode: true,
    };
  }
};
