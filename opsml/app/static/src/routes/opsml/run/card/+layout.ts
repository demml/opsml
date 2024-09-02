import {
  type FileExists,
  type CardRequest,
  type CardResponse,
  type RunCard,
  type MetricNames,
  type Metrics,
  type Metric,
  type Parameters,
  type RunMetrics,
  type ChartjsData,
  type TableMetric,
  type ParsedHardwareMetrics,
  RegistryName,
  type HardwareMetricsResponse,
} from "$lib/scripts/types";

import {
  listCards,
  getRunCard,
  getRunMetrics,
  getRunMetricNames,
  getRunParameters,
  createMetricVizData,
  getHardwareMetrics,
  parseHardwareMetrics,
} from "$lib/scripts/utils";

export const ssr = false;
export const prerender = false;

const opsmlRoot: string = `opsml-root:/${RegistryName.Run}`;

/** @type {import('./$types').LayoutLoad} */
export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  const registry = "run";

  /** get last path from url */
  //const tab: string | undefined = (url as URL).pathname.split("/").pop();
  const tab: string = "home";

  const cardReq: CardRequest = {
    name,
    repository: repository!,
    registry_type: registry,
    version: version!,
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

  if (tab === "metrics" || tab === "compare") {
    // create chartjs data
    metricVizData = createMetricVizData(metrics, "bar");
    // let cardMap = new Map<string, RunMetrics>();
    // cardMap.set(selectedCard.name, metrics);
    // tableMetrics = metricsToTable(cardMap, metricNames.metric);
  }

  let parsedMetrics: ParsedHardwareMetrics | undefined;

  if (tab === "hardware") {
    const hardwareVizData = await getHardwareMetrics(runCard.uid);

    // process hardware metrics
    if (hardwareVizData.metrics.length > 0) {
      parsedMetrics = parseHardwareMetrics(hardwareVizData.metrics);
    }
  }

  console.log("loaded");

  return {
    registry,
    repository: selectedCard.repository,
    name: selectedCard.name,
    card: selectedCard,
    metadata: runCard,
    tabSet: tab,
    metricNames: metricNames.metric,
    metrics,
    tableMetrics,
    parameters: parameters.parameter,
    searchableMetrics,
    metricVizData,
    parsedMetrics,
  };
}
