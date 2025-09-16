import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { type Card } from "$lib/components/home/types";
import { RegistryType } from "$lib/utils";
import { userStore } from "../user/user.svelte";

interface RecentCards {
  modelcards: Card[];
  datacards: Card[];
  experimentcards: Card[];
  promptcards: Card[];
}

interface HomePageStats {
  nbrModels: number;
  nbrData: number;
  nbrPrompts: number;
  nbrExperiments: number;
}

async function getCards(registry: string, space?: string): Promise<Card[]> {
  const response = await opsmlClient.get(
    RoutePaths.LIST_CARDS,
    {
      registry_type: registry,
      limit: "10",
      space: space,
      sort_by_timestamp: "true",
    },
    userStore.jwt_token
  );
  const data = (await response.json()) as Card[];
  return data;
}

async function getRecentCards(space?: string): Promise<RecentCards> {
  const [modelcards, datacards, experimentcards, promptcards] =
    await Promise.all([
      getCards(RegistryType.Model, space),
      getCards(RegistryType.Data, space),
      getCards(RegistryType.Experiment, space),
      getCards(RegistryType.Prompt, space),
    ]);

  return {
    modelcards,
    datacards,
    experimentcards,
    promptcards,
  };
}

export { getRecentCards, getCards };
export type { RecentCards, HomePageStats };
