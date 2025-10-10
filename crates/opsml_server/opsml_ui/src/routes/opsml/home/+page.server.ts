import { getRegistryStats } from "$lib/server/card/utils";
import {
  getRecentCards,
  type HomePageStats,
} from "$lib/components/home/utils.server";
import { RegistryType } from "$lib/utils";
import type { PageServerLoad } from "./$types";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";

async function get_registry_stats(
  fetch: typeof globalThis.fetch,
  jwt_token: string | undefined
): Promise<HomePageStats> {
  const opsmlClient = createOpsmlClient(fetch, jwt_token);
  const [modelStats, dataStats, promptStats, experimentStats] =
    await Promise.all([
      getRegistryStats(opsmlClient, RegistryType.Model),
      getRegistryStats(opsmlClient, RegistryType.Data),
      getRegistryStats(opsmlClient, RegistryType.Prompt),
      getRegistryStats(opsmlClient, RegistryType.Experiment),
    ]);

  return {
    nbrModels: modelStats.stats.nbr_names,
    nbrData: dataStats.stats.nbr_names,
    nbrPrompts: promptStats.stats.nbr_names,
    nbrExperiments: experimentStats.stats.nbr_names,
  };
}

export const load: PageServerLoad = async ({ cookies, fetch }) => {
  let cards = await getRecentCards(fetch, cookies.get("jwt_token"));
  let stats = await get_registry_stats(fetch, cookies.get("jwt_token"));
  return { cards, stats };
};
