import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { Metric, Parameter } from "../card_interfaces/experimentcard";
import { type CardQueryArgs } from "$lib/components/api/schema";
import type { BaseCard, Card } from "$lib/components/home/types";
import { RegistryType } from "$lib/utils";

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
