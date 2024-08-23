import { d } from "svelte-highlight/languages";
import {
  type CardRequest,
  type CardResponse,
  type CompareMetricPage,
  CardRegistries,
  type Card,
  type RunMetrics,
  type RunCard,
  type ChartjsData,
} from "$lib/scripts/types";
import { listCards } from "$lib/scripts/utils";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ parent, url }) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
  const data = await parent();

  const name = (url as URL).searchParams.get("name") as string | undefined;

  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  const cardReq: CardRequest = {
    name,
    repository: repository!,
    registry_type: CardRegistries.Run,
    limit: 50,
    version: version,
  };

  const cards: CardResponse = await listCards(cardReq);

  const cardMap: Map<string, Card> = new Map();

  for (const card of cards.cards) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    if (card.uid !== data.metadata.uid) {
      cardMap.set(card.name, card);
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  const runMetrics = data.metrics as RunMetrics;
  const referenceMetrics = new Map<string, number>();

  // iterate through runMetrics
  for (const metricName in runMetrics) {
    const metric = runMetrics[metricName];
    // get last value
    const metricValue = metric[metric.length - 1].value;
    referenceMetrics.set(metricName, metricValue);
  }

  const comparePageData: CompareMetricPage = {
    cards: cardMap,
    name: name!,
    repository: repository!,
    version: version!,

    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    card: data.metadata as RunCard,

    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    metricNames: data.metricNames as string[],

    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    metrics: data.metrics as RunMetrics,

    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    searchableMetrics: data.searchableMetrics as string[],
    show: false,

    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    metricVizData: data.metricVizData as ChartjsData | undefined,
    referenceMetrics,
  };

  return comparePageData;
}
