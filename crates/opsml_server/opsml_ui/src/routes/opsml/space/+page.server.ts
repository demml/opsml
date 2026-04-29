export const ssr = false;

import { buildMockSpaceStats } from "$lib/components/mock/opsmlMockData";
import { getAllSpaceStats } from "$lib/server/space/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  const useMockFallback = isDevMockEnabled(cookies);

  try {
    let spaces = await getAllSpaceStats(fetch);

    if (useMockFallback && spaces.stats.length === 0) {
      return { spaces: buildMockSpaceStats(), mockMode: true };
    }

    return { spaces, mockMode: false };
  } catch {
    if (useMockFallback) {
      return { spaces: buildMockSpaceStats(), mockMode: true };
    }

    return { spaces: { stats: [] }, mockMode: false };
  }
};
