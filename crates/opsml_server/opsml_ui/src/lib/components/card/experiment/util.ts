import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { Metric, Parameter } from "../card_interfaces/experimentcard";
import { type CardQueryArgs } from "$lib/components/api/schema";
import type { BaseCard, Card } from "$lib/components/home/types";
import { RegistryType } from "$lib/utils";
import { promise } from "zod";
import type {
  GetMetricNamesRequest,
  GetMetricRequest,
  GetParameterRequest,
  GroupedMetrics,
  Experiment,
  UiMetricRequest,
  GetHardwareMetricRequest,
  HardwareMetrics,
  UiHardwareMetrics,
} from "./types";

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

export async function getRecentExperiments(
  repository: string,
  name: string,
  currentVersion: string
): Promise<Experiment[]> {
  const params: CardQueryArgs = {
    registry_type: RegistryType.Experiment,
    name,
    repository,
    limit: 50,
  };

  const response = await opsmlClient.get(RoutePaths.LIST_CARDS, params);
  const cards = (await response.json()) as Card[];

  return cards
    .filter((card) => {
      const version = card.data.version?.trim().toLowerCase();
      const current = currentVersion.trim().toLowerCase();
      return version && version !== current;
    })
    .map((card) => ({
      uid: card.data.uid,
      version: card.data.version,
    }));
}

export async function getGroupedMetrics(
  experiments: Experiment[],
  selectedMetrics: string[]
): Promise<GroupedMetrics> {
  let uiMetricRequest: UiMetricRequest = {
    experiments: experiments,
    metric_names: selectedMetrics,
  };

  // Process current card metrics
  const response = await opsmlClient.post(
    RoutePaths.EXPERIMENT_GROUPED_METRICS,
    uiMetricRequest
  );

  return (await response.json()) as GroupedMetrics;
}

/**
 * Extract all hardware metrics with timestamps in a single pass for UI rendering
 * Converts network bytes to kilobytes
 */
export function extractAllHardwareMetrics(metrics: HardwareMetrics[]): {
  created_at: string[];
  cpuUtilization: number[];
  usedPercentMemory: number[];
  networkKbRecv: number[];
  networkKbSent: number[];
} {
  return {
    created_at: metrics.map((m) => m.created_at),
    cpuUtilization: metrics.map((m) => m.cpu.cpu_percent_utilization),
    usedPercentMemory: metrics.map((m) => m.memory.used_percent_memory),
    networkKbRecv: metrics.map((m) => m.network.bytes_recv / 1024),
    networkKbSent: metrics.map((m) => m.network.bytes_sent / 1024),
  };
}

export async function getHardwareMetrics(
  uid: string
): Promise<UiHardwareMetrics> {
  const request: GetHardwareMetricRequest = {
    experiment_uid: uid,
  };

  const response = await opsmlClient.get(
    RoutePaths.EXPERIMENT_METRICS,
    request
  );
  let metrics = (await response.json()) as HardwareMetrics[];

  return extractAllHardwareMetrics(metrics);
}
