import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { type Card } from "$lib/components/home/types";
import { RegistryType } from "$lib/utils";

interface RecentCards {
  modelcards: Card[];
  datacards: Card[];
  experimentcards: Card[];
  promptcards: Card[];
}

async function getCards(registry: string): Promise<Card[]> {
  const response = await opsmlClient.get(RoutePaths.LIST_CARDS, {
    registry_type: registry,
    limit: "10",
    sort_by_timestamp: "true",
  });
  const data = (await response.json()) as Card[];
  return data;
}

async function getRecentCards(): Promise<RecentCards> {
  const [modelcards, datacards, experimentcards, promptcards] =
    await Promise.all([
      getCards(RegistryType.Model),
      getCards(RegistryType.Data),
      getCards(RegistryType.Experiment),
      getCards(RegistryType.Prompt),
    ]);

  return {
    modelcards,
    datacards,
    experimentcards,
    promptcards,
  };
}

export { getRecentCards, getCards };
export type { RecentCards };
