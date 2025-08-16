import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { Metric, Parameter } from "../card_interfaces/experimentcard";
import { type CardQueryArgs } from "$lib/components/api/schema";
import type { Card } from "$lib/components/home/types";
import { RegistryType, getRegistryTableName } from "$lib/utils";
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
  ArtifactQueryArgs,
  ArtifactRecord,
} from "./types";
import { ArtifactType, CommonPaths } from "./types";
import { userStore } from "$lib/components/user/user.svelte";
import type { RawFile, RawFileRequest } from "$lib/components/files/types";

const BYTES_TO_MB = 1024 * 1024;

// Get the metric names for a given experiment
export async function getCardMetricNames(uid: string): Promise<string[]> {
  const request: GetMetricNamesRequest = {
    experiment_uid: uid,
  };

  const response = await opsmlClient.get(
    RoutePaths.EXPERIMENT_METRIC_NAMES,
    request,
    userStore.jwt_token
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
    request,
    userStore.jwt_token
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
    request,
    userStore.jwt_token
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
  space: string,
  name: string,
  currentVersion: string
): Promise<Experiment[]> {
  const params: CardQueryArgs = {
    registry_type: RegistryType.Experiment,
    name,
    space,
    limit: 50,
  };

  const response = await opsmlClient.get(
    RoutePaths.LIST_CARDS,
    params,
    userStore.jwt_token
  );
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
    uiMetricRequest,
    userStore.jwt_token
  );

  return (await response.json()) as GroupedMetrics;
}

/**
 * Extract all hardware metrics with timestamps in a single pass for UI rendering
 * Converts network bytes to kilobytes
 */
export function extractAllHardwareMetrics(metrics: HardwareMetrics[]): {
  createdAt: string[];
  cpuUtilization: number[];
  usedPercentMemory: number[];
  networkMbRecv: number[];
  networkMbSent: number[];
} {
  return {
    createdAt: metrics.map((m) => m.created_at),
    cpuUtilization: metrics.map((m) => m.cpu.cpu_percent_utilization),
    usedPercentMemory: metrics.map((m) => m.memory.used_percent_memory),
    networkMbRecv: metrics.map((m) => m.network.bytes_recv / BYTES_TO_MB),
    networkMbSent: metrics.map((m) => m.network.bytes_sent / BYTES_TO_MB),
  };
}

export async function getHardwareMetrics(
  uid: string
): Promise<UiHardwareMetrics> {
  const request: GetHardwareMetricRequest = {
    experiment_uid: uid,
  };

  const response = await opsmlClient.get(
    RoutePaths.HARDWARE_METRICS,
    request,
    userStore.jwt_token
  );
  let metrics = (await response.json()) as HardwareMetrics[];

  return extractAllHardwareMetrics(metrics);
}

export async function getExperimentFigures(
  uid: string,
  space: string,
  name: string,
  version: string
): Promise<RawFile[]> {
  const tableName = getRegistryTableName(RegistryType.Experiment);
  const path = `${tableName}/${space}/${name}/v${version}/${CommonPaths.Artifacts}/${CommonPaths.Figures}`;

  const request: RawFileRequest = {
    uid,
    path,
    registry_type: RegistryType.Experiment,
  };

  const response = await opsmlClient.post(
    RoutePaths.FILE_CONTENT_BATCH,
    request,
    userStore.jwt_token
  );

  return (await response.json()) as RawFile[];
}
