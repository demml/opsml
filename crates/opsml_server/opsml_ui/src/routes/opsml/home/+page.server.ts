import { getDashboardStats } from "$lib/server/card/utils";
import {
  getRecentCards,
  type HomePageStats,
} from "$lib/components/home/utils.server";
import {
  buildMockHomeData,
  isRecentCardsEmpty,
} from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type { PageServerLoad } from "./$types";

async function get_registry_stats(
  fetch: typeof globalThis.fetch,
): Promise<HomePageStats> {
  const stats = await getDashboardStats(fetch);

  return {
    nbrModels: stats.stats.nbr_models,
    nbrData: stats.stats.nbr_data,
    nbrPrompts: stats.stats.nbr_prompts,
    nbrExperiments: stats.stats.nbr_experiments,
  };
}

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  const useMockFallback = isDevMockEnabled(cookies);

  try {
    const [cards, stats] = await Promise.all([
      getRecentCards(fetch),
      get_registry_stats(fetch),
    ]);

    if (useMockFallback && isRecentCardsEmpty(cards)) {
      return { ...buildMockHomeData(), mockMode: true };
    }

    return { cards, stats, mockMode: false };
  } catch {
    if (useMockFallback) {
      return { ...buildMockHomeData(), mockMode: true };
    }

    return {
      cards: {
        modelcards: [],
        datacards: [],
        experimentcards: [],
        promptcards: [],
      },
      stats: { nbrModels: 0, nbrData: 0, nbrPrompts: 0, nbrExperiments: 0 },
      mockMode: false,
    };
  }
};
