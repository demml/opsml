import { getDashboardStats } from "$lib/server/card/utils";
import {
  getRecentCards,
  type HomePageStats,
} from "$lib/components/home/utils.server";
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

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const [cards, stats] = await Promise.all([
      getRecentCards(fetch),
      get_registry_stats(fetch),
    ]);
    return { cards, stats };
  } catch {
    return {
      cards: [],
      stats: { nbrModels: 0, nbrData: 0, nbrPrompts: 0, nbrExperiments: 0 },
    };
  }
};
