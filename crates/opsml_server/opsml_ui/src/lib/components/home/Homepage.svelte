import { apiHandler } from "$lib/components/api/apiHandler";
import { RoutePaths } from "$lib/components/api/routes";
import type { Card, CardQueryArgs } from './types';

interface RecentCards {
  modelcards: Card[];
  datacards: Card[];
  experimentcards: Card[];
  auditcards: Card[];
  promptcards: Card[];
}

async function getCards(registry: string): Promise<Card[]> {
  const response = await apiHandler.post<Card[]>(
    CommonPaths.LIST_CARDS,
    {
      registry_type: registry,
      limit: 10,
      sort_by_timestamp: true
    } as CardQueryArgs,
    "application/json",
    { Accept: "application/json" }
  );

  return response;
}

async function getRecentCards(): Promise<RecentCards> {
  const modelcards = await getCards("model");
  const datacards = await getCards("data");
  const experimentcards = await getCards("experiment");
  const auditcards = await getCards("audit");
  const promptcards = await getCards("prompt");

  return {
    modelcards,
    datacards,
    experimentcards,
    auditcards,
    promptcards
  };
}

export { getRecentCards, getCards };
export type { Card, RecentCards };