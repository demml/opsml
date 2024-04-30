import {
  type FileExists,
  type CardRequest,
  type CardResponse,
  type RunCard,
  type MetricNames,
  type Metrics,
  type Metric,
  type Parameters,
  RegistryName,
} from "$lib/scripts/types";

import {
  listCards,
  getRunCard,
  getRunMetrics,
  getRunMetricNames,
  getRunParameters,
} from "$lib/scripts/utils";

export const ssr = false;
const opsmlRoot: string = `opsml-root:/${RegistryName.Run}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version: string | null = url.searchParams.get("version");
  const uid: string | null = url.searchParams.get("uid");
  const registry = "run";

  /** get last path from url */
  const tab = url.pathname.split("/").pop();

  const cardReq: CardRequest = {
    name,
    repository,
    registry_type: registry,
  };

  if (uid !== null) {
    cardReq.uid = uid;
  }

  if (version !== null) {
    cardReq.version = version;
  }

  // get card info
  const cards: CardResponse = await listCards(cardReq);
  const selectedCard = cards.cards[0];

  // get runcard
  const runCard: RunCard = await getRunCard(cardReq);

  // get runcard metrics
  const metricNames = await getRunMetricNames(runCard.uid);

  const metrics: Metric[] = [];
  if (metricNames.metric.length > 0) {
    // get first step for each metric
    // create loop for metricNames.metric

    for (const metric of metricNames.metric) {
      const metricData: Metrics = await getRunMetrics(runCard.uid, metric);
      metrics.push(metricData.metric[metricData.metric.length - 1]);
    }
  }

  // get parameters
  const parameters: Parameters = await getRunParameters(runCard.uid);

  return {
    registry,
    repository: selectedCard.repository,
    name: selectedCard.name,
    card: selectedCard,
    metadata: runCard,
    tabSet: tab,
    metricNames: metricNames.metric,
    metrics,
    parameters: parameters.parameter,
  };
}
