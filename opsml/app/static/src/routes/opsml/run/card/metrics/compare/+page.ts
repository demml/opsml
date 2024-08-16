import {
  type CardRequest,
  type CardResponse,
  type CompareMetricPage,
  CardRegistries,
  type Card,
  type RunMetrics,
} from "$lib/scripts/types";
import { listCards } from "$lib/scripts/utils";
import { d } from "svelte-highlight/languages";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ parent, url }) {
  const data = await parent();

  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version: string = url.searchParams.get("version")!;

  let cardReq: CardRequest = {
    repository: repository,
    registry_type: CardRegistries.Run,
    limit: 50,
  };

  const cards: CardResponse = await listCards(cardReq);

  const cardMap: Map<string, Card> = new Map();

  for (let card of cards.cards) {
    if (card.uid !== data.metadata.uid) {
      cardMap.set(card.name, card);
    }
  }

  let runMetrics: RunMetrics = data.metrics;
  let referenceMetrics = new Map<string, number>();

  // iterate through runMetrics
  for (let metricName in runMetrics) {
    let metric = runMetrics[metricName];
    // get last value
    let metricValue = metric[metric.length - 1].value;
    referenceMetrics.set(metricName, metricValue);
  }

  let comparePageData: CompareMetricPage = {
    cards: cardMap,
    name: name,
    repository: repository,
    version: version,
    card: data.metadata,
    metricNames: data.metricNames,
    metrics: data.metrics,
    searchableMetrics: data.searchableMetrics,
    show: false,
    metricVizData: data.metricVizData,
    referenceMetrics: referenceMetrics,
  };

  return comparePageData;
}
