import { opsmlClient } from "$lib/components/api/client.svelte";
import { getRegistryStats } from "$lib/components/card/utils";
import {
  getRecentCards,
  type HomePageStats,
} from "$lib/components/home/utils.server";
import { RegistryType } from "$lib/utils";
import type { PageServerLoad } from "./$types";

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

export const load: PageServerLoad = async ({ cookies }) => {
  opsmlClient.setToken(cookies.get("jwt_token"));

  let cards = await getRecentCards();
  let stats = await get_registry_stats();

  return { cards, stats };
};
