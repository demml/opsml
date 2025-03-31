import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { Metric, Parameter } from "../card_interfaces/experimentcard";
import { type CardQueryArgs } from "$lib/components/api/schema";
import type { BaseCard, Card } from "$lib/components/home/types";
import { RegistryType } from "$lib/utils";
import { promise } from "zod";
import type { MetricData } from "$lib/components/viz/linechart";

export interface GetMetricRequest {
  experiment_uid: string;
  names: string[];
}

export interface GetMetricNamesRequest {
  experiment_uid: string;
}

export interface GetParameterRequest {
  experiment_uid: string;
  names: string[];
}

// Get the metric names for a given experiment
export async function getCardMetricNames(uid: string): Promise<string[]> {
  const request: GetMetricNamesRequest = {
    experiment_uid: uid,
  };

  const response = await opsmlClient.get(
    RoutePaths.EXPERIMENT_METRIC_NAMES,
    request
  );
  return (await response.json()) as string[];
}

export async function getCardParameters(uid: string): Promise<Parameter[]> {
  const request: GetParameterRequest = {
    experiment_uid: uid,
    names: [],
  };

  const response = await opsmlClient.post(
    RoutePaths.EXPERIMENT_PARAMETERS,
    request
  );
  return (await response.json()) as Parameter[];
}

// Get the metrics for a given experiment
export async function getCardMetrics(
  uid: string,
  names: string[]
): Promise<Metric[]> {
  const request: GetMetricRequest = {
    experiment_uid: uid,
    names: names,
  };

  const response = await opsmlClient.post(
    RoutePaths.EXPERIMENT_METRICS,
    request
  );
  return (await response.json()) as Metric[];
}

// Parse the metrics into a map
export function parseMetricsToMap(metrics: Metric[]): Map<string, Metric[]> {
  const metricsMap = new Map<string, Metric[]>();
  for (const metric of metrics) {
    const metricName = metric.name;
    if (!metricsMap.has(metricName)) {
      metricsMap.set(metricName, []);
    }
    metricsMap.get(metricName)?.push(metric);
  }
  return metricsMap;
}

export async function getCardVersions(
  repository: string,
  name: string,
  currentVersion: string
): Promise<BaseCard[]> {
  const params: CardQueryArgs = {
    registry_type: RegistryType.Experiment,
    name: name,
    repository: repository,
    limit: 50,
  };

  const response = await opsmlClient.get(RoutePaths.LIST_CARDS, params);
  const cards = (await response.json()) as Card[];

  // extract data from the card and filter out the current version
  const filteredCardData = cards
    .filter(
      (card) =>
        card.data.version &&
        card.data.version.trim().toLowerCase() !==
          currentVersion.trim().toLowerCase()
    )
    .map((card) => card.data);

  // @ts-ignore
  return filteredCardData;
}

export async function processCardMetrics(
  card: BaseCard,
  selectedMetrics: string[],
  metricData: MetricData
): Promise<void> {
  // get grouped metrics

  const metrics = await getCardMetrics(card.uid, selectedMetrics);
  const parsedMetrics = parseMetricsToMap(metrics);

  for (const [metricName, metricArray] of parsedMetrics.entries()) {
    if (!metricData[metricName]) {
      metricData[metricName] = {
        x: metricArray.map((m) => m.step ?? metricArray.indexOf(m)), // use step if available, fallback to index
        y: {},
      };
    }

    // Sort metrics by step to ensure correct ordering
    const sortedMetrics = [...metricArray].sort(
      (a, b) => (a.step ?? 0) - (b.step ?? 0)
    );

    metricData[metricName].y[card.name] = sortedMetrics.map((m) => m.value);
  }
}

export async function preparePlotData(
  currentCard: BaseCard,
  selectedMetrics: string[],
  selectedCards: BaseCard[]
): Promise<MetricData> {
  const metricData: MetricData = {};

  // Process current card metrics
  await processCardMetrics(currentCard, selectedMetrics, metricData);

  // Process selected cards metrics
  for (const card of selectedCards) {
    await processCardMetrics(card, selectedMetrics, metricData);
  }

  return metricData;
}
