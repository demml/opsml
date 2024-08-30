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
import { createMetricVizData, listCards } from "$lib/scripts/utils";

export async function loadComparePageData(
  data: any,
  url: URL
): Promise<CompareMetricPage> {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call

  const name = url.searchParams.get("name") as string | undefined;

  const repository = url.searchParams.get("repository") as string | undefined;

  const version = url.searchParams.get("version") as string | undefined;

  // want to pull in all cards for this repository
  const cardReq: CardRequest = {
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

  let metricVizData: ChartjsData | undefined = undefined;

  if (Object.keys(data.metrics).length > 0) {
    metricVizData = createMetricVizData(data.metrics, "bar");
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

    metricVizData: metricVizData,
    referenceMetrics,
  };

  return comparePageData;
}
