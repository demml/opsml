import {
  type registryStats,
  type registryPage,
  type repositories,
  type CardRequest,
  type CardResponse,
  type CompareMetricPage,
  CardRegistries,
  type RunCard,
} from "$lib/scripts/types";
import { listCards } from "$lib/scripts/utils";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ parent, url }) {
  const data = await parent();

  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version: string = url.searchParams.get("version")!;

  let cardReq: CardRequest = {
    name: name,
    repository: repository,
    registry_type: CardRegistries.Run,
  };

  const cards: CardResponse = await listCards(cardReq);

  let comparePageData: CompareMetricPage = {
    cards: cards.cards,
    name: name,
    repository: repository,
    version: version,
    card: data.metadata,
    metricNames: data.metricNames,
    metrics: data.metrics,
    searchableMetrics: data.searchableMetrics,
  };

  return comparePageData;
}
