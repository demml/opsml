import { RoutePaths } from "$lib/components/api/routes";
import { type Card } from "$lib/components/home/types";
import { createOpsmlClient } from "$lib/server/api/opsmlClient";
import { RegistryType } from "$lib/utils";

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

async function getCards(
  opsmlClient: ReturnType<typeof createOpsmlClient>,
  registry: string,
  space?: string
): Promise<Card[]> {
  const response = await opsmlClient.get(RoutePaths.LIST_CARDS, {
    registry_type: registry,
    limit: "10",
    space: space,
    sort_by_timestamp: "true",
  });
  const data = (await response.json()) as Card[];
  return data;
}

async function getRecentCards(
  fetch: typeof globalThis.fetch,
  jwt_token: string | undefined,
  space?: string
): Promise<RecentCards> {
  const opsmlClient = createOpsmlClient(fetch, jwt_token);
  const [modelcards, datacards, experimentcards, promptcards] =
    await Promise.all([
      getCards(opsmlClient, RegistryType.Model, space),
      getCards(opsmlClient, RegistryType.Data, space),
      getCards(opsmlClient, RegistryType.Experiment, space),
      getCards(opsmlClient, RegistryType.Prompt, space),
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
