import {
  type CardRequest,
  type CardResponse,
  type RunCard,
  type Metric,
  type Parameters,
  type RunMetrics,
  type ChartjsData,
  type TableMetric,
  type RunPageReturn,
} from "$lib/scripts/types";

import {
  listCards,
  getRunCard,
  getRunMetrics,
  getRunMetricNames,
  getRunParameters,
} from "$lib/scripts/utils";
import { RunCardStore } from "$routes/store.js";

export const ssr = false;

/** @type {import('./$types').LayoutLoad} */
export async function load({ url }): Promise<RunPageReturn> {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  const uid = (url as URL).searchParams.get("uid") as string | undefined;
  const registry = "run";

  /** get last path from url */
  //const tab: string | undefined = (url as URL).pathname.split("/").pop();
  RunCardStore.reset();

  const cardReq: CardRequest = {
    name,
    repository: repository!,
    registry_type: registry,
    version: version,
    uid,
  };

  // get card info
  const cards: CardResponse = await listCards(cardReq);
  const selectedCard = cards.cards[0];

  // get runcard
  const runCard: RunCard = await getRunCard(cardReq);

  // get runcard metrics
  const metricNames = await getRunMetricNames(runCard.uid);

  // dictionary to store metrics
  let metrics: RunMetrics = {};

  if (metricNames.metric.length > 0) {
    // get first step for each metric
    metrics = await getRunMetrics(runCard.uid, metricNames.metric);
  }

  // List of metrics for table
  const tableMetrics: Metric[] | Map<string, TableMetric[]> = [];

  // get last entry for each metric in metrics

  Object.keys(metrics).forEach((metric) => {
    const lastEntry = metrics[metric][metrics[metric].length - 1];
    tableMetrics.push(lastEntry);
  });

  // get parameters
  const parameters: Parameters = await getRunParameters(runCard.uid);

  const searchableMetrics = metricNames.metric;

  // add "select all" to searchableMetrics
  searchableMetrics.unshift("select all");

  // check if "run/card/metrics" exists in url
  let metricVizData: ChartjsData | undefined;

  console.log("loaded");

  return {
    registry,
    repository: selectedCard.repository,
    name: selectedCard.name,
    card: selectedCard,
    metadata: runCard,
    metricNames: metricNames.metric,
    metrics,
    tableMetrics,
    parameters: parameters.parameter,
    searchableMetrics,
    metricVizData,
    parsedMetrics: undefined,
  };
}
