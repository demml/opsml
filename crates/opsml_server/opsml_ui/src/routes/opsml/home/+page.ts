import type { RegistryStatsResponse } from "$lib/components/card/types";
import { getRegistryStats } from "$lib/components/card/utils";
import { getRecentCards, type HomePageStats } from "$lib/components/home/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import { RegistryType } from "$lib/utils";
import type { Home } from "lucide-svelte";
import type { PageLoad } from "./$types";

async function get_registry_stats(): Promise<HomePageStats> {
  const [modelStats, dataStats, promptStats, experimentStats] =
    await Promise.all([
      getRegistryStats(RegistryType.Model),
      getRegistryStats(RegistryType.Data),
      getRegistryStats(RegistryType.Prompt),
      getRegistryStats(RegistryType.Experiment),
    ]);

  return {
    nbrModels: modelStats.stats.nbr_names,
    nbrData: dataStats.stats.nbr_names,
    nbrPrompts: promptStats.stats.nbr_names,
    nbrExperiments: experimentStats.stats.nbr_names,
  };
}

export const load: PageLoad = async ({}) => {
  await validateUserOrRedirect();

  let cards = await getRecentCards();
  let stats = await get_registry_stats();

  return { cards: cards, stats: stats };
};
