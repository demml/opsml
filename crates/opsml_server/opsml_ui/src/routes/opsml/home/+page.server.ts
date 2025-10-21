import { getRegistryStats } from "$lib/server/card/utils";
import {
  getRecentCards,
  type HomePageStats,
} from "$lib/components/home/utils.server";
import { RegistryType } from "$lib/utils";
import type { PageServerLoad } from "./$types";

async function get_registry_stats(
  fetch: typeof globalThis.fetch
): Promise<HomePageStats> {
  const [modelStats, dataStats, promptStats, experimentStats] =
    await Promise.all([
      getRegistryStats(fetch, RegistryType.Model),
      getRegistryStats(fetch, RegistryType.Data),
      getRegistryStats(fetch, RegistryType.Prompt),
      getRegistryStats(fetch, RegistryType.Experiment),
    ]);

  return {
    nbrModels: modelStats.stats.nbr_names,
    nbrData: dataStats.stats.nbr_names,
    nbrPrompts: promptStats.stats.nbr_names,
    nbrExperiments: experimentStats.stats.nbr_names,
  };
}

export const load: PageServerLoad = async ({ fetch }) => {
  let cards = await getRecentCards(fetch);
  let stats = await get_registry_stats(fetch);
  return { cards, stats };
};
